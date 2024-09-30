import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './assets/main.css'
import 'tailwindcss/tailwind.css'

const app = createApp(App)

app.use(router)

app.mount('#app')

console.log('Vue app mounted') // Add this line for debugging
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css' // Import Tailwind CSS

const app = createApp(App)

app.use(router)

app.mount('#app')
