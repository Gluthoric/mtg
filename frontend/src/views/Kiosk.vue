<!-- Kiosk.vue -->
<template>
  <div class="container">
    <h1 class="text-center mb-2">Kiosk Inventory</h1>
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
        <router-link :to="{ name: 'KioskSetCards', params: { setCode: set.code } }">
          <div class="set-icon">
            <img :src="set.icon_svg_uri" :alt="set.name" />
          </div>
          <h3>{{ set.name }}</h3>
          <p>Code: {{ set.code }}</p>
          <p>Type: {{ set.set_type }}</p>
          <p>Released: {{ formatDate(set.released_at) }}</p>
          <p>Kiosk Cards: {{ set.kiosk_count }} / {{ set.card_count }}</p>
          <p>Completion: {{ Math.round(set.kiosk_percentage) }}%</p>
          <div class="progress-container">
            <div
              class="progress-bar"
              :style="{ width: `${set.kiosk_percentage}%`, backgroundColor: getProgressColor(set.kiosk_percentage) }"
            ></div>
          </div>
        </router-link>
      </div>
    </div>
    <div v-else-if="!loading && sets.length === 0" class="text-center mt-1">
      <p>No sets found in your kiosk inventory.</p>
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
  name: 'Kiosk',
  components: {
    SetListControls
  },
  setup() {
    const sets = ref([])
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

    const fetchSets = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get('/api/kiosk/sets', {
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
        console.error('Error fetching kiosk sets:', err)
        error.value = 'Failed to load kiosk sets'
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
      fetchSets()
    })

    return {
      sets,
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