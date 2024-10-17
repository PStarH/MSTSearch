import jieba
import numpy as np
from gensim.models import Word2Vec
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

warnings.filterwarnings("ignore", message="The parameter 'token_pattern' will not be used since 'tokenizer' is not None")

class Sort:
    def __init__(self, search_results, query):
        self.search_results = search_results  # Now accepts the search results directly
        self.query = query
        self.documents = [result['content'] for result in self.search_results]
        self.tokenized_docs = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = None
        self.vectorizer = None
        self.word2vec_model = None

    def tokenize_query(self):
        return list(jieba.cut(self.query))

    def compute_bm25_scores(self, query_tokens):
        self.bm25 = BM25Okapi(self.tokenized_docs)
        return self.bm25.get_scores(query_tokens)

    def compute_tfidf_scores(self, query_tokens):
        self.vectorizer = TfidfVectorizer(tokenizer=jieba.cut)
        tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        query_vector = self.vectorizer.transform([self.query])
        return sk_cosine_similarity(query_vector, tfidf_matrix).flatten()

    def compute_word2vec_scores(self, query_tokens):
        self.word2vec_model = Word2Vec(sentences=self.tokenized_docs, vector_size=100, window=5, min_count=1, workers=4)
        query_vector_w2v = np.mean([self.word2vec_model.wv[word] for word in query_tokens if word in self.word2vec_model.wv] or [
            np.zeros(self.word2vec_model.vector_size)], axis=0)
        doc_vectors_w2v = np.array([np.mean(
            [self.word2vec_model.wv[word] for word in doc if word in self.word2vec_model.wv] or [np.zeros(self.word2vec_model.vector_size)],
            axis=0) for doc in self.tokenized_docs])
        return np.array(
            [1 - sk_cosine_similarity([query_vector_w2v], [doc_vector])[0][0] for doc_vector in doc_vectors_w2v])

    def normalize_scores(self, bm25_scores, cosine_similarities, w2v_similarities):
        bm25_score_max = np.max(bm25_scores) if bm25_scores.size > 0 else 1
        cosine_score_max = np.max(cosine_similarities) if cosine_similarities.size > 0 else 1
        w2v_score_max = np.max(w2v_similarities) if w2v_similarities.size > 0 else 1

        final_scores = []
        for i, result in enumerate(self.search_results):
            bm25_score = (bm25_scores[i] / bm25_score_max) * 100 if bm25_score_max != 0 else 0
            cosine_score = (cosine_similarities[i] / cosine_score_max) * 100 if cosine_score_max != 0 else 0
            w2v_score = (w2v_similarities[i] / w2v_score_max) * 100 if w2v_score_max != 0 else 0

            combined_score = (bm25_score + cosine_score + w2v_score) / 3

            final_scores.append({
                'title': result.get('title', 'No Title'),  # Add default if title is missing
                'content': result.get('content', 'No Content'),  # Add default if content is missing
                'URL': result.get('URL', '#'),  # Add default if URL is missing
                'engine_name': result.get('engine_name', 'Unknown'),  # Add engine_name
                'score': round(combined_score, 2) if not np.isnan(combined_score) else 0.01
            })

        return final_scores

    def handle_anti_scraping(self, final_scores):
        average_score = np.mean([item['score'] for item in final_scores if item['score'] > 0]) if final_scores else 0.01

        for result in final_scores:
            if result['score'] == 0 or "Anti-scraping measure detected." in result.get('content', ''):
                result['score'] = max(average_score, 0.01)

        return final_scores

    def sort_results(self, final_scores):
        # Sort the results but return all of them
        return sorted(final_scores, key=lambda x: x['score'], reverse=True)

    def run_sorting(self):
        query_tokens = self.tokenize_query()
        try:
            bm25_scores = self.compute_bm25_scores(query_tokens)
        except Exception as e:
            print(f"Error in BM25 scoring: {e}")
            bm25_scores = np.zeros(len(self.search_results))

        try:
            cosine_similarities = self.compute_tfidf_scores(query_tokens)
        except Exception as e:
            print(f"Error in TF-IDF scoring: {e}")
            cosine_similarities = np.zeros(len(self.search_results))

        try:
            w2v_similarities = self.compute_word2vec_scores(query_tokens)
        except Exception as e:
            print(f"Error in Word2Vec scoring: {e}")
            w2v_similarities = np.zeros(len(self.search_results))

        final_scores = self.normalize_scores(bm25_scores, cosine_similarities, w2v_similarities)
        final_scores = self.handle_anti_scraping(final_scores)
        sorted_results = self.sort_results(final_scores)

        return sorted_results
