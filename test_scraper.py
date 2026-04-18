from scraper import IIITRScraper
import sys

scraper = IIITRScraper()
print("Scraping...")
scraper.scrape("https://iiitr.ac.in", depth=1)
text = scraper.get_combined_text()
print(f"Scraped {len(scraper.knowledge_base)} pages.")
print(f"Text length: {len(text)}")
if len(text) > 500:
    print("Sample text:")
    print(text[:500] + "...")
else:
    print("Full text:")
    print(text)
