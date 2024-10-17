import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import gzip
import brotli
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngineScraper:
    def __init__(self):
        self.session = self.create_session()
        self.results = []
        # Mapping of engine names to their corresponding methods
        self.engine_method_map = {
            'sogou': self.scrape_sogou_search,
            'bing': self.scrape_bing_search,
            'quark': self.scrape_quark_search,
            'mso': self.scrape_mso_search
            # Add other mappings as needed
        }

    @staticmethod
    def create_session():
        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def get_random_user_agent():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
        ]
        return random.choice(user_agents)

    def scrape_search_engine(self, engine, query, result_number=10):
        self.results = []
        scrape_method = self.engine_method_map.get(engine)
        
        # Debugging: Print attempted engine and available engines
        logger.info(f"Attempting to scrape engine: {engine}")
        logger.debug(f"Available engines: {list(self.engine_method_map.keys())}")
        
        if scrape_method:
            scrape_method(engine, query, result_number)
        else:
            raise ValueError(f"Unsupported search engine: {engine}")
        return self.results

    def scrape_sogou_search(self, engine, query, result_number):
        encoded_query = urllib.parse.quote(query)
        results_to_scrape = result_number // 10 + (1 if result_number % 10 else 0)  # Pages to scrape

        for page in range(1, results_to_scrape + 1):
            if len(self.results) >= result_number:
                break

            url = f"https://www.sogou.com/web?query={encoded_query}&page={page}"
            headers = self.get_headers()

            try:
                time.sleep(random.uniform(2, 5))
                response = self.session.get(url, headers=headers, timeout=10)
                logger.info(f"Received status code {response.status_code} from {engine}")
                response.raise_for_status()

                content = response.text  # Directly use response.text

                if not content:
                    logger.warning(f"Failed to get content for Sogou page {page}. Skipping.")
                    continue

                soup = BeautifulSoup(content, 'html.parser')
                results = soup.find_all('div', class_='vrwrap') or soup.find_all('div', class_='rb')

                if not results:
                    logger.warning(
                        f"No results found on Sogou page {page}. This might indicate a parsing issue or a change in Sogou's HTML structure.")

                for result in results:
                    if len(self.results) >= result_number:
                        break

                    title_elem = result.find('h3', class_='vr-title') or result.find('h3', class_='pt')
                    if title_elem:
                        title = title_elem.text.strip()
                        url_elem = title_elem.find('a')
                        url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else "URL not found"

                        # Description is left blank
                        description = ""

                        self.results.append({
                            "engine_name": engine.capitalize(),
                            "title": title,
                            "content": description,
                            "URL": url
                        })

            except requests.exceptions.RequestException as e:
                logger.error(f"Error accessing Sogou on page {page}: {e}")
                continue
            except Exception as e:
                logger.exception(f"Unexpected error on Sogou page {page}: {e}")
                continue

    def scrape_bing_search(self, engine, query, result_number):
        encoded_query = urllib.parse.quote(query)
        results_to_scrape = result_number // 10 + (1 if result_number % 10 else 0)  # Pages to scrape

        for page in range(1, results_to_scrape + 1):
            if len(self.results) >= result_number:
                break

            url = f"https://www.bing.com/search?q={encoded_query}&first={10 * (page - 1) + 1}"
            headers = self.get_headers()

            try:
                time.sleep(random.uniform(2, 5))
                response = self.session.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                content = response.text  # Directly use response.text

                if not content:
                    logger.warning(f"Failed to get content for Bing page {page}. Skipping.")
                    continue

                soup = BeautifulSoup(content, 'html.parser')

                results = (soup.find_all('li', class_='b_algo') or
                           soup.find_all('div', class_='b_title') or
                           soup.find_all('div', class_='b_attribution'))

                if not results:
                    logger.warning(
                        f"No results found on Bing page {page}. This might indicate a parsing issue or a change in Bing's HTML structure.")

                for result in results:
                    if len(self.results) >= result_number:
                        break

                    title = "No title found"
                    url = "No URL found"
                    description = "No description available"

                    title_elem = result.find('h2') or result.find('a')
                    if title_elem:
                        title = title_elem.text.strip()
                        url_elem = title_elem.find('a') or title_elem
                        url = url_elem.get('href', "No URL found")

                    description_elem = (result.find('div', class_='b_caption') or
                                        result.find('p') or
                                        result.find('div', class_='b_snippet'))
                    if description_elem:
                        description = description_elem.text.strip()

                    self.results.append({
                        "engine_name": engine.capitalize(),
                        "title": title,
                        "content": description,
                        "URL": url
                    })

            except requests.exceptions.RequestException as e:
                logger.error(f"Error accessing Bing on page {page}: {e}")
                continue
            except Exception as e:
                logger.exception(f"Unexpected error on Bing page {page}: {e}")
                continue

    def scrape_quark_search(self, engine, query, result_number):
        """
        Scrape search results from Quark search engine.

        Args:
            engine (str): Name of the search engine ('quark').
            query (str): The search keyword.
            result_number (int): Number of results to scrape.

        Returns:
            list: A list of dictionaries containing search results.
        """
        encoded_query = urllib.parse.quote(query)
        max_results = 13
        result_number = min(result_number, max_results)  # Limit to max 13 results

        url = f"https://quark.sm.cn/s?q={encoded_query}&safe=1"
        headers = self.get_headers()

        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            content = response.text  # Directly use response.text
            if not content:
                logger.warning("Failed to get content for Quark. Skipping.")
                return []

            soup = BeautifulSoup(content, 'html.parser')
            results = soup.find_all('div', class_='sc sc_structure_template_normal')

            if not results:
                logger.warning("No results found on Quark. This might indicate a parsing issue or a change in Quark's HTML structure.")
                return []

            custom_results = []
            for result in results[:result_number]:
                # Title and URL Extraction
                title_content_div = result.find('div', class_='qk-title-content')
                if not title_content_div:
                    continue

                link = title_content_div.find('a', class_='qk-link-wrapper')
                if not link or 'href' not in link.attrs:
                    continue

                title_text_div = link.find('div', class_='qk-title-text qk-font-bold')
                title = title_text_div.get_text(strip=True) if title_text_div else "No title found"
                href = link['href']

                # Description is left blank
                description = ""

                custom_results.append({
                    "engine_name": engine.capitalize(),
                    "title": title,
                    "content": description,
                    "URL": href
                })

            logger.info(f"Found {len(custom_results)} results from Quark search.")
            self.results.extend(custom_results)
            return custom_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing quark.sm.cn: {e}")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error while scraping Quark: {e}")
            return []
    
    def scrape_mso_search(self, engine, query, result_number):
        encoded_query = urllib.parse.quote(query)
        max_results = 7
        result_number = min(result_number, max_results)  # Limit to max 7 results

        url = f"https://m.so.com/s?q={encoded_query}"
        headers = self.get_headers()
        headers[
            "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1"

        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            content = response.text  # Directly use response.text
            if not content:
                logger.warning("Failed to get content for MSO. Skipping.")
                return

            if "anti-bot" in content.lower() or "验证码" in content:
                logger.warning("Anti-bot measures detected on MSO. Skipping further scraping.")
                return

            soup = BeautifulSoup(content, 'html.parser')
            results = soup.find_all('div', class_='result')

            if not results:
                logger.warning("No results found on MSO. This might indicate a parsing issue or a change in MSO's HTML structure.")

            for result in results[:result_number]:
                title_elem = result.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else "No title found"
                url_elem = title_elem.find('a') if title_elem else None
                url = url_elem.get('href', "No URL found") if url_elem else "No URL found"

                # Description is left blank
                description = ""

                self.results.append({
                    "engine_name": engine.capitalize(),
                    "title": title,
                    "content": description,
                    "URL": url
                })

        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing m.so.com: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error on MSO: {e}")
    @staticmethod
    def get_headers():
        return {
            "User-Agent": SearchEngineScraper.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

    @staticmethod
    def decode_content(response):
        content_encoding = response.headers.get('Content-Encoding')
        try:
            if content_encoding == 'gzip':
                return gzip.decompress(response.content).decode('utf-8')
            elif content_encoding == 'br':
                return brotli.decompress(response.content).decode('utf-8')
            else:
                return response.text  # No special decoding needed
        except (gzip.BadGzipFile, brotli.error) as e:
            logger.warning(f"Decoding error: {e}. Falling back to response.text.")
            return response.text
        
    def scrape_custom_search_engine(self, url, query):
        encoded_query = urllib.parse.quote(query)
        full_url = f"{url}?q={encoded_query}"
        headers = self.get_headers()

        try:
            time.sleep(random.uniform(2, 5))
            response = self.session.get(full_url, headers=headers, timeout=10)
            response.raise_for_status()

            content = response.text
            if not content:
                logger.warning(f"Failed to get content for custom search engine {url}. Skipping.")
                return None

            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all <a> tags
            links = soup.find_all('a')
            
            custom_results = []
            for link in links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                # Ensure the URL is absolute
                if href and not href.startswith(('http://', 'https://')):
                    href = urllib.parse.urljoin(url, href)
                
                # Skip if there's no title or href
                if not title or not href:
                    continue
                
                # Get the parent element for potential description
                parent = link.parent
                description = parent.get_text(strip=True) if parent else ""
                description = description.replace(title, "").strip()  # Remove title from description
                
                custom_results.append({
                    "engine_name": "Custom",
                    "title": title,
                    "content": description[:200] + "..." if len(description) > 200 else description,
                    "URL": href
                })

            logger.info(f"Found {len(custom_results)} results from custom search engine {url}")
            return custom_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing custom search engine {url}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error on custom search engine {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = SearchEngineScraper()
    test_query = "你好"
    engines = ["sogou", "bing", "quark", "mso"]

    for engine in engines:
        print(f"\nTesting {engine.capitalize()} Search Engine")
        print("-" * 40)
        
        if engine == "sogou":
            test_results = scraper.scrape_sogou_search(engine, test_query, 1)
        elif engine == "bing":
            test_results = scraper.scrape_bing_search(engine, test_query, 1)
        elif engine == "quark":
            test_results = scraper.scrape_quark_search(engine, test_query, 1)
        elif engine == "mso":
            test_results = scraper.scrape_mso_search(engine, test_query, 1)

        print(f"Test Results for query '{test_query}':")
        if test_results:
            for result in test_results:
                print(f"Title: {result['title']}")
                print(f"URL: {result['URL']}")
                print(f"Description: {result['content']}")
                print()
        else:
            print("No results found or an error occurred.")
        
        print("\n")
