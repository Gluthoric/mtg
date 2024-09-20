import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/collection',
      name: 'Collection',
      component: () => import('./views/Collection.vue')
    },
    {
      path: '/kiosk',
      name: 'Kiosk',
      component: () => import('./views/Kiosk.vue')
    },
    {
      path: '/import',
      name: 'Import',
      component: () => import('./views/Import.vue')
    }
  ]
})

export default router