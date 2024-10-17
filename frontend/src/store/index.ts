import { createStore } from "vuex";
import axios from "axios";

interface SearchEngine {
  name: string;
  url: string;
  // Add other relevant properties
}

interface State {
  searchEngines: string[]; // Define the appropriate type for searchEngines
}

const state: State = {
  searchEngines: [], // Now TypeScript knows this is a string array
};

const mutations = {
  addSearchEngine(state: State, searchEngine: string) {
    // Specify the type of searchEngine
    state.searchEngines.push(searchEngine);
  },
};

export default createStore({
  state: {
    searchResults: [],
    aiSettings: {
      model: "",
      apiKey: "",
      provider: "",
    },
    searchEngines: [], // New state for search engines
  },
  getters: {
    getSearchResults: (state) => state.searchResults,
    getAISettings: (state) => state.aiSettings,
    getSearchEngines: (state) => state.searchEngines, // Getter for search engines
  },
  mutations: {
    setSearchResults(state, results) {
      state.searchResults = results.map((result: { engine_name: any }) => ({
        ...result,
        engine_name: result.engine_name || "Unknown",
      }));
    },
    setAISettings(state, settings) {
      state.aiSettings = settings;
    },
    setSearchEngines(state, searchEngines) {
      // Mutation to set search engines
      state.searchEngines = searchEngines;
    },
    addSearchEngine(state: State, searchEngine: string) {
      // Mutation to add a new search engine
      state.searchEngines.push(searchEngine);
    },
  },
  actions: {
    async fetchSearchEngines({ commit }) {
      // Action to fetch search engines from backend
      try {
        const response = await axios.get("/api/search-engines");
        commit("setSearchEngines", response.data.searchEngines);
      } catch (error) {
        console.error("Error fetching search engines:", error);
      }
    },
    async addSearchEngine({ commit }, url) {
      // Action to add a new search engine
      try {
        const response = await axios.post("/api/search-engines", { url });
        if (response.data.success) {
          commit("addSearchEngine", response.data.searchEngine);
        } else {
          throw new Error(
            response.data.message || "Failed to add search engine."
          );
        }
      } catch (error) {
        console.error("Error adding search engine:", error);
        throw error;
      }
    },
  },
  modules: {},
});
