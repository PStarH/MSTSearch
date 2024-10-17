import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import ResultPage from "../views/ResultPage.vue";
import SearchPage from "../views/SearchPage.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "Search",
    component: SearchPage,
  },
  {
    path: "/results",
    name: "Results",
    component: ResultPage, // You can use the same ResultPage or create a separate component
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
