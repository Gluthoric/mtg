<template>
  <div class="container">
    <h1 class="text-center mb-2">{{ setName }}</h1>
    <div v-if="loading" class="loading text-center mt-1">Loading...</div>
    <div v-else-if="error" class="error text-center mt-1">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 md:grid-cols-2 gap-1 mb-2">
        <input
          v-model="nameFilter"
          @input="applyFilters"
          placeholder="Filter by name"
        />
        <select v-model="rarityFilter" @change="applyFilters">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
      </div>
      <div class="card-grid grid grid-cols-auto gap-1">
        <div
          v-for="card in sortedCards"
          :key="card.id"
          class="card"
          :class="{ 'border-error': isMissing(card) }"
        >
          <img
            v-if="getImageUrl(card)"
            :src="getImageUrl(card)"
            :alt="card.name"
            class="img-responsive"
            @error="handleImageError($event, card)"
          />
          <div v-else class="p-2 text-center bg-secondary">No image available</div>
          <div class="card-info p-1">
            <h3 class="mb-1">{{ card.name }}</h3>
            <p class="mb-1">Collector Number: {{ card.collector_number }}</p>
            <p class="mb-1">Rarity: {{ card.rarity }}</p>
            <div class="card-quantities grid grid-cols-2 gap-1">
              <QuantityControl
                label="Regular"
                :fieldId="'regular-' + card.id"
                :value="card.quantity_regular"
                @update="(val) => updateQuantity(card, 'regular', val)"
              />
              <QuantityControl
                label="Foil"
                :fieldId="'foil-' + card.id"
                :value="card.quantity_foil"
                @update="(val) => updateQuantity(card, 'foil', val)"
              />
            </div>
          </div>
          <div v-if="isMissing(card)" class="missing-indicator absolute top-2 right-2 bg-error text-white p-1 rounded text-sm font-bold">Missing</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import QuantityControl from './QuantityControl.vue' // Adjust the path as needed

export default {
  name: 'CollectionSetCards',
  components: {
    QuantityControl
  },
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
      const noImageDiv = event.target.parentNode.querySelector('.bg-secondary');
      if (noImageDiv) {
        noImageDiv.style.display = 'block';
      }
    }

    const updateQuantity = async (card, type, newValue) => {
      const updatedCard = { ...card }
      if (type === 'regular') {
        updatedCard.quantity_regular = newValue
      } else if (type === 'foil') {
        updatedCard.quantity_foil = newValue
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
      updateQuantity
    }
  }
}
</script>

<style scoped>
/* Component-specific styles can be added here if needed */
</style>
