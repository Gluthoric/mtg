<template>
  <div class="container">
    <h1 class="text-center mb-4">MTG Collection Manager</h1>
    <div class="dashboard grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div class="card text-center">
        <h2 class="mb-2">Total Cards</h2>
        <p class="text-2xl font-bold">{{ stats.totalCards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Unique Cards</h2>
        <p class="text-2xl font-bold">{{ stats.uniqueCards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Sets Collected</h2>
        <p class="text-2xl font-bold">{{ stats.setsCollected }}</p>
      </div>
    </div>
    <div class="text-center">
      <button @click="refreshStats" class="px-4 py-2">Refresh Stats</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Home',
  setup() {
    const stats = ref({
      totalCards: 0,
      uniqueCards: 0,
      setsCollected: 0
    })
    let refreshInterval

    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/stats')
        stats.value = response.data
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    const refreshStats = () => {
      fetchStats()
    }

    onMounted(() => {
      fetchStats()
      refreshInterval = setInterval(fetchStats, 300000) // Refresh every 5 minutes
    })

    onUnmounted(() => {
      clearInterval(refreshInterval)
    })

    return {
      stats,
      refreshStats
    }
  }
}
</script>