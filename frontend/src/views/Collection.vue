<template>
  <div class="collection">
    <h1>My Collection</h1>
    <div v-if="stats" class="collection-stats">
      <p>Total Cards: {{ stats.total_cards }}</p>
      <p>Unique Cards: {{ stats.unique_cards }}</p>
      <p>Total Value: ${{ stats.total_value.toFixed(2) }}</p>
    </div>
    <SetListControls
      :setTypes="setTypes"
      :totalPages="totalPages"
      @update-filters="updateFilters"
      @update-sorting="updateSorting"
      @update-per-page="updatePerPage"
    />
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="set-grid">
      <div v-for="set in sets" :key="set.code" class="set-card">
        <router-link :to="{ name: 'CollectionSetCards', params: { setCode: set.code } }">
          <div class="set-icon">
            <img :src="set.icon_svg_uri" :alt="set.name" />
            <div class="completion-circle" :style="{ '--percentage': set.collection_percentage + '%' }"></div>
          </div>
          <h3>{{ set.name }}</h3>
          <p>Code: {{ set.code }}</p>
          <p>Type: {{ set.set_type }}</p>
          <p>Released: {{ formatDate(set.released_at) }}</p>
          <p>Collection: {{ set.collection_count }} / {{ set.card_count }}</p>
          <p>Completion: {{ Math.round(set.collection_percentage) }}%</p>
        </router-link>
      </div>
    </div>
    <div class="pagination">
      <button @click="changePage(-1)" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
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
        totalPages.value = Math.ceil(response.data.sets.length / perPage.value)
        currentPage.value = 1
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
      formatDate
    }
  }
}
</script>

<style scoped>
.collection {
  padding: 1rem;
}

.collection-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 8px;
}

.set-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.set-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  background-color: #f9f9f9;
}

.set-icon {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 1rem;
}

.set-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.completion-circle {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    #4CAF50 calc(var(--percentage) * 1%),
    #e0e0e0 calc(var(--percentage) * 1%)
  );
  opacity: 0.7;
}

.loading, .error {
  text-align: center;
  margin-top: 2rem;
  font-size: 1.2rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
}

.pagination button {
  margin: 0 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>