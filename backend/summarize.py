import json
import importlib


class AIQuestionAnswerer:
    def __init__(self, api_key, provider, model, search_results_file, question):
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.search_results_file = search_results_file
        self.question = question
        self.lc = None
        self._initialize_provider()

    def _initialize_provider(self):
        # Dynamically import the provider package
        package_name = f"langchain-{self.provider.lower()}"
        provider_module = importlib.import_module(package_name)

        # Initialize LangChain with the chosen model
        self.lc = provider_module.LangChain(api_key=self.api_key, model=self.model)

    def _load_search_results(self):
        # Load search results with scores from the JSON file
        with open(self.search_results_file, 'r') as file:
            search_results = json.load(file)

        # Convert search results to a string with scores
        search_results_str = "\n".join([
            f"Title: {result['title']}\nContent: {result['content']}\nURL: {result['URL']}\nScore: {result['score']}"
            for result in search_results
        ])
        return search_results_str

    def answer_question(self):
        search_results_str = self._load_search_results()

        # Create a prompt with the search results as context and the user's question
        prompt = f"Context:\n{search_results_str}\n\nQuestion: {self.question}\n\nAnswer:"

        # Get the answer from the model
        response = self.lc(prompt)
        return response


# Example usage
if __name__ == "__main__":
    # Parameters for the AIQuestionAnswerer
    api_key = "your_api_key_here"
    provider = "OpenAILLM"
    model = "gpt-4"
    search_results_file = "sorted_results.json"
    question = "What is the main topic of the search results?"

    # Instantiate and use the AIQuestionAnswerer
    ai_answerer = AIQuestionAnswerer(api_key, provider, model, search_results_file, question)
    answer = ai_answerer.answer_question()
    print("Answer:")
    print(answer)
