import { createApp } from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import store from "./store";

import "./assets/tailwind.css";

// Add these lines
import "tailwindcss/tailwind.css";
import "@/assets/index.css";

createApp(App).use(store).use(router).mount("#app");
