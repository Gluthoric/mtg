<template>
  <div class="collection">
    <h1>My Collection</h1>
    <div class="filters">
      <input v-model="filters.name" placeholder="Search by name" @input="fetchCards">
      <select v-model="filters.set" @change="fetchCards">
        <option value="">All Sets</option>
        <option v-for="set in sets" :key="set.code" :value="set.code">{{ set.name }}</option>
      </select>
      <select v-model="filters.rarity" @change="fetchCards">
        <option value="">All Rarities</option>
        <option value="common">Common</option>
        <option value="uncommon">Uncommon</option>
        <option value="rare">Rare</option>
        <option value="mythic">Mythic</option>
      </select>
    </div>
    <div class="card-list">
      <div v-for="card in cards" :key="card.id" class="card-item">
        <img :src="card.image_uris.small" :alt="card.name">
        <div class="card-details">
          <h3>{{ card.name }}</h3>
          <p>Set: {{ card.set_name }}</p>
          <p>Rarity: {{ card.rarity }}</p>
          <p>Quantity: {{ card.quantity.quantity_regular + card.quantity.quantity_foil }}</p>
          <button @click="openEditModal(card)">Edit</button>
        </div>
      </div>
    </div>
    <div class="pagination">
      <button @click="changePage(-1)" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="changePage(1)" :disabled="currentPage === totalPages">Next</button>
    </div>
    <!-- Edit Modal (implement later) -->
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Collection',
  setup() {
    const cards = ref([])
    const sets = ref([])
    const filters = ref({ name: '', set: '', rarity: '' })
    const currentPage = ref(1)
    const totalPages = ref(1)

    const fetchCards = async () => {
      try {
        const response = await axios.get('/api/collection', {
          params: {
            ...filters.value,
            page: currentPage.value
          }
        })
        cards.value = response.data.collection
        totalPages.value = response.data.pages
      } catch (error) {
        console.error('Error fetching cards:', error)
      }
    }

    const fetchSets = async () => {
      try {
        const response = await axios.get('/api/sets')
        sets.value = response.data.sets
      } catch (error) {
        console.error('Error fetching sets:', error)
      }
    }

    const changePage = (delta) => {
      currentPage.value += delta
      fetchCards()
    }

    const openEditModal = (card) => {
      // Implement edit modal logic
      console.log('Edit card:', card)
    }

    onMounted(() => {
      fetchCards()
      fetchSets()
    })

    return {
      cards,
      sets,
      filters,
      currentPage,
      totalPages,
      fetchCards,
      changePage,
      openEditModal
    }
  }
}
</script>

<style scoped>
.filters {
  margin-bottom: 1rem;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.card-item {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.5rem;
}

.card-item img {
  width: 100%;
  height: auto;
}

.pagination {
  margin-top: 1rem;
}
</style>