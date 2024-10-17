import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os


class BaiduScraper:
    def __init__(self, driver_dir="./driver"):
        self.driver_dir = driver_dir
        self.driver_path = os.path.join(self.driver_dir, "chromedriver")
        self.setup_driver()
        self.results = []

    def setup_driver(self):
        if not os.path.exists(self.driver_dir):
            os.makedirs(self.driver_dir)
            print(f"Directory created: {self.driver_dir}")

        if not os.path.exists(self.driver_path):
            driver = ChromeDriverManager().install()
            os.rename(driver, self.driver_path)
            print(f"Driver downloaded to: {self.driver_path}")
        else:
            print(f"Driver already exists at: {self.driver_path}")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.javascript": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--log-level=3")

        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)

    def search(self, query, max_results):
        self.results = []  # Reset results
        start_time = time.time()

        self.driver.get('https://baidu.com')
        self.driver.find_element(By.XPATH, '//*[@id="kw"]').send_keys(query)
        self.driver.find_element(By.XPATH, '//*[@id="su"]').click()

        WebDriverWait(self.driver, 5).until(EC.title_contains(query))

        page_number = 1
        while len(self.results) < max_results:
            print(f"\nScraping page {page_number}")
            self.scrape_page(max_results)

            if len(self.results) >= max_results:
                print(f"Reached the maximum number of results ({max_results}). Exiting.")
                break

            if not self.go_to_next_page():
                break
            page_number += 1

        total_execution_time = time.time() - start_time
        print(f"\nTotal time taken for the entire process: {total_execution_time:.2f} seconds")

        return self.results  # Ensure the method returns the results list

    def scrape_page(self, max_results):
        result_containers = self.driver.find_elements(By.CSS_SELECTOR, 'div.result')
        for container in result_containers:
            if len(self.results) >= max_results:
                break
            if self.is_not_ad(container):
                result = self.get_result_info(container)
                self.results.append(result)
                print(f"Title: {result['title']}")
                print(f"URL: {result['URL']}")
                print("-" * 50)

    def is_not_ad(self, element):
        try:
            element.find_element(By.XPATH, './/span[contains(text(), "广告")]')
            return False
        except:
            return True

    def get_result_info(self, container):
        try:
            title = container.find_element(By.CSS_SELECTOR, 'h3.t').text
        except:
            title = "Title not found"

        try:
            url = container.find_element(By.CSS_SELECTOR, 'h3.t a').get_attribute('href')
        except:
            url = "URL not found"

        try:
            content = container.find_element(By.CSS_SELECTOR, 'div.c-span9.c-span-last span.content-right_2s-H4').text
        except:
            content = "Content not found"

        return {
            "engine_name": "Baidu",
            "title": title,
            "content": content,
            "URL": url
        }

    def go_to_next_page(self):
        try:
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "下一页")]'))
            )
            next_button.click()
            time.sleep(0.5)
            return True
        except:
            print("No more pages or error occurred. Exiting.")
            return False

    def save_results(self, filename="search_results.json"):
        # Load existing results if file exists
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_results = []

        # Merge new results with existing results
        existing_results.extend(self.results)

        # Save the merged results back to the file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_results, f, ensure_ascii=False, indent=4)

        print(f"Results appended to {filename}")

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    scraper = BaiduScraper()
    search_query = input("Enter the search query: ")
    max_results = int(input("Enter the number of results to scrape: "))

    scraper.search(search_query, max_results)
    scraper.save_results()
    scraper.close()
