<template>
  <div class="container">
    <h1 class="text-center mb-4">MTG Collection Manager</h1>

    <!-- Collection Stats -->
    <div class="dashboard grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div class="card text-center">
        <h2 class="mb-2">Collection Total Cards</h2>
        <p class="text-2xl font-bold">{{ stats.collection.total_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Collection Unique Cards</h2>
        <p class="text-2xl font-bold">{{ stats.collection.unique_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Collection Total Value</h2>
        <p class="text-2xl font-bold">${{ stats.collection.total_value.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Kiosk Stats -->
    <div class="dashboard grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div class="card text-center">
        <h2 class="mb-2">Kiosk Total Cards</h2>
        <p class="text-2xl font-bold">{{ stats.kiosk.total_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Kiosk Unique Cards</h2>
        <p class="text-2xl font-bold">{{ stats.kiosk.unique_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Kiosk Total Value</h2>
        <p class="text-2xl font-bold">${{ stats.kiosk.total_value.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Total Stats -->
    <div class="dashboard grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div class="card text-center">
        <h2 class="mb-2">Total Cards</h2>
        <p class="text-2xl font-bold">{{ stats.total.total_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Total Unique Cards</h2>
        <p class="text-2xl font-bold">{{ stats.total.unique_cards }}</p>
      </div>
      <div class="card text-center">
        <h2 class="mb-2">Total Value</h2>
        <p class="text-2xl font-bold">${{ stats.total.total_value.toFixed(2) }}</p>
      </div>
    </div>

    <!-- Refresh Button -->
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
      collection: { total_cards: 0, unique_cards: 0, total_value: 0 },
      kiosk: { total_cards: 0, unique_cards: 0, total_value: 0 },
      total: { total_cards: 0, unique_cards: 0, total_value: 0 }
    })
    let refreshInterval

    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/stats')
        stats.value = response.data // Set the entire response as stats
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