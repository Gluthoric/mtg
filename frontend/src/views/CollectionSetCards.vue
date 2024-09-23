<template>
  <div class="collection-set-cards">
    <h1 class="set-title">{{ setName }}</h1>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="filters">
        <input
          v-model="nameFilter"
          @input="applyFilters"
          placeholder="Filter by name"
          class="filter-input"
        />
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
          v-for="card in sortedCards"
          :key="card.id"
          class="card"
          :class="{ missing: isMissing(card) }"
        >
          <img
            v-if="getImageUrl(card)"
            :src="getImageUrl(card)"
            :alt="card.name"
            class="card-image"
            @error="handleImageError($event, card)"
          />
          <div v-else class="no-image">No image available</div>
          <div class="card-info">
            <h3 class="card-name">{{ card.name }}</h3>
            <p class="card-collector-number">Collector Number: {{ card.collector_number }}</p>
            <p class="card-rarity">Rarity: {{ card.rarity }}</p>
            <div class="card-quantities">
              <div class="quantity-control">
                <span>Regular: {{ card.quantity_regular }}</span>
                <button @click="decrementQuantity(card, 'regular')" :disabled="card.quantity_regular === 0">−</button>
                <button @click="incrementQuantity(card, 'regular')">+</button>
              </div>
              <div class="quantity-control">
                <span>Foil: {{ card.quantity_foil }}</span>
                <button @click="decrementQuantity(card, 'foil')" :disabled="card.quantity_foil === 0">−</button>
                <button @click="incrementQuantity(card, 'foil')">+</button>
              </div>
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
        console.log('Fetched cards:', cards.value)
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

    const sortedCards = computed(() => {
      return cards.value.slice().sort((a, b) => {
        if (!a.collector_number && !b.collector_number) return 0;
        if (!a.collector_number) return 1;
        if (!b.collector_number) return -1;

        const numA = parseInt(a.collector_number, 10);
        const numB = parseInt(b.collector_number, 10);

        if (!isNaN(numA) && !isNaN(numB)) {
          return numA - numB;
        }
        return a.collector_number.localeCompare(b.collector_number);
      });
    });

    const getImageUrl = (card) => {
      const imageSizes = ['normal', 'large', 'small', 'png', 'art_crop', 'border_crop'];

      if (card.image_uris) {
        for (const size of imageSizes) {
          if (card.image_uris[size]) {
            return card.image_uris[size];
          }
        }
      }

      if (card.card_faces && card.card_faces[0].image_uris) {
        for (const size of imageSizes) {
          if (card.card_faces[0].image_uris[size]) {
            return card.card_faces[0].image_uris[size];
          }
        }
      }

      console.warn('No image URL found for card:', card.name);
      return null;
    }

    const handleImageError = (event, card) => {
      console.error('Image failed to load for card:', card.name, 'URL:', event.target.src);
      event.target.style.display = 'none';
      event.target.parentNode.querySelector('.no-image').style.display = 'block';
    }

    const incrementQuantity = async (card, type) => {
      const updatedCard = { ...card }
      if (type === 'regular') {
        updatedCard.quantity_regular += 1
      } else if (type === 'foil') {
        updatedCard.quantity_foil += 1
      }

      try {
        const response = await axios.put(`/api/collection/${card.id}`, {
          quantity_regular: updatedCard.quantity_regular,
          quantity_foil: updatedCard.quantity_foil
        })
        // Update the local card data
        const index = cards.value.findIndex(c => c.id === card.id)
        if (index !== -1) {
          cards.value[index] = response.data
        }
      } catch (err) {
        console.error('Error updating quantity:', err)
        alert('Failed to update quantity. Please try again.')
      }
    }

    const decrementQuantity = async (card, type) => {
      const updatedCard = { ...card }
      if (type === 'regular' && updatedCard.quantity_regular > 0) {
        updatedCard.quantity_regular -= 1
      } else if (type === 'foil' && updatedCard.quantity_foil > 0) {
        updatedCard.quantity_foil -= 1
      } else {
        return
      }

      try {
        const response = await axios.put(`/api/collection/${card.id}`, {
          quantity_regular: updatedCard.quantity_regular,
          quantity_foil: updatedCard.quantity_foil
        })
        // Update the local card data
        const index = cards.value.findIndex(c => c.id === card.id)
        if (index !== -1) {
          cards.value[index] = response.data
        }
      } catch (err) {
        console.error('Error updating quantity:', err)
        alert('Failed to update quantity. Please try again.')
      }
    }

    return {
      setName,
      cards,
      loading,
      error,
      nameFilter,
      rarityFilter,
      applyFilters,
      isMissing,
      sortedCards,
      getImageUrl,
      handleImageError,
      incrementQuantity,
      decrementQuantity
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

.no-image {
  display: none;
  padding: 2rem;
  text-align: center;
  background-color: #f0f0f0;
  color: #666;
}

.card-info {
  padding: 1rem;
}

.card-name {
  font-size: 1rem;
  margin: 0 0 0.5rem;
  color: #333;
}

.card-collector-number {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 0.5rem;
}

.card-rarity {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.card-quantities {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-control button {
  padding: 0.2rem 0.5rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 3px;
  cursor: pointer;
  font-size: 1rem;
}

.quantity-control button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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
