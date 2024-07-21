import os
import pandas as pd
import requests
import csv
import argparse
import numpy as np
from tenacity import retry, stop_after_attempt, wait_random_exponential

class EmbeddingsGenerator:
    def __init__(self, input_directory, output_directory, api_key):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.url = "https://api.openai.com/v1/embeddings"
        os.makedirs(self.output_directory, exist_ok=True)

    def read_chunks(self):
        csv_path = os.path.join(self.input_directory, 'chunks.csv')
        return pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()

    def create_chunk_batches(self, dataframe, batch_size=128):
        return [dataframe[start:start + batch_size]['Chunk Text'].tolist() for start in range(0, len(dataframe), batch_size)]

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(10))
    def get_embeddings_with_backoff(self, clean_batch):
        response = requests.post(self.url, headers=self.headers, json={"input": clean_batch, "model": "text-embedding-ada-002"})
        response.raise_for_status()
        return response

    def get_embeddings(self, text_batches):
        embeddings = []
        for batch in text_batches:
            clean_batch = []
            for text in batch:
                if isinstance(text, str):
                    clean_batch.append(text)
                elif isinstance(text, float) and (np.isnan(text) or np.isinf(text)):
                    clean_batch.append("invalid data")
                else:
                    clean_batch.append(str(text))

            try:
                response = self.get_embeddings_with_backoff(clean_batch)
                for embeddingJSON in response.json()['data']:
                    embedding = embeddingJSON["embedding"]
                    embeddings.append(embedding)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                continue
        return embeddings

    def save_embeddings(self, text_batches, embeddings):
        csv_path = os.path.join(self.output_directory, 'chunk_embeddings.csv')
        chunks = [chunk for batch in text_batches for chunk in batch]
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Chunk Text', 'Embedding'])
            for text, embed in zip(chunks, embeddings):
                writer.writerow([text, embed])

    def process_directory(self):
        df = self.read_chunks()
        if not df.empty:
            text_batches = self.create_chunk_batches(df)
            embeddings = self.get_embeddings(text_batches)
            self.save_embeddings(text_batches, embeddings)
            print(f"Processed and saved embeddings for directory: {self.output_directory}")

def find_directories(input_root):
    directories = []
    for dirpath, dirnames, _ in os.walk(input_root):
        for dirname in dirnames:
            sub_dir = os.path.join(dirpath, dirname)
            if 'chunks.csv' in os.listdir(sub_dir):
                directories.append(sub_dir)
    return directories

def main(api_key):
    input_root = "chunker"
    output_root = "embedder"

    directories = find_directories(input_root)
    for dir in directories:
        EmbeddingsGenerator(dir, os.path.join(output_root, os.path.basename(dir)), api_key).process_directory()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate embeddings from text chunks.')
    args = parser.parse_args()

    api_key = "sk-None-LvNsqypaMW2yIvPSA9R8T3BlbkFJte8SFRMxh2LNPAlg8ERs"

    main(api_key)
