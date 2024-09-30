import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './assets/main.css'
import 'tailwindcss/tailwind.css'

const app = createApp(App)

app.use(router)

app.mount('#app')

console.log('Vue app mounted') // For debugging
