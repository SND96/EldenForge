from bs4 import BeautifulSoup
from base_chunker import Chunker
import re


class IGNChunker(Chunker):
    def add_spaces_around_tags(self, html_content):
        spaced_html_content = re.sub(r'(<[^>]+>)', r' \1 ', html_content)
        return spaced_html_content
    
    def extract_text_from_html_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        spaced_html_content = self.add_spaces_around_tags(html_content)
        soup = BeautifulSoup(spaced_html_content, 'html.parser')
    
        wiki_sections = soup.find_all('div', class_=lambda x: x and 'content-block-regular' in x.split())
        extracted_sections = []
    
        for section in wiki_sections:
            p_tags = section.find_all('p')
            for p in p_tags:
                extracted_sections.append(' '.join(p.stripped_strings))
            
            emaki_sections = section.find_all('section', class_='emaki-custom-block emaki-custom-tip')
            for emaki_section in emaki_sections:
                extracted_sections.append(' '.join(emaki_section.stripped_strings))
        
        if extracted_sections:
            return ' '.join(extracted_sections)
        return "No content found."

def process_chunker(config):
    print("Starting processing for:", config['website_name'])
    try:
        chunker = IGNChunker(config)
        chunker.write_chunks_csv()
        print(f"Processed chunks for {config['website_name']} at {config['input_directory']}")
    except Exception as e:
        print(f"Failed to process chunks for {config['website_name']}: {e}")

if __name__ == "__main__":
    
    config = {
        "input_directory": "scraper/www.thegamer.com",
        "website_name": "TheGamer",
        }
    process_chunker(config)