<template>
  <div class="sets">
    <h1>Magic: The Gathering Sets</h1>
    <div v-if="loading">Loading sets...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else-if="sets.length === 0">No sets found.</div>
    <div v-else>
      <p>Total sets: {{ sets.length }}</p>
      <div class="set-grid">
        <div v-for="set in sets" :key="set.code" class="set-card">
          <router-link :to="{ name: 'SetDetails', params: { setCode: set.code } }">
            <img :src="set.icon_svg_uri" :alt="set.name" class="set-icon" />
            <h2>{{ set.name }}</h2>
            <p>Released: {{ formatDate(set.released_at) }}</p>
            <div class="progress-container">
              <div
                class="progress-bar"
                :style="{ width: `${set.collection_percentage}%` }"
                :class="getProgressBarClass(set.collection_percentage)"
              ></div>
            </div>
            <p class="collection-status">{{ formatCollectionProgress(set) }}</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Sets',
  setup() {
    const sets = ref([])
    const filters = ref({ name: '', set_type: '' })
    const currentPage = ref(1)
    const totalPages = ref(1)
    const loading = ref(true)
    const error = ref(null)

    const fetchSets = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get('/api/sets', {
          params: {
            ...filters.value,
            page: currentPage.value
          }
        })
        sets.value = response.data.sets
        totalPages.value = response.data.pages
      } catch (err) {
        console.error('Error fetching sets:', err)
        error.value = 'Failed to load sets'
      } finally {
        loading.value = false
      }
    }

    const changePage = (delta) => {
      currentPage.value += delta
      fetchSets()
    }

    const formatDate = (dateString) => {
      return dateString ? new Date(dateString).toLocaleDateString() : 'N/A'
    }

    const formatCollectionProgress = (set) => {
      if (set.collection_count === 0) {
        return 'Not Started (0%)'
      } else if (set.collection_count === set.card_count) {
        return 'Complete (100%)'
      } else {
        return `${set.collection_count}/${set.card_count} (${set.collection_percentage.toFixed(2)}%)`
      }
    }

    const getProgressBarClass = (percentage) => {
      if (percentage === 0) return 'not-started'
      if (percentage < 25) return 'just-started'
      if (percentage < 50) return 'in-progress'
      if (percentage < 75) return 'well-progressed'
      if (percentage < 100) return 'almost-complete'
      return 'complete'
    }

    onMounted(fetchSets)

    return {
      sets,
      filters,
      currentPage,
      totalPages,
      loading,
      error,
      fetchSets,
      changePage,
      formatDate,
      formatCollectionProgress,
      getProgressBarClass
    }
  }
}
</script>

<style scoped>
.sets {
  padding: 20px;
}

.sets h1 {
  font-size: 2em;
  color: #ffffff;
  margin-bottom: 20px;
  text-align: center;
}

.set-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.set-card {
  background-color: #2c3e50;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  transition: transform 0.3s ease;
}

.set-card:hover {
  transform: scale(1.05);
}

.set-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 10px;
}

.set-card h2 {
  font-size: 1.2em;
  color: #ffffff;
  margin-bottom: 5px;
}

.set-card p {
  font-size: 0.9em;
  color: #cccccc;
  margin: 5px 0;
}

.progress-container {
  width: 100%;
  background-color: #34495e;
  border-radius: 10px;
  margin: 10px 0;
  overflow: hidden;
}

.progress-bar {
  height: 10px;
  transition: width 0.5s ease-in-out;
}

.progress-bar.not-started {
  background-color: #95a5a6;
}
.progress-bar.just-started {
  background-color: #e74c3c;
}
.progress-bar.in-progress {
  background-color: #e67e22;
}
.progress-bar.well-progressed {
  background-color: #f1c40f;
}
.progress-bar.almost-complete {
  background-color: #2ecc71;
}
.progress-bar.complete {
  background-color: #3498db;
}

.collection-status {
  font-weight: bold;
  color: #ffffff;
}
</style>