import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import time
import os


class SohuCrawler:
    def __init__(self, driver_dir="./driver"):
        self.driver_dir = driver_dir
        self.driver = None
        self.engine_name = "Sohu"  # Engine name

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver_path = os.path.join(self.driver_dir, "chromedriver")

        if not os.path.exists(driver_path):
            raise FileNotFoundError(
                f"ChromeDriver not found at {driver_path}. Please ensure it's in the correct location."
            )

        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    @staticmethod
    def is_valid_result(result):
        # Check if the result has a valid title, content, and link
        has_title = result['title'] and not result['title'].isspace()
        has_content = result['content'] and not result['content'].isspace()

        # Check if content is a single number and exclude such results
        is_single_number = result['content'].isdigit() and len(result['content']) == 1

        # Exclude invalid links and 'javascript:void(0)'
        has_valid_link = result['link'] and \
                         not result['link'].startswith("javascript:") and \
                         not result['link'].startswith("//www.sohu.com") and \
                         not result['link'].isspace()

        # Only return true if all conditions are satisfied and content is not a single number
        return has_title and has_content and has_valid_link and not is_single_number

    def scrape_sohu_search(self, keyword, max_results=10):
        """
        Scrape Sohu search results for the given keyword.

        :param keyword: The keyword to search.
        :param max_results: The maximum number of results to return.
        :return: A list of valid search results.
        """
        url = f"https://search.sohu.com/?keyword={keyword}"
        self.setup_driver()

        try:
            self.driver.get(url)
            print(f"Successfully loaded the page. Current URL: {self.driver.current_url}")

            time.sleep(1)  # Wait for the page to load completely

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for any additional content to load

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            print("First 1000 characters of the HTML after JavaScript rendering:")
            print(soup.prettify()[:1000])

            results = []
            seen_titles = set()
            seen_contents = set()
            seen_title_content_combinations = set()

            # Locate the main container with class "search-content-left"
            main_container = soup.find('div', class_='search-content-left')
            if not main_container:
                print("Main container with class 'search-content-left' not found.")
                return results

            # Extract individual result items within the main container
            # Adjust the selector based on the actual HTML structure
            potential_result_containers = main_container.find_all('div', class_=lambda x: x and 'result-item' in x)

            if potential_result_containers:
                for container in potential_result_containers:
                    if len(results) >= max_results:
                        break  # Stop if we have reached the max number of results
                    print(f"Found potential result container: {container.get('class')}")
                    link_tag = container.find('a', href=True)
                    description_tag = container.find('p')  # Assuming description is within a <p> tag

                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        href = link_tag.get('href')
                        content = description_tag.get_text(strip=True) if description_tag else "No content found"

                        # Normalize title and content
                        normalized_title = title.strip().lower()
                        normalized_content = content.strip().lower()

                        # Create unique keys
                        title_key = normalized_title
                        content_key = normalized_content
                        title_vs_content_key = (normalized_title, normalized_content)
                        content_vs_title_key = (normalized_content, normalized_title)

                        result = {
                            'engine_name': self.engine_name,
                            'title': title,
                            'content': content,
                            'link': href,
                        }

                        if self.is_valid_result(result):
                            if (title_key not in seen_titles and
                                    content_key not in seen_contents and
                                    title_vs_content_key not in seen_title_content_combinations and
                                    content_vs_title_key not in seen_title_content_combinations):
                                results.append(result)
                                seen_titles.add(title_key)
                                seen_contents.add(content_key)
                                seen_title_content_combinations.add(title_vs_content_key)
                                seen_title_content_combinations.add(content_vs_title_key)

            if not results:
                print("No valid results found within 'search-content-left'. Dumping all links on the page:")
                for link in main_container.find_all('a'):
                    print(f"Text: {link.text.strip()}, href: {link.get('href')}")

            return results[:max_results]  # Only return up to the number of max results requested

        finally:
            self.driver.quit()

    @staticmethod
    def append_results_to_json(results, filename="search_results.json"):
        # Read existing data
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Append new results
        data.extend(results)

        # Write updated data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Results appended to {filename}")


if __name__ == "__main__":
    keyword = input("Enter the search keyword: ")
    max_results = int(input("Enter the number of results to retrieve: "))

    crawler = SohuCrawler()

    try:
        results = crawler.scrape_sohu_search(keyword, max_results)

        if results:
            crawler.append_results_to_json(results)
            print("\nScraped Results:")
            for result in results:
                print(f"Title: {result['title']}\nLink: {result['link']}\nDescription: {result['content']}\n")
        else:
            print("No valid results found. Check the output above for more details.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the ChromeDriver is in the correct location.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print(f"\nPython version: {sys.version}")
    print(f"BeautifulSoup version: {BeautifulSoup.__version__ if hasattr(BeautifulSoup, '__version__') else 'Not available'}")
