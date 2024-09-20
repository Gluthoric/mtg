import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Collection from '../views/Collection.vue'
import Kiosk from '../views/Kiosk.vue'
import Import from '../views/Import.vue'
import Sets from '../views/Sets.vue'
import SetDetails from '../views/SetDetails.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/collection',
    name: 'Collection',
    component: Collection
  },
  {
    path: '/kiosk',
    name: 'Kiosk',
    component: Kiosk
  },
  {
    path: '/import',
    name: 'Import',
    component: Import
  },
  {
    path: '/sets',
    name: 'Sets',
    component: Sets
  },
  {
    path: '/sets/:setCode',
    name: 'SetDetails',
    component: SetDetails,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router