<template>
  <div
    class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-8 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-7xl mx-auto">
      <div class="mb-8">
        <h1
          class="text-4xl sm:text-5xl lg:text-6xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600"
        >
          MSTSearch
        </h1>
        <form
          @submit.prevent="performSearch"
          class="flex flex-col sm:flex-row items-center"
        >
          <input
            v-model="newQuery"
            type="text"
            placeholder="Enter your search query"
            class="flex-grow px-4 py-2 rounded-md sm:rounded-l-md sm:rounded-r-none border-2 border-gray-700 bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4 sm:mb-0"
          />
          <button
            type="submit"
            class="w-full sm:w-auto px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-md sm:rounded-r-md hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-700 focus:ring-offset-2 focus:ring-offset-gray-800"
          >
            Search
          </button>
        </form>
      </div>

      <h2 class="text-2xl font-bold text-white mb-6">
        Search Results for "{{ currentQuery }}"
      </h2>

      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Search Results Column -->
        <div class="lg:w-2/3">
          <div
            class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0"
          >
            <div class="flex items-center space-x-4">
              <label for="sort-order" class="text-sm font-medium text-gray-300"
                >Sort by:</label
              >
              <select
                id="sort-order"
                v-model="sortOrder"
                @change="handleSort"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-600 bg-gray-700 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="relevance">Relevance</option>
                <option value="source">Source</option>
              </select>
            </div>
            <div class="flex items-center space-x-4">
              <label
                for="filter-source"
                class="text-sm font-medium text-gray-300"
                >Filter by source:</label
              >
              <select
                id="filter-source"
                v-model="selectedSource"
                @change="handleFilter"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-600 bg-gray-700 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="">All Sources</option>
                <option
                  v-for="source in uniqueSources"
                  :key="source"
                  :value="source"
                >
                  {{ source }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="loading" class="text-center py-12">
            <p class="text-xl text-gray-300">Loading results...</p>
          </div>

          <div
            v-else
            class="space-y-6 overflow-y-auto max-h-[calc(100vh-300px)] lg:max-h-full"
          >
            <div
              v-for="(result, index) in displayedResults"
              :key="index"
              class="bg-gray-800 shadow-md rounded-lg overflow-hidden"
            >
              <div
                class="p-4 cursor-pointer flex justify-between items-center"
                @click="toggleExpand(index)"
              >
                <div>
                  <h3
                    class="text-lg font-medium text-blue-400 hover:text-blue-300"
                  >
                    {{ result.title || "No Title" }}
                  </h3>
                  <div class="flex items-center space-x-4 mt-2">
                    <!-- Relevance Score -->
                    <span class="text-sm text-gray-400">
                      <strong>Score:</strong>
                      {{ result.score ? result.score.toFixed(2) : "0.01" }}
                    </span>
                    <!-- Search Engine -->
                    <span class="text-sm text-gray-400">
                      <strong>Engine:</strong>
                      {{ result.engine_name || "Unknown" }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <a
                    :href="result.URL || result.link || '#'"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-400 hover:text-blue-300 flex items-center mr-2"
                    @click.stop
                  >
                    Visit Page
                    <ExternalLinkIcon class="h-4 w-4 ml-1" />
                  </a>
                  <ChevronDownIcon
                    v-if="expandedResult !== index"
                    class="h-5 w-5 text-gray-400"
                  />
                  <ChevronUpIcon v-else class="h-5 w-5 text-gray-400" />
                </div>
              </div>
              <div v-if="expandedResult === index" class="px-4 pb-4">
                <p class="text-gray-300 mb-2">
                  {{ result.content || "No Content" }}
                </p>
                <div
                  class="flex flex-col sm:flex-row justify-between items-start sm:items-center text-sm"
                >
                  <!-- Relevance Score -->
                  <span class="text-gray-400 mb-2 sm:mb-0">
                    <strong>Relevance Score:</strong>
                    {{
                      typeof result.score === "number"
                        ? result.score.toFixed(2)
                        : "N/A"
                    }}
                  </span>
                  <!-- Search Engine -->
                  <span class="text-gray-400 mb-2 sm:mb-0">
                    <strong>Search Engine:</strong>
                    {{ result.engine_name || "Unknown" }}
                  </span>
                  <!-- Visit Page Link -->
                  <a
                    :href="result.URL || result.link || '#'"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-400 hover:text-blue-300 flex items-center"
                  >
                    Visit Page
                    <ExternalLinkIcon class="h-4 w-4 ml-1" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="!loading && displayedResults.length === 0"
            class="text-center py-12"
          >
            <p class="text-xl text-gray-300">
              No results found for "{{ currentQuery }}"
            </p>
            <p class="mt-2 text-gray-400">
              Try adjusting your search terms or filters
            </p>
          </div>
        </div>

        <!-- AI Summary Column -->
        <div class="lg:w-1/3">
          <div class="bg-gray-800 shadow-md rounded-lg p-6 sticky top-8">
            <h2 class="text-xl font-semibold text-white mb-4">AI Summary</h2>
            <p v-if="loading" class="text-gray-300">Generating summary...</p>
            <p v-else-if="aiSummary" class="text-gray-300">{{ aiSummary }}</p>
            <p v-else class="text-gray-300">No summary available</p>
            <div v-if="!loading && topSources.length" class="mt-6">
              <h3 class="text-lg font-semibold text-white mb-2">Top Sources</h3>
              <ul class="list-disc list-inside text-gray-300">
                <li v-for="(source, index) in topSources" :key="index">
                  {{ source }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  ChevronDownIcon,
  ChevronUpIcon,
  ExternalLinkIcon,
} from "lucide-vue-next";
import { useStore } from "vuex";

const store = useStore();
const currentQuery = ref("");
const newQuery = ref("");
const expandedResult = ref(null);
const sortOrder = ref("relevance");
const selectedSource = ref("");
const loading = ref(false);
const aiSummary = ref("");

const aiSettings = computed(() => store.getters.getAISettings);
const results = computed(() => store.getters.getSearchResults);

const toggleExpand = (index) => {
  expandedResult.value = expandedResult.value === index ? null : index;
};

const summarizeResults = computed(() => {
  const sourceCount = new Set(results.value.map((r) => r.engine_name)).size;
  return `We found ${results.value.length} relevant results from ${sourceCount} different sources for "${currentQuery.value}".`;
});

const topSources = computed(() => {
  const sourceCounts = results.value.reduce((acc, result) => {
    if (result.engine_name) {
      acc[result.engine_name] = (acc[result.engine_name] || 0) + 1;
    }
    return acc;
  }, {});
  return Object.entries(sourceCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([source, count]) => `${source} (${count} results)`);
});

const uniqueSources = computed(() => {
  return [...new Set(results.value.map((r) => r.engine_name).filter(Boolean))];
});

const displayedResults = computed(() => {
  let filteredResults = results.value;
  if (selectedSource.value) {
    filteredResults = filteredResults.filter(
      (r) => (r.engine_name || "Unknown") === selectedSource.value
    );
  }
  return filteredResults.sort((a, b) => {
    if (sortOrder.value === "relevance") {
      return (b.score || 0) - (a.score || 0);
    } else {
      const nameA = a.engine_name || "Unknown";
      const nameB = b.engine_name || "Unknown";
      return nameA.localeCompare(nameB);
    }
  });
});

const handleSort = () => {
  // Sorting is handled by the computed property
};

const handleFilter = () => {
  // Filtering is handled by the computed property
};

const performSearch = async () => {
  if (newQuery.value.trim()) {
    currentQuery.value = newQuery.value;
    loading.value = true;
    try {
      const response = await fetch("http://127.0.0.1:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keyword: newQuery.value,
          search_engines: [
            { name: "Bing", percentage: 40, resultsCount: 20 },
            { name: "Baidu", percentage: 20, resultsCount: 10 },
            { name: "Sohu", percentage: 20, resultsCount: 10 },
            { name: "quark", percentage: 20, resultsCount: 10 },
            { name: "Sogou", percentage: 0, resultsCount: 0 },
            { name: "mso", percentage: 0, resultsCount: 0 },
          ],
        }),
      });

      const data = await response.json();
      console.log("Raw data from backend:", JSON.stringify(data, null, 2));

      if (data.status === "success") {
        // Ensure each result has an engine_name and score
        const processedResults = data.results.map((result) => ({
          ...result,
          engine_name: result.engine_name || "Unknown",
          score: result.score || 0,
        }));
        console.log(
          "Processed results:",
          JSON.stringify(processedResults, null, 2)
        );
        store.commit("setSearchResults", processedResults);
        // Generate AI summary
        const summaryResponse = await fetch("http://127.0.0.1:5000/answer", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: `Summarize the search results for "${newQuery.value}"`,
            api_key: aiSettings.value.apiKey,
            provider: aiSettings.value.provider,
            model: aiSettings.value.model,
          }),
        });

        const summaryData = await summaryResponse.json();
        aiSummary.value = summaryData.answer || "No summary available";

        loading.value = false;
        newQuery.value = "";
        selectedSource.value = "";
      } else {
        console.error("Search failed:", data.message);
      }
    } catch (error) {
      console.error("Error performing search:", error);
    } finally {
      loading.value = false;
    }
  }
};

onMounted(() => {
  // Optionally, fetch initial results if needed
});
</script>

<style>
/* Existing styles */

/* New styles for result details in collapsed view */
.result-details {
  display: flex;
  flex-direction: column;
}

.result-details span {
  margin-bottom: 0.25rem;
}

@media (min-width: 640px) {
  .result-details {
    flex-direction: row;
    gap: 1rem;
  }
}
</style>
