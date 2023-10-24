import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UserView from "../views/UserView.vue";
import ObserverView from "../views/ObserverView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/user',
      name: 'user',
      component: UserView
    },
    {
      path: '/observer',
      name: 'observer',
      component: ObserverView
    },
    {
      path: '/',
      name: 'home',
      component: HomeView
    }
  ]
})

export default router
