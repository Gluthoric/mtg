<template>
  <div class="collection-set-cards">
    <h1 class="set-title">{{ setName }}</h1>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="filters">
        <input v-model="nameFilter" @input="applyFilters" placeholder="Filter by name" class="filter-input" />
        <select v-model="rarityFilter" @change="applyFilters" class="filter-select">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
      </div>
      <div class="card-grid">
        <div
          v-for="card in filteredCards"
          :key="card.id"
          class="card"
          :class="{ missing: isMissing(card) }"
        >
          <img :src="card.image_uris.small" :alt="card.name" class="card-image" />
          <div class="card-info">
            <h3 class="card-name">{{ card.name }}</h3>
            <p class="card-rarity">{{ card.rarity }}</p>
            <div class="card-quantities">
              <p>Regular: {{ card.quantity_regular }}</p>
              <p>Foil: {{ card.quantity_foil }}</p>
            </div>
          </div>
          <div v-if="isMissing(card)" class="missing-indicator">Missing</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
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

    const fetchCards = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get(`/api/sets/${setCode.value}/cards`, {
          params: {
            name: nameFilter.value,
            rarity: rarityFilter.value
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

    const isMissing = (card) => {
      return (card.quantity_regular + card.quantity_foil) === 0
    }

    const filteredCards = computed(() => {
      return cards.value
    })

    return {
      setName,
      cards,
      loading,
      error,
      nameFilter,
      rarityFilter,
      applyFilters,
      isMissing,
      filteredCards
    }
  }
}
</script>

<style scoped>
.collection-set-cards {
  padding: 2rem;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.set-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.card {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  background-color: #fff;
  position: relative;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.card.missing {
  box-shadow: 0 4px 6px rgba(244, 67, 54, 0.3);
}

.card-image {
  width: 100%;
  height: auto;
  display: block;
}

.card-info {
  padding: 1rem;
}

.card-name {
  font-size: 1rem;
  margin: 0 0 0.5rem;
  color: #333;
}

.card-rarity {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.card-quantities {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.filter-input,
.filter-select {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
}

.filter-input {
  width: 250px;
}

.filter-select {
  width: 150px;
}

.loading,
.error {
  text-align: center;
  margin-top: 2rem;
  font-size: 1.2rem;
  color: #666;
}

.missing-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #f44336;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}
</style>