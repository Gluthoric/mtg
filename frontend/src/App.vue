<template>
  <div id="app" class="flex flex-col min-h-screen bg-white dark:bg-theme-dark-300 text-black dark:text-white">
    <Header @toggle-dark-mode="toggleDarkMode" />
    <main class="flex-1 overflow-x-hidden overflow-y-auto p-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref } from 'vue'
import Header from './components/Header.vue'

export default defineComponent({
  name: 'App',
  components: {
    Header
  },
  setup() {
    const isDarkMode = ref(false)

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      document.documentElement.classList.toggle('dark', isDarkMode.value)
      localStorage.setItem('darkMode', isDarkMode.value)
    }

    onMounted(() => {
      const savedDarkMode = localStorage.getItem('darkMode')
      if (savedDarkMode !== null) {
        isDarkMode.value = JSON.parse(savedDarkMode)
        document.documentElement.classList.toggle('dark', isDarkMode.value)
      }
    })

    return {
      toggleDarkMode
    }
  }
})
</script>

<style>
#app {
  font-family: Arial, sans-serif;
}

body {
  margin: 0;
  padding: 0;
}
</style>
