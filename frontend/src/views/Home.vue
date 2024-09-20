<template>
  <div class="home">
    <h1>Welcome to MTG Collection Kiosk</h1>
    <p>Manage your Magic: The Gathering card collection and kiosk inventory with ease.</p>
    <div class="dashboard">
      <div class="stat-card">
        <h3>Collection Stats</h3>
        <p>Total Cards: {{ collectionStats.totalCards }}</p>
        <p>Unique Cards: {{ collectionStats.uniqueCards }}</p>
        <p>Total Value: ${{ collectionStats.totalValue.toFixed(2) }}</p>
      </div>
      <div class="stat-card">
        <h3>Kiosk Stats</h3>
        <p>Total Cards: {{ kioskStats.totalCards }}</p>
        <p>Unique Cards: {{ kioskStats.uniqueCards }}</p>
        <p>Total Value: ${{ kioskStats.totalValue.toFixed(2) }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Home',
  setup() {
    const collectionStats = ref({ totalCards: 0, uniqueCards: 0, totalValue: 0 })
    const kioskStats = ref({ totalCards: 0, uniqueCards: 0, totalValue: 0 })

    const fetchStats = async () => {
      try {
        const [collectionResponse, kioskResponse] = await Promise.all([
          axios.get('/api/collection/stats'),
          axios.get('/api/kiosk/stats')
        ])
        collectionStats.value = collectionResponse.data
        kioskStats.value = kioskResponse.data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    onMounted(fetchStats)

    return {
      collectionStats,
      kioskStats
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
}

.stat-card {
  background-color: #f0f0f0;
  border-radius: 8px;
  padding: 1rem;
  width: 45%;
}
</style>