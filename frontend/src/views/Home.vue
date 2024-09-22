<template>
  <div class="home">
    <h1>MTG Collection Manager</h1>
    <div class="dashboard">
      <div class="stat-card">
        <h2>Total Cards</h2>
        <p>{{ stats.totalCards }}</p>
      </div>
      <div class="stat-card">
        <h2>Unique Cards</h2>
        <p>{{ stats.uniqueCards }}</p>
      </div>
      <div class="stat-card">
        <h2>Sets Collected</h2>
        <p>{{ stats.setsCollected }}</p>
      </div>
    </div>
    <button @click="refreshStats">Refresh Stats</button>
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

<style scoped>
.home {
  padding: 1rem;
}

.dashboard {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
}

.stat-card {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  color: var(--text-color);
}

button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: var(--link-color);
}
</style>