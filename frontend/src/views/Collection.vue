<template>
  <div class="container">
    <h1 class="text-center mb-2">My Collection</h1>
    <div v-if="stats" class="collection-stats card grid grid-cols-3 mb-2">
      <div class="stat">
        <h2>Total Cards</h2>
        <p>{{ stats.total_cards }}</p>
      </div>
      <div class="stat">
        <h2>Unique Cards</h2>
        <p>{{ stats.unique_cards }}</p>
      </div>
      <div class="stat">
        <h2>Total Value</h2>
        <p>${{ stats.total_value.toFixed(2) }}</p>
      </div>
    </div>
    <SetListControls
      :setTypes="setTypes"
      :totalPages="totalPages"
      @update-filters="updateFilters"
      @update-sorting="updateSorting"
      @update-per-page="updatePerPage"
    />
    <div v-if="loading" class="loading text-center mt-1">Loading...</div>
    <div v-else-if="error" class="error text-center mt-1">{{ error }}</div>
    <div v-else-if="sets && sets.length > 0" class="set-grid grid grid-cols-auto">
      <div v-for="set in sets" :key="set.code" class="card">
        <router-link :to="{ name: 'CollectionSetCards', params: { setCode: set.code } }">
          <div class="set-icon">
            <img :src="set.icon_svg_uri" :alt="set.name" />
          </div>
          <h3>{{ set.name }}</h3>
          <p>Code: {{ set.code }}</p>
          <p>Type: {{ set.set_type }}</p>
          <p>Released: {{ formatDate(set.released_at) }}</p>
          <p>Collection: {{ set.collection_count }} / {{ set.card_count }}</p>
          <p>Completion: {{ Math.round(set.collection_percentage) }}%</p>
          <div class="progress-container">
            <div
              class="progress-bar"
              :style="{ width: `${set.collection_percentage}%`, backgroundColor: getProgressColor(set.collection_percentage) }"
            ></div>
          </div>
        </router-link>
      </div>
    </div>
    <div v-else-if="!loading && sets.length === 0" class="text-center mt-1">
      <p>No sets found in your collection.</p>
    </div>
    <div class="pagination text-center mt-2">
      <button @click="changePage(-1)" :disabled="currentPage === 1">Previous</button>
      <span class="p-1">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="changePage(1)" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import SetListControls from '../components/SetListControls.vue'

export default {
  name: 'Collection',
  components: {
    SetListControls
  },
  setup() {
    const sets = ref([])
    const stats = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const filters = ref({})
    const sorting = ref({ sortBy: 'released_at', sortOrder: 'desc' })
    const currentPage = ref(1)
    const totalPages = ref(1)
    const perPage = ref(20)
    const setTypes = ref([
      'core', 'expansion', 'masters', 'draft_innovation', 'funny',
      'starter', 'box', 'promo', 'token', 'memorabilia'
    ])

    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/collection/stats')
        stats.value = response.data
      } catch (err) {
        console.error('Error fetching collection stats:', err)
        error.value = 'Failed to load collection stats'
      }
    }

    const fetchSets = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get('/api/collection/sets', {
          params: {
            ...filters.value,
            ...sorting.value,
            page: currentPage.value,
            per_page: perPage.value
          }
        })
        sets.value = response.data.sets
        totalPages.value = response.data.pages
        currentPage.value = response.data.current_page
      } catch (err) {
        console.error('Error fetching collection sets:', err)
        error.value = 'Failed to load collection sets'
      } finally {
        loading.value = false
      }
    }

    const updateFilters = (newFilters) => {
      filters.value = { ...filters.value, ...newFilters }
      currentPage.value = 1
      fetchSets()
    }

    const updateSorting = (newSorting) => {
      sorting.value = { ...newSorting }
      fetchSets()
    }

    const updatePerPage = (newPerPage) => {
      perPage.value = newPerPage
      currentPage.value = 1
      fetchSets()
    }

    const changePage = (delta) => {
      const newPage = currentPage.value + delta
      if (newPage >= 1 && newPage <= totalPages.value) {
        currentPage.value = newPage
        fetchSets()
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getProgressColor = (percentage) => {
      if (percentage < 25) return '#f44336'
      if (percentage < 50) return '#ff9800'
      if (percentage < 75) return '#ffc107'
      return '#4caf50'
    }

    onMounted(() => {
      fetchStats()
      fetchSets()
    })

    return {
      sets,
      stats,
      loading,
      error,
      filters,
      sorting,
      currentPage,
      totalPages,
      perPage,
      setTypes,
      updateFilters,
      updateSorting,
      updatePerPage,
      changePage,
      formatDate,
      getProgressColor
    }
  }
}
</script>

<style scoped>
.collection-stats .stat {
  text-align: center;
}

.set-icon {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
}

.set-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
