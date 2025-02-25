from base_scraper import Scraper
from bs4 import BeautifulSoup
import requests
import time
import random
from urllib.parse import urlparse, urljoin
import json

class GamerScraper(Scraper):
    def __init__(self):
        super().__init__("https://www.thegamer.com/elden-ring-complete-guide-and-walkthrough/")
        self.max_retries = 3
        self.retry_delay = 5
        self.load_cookies("thegamer_cookies.json")

    def load_cookies(self, cookies_file):
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))

    def is_valid_url(self, url):
        return "www.thegamer.com/elden-ring" in url and "mailto" not in url and "#" not in url

    def extract_title(self, soup):
        title_element = soup.select_one("h1.article-header-title")
        return title_element.text.strip() if title_element else super().extract_title(soup)

    def get_page_with_retry(self, url):
        for attempt in range(self.max_retries):
            try:
                time.sleep(random.uniform(1, 3))  # Random delay between requests
                response = self.session.get(url, timeout=10)
                if response.status_code == 404:
                    print(f"Error 404: Not Found for {url}")
                    return None
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Max retries reached for {url}")
                    return None

    def scrape(self):
        while self.queue:
            url = self.queue.popleft()
            if not self.is_valid_url(url):
                continue
            
            response = self.get_page_with_retry(url)
            if response is None:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(url)
            title = self.extract_title(soup)
            self.data.append({'title': title, 'url': url})
            
            filename = f"{urlparse(url).path.replace('/', '_')}.html"
            self.download_page_as_html(response.text, filename)
            
            links = self.get_links(soup)
            for link in links:
                if link not in self.visited and self.is_valid_url(link):
                    self.queue.append(link)
                    self.visited.add(link)
            
            if len(self.data) % 10 == 0:
                self.write_csv(self.data)
        
        self.write_csv(self.data)

if __name__ == "__main__":
    scraper = GamerScraper()
    scraper.scrape()
