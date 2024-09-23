<template>
  <div class="collection-set-cards">
    <h1>{{ setName }}</h1>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="filters">
        <input v-model="nameFilter" @input="applyFilters" placeholder="Filter by name" />
        <select v-model="rarityFilter" @change="applyFilters">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
      </div>
      <div class="card-grid">
        <div v-for="card in cards" :key="card.id" class="card">
          <img :src="card.image_uris.small" :alt="card.name" />
          <h3>{{ card.name }}</h3>
          <p>Rarity: {{ card.rarity }}</p>
          <p>Regular: {{ card.quantity_regular }}</p>
          <p>Foil: {{ card.quantity_foil }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

export default {
  name: 'CollectionSetCards',
  setup() {
    const route = useRoute()
    const setCode = ref(route.params.setCode)
    const setName = ref('')
    const cards = ref([])
    const loading = ref(true)
    const error = ref(null)
    const nameFilter = ref('')
    const rarityFilter = ref('')
    const perPage = ref(1000) // Increased to 100 as requested

    const fetchCards = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get(`/api/collection/sets/${setCode.value}/cards`, {
          params: {
            name: nameFilter.value,
            rarity: rarityFilter.value,
            per_page: perPage.value // Added per_page parameter
          }
        })
        cards.value = response.data.cards
        setName.value = cards.value.length > 0 ? cards.value[0].set_name : ''
      } catch (err) {
        console.error('Error fetching set cards:', err)
        error.value = 'Failed to load set cards'
      } finally {
        loading.value = false
      }
    }

    const applyFilters = () => {
      fetchCards()
    }

    watch(() => route.params.setCode, (newSetCode) => {
      setCode.value = newSetCode
      fetchCards()
    })

    onMounted(() => {
      fetchCards()
    })

    return {
      setName,
      cards,
      loading,
      error,
      nameFilter,
      rarityFilter,
      applyFilters
    }
  }
}
</script>

<style scoped>
.collection-set-cards {
  padding: 1rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.card img {
  max-width: 100%;
  height: auto;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filters input,
.filters select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.loading,
.error {
  text-align: center;
  margin-top: 2rem;
  font-size: 1.2rem;
}
</style>
