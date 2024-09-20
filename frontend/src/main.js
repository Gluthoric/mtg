import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

import './assets/main.css'

const app = createApp(App)

app.use(router)

// Configure Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Make Axios available globally
app.config.globalProperties.$axios = axios

app.mount('#app')