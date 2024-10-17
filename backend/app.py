from flask import Flask, request, jsonify
from flask_cors import CORS
from BaiduCrawler import BaiduScraper
from SohuCrawler import SohuCrawler
from crawler import SearchEngineScraper
from sort import Sort  # Use the modified Sort class
from summarize import AIQuestionAnswerer
from process_result import JsonCleaner  # Import the JsonCleaner class
import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import re
import string

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "100 per hour"],
)
limiter.init_app(app)  # Properly initialize the Limiter with the Flask app

# 缓存配置：开发环境中使用SimpleCache，生产环境建议使用RedisCache
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

SEARCH_ENGINES_FILE = 'search_engines.json'

# Define the keyword_pattern regex for validation
keyword_pattern = re.compile(r'^[A-Za-z0-9 \u4e00-\u9fa5]{1,100}$')  # Adjusted to include Chinese characters

# Load existing search engines
def load_search_engines():
    if not os.path.exists(SEARCH_ENGINES_FILE):
        return []
    with open(SEARCH_ENGINES_FILE, 'r') as f:
        return json.load(f)

# Save search engines
def save_search_engines(search_engines):
    with open(SEARCH_ENGINES_FILE, 'w') as f:
        json.dump(search_engines, f, indent=4)

@app.route('/api/search-engines', methods=['GET'])
def get_search_engines():
    search_engines = load_search_engines()
    return jsonify({'searchEngines': search_engines}), 200

@app.route('/api/search-engines', methods=['POST'])
def add_search_engine():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'message': 'URL is required.'}), 400

    # Validate URL format
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return jsonify({'success': False, 'message': 'Invalid URL format.'}), 400

    try:
        scraper = SearchEngineScraper(url)
        links = scraper.extract_links()
        search_engines = load_search_engines()

        new_engine = {
            'id': len(search_engines) + 1,
            'url': url,
            'links': links
        }

        search_engines.append(new_engine)
        save_search_engines(search_engines)

        return jsonify({'success': True, 'searchEngine': new_engine}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/search-engines/<int:engine_id>', methods=['DELETE'])
def delete_search_engine(engine_id):
    search_engines = load_search_engines()
    updated_search_engines = [engine for engine in search_engines if engine['id'] != engine_id]

    if len(updated_search_engines) == len(search_engines):
        return jsonify({'success': False, 'message': 'Search engine not found.'}), 404

    save_search_engines(updated_search_engines)
    return jsonify({'success': True, 'message': 'Search engine deleted successfully.'}), 200

def scrape_engine(engine, keyword, max_results):
    name = engine.get('name')
    try:
        if name.lower() == 'bing':
            crawler = SearchEngineScraper()
            return crawler.scrape_search_engine('bing', keyword, max_results)
        elif name.lower() == 'baidu':
            baidu_scraper = BaiduScraper()
            baidu_results = baidu_scraper.search(keyword, max_results)
            return baidu_results if baidu_results else []
        elif name.lower() == 'sohu':
            sohu_scraper = SohuCrawler()
            sohu_results = sohu_scraper.scrape_sohu_search(keyword, max_results)
            return sohu_results if sohu_results else []
        elif name.lower() in ['sogou', 'mso', 'quark']:
            crawler = SearchEngineScraper()
            return crawler.scrape_search_engine(name.lower(), keyword, max_results)
        elif isinstance(name, dict) and 'url' in name:
            # Handle custom search engine
            custom_scraper = SearchEngineScraper()
            custom_results = custom_scraper.scrape_custom_search_engine(name['url'], keyword)
            return custom_results if custom_results else []
        else:
            print(f"Unsupported search engine: {name}")
            return []
    except Exception as e:
        print(f"Error scraping {name}: {e}")
        return []

@app.route('/search', methods=['POST'])
@limiter.limit("10 per minute")
def search():
    try:
        data = request.json
        app.logger.info(f"Received search request data: {data}")

        if data is None:
            app.logger.error("No JSON data received in the request")
            return jsonify({'status': 'error', 'message': 'No JSON data received'}), 400

        keyword = data.get('keyword', '').strip()
        search_engines = data.get('search_engines', [])

        app.logger.info(f"Keyword: {keyword}")
        app.logger.info(f"Search engines: {search_engines}")

        if not keyword:
            app.logger.error("Empty keyword received")
            return jsonify({'status': 'error', 'message': 'Keyword cannot be empty'}), 400

        # Define cache_key here
        cache_key = f"search:{keyword}"

        # Check cache
        cached_response = cache.get(cache_key)
        if cached_response:
            app.logger.info(f"Returning cached response for keyword: {keyword}")
            return jsonify(cached_response), 200

        # 输入验证：仅允许字母、数字、中文字符、空格和常见标点符号，长度1-100
        allowed_chars = string.ascii_letters + string.digits + string.whitespace + ',.?!，。？！'
        keyword_pattern = re.compile(f'^[{re.escape(allowed_chars)}\u4e00-\u9fa5]{{1,100}}$')
        if not keyword_pattern.match(keyword):
            app.logger.error(f"Invalid keyword format: {keyword}")
            return jsonify({'status': 'error', 'message': 'Invalid keyword format'}), 400

        if not search_engines:
            app.logger.error("No search engines specified")
            return jsonify({'status': 'error', 'message': 'At least one search engine must be specified'}), 400

        results = []

        with ProcessPoolExecutor(max_workers=4) as executor:
            future_to_engine = {
                executor.submit(scrape_engine, engine, keyword, engine.get('resultsCount', 10)): engine
                for engine in search_engines if engine.get('name')
            }

            for future in as_completed(future_to_engine):
                engine = future_to_engine[future]
                try:
                    engine_results = future.result()
                    if engine_results:
                        # Ensure each result has the engine_name
                        for result in engine_results:
                            result['engine_name'] = engine['name']
                        results.extend(engine_results)
                except Exception as e:
                    app.logger.error(f"Error processing engine {engine.get('name')}: {e}")

        # Log the results before sending
        app.logger.info(f"Search results: {results}")

        # 清理结果
        cleaner = JsonCleaner()
        try:
            cleaned_results = cleaner.clean_json_data(results)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Cleaning failed: {str(e)}"}), 500

        # 排序结果
        sorter = Sort(cleaned_results, keyword)
        sorted_results = sorter.run_sorting()

        # Add this logging
        print("Sorted results:", json.dumps(sorted_results, indent=2))

        response = {'status': 'success', 'results': sorted_results}
        cache.set(cache_key, response, timeout=300)  # Cache for 5 minutes
        return jsonify(response)

    except Exception as e:
        app.logger.error(f"Unexpected error in search function: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    question = data.get('question')
    api_key = data.get('api_key')
    provider = data.get('provider')
    model = data.get('model')

    try:
        # First attempt to call the tool
        ai_answerer = AIQuestionAnswerer(api_key, provider, model, 'sorted_results.json', question)
        answer = ai_answerer.answer_question()
        return jsonify({'answer': answer})

    except Exception as e:
        # Retry logic: if there's an exception, retry with a fallback model (like GPT-4)
        try:
            fallback_model = "gpt-4"  # Define your fallback model here
            ai_answerer = AIQuestionAnswerer(api_key, provider, fallback_model, 'sorted_results.json', question)
            answer = ai_answerer.answer_question()
            return jsonify({'answer': answer, 'note': 'Answer generated using fallback model (GPT-4).'})

        except Exception as fallback_error:
            return jsonify({
                'error': 'An error occurred while generating the answer with fallback model.',
                'details': str(fallback_error)
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
