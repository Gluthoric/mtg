<template>
  <div class="container mx-auto px-4">
    <h1 class="text-center mb-4 text-2xl font-bold text-blue-600">{{ setName }}</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <input
          v-model="nameFilter"
          @input="applyFilters"
          placeholder="Filter by name"
          class="p-2 border rounded"
        />
        <select v-model="rarityFilter" @change="applyFilters" class="p-2 border rounded">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
      </div>

      <!-- Slider to Adjust Card Size -->
      <div class="mb-4">
        <label for="card-size-slider" class="block text-sm font-medium mb-2">Card Size</label>
        <input
          id="card-size-slider"
          type="range"
          v-model="cardSize"
          min="100"
          max="300"
          class="w-full"
        />
      </div>

      <div class="card-grid grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" :style="gridStyle">
        <div
          v-for="card in sortedCards"
          :key="card.id"
          class="card bg-white shadow-md rounded-lg overflow-hidden relative"
          :class="{ 'border-2 border-red-500': isMissing(card) }"
        >
          <div class="image-container" :style="{ height: `${cardSize}px` }">
            <img
              v-if="getImageUrl(card)"
              :src="getImageUrl(card)"
              :alt="card.name"
              class="w-full h-full object-contain"
              @error="handleImageError($event, card)"
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500">
              No image available
            </div>
          </div>
          <div class="card-info p-4">
            <h3 class="text-lg font-semibold mb-2 truncate">{{ card.name }}</h3>
            <p class="text-sm mb-1">Collector Number: {{ card.collector_number }}</p>
            <p class="text-sm mb-2">Rarity: {{ card.rarity }}</p>
            <div class="card-quantities grid grid-cols-2 gap-2">
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
          <div v-if="isMissing(card)" class="missing-indicator absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">
            Missing
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import QuantityControl from './QuantityControl.vue'; // Adjust the path as needed

export default {
  name: 'CollectionSetCards',
  components: {
    QuantityControl,
  },
  setup() {
    const route = useRoute();
    const setCode = ref(route.params.setCode);
    const setName = ref('');
    const cards = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const nameFilter = ref('');
    const rarityFilter = ref('');

    // Card size slider
    const cardSize = ref(200); // Default card size

    const fetchCards = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get(`/api/sets/${setCode.value}/cards`, {
          params: {
            name: nameFilter.value,
            rarity: rarityFilter.value,
          },
        });
        cards.value = response.data.cards;
        setName.value = cards.value.length > 0 ? cards.value[0].set_name : '';
      } catch (err) {
        console.error('Error fetching set cards:', err);
        error.value = 'Failed to load set cards';
      } finally {
        loading.value = false;
      }
    };

    const applyFilters = () => {
      fetchCards();
    };

    watch(
      () => route.params.setCode,
      (newSetCode) => {
        setCode.value = newSetCode;
        fetchCards();
      }
    );

    onMounted(() => {
      fetchCards();
    });

    const isMissing = (card) => {
      return card.quantity_regular + card.quantity_foil === 0;
    };

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
    };

    const handleImageError = (event, card) => {
      console.error('Image failed to load for card:', card.name, 'URL:', event.target.src);
      event.target.style.display = 'none';
      const noImageDiv = event.target.parentNode.querySelector('.bg-secondary');
      if (noImageDiv) {
        noImageDiv.style.display = 'block';
      }
    };

    const updateQuantity = async (card, type, newValue) => {
      const updatedCard = { ...card };
      if (type === 'regular') {
        updatedCard.quantity_regular = newValue;
      } else if (type === 'foil') {
        updatedCard.quantity_foil = newValue;
      }

      try {
        const response = await axios.put(`/api/collection/${card.id}`, {
          quantity_regular: updatedCard.quantity_regular,
          quantity_foil: updatedCard.quantity_foil,
        });
        // Update the local card data
        const index = cards.value.findIndex((c) => c.id === card.id);
        if (index !== -1) {
          cards.value[index] = response.data;
        }
      } catch (err) {
        console.error('Error updating quantity:', err);
        alert('Failed to update quantity. Please try again.');
      }
    };

    const gridStyle = computed(() => ({
      gridTemplateColumns: `repeat(auto-fill, minmax(${cardSize.value}px, 1fr))`,
    }));

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
      updateQuantity,
      cardSize,
      gridStyle,
    };
  },
};
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
}

.card-info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-quantities {
  margin-top: auto;
}

.image-container {
  width: 100%;
  overflow: hidden;
}

.missing-indicator {
  position: absolute;
}

.bg-secondary {
  background-color: #f2f2f2;
}
</style>
