import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import VueLazyload from 'vue-lazyload'
import VueVirtualScroller from 'vue3-virtual-scroller'
import axios from 'axios'

import './assets/main.css'
import 'vue3-virtual-scroller/dist/vue3-virtual-scroller.css'

const app = createApp(App)

app.use(VueLazyload, {
  preLoad: 1.3,
  error: '/path-to-error-image.png',
  loading: '/path-to-loading-image.gif',
  attempt: 1
})

app.use(router)
app.use(VueVirtualScroller)

// Configure Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Make Axios available globally
app.config.globalProperties.$axios = axios

app.mount('#app')
