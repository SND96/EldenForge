import requests
import csv
import os
from urllib.parse import urlparse, urljoin
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class Scraper:
    HTML_FOLDER_NAME = 'html_files'
    CSV_FILE_NAME = 'publications.csv'

    def __init__(self, base_url, use_selenium=False):
        self.base_url = base_url
        self.use_selenium = use_selenium
        self.prepare_output()
        self.data = []
        self.visited = set()
        self.queue = deque([base_url])
        self.visited.add(base_url)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        if self.use_selenium:
            self.driver = self.initialize_selenium()

    def initialize_selenium(self):
        chrome_options = Options()
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def download_page_as_html(self, html_content, filename):
        try:
            file_path = os.path.join(self.DOWNLOAD_FOLDER, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            return file_path
        except Exception as e:
            print(f"Error saving HTML: {e}")
            return ""

    def write_csv(self, data):
        with open(self.CSV_FILE_NAME, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'url'])
            writer.writeheader()
            writer.writerows(data)

    def prepare_output(self):
        parsed_uri = urlparse(self.base_url)
        root_folder_base_name = "scraper"
        root_folder_name = os.path.join(root_folder_base_name, parsed_uri.netloc)
        download_folder = os.path.join(root_folder_name, self.HTML_FOLDER_NAME)
        csv_file = os.path.join(root_folder_name, self.CSV_FILE_NAME)
        os.makedirs(download_folder, exist_ok=True)
        self.DOWNLOAD_FOLDER = download_folder
        self.CSV_FILE_NAME = csv_file

    def get_page_with_retry(self, url):
        for attempt in range(self.max_retries):
            try:
                time.sleep(random.uniform(1, 3))  # Random delay between requests
                if self.use_selenium:
                    self.driver.get(url)
                    return self.driver.page_source
                else:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 404:
                        print(f"Error 404: Not Found for {url}")
                        return None
                    response.raise_for_status()
                    return response.text
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Max retries reached for {url}")
                    return None

    def get_links(self, soup):
        return [urljoin(self.base_url, a.get('href')) for a in soup.find_all('a', href=True)]

    def scrape(self):
        pass

    def is_valid_url(self, url):
        pass

    def extract_title(self, soup):
        pass

    def cleanup(self):
        if self.use_selenium:
            self.driver.quit()