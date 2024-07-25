import requests
import json
import base64
import argparse
import cohere
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

# OpenAI API Key
# OPENAI_API_KEY = 'sk-None-LvNsqypaMW2yIvPSA9R8T3BlbkFJte8SFRMxh2LNPAlg8ERs'
OPENAI_API_KEY = 'sk-proj-2VVsetSPUZAR9jbBmTKoT3BlbkFJVd86BXtEzpRU133a8nEI'
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}
COHERE_API_KEY = "h1XkPfFdekjbWlPdK8kTG1VFCy4gjBDDYpa5KpY2"

class RateLimitError(Exception):
    pass

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

@retry(retry=retry_if_exception_type(RateLimitError), wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(6))
def get_embedding(text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=HEADERS,
            json={"input": [text], "model": "text-embedding-ada-002"}
        )
        if response.status_code == 429:
            print("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")
        response.raise_for_status()
        return response.json()['data'][0]['embedding']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get embedding: {e}")

@retry(retry=retry_if_exception_type(RateLimitError), wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(6))
def generate_query_from_image_and_text(image_path, user_query=None):
    try:
        base64_image = encode_image(image_path)
        messages = [{
                    "role": "system",
                    "content": "You are an AI that helps generate text queries from images and text for an Elden Ring RAG system."
                    }]
        
        content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]

        if user_query:
            content.append({"type": "text", "text": f"Query: {user_query}"})

        content.append({"type": "text", "text": f"Generate a query for an Elden Ring RAG system given the information."})
        messages.append({"role": "user", "content": content})
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 300, "temperature": 0.5}
        )
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to generate query from image and text: {e}")

@retry(retry=retry_if_exception_type(RateLimitError), wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(6))
def submit_query_to_gpt4(context_file, question):
    with open(context_file, 'r') as f:
        results = json.load(f)

    context_messages = []
    if 'results' in results:
        for result in results['results']:
            context_messages.append({"role": "system", "content": result})
    
    context_messages.append({"role": "user", "content": question})

    data = {
        'model': 'gpt-4-turbo',
        'messages': context_messages,
        'temperature': 0.5
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=HEADERS, json=data)
    if response.status_code == 429:
        raise RateLimitError("Rate limit exceeded")
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Failed to interact with GPT-4: {response.text}")

def main():
    parser = argparse.ArgumentParser(description='Query the OpenAI GPT-4 model with text and/or image input.')
    parser.add_argument('--query', type=str, help='The text query to be processed.')
    parser.add_argument('--image', type=str, help='The path to the image to be processed.')
    args = parser.parse_args()

    query = args.query
    image_path = args.image

    if image_path:
        try:
            if query:
                query = generate_query_from_image_and_text(image_path, query)
            else:
                query = generate_query_from_image_and_text(image_path)
            print(f"Generated Query: \"{query}\" \n\n")
            return query
        except Exception as e:
            print(f"Error generating query from image: {e}")
            return "Error"
    elif not query:
        print("No query provided. Exiting.")
        return

    k = 10
    try:
        embedding = get_embedding(query)
        response = requests.post('http://127.0.0.1:5000/search', json={'embedding': embedding, 'k': k})

        if response.status_code == 200:
            results = response.json()
            with open('results.json', 'w') as f:
                json.dump(results, f, indent=4)
            
            co = cohere.Client(COHERE_API_KEY)
            docs = list(set(results['results']))

            response = co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=docs,
                top_n=3
                )
            
            top_indices = [result["index"] for result in json.loads(response.json())["results"]]
            top_docs = [docs[index] for index in top_indices]
            top_results = {"results": top_docs}
            with open('top_results.json', 'w') as f:
                json.dump(top_results, f, indent=4)
            
            framed_question = query
            answer = submit_query_to_gpt4('top_results.json', framed_question)
            print("\nGPT-4 Response:\n")
            print(answer)
            print('\n')
            return answer
        else:
            print("Failed to query the server:", response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
