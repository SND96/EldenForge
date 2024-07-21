from base_scraper import Scraper
from bs4 import BeautifulSoup
import requests
import time
import random
from urllib.parse import urlparse

class IGNScraper(Scraper):
    def __init__(self):
        super().__init__("https://www.ign.com/wikis/elden-ring")
        self.max_retries = 3
        self.retry_delay = 5

    def is_valid_url(self, url):
        return "ign.com" in url and "wikis" in url and "elden-ring" in url.lower()

    def extract_title(self, soup):
        title_element = soup.select_one("h1.display-title[itemprop='name']")
        return title_element.text if title_element else super().extract_title(soup)
    
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
                    if '#' in link:
                        base_url, section = link.split("#")
                        if base_url in self.visited:
                            continue
                    self.queue.append(link)
                    self.visited.add(link)
            
            if len(self.data) % 10 == 0:
                self.write_csv(self.data)
        
        self.write_csv(self.data)

if __name__ == "__main__":
    scraper = IGNScraper()
    scraper.scrape()
