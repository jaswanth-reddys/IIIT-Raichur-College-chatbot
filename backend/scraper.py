import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class IIITRScraper:
    def __init__(self, base_url="https://iiitr.ac.in"):
        self.base_url = base_url
        self.visited_urls = set()
        self.knowledge_base = []

    def is_valid(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == urlparse(self.base_url).netloc

    def scrape(self, url, depth=1):
        if depth == 0 or url in self.visited_urls:
            return
        
        print(f"Scraping: {url}")
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            self.knowledge_base.append({
                "url": url,
                "content": text
            })
            
            # Find more links
            if depth > 1:
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if self.is_valid(next_url):
                        self.scrape(next_url, depth - 1)
                        
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    def get_combined_text(self):
        return "\n\n".join([f"Source: {item['url']}\nContent: {item['content']}" for item in self.knowledge_base])

if __name__ == "__main__":
    scraper = IIITRScraper()
    scraper.scrape("https://iiitr.ac.in", depth=1)
    print(f"Scraped {len(scraper.knowledge_base)} pages.")
