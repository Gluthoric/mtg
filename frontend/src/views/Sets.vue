<template>
  <div class="sets">
    <h1>Magic: The Gathering Sets</h1>
    <div class="filters">
      <input v-model="filters.name" placeholder="Search by set name" @input="fetchSets">
      <select v-model="filters.set_type" @change="fetchSets">
        <option value="">All Set Types</option>
        <option value="core">Core</option>
        <option value="expansion">Expansion</option>
        <option value="masters">Masters</option>
        <option value="draft_innovation">Draft Innovation</option>
        <option value="funny">Funny</option>
        <!-- Add more set types as needed -->
      </select>
    </div>
    <div class="set-list">
      <div v-for="set in sets" :key="set.code" class="set-item">
        <router-link :to="{ name: 'SetDetails', params: { setCode: set.code } }">
          <img :src="set.icon_svg_uri" :alt="set.name" class="set-icon">
          <h3>{{ set.name }}</h3>
          <p>Code: {{ set.code }}</p>
          <p>Released: {{ new Date(set.released_at).toLocaleDateString() }}</p>
          <p>Card Count: {{ set.card_count }}</p>
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

export default {
  name: 'Sets',
  setup() {
    const sets = ref([])
    const filters = ref({ name: '', set_type: '' })
    const currentPage = ref(1)
    const totalPages = ref(1)

    const fetchSets = async () => {
      try {
        const response = await axios.get('/api/sets', {
          params: {
            ...filters.value,
            page: currentPage.value
          }
        })
        sets.value = response.data.sets
        totalPages.value = response.data.pages
      } catch (error) {
        console.error('Error fetching sets:', error)
      }
    }

    const changePage = (delta) => {
      currentPage.value += delta
      fetchSets()
    }

    onMounted(fetchSets)

    return {
      sets,
      filters,
      currentPage,
      totalPages,
      fetchSets,
      changePage
    }
  }
}
</script>

<style scoped>
.filters {
  margin-bottom: 1rem;
}

.set-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.set-item {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.5rem;
  text-align: center;
}

.set-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 0.5rem;
}

.pagination {
  margin-top: 1rem;
}
</style>