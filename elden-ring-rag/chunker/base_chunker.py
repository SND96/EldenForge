import os
import csv
import spacy
from bs4 import BeautifulSoup
from langchain.text_splitter import SpacyTextSplitter

class Chunker:
    HTML_FOLDER_NAME = 'html_files'
    CHUNKS_FILE_NAME = 'chunks.csv'

    def __init__(self, config):
        self.input_directory = config["input_directory"]
        self.output_directory = os.path.join('chunker', os.path.basename(self.input_directory))
        os.makedirs(self.output_directory, exist_ok=True)
        self.website_name = config["website_name"]

    def chunk_text(self, text, max_chunk_length=4000):
        spacy.util.fix_random_seed(0)  
        max_length = 1000000  
        text_splitter = SpacyTextSplitter()
        
        if len(text) > max_length:
            parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        else:
            parts = [text]

        initial_chunks = []
        for part in parts:
            initial_chunks.extend(text_splitter.split_text(part))
        
        final_chunks = []
        for chunk in initial_chunks:
            if len(chunk) <= max_chunk_length:
                final_chunks.append(chunk)
            else:
                while len(chunk) > max_chunk_length:
                    last_space = chunk.rfind(' ', 0, max_chunk_length)
                    if last_space == -1:  
                        last_space = max_chunk_length
                    final_chunks.append(chunk[:last_space].strip())
                    chunk = chunk[last_space:].strip()
                if chunk:
                    final_chunks.append(chunk)

        return final_chunks

    def extract_text_from_html_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        article_content = soup.find(self.container_element, class_=self.class_name)
        if article_content:
            return ' '.join(article_content.stripped_strings)
        return "No content found."
    
    def write_chunks_csv(self):
        chunks_file = os.path.join(self.output_directory, self.CHUNKS_FILE_NAME)
        files_dir = os.path.join(self.input_directory, self.HTML_FOLDER_NAME)

        with open(chunks_file, mode="w", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Website', 'Article Title', 'Chunk Text'], escapechar='\\', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()

            for filename in os.listdir(files_dir):
                file_path = os.path.join(files_dir, filename)
                text = self.extract_text_from_html_file(file_path)
                content_chunks = self.chunk_text(text)
                title = os.path.splitext(filename)[0]  
                for chunk in content_chunks:
                    try:
                        writer.writerow({'Website': self.website_name, 'Article Title': title, 'Chunk Text': chunk})
                    except Exception as e:
                        print(f"Error writing row for {title}: {e}")