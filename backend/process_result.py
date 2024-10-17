import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class JsonCleaner:
    def __init__(self):
        pass

    def scrape_content(self, url):
        """Scrape text content from the given URL."""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            # Check if the response contains a message indicating anti-scraping measures
            if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                print(f"Anti-scraping measure detected at {url}.")
                return "Anti-scraping measure detected.", url

            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ' '.join(p.get_text() for p in paragraphs)
            return content, url

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return "Error fetching content.", url

    def clean_json_data(self, data):
        """
        Clean the JSON data by removing invalid entries and updating content.

        :param data: List of dictionaries containing search results.
        :return: List of cleaned and unique search results.
        """
        unique_entries = []
        seen = set()

        for entry in data:
            # Skip entries without a URL
            if 'URL' not in entry or not entry['URL']:
                continue

            # If there's no title, create one using the search engine name
            if 'title' not in entry or not entry['title']:
                entry['title'] = f"{entry.get('engine_name', 'SearchEngine')} Result"

            # Attempt to scrape content if it's missing or indicates an error
            if 'content' not in entry or not entry['content'] or entry['content'] in ["Anti-scraping measure detected.", "Error fetching content."]:
                try:
                    content, new_url = self.scrape_content(entry['URL'])
                    if content:
                        entry['content'] = content
                        entry['URL'] = new_url
                except Exception as e:
                    # If scraping fails, keep the original content or set a default message
                    if 'content' not in entry or not entry['content']:
                        entry['content'] = f"Unable to fetch content: {str(e)}"

            # Create a unique identifier for the entry
            identifier = (entry['title'], entry['URL'])
            if identifier not in seen:
                seen.add(identifier)
                unique_entries.append(entry)

        return unique_entries
