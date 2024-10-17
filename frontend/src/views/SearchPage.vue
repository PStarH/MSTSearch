<template>
  <div
    class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-2 sm:p-4"
  >
    <div
      class="w-full max-w-4xl bg-gray-800 rounded-lg shadow-2xl p-3 sm:p-4 md:p-6 max-h-[90vh] overflow-y-auto"
    >
      <h1
        class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-extrabold text-center mb-2 sm:mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600"
      >
        MSTSearch
      </h1>

      <!-- Tenets -->
      <div class="flex justify-center mb-3 sm:mb-4">
        <div
          class="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-full text-xs sm:text-sm md:text-base font-bold shadow-lg whitespace-nowrap overflow-x-auto max-w-full"
        >
          {{ tenets.join(" | ") }}
        </div>
      </div>

      <!-- Search Bar -->
      <div class="relative mb-3 sm:mb-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter your search query"
          class="w-full px-3 py-2 sm:px-4 sm:py-3 text-sm sm:text-base md:text-lg bg-gray-700 border-2 border-gray-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
          @keyup.enter="performSearch"
        />
        <button
          @click="performSearch"
          :disabled="isLoading"
          class="absolute right-1 sm:right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full p-1 sm:p-2 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-700 transition-all duration-200 disabled:opacity-50"
        >
          <SearchIcon v-if="!isLoading" class="h-4 w-4 sm:h-5 sm:w-5" />
          <svg
            v-else
            class="animate-spin h-4 w-4 sm:h-5 sm:w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </button>
      </div>

      <div class="text-right">
        <button
          @click="showSettings = true"
          class="text-blue-400 hover:text-blue-300 focus:outline-none transition-colors duration-200 flex items-center"
        >
          <SettingsIcon class="h-5 w-5 sm:h-6 sm:w-6 inline-block mr-1" />
          <span class="text-sm sm:text-base font-semibold">Settings</span>
        </button>
      </div>
    </div>

    <!-- Settings Popup -->
    <div
      v-if="showSettings"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-2 sm:p-4 z-50"
    >
      <div
        class="bg-gray-800 rounded-lg shadow-2xl w-full max-w-md border border-gray-700 max-h-[90vh] overflow-y-auto"
      >
        <div class="p-3 sm:p-4">
          <div class="flex justify-between items-center mb-3 sm:mb-4">
            <h2 class="text-xl sm:text-2xl font-bold text-white">Settings</h2>
            <button
              @click="showSettings = false"
              class="text-gray-400 hover:text-white focus:outline-none transition-colors duration-200"
            >
              <XIcon class="h-5 w-5 sm:h-6 sm:w-6" />
            </button>
          </div>

          <div>
            <!-- Tab Navigation -->
            <div class="flex mb-3 sm:mb-4">
              <button
                @click="currentTab = 'search-engines'"
                :class="[
                  'px-2 py-1 sm:px-3 sm:py-2 rounded-t-lg transition-colors duration-200 text-xs sm:text-sm',
                  currentTab === 'search-engines'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600',
                ]"
              >
                Search Engines
              </button>
              <button
                @click="currentTab = 'ai-settings'"
                :class="[
                  'px-2 py-1 sm:px-3 sm:py-2 rounded-t-lg transition-colors duration-200 text-xs sm:text-sm',
                  currentTab === 'ai-settings'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600',
                ]"
              >
                AI Settings
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-4 bg-gray-800 text-white rounded-b-lg">
              <div v-if="currentTab === 'search-engines'">
                <h2 class="text-xl font-semibold mb-4">
                  Manage Search Engines
                </h2>
                <!-- Add Search Engine Form -->
                <form @submit.prevent="handleAddSearchEngine" class="mb-6">
                  <div class="flex flex-col sm:flex-row items-center">
                    <input
                      type="url"
                      v-model="newSearchEngineUrl"
                      placeholder="https://example.com"
                      required
                      class="w-full sm:flex-1 px-4 py-2 rounded-md text-gray-800 focus:outline-none"
                    />
                    <button
                      type="submit"
                      class="mt-2 sm:mt-0 sm:ml-4 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      Add
                    </button>
                  </div>
                </form>

                <!-- Feedback Messages -->
                <div v-if="successMessage" class="mb-4 text-green-400">
                  {{ successMessage }}
                </div>
                <div v-if="errorMessage" class="mb-4 text-red-400">
                  {{ errorMessage }}
                </div>

                <!-- List of Search Engines -->
                <div>
                  <h3 class="text-lg font-semibold mb-2">
                    Existing Search Engines:
                  </h3>
                  <ul v-if="searchEngines && searchEngines.length > 0">
                    <li
                      v-for="engine in searchEngines"
                      :key="engine.name"
                      class="mb-2"
                    >
                      <div
                        class="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-gray-700 p-3 rounded-md"
                      >
                        <div>
                          <span class="text-blue-400">{{ engine.name }}</span>
                          <div class="flex items-center mt-1">
                            <label
                              :for="'results-' + engine.name"
                              class="text-sm text-gray-300 mr-2"
                            >
                              Results:
                            </label>
                            <input
                              :id="'results-' + engine.name"
                              v-model.number="engine.resultsCount"
                              type="number"
                              min="0"
                              max="100"
                              class="w-16 px-2 py-1 rounded-md text-gray-800 focus:outline-none"
                              @input="calculatePercentages"
                            />
                          </div>
                          <div class="flex items-center mt-1">
                            <span class="text-sm text-gray-300">
                              Percentage: {{ engine.percentage.toFixed(2) }}%
                            </span>
                          </div>
                        </div>
                        <!-- Add delete button -->
                        <button
                          @click="removeSearchEngine(engine.name)"
                          class="mt-2 sm:mt-0 text-red-500 hover:text-red-400 text-sm"
                        >
                          Remove
                        </button>
                      </div>
                    </li>
                  </ul>
                  <div v-else class="text-gray-400">
                    No search engines configured.
                  </div>
                </div>
              </div>

              <div v-else-if="currentTab === 'ai-settings'">
                <h2 class="text-xl font-semibold mb-4">AI Settings</h2>
                <form @submit.prevent="saveSettings" class="space-y-4">
                  <div>
                    <label
                      for="model"
                      class="block text-sm font-medium text-gray-300"
                      >Model</label
                    >
                    <select
                      v-model="aiSettings.model"
                      id="model"
                      class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a model</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="gpt-4">GPT-4</option>
                      <option value="text-davinci-002">Text Davinci 002</option>
                      <option value="text-davinci-003">Text Davinci 003</option>
                      <option value="claude-v1">Claude v1</option>
                      <option value="claude-instant-v1">
                        Claude Instant v1
                      </option>
                      <option value="palm-2">PaLM 2</option>
                    </select>
                  </div>
                  <div>
                    <label
                      for="apiKey"
                      class="block text-sm font-medium text-gray-300"
                      >API Key</label
                    >
                    <input
                      v-model="aiSettings.apiKey"
                      id="apiKey"
                      type="password"
                      class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label
                      for="provider"
                      class="block text-sm font-medium text-gray-300"
                      >Provider</label
                    >
                    <select
                      v-model="aiSettings.provider"
                      id="provider"
                      class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a provider</option>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="google">Google</option>
                    </select>
                  </div>
                  <button
                    type="submit"
                    class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                  >
                    Save Settings
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { SearchIcon, SettingsIcon, XIcon } from "lucide-vue-next";
import axios from "axios";

const router = useRouter();
const store = useStore();

const searchQuery = ref("");
const showSettings = ref(false);
const currentTab = ref("search-engines");
const isLoading = ref(false);

const tenets = [
  "Multi-Source Aggregation",
  "NLP Enhanced Sorting",
  "Intelligent Summarization",
];

const searchEngines = ref([
  { name: "Bing", resultsCount: 20, percentage: 0 },
  { name: "Baidu", resultsCount: 10, percentage: 0 },
  { name: "Sohu", resultsCount: 10, percentage: 0 },
  { name: "quark", resultsCount: 10, percentage: 0 },
  { name: "Sogou", resultsCount: 0, percentage: 0 },
  { name: "mso", resultsCount: 0, percentage: 0 },
]);

const aiSettings = ref({
  model: "",
  apiKey: "",
  provider: "",
});

const newSearchEngineUrl = ref("");
const errorMessage = ref("");
const successMessage = ref("");

const calculatePercentages = () => {
  const totalResults = searchEngines.value.reduce(
    (sum, engine) => sum + engine.resultsCount,
    0
  );
  searchEngines.value.forEach((engine) => {
    engine.percentage = (engine.resultsCount / totalResults) * 100;
  });
};

// Call calculatePercentages initially to set up percentages
calculatePercentages();

const performSearch = async () => {
  if (searchQuery.value.trim() === "") return;

  isLoading.value = true;
  try {
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        keyword: searchQuery.value,
        search_engines: searchEngines.value.map((engine) => ({
          name: engine.name,
          percentage: engine.percentage,
          resultsCount: engine.resultsCount,
        })),
      }),
    });

    const data = await response.json();

    if (data.status === "success") {
      store.commit("setSearchResults", data.results);
      router.push("/results");
    } else {
      console.error("Search failed:", data.message);
    }
  } catch (error) {
    console.error("Search error:", error);
  } finally {
    isLoading.value = false;
  }
};

const saveSettings = async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        api_key: aiSettings.value.apiKey,
        model: aiSettings.value.model,
        provider: aiSettings.value.provider,
      }),
    });

    const data = await response.json();

    if (data.status === "success") {
      store.commit("setAISettings", aiSettings.value);
      showSettings.value = false;
    } else {
      console.error("Save settings failed:", data.message);
    }
  } catch (error) {
    console.error("Error saving settings:", error);
  }
};

const handleAddSearchEngine = () => {
  if (!newSearchEngineUrl.value) {
    errorMessage.value = "You need to enter a URL";
    return;
  }

  try {
    const url = new URL(newSearchEngineUrl.value);
    let engineName = url.hostname.replace(/^www\./, "");
    // Extract the main domain name
    const domainParts = engineName.split(".");
    if (domainParts.length > 2) {
      engineName = domainParts.slice(-2).join(".");
    }

    // Special case for known search engines
    if (engineName.includes("bilibili")) {
      engineName = "Bilibili";
    } else if (engineName.includes("google")) {
      engineName = "Google";
    } else if (engineName.includes("bing")) {
      engineName = "Bing";
    } else if (engineName.includes("baidu")) {
      engineName = "Baidu";
    } else if (engineName.includes("yahoo")) {
      engineName = "Yahoo";
    } else if (engineName.includes("duckduckgo")) {
      engineName = "DuckDuckGo";
    } else {
      // Capitalize the first letter of each word
      engineName = engineName
        .split(".")[0]
        .replace(/\b\w/g, (l) => l.toUpperCase());
    }

    if (
      searchEngines.value.some(
        (engine) => engine.name.toLowerCase() === engineName.toLowerCase()
      )
    ) {
      errorMessage.value = "This search engine already exists";
      return;
    }

    // Add the new engine to the searchEngines array
    searchEngines.value.push({
      name: engineName,
      url: newSearchEngineUrl.value,
      resultsCount: 10, // Default value, can be adjusted
      percentage: 0, // Will be recalculated
    });

    newSearchEngineUrl.value = "";
    successMessage.value = "Search engine added successfully";
    errorMessage.value = "";

    calculatePercentages();
    // Update the store
    store.commit("setSearchEngines", searchEngines.value);
  } catch (error) {
    errorMessage.value = "Please enter a valid URL";
  }
};

const removeSearchEngine = async (engineName) => {
  try {
    console.log(`Attempting to remove search engine: ${engineName}`);
    const response = await axios.delete(
      "http://127.0.0.1:5000/manage-search-engines",
      {
        data: { name: engineName },
      }
    );

    console.log("Response from server:", response.data);

    if (response.data.status === "success") {
      const index = searchEngines.value.findIndex(
        (engine) => engine.name === engineName
      );
      if (index !== -1) {
        searchEngines.value.splice(index, 1);
        calculatePercentages();
        successMessage.value = response.data.message;
        errorMessage.value = "";
        // Update the store
        store.commit("setSearchEngines", searchEngines.value);
        console.log(`Search engine ${engineName} removed successfully`);
      } else {
        console.warn(`Search engine ${engineName} not found in local array`);
      }
    } else {
      errorMessage.value = "Failed to remove search engine. Please try again.";
      successMessage.value = "";
      console.error("Server responded with an error:", response.data);
    }
  } catch (error) {
    console.error("Error removing search engine:", error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("Error data:", error.response.data);
      console.error("Error status:", error.response.status);
      console.error("Error headers:", error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error("No response received:", error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("Error message:", error.message);
    }
    errorMessage.value =
      "An error occurred while removing the search engine. Please check the console for more details.";
    successMessage.value = "";
  }
};

// Define totalPercentage as a reactive reference
const totalPercentage = ref(50);

onMounted(() => {
  // Ensure the initial total is 50%
  const initialTotal = totalPercentage.value;
  if (initialTotal !== 50) {
    const adjustment = 50 - initialTotal;
    searchEngines.value[0].percentage += adjustment;
  }
});
</script>
