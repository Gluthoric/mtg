<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">{{ setName }}</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <!-- Name Filter -->
        <input
          v-model="nameFilter"
          @input="debouncedApplyFilters"
          placeholder="Filter by name"
          class="p-2 border rounded bg-dark-100 text-white placeholder-gray-medium w-full"
        />

        <!-- Rarity Filter -->
        <select v-model="rarityFilter" @change="applyFilters" class="p-2 border rounded bg-dark-100 text-white w-full">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>

        <!-- Color Filter -->
        <div class="color-filter">
          <label class="block text-sm font-medium mb-2 text-gray-light">Colors</label>
          <div class="flex flex-wrap gap-2">
            <label v-for="color in availableColors" :key="color" class="flex items-center">
              <input
                type="checkbox"
                :value="color"
                v-model="colorFilters"
                @change="applyFilters"
                class="mr-1"
              />
              <span :class="colorClass(color)" class="capitalize">{{ color }}</span>
            </label>
          </div>
        </div>

        <!-- Missing Filter Button -->
        <button
          @click="toggleMissingFilter"
          class="p-2 border rounded bg-dark-100 text-white w-full hover:bg-dark-200"
          :class="{ 'bg-blue-600': missingFilter }"
        >
          {{ missingFilter ? 'Show All Cards' : 'Show Missing Cards' }}
        </button>
      </div>

      <!-- Cards Per Row Slider -->
      <div class="mb-4">
        <label for="cards-per-row-slider" class="block text-sm font-medium mb-2 text-gray-light">Cards per row</label>
        <input
          id="cards-per-row-slider"
          type="range"
          v-model="cardsPerRow"
          min="5"
          max="12"
          step="1"
          class="w-full bg-dark-100"
        />
        <div class="text-sm text-gray-light mt-1">{{ cardsPerRow }} cards per row</div>
      </div>

      <!-- Cards Grid -->
      <div class="card-grid grid gap-6" :style="gridStyle">
        <div
          v-for="card in filteredAndSortedCards"
          :key="card.id"
          class="card bg-dark-200 shadow-md rounded-lg overflow-hidden relative flex flex-col"
          :class="{ 'border-2 border-red-500': isMissing(card) }"
          :style="{ width: '100%', maxWidth: `${cardSize * 1.2}px` }"
        >
          <div class="card-info p-2 z-10 bg-dark-200 bg-opacity-80">
            <h3 class="text-base font-semibold truncate text-primary">{{ card.name }}</h3>
          </div>
          <div class="image-container" :style="{ height: `${cardSize * 1.4}px` }">
            <img
              v-if="getImageUrl(card)"
              :src="getImageUrl(card)"
              :alt="card.name"
              class="w-full h-full object-contain"
              @error="handleImageError($event, card)"
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-dark-100 text-gray-medium">
              No image available
            </div>
          </div>
          <div class="card-info p-2 flex flex-col">
            <div class="flex justify-between items-center mb-2">
              <p class="text-xs text-gray-light">CN: {{ card.collector_number }}</p>
              <p class="text-xs text-gray-light">{{ card.rarity }}</p>
            </div>
            <div class="card-quantities flex flex-col space-y-2">
              <!-- Regular Quantity Control -->
              <div class="quantity-control">
                <label :for="'regular-' + card.id" class="quantity-label text-xs font-semibold text-gray-light block mb-1">
                  Regular
                </label>
                <div class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden">
                  <button
                    @click="decrement(card, 'regular')"
                    class="btn decrement-btn w-8 h-8 flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Regular Quantity"
                    :disabled="card.quantity_regular === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'regular-' + card.id"
                    v-model.number="card.quantity_regular"
                    type="number"
                    min="0"
                    class="quantity-input w-12 h-8 text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="onInput(card, 'regular')"
                  />
                  <button
                    @click="increment(card, 'regular')"
                    class="btn increment-btn w-8 h-8 flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Increment Regular Quantity"
                  >
                    +
                  </button>
                </div>
                <div class="price text-xs text-gray-light mt-1">
                  Price: ${{ card.prices?.usd || 'N/A' }}
                </div>
              </div>

              <!-- Foil Quantity Control -->
              <div class="quantity-control">
                <label :for="'foil-' + card.id" class="quantity-label text-xs font-semibold text-gray-light block mb-1">
                  Foil
                </label>
                <div class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden">
                  <button
                    @click="decrement(card, 'foil')"
                    class="btn decrement-btn w-8 h-8 flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Foil Quantity"
                    :disabled="card.quantity_foil === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'foil-' + card.id"
                    v-model.number="card.quantity_foil"
                    type="number"
                    min="0"
                    class="quantity-input w-12 h-8 text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="onInput(card, 'foil')"
                  />
                  <button
                    @click="increment(card, 'foil')"
                    class="btn increment-btn w-8 h-8 flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Increment Foil Quantity"
                  >
                    +
                  </button>
                </div>
                <div class="price text-xs text-gray-light mt-1">
                  Price: ${{ card.prices?.usd_foil || 'N/A' }}
                </div>
              </div>
            </div>
          </div>
          <div v-if="isMissing(card)" class="missing-indicator absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded text-xs font-bold shadow">
            Missing
          </div>
        </div>
      </div>

      <!-- Handle No Cards Matching Filters -->
      <div v-if="filteredAndSortedCards.length === 0" class="text-center text-gray-light">
        No cards match the selected filters.
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import qs from 'qs';  // Import qs for query string serialization

export default {
  name: 'CollectionSetCards',
  setup() {
    const route = useRoute();
    const setCode = ref(route.params.setCode);
    const setName = ref('');
    const cards = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const nameFilter = ref('');
    const rarityFilter = ref('');
    const colorFilters = ref([]); // Reactive variable for color filters
    const missingFilter = ref(false);
    const cardsPerRow = ref(6);
    let debounceTimer = null;
    const cardSize = 180;

    const availableColors = ['W', 'U', 'B', 'R', 'G']; // Define available colors

    const fetchCards = async () => {
      loading.value = true;
      error.value = null;
      try {
        const params = {
          name: nameFilter.value,
          rarity: rarityFilter.value,
          colors: colorFilters.value, // Send colors as array
        };

        const response = await axios.get(`/api/collection/sets/${setCode.value}/cards`, {
          params,
          paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' }) // Serialize as colors=W&colors=U
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

    const toggleMissingFilter = () => {
      missingFilter.value = !missingFilter.value;
    };

    const debouncedApplyFilters = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        fetchCards();
      }, 300);
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

    const filteredAndSortedCards = computed(() => {
      return cards.value
        .filter(card => {
          if (missingFilter.value) {
            return card.quantity_regular === 0 && card.quantity_foil === 0;
          }
          return true;
        })
        .sort((a, b) => {
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
      const noImageDiv = event.target.parentNode.querySelector('.bg-dark-100');
      if (noImageDiv) {
        noImageDiv.style.display = 'flex';
      }
    };

    const updateQuantity = async (card) => {
      try {
        const response = await axios.put(`/api/collection/${card.id}`, {
          quantity_regular: card.quantity_regular,
          quantity_foil: card.quantity_foil,
        });
        const index = cards.value.findIndex((c) => c.id === card.id);
        if (index !== -1) {
          cards.value[index] = response.data;
        }
      } catch (err) {
        console.error('Error updating quantity:', err);
        alert('Failed to update quantity. Please try again.');
      }
    };

    const increment = (card, type) => {
      if (type === 'regular') {
        card.quantity_regular += 1;
      } else if (type === 'foil') {
        card.quantity_foil += 1;
      }
      updateQuantity(card);
    };

    const decrement = (card, type) => {
      if (type === 'regular' && card.quantity_regular > 0) {
        card.quantity_regular -= 1;
        updateQuantity(card);
      } else if (type === 'foil' && card.quantity_foil > 0) {
        card.quantity_foil -= 1;
        updateQuantity(card);
      }
    };

    const onInput = (card, type) => {
      if (type === 'regular') {
        card.quantity_regular = Math.max(0, parseInt(card.quantity_regular) || 0);
      } else if (type === 'foil') {
        card.quantity_foil = Math.max(0, parseInt(card.quantity_foil) || 0);
      }
      updateQuantity(card);
    };

    const gridStyle = computed(() => ({
      gridTemplateColumns: `repeat(${cardsPerRow.value}, 1fr)`,
    }));

    const colorClass = (color) => {
      const colorMap = {
        W: 'text-white',
        U: 'text-blue-500',
        B: 'text-black',
        R: 'text-red-500',
        G: 'text-green-500',
      };
      return colorMap[color] || 'text-gray-500';
    };

    return {
      setName,
      cards,
      loading,
      error,
      nameFilter,
      rarityFilter,
      applyFilters,
      debouncedApplyFilters,
      isMissing,
      filteredAndSortedCards,
      getImageUrl,
      handleImageError,
      increment,
      decrement,
      onInput,
      cardsPerRow,
      gridStyle,
      missingFilter,
      toggleMissingFilter,
      availableColors,
      colorFilters,
      colorClass,
      cardSize,
    };
  },
};
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out;
  width: 100%;
  height: 100%;
  justify-content: space-between;
}

.card-info {
  padding: 0.75rem;
}

.image-container {
  width: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.card {
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out;
  width: 100%;
}

.card:hover {
  transform: scale(1.02);
}

.card-info {
  flex-grow: 0;
}

.card-quantities {
  display: flex;
  justify-content: space-between;
}

.image-container {
  width: 100%;
  overflow: hidden;
  aspect-ratio: 5 / 7;
}

.quantity-control {
  width: 48%;
}

.quantity-label {
  font-size: 0.75rem;
}

.quantity-input {
  -webkit-appearance: textfield;
  -moz-appearance: textfield;
  appearance: textfield;
}

.quantity-input::-webkit-inner-spin-button,
.quantity-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

.buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.missing-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: red;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
  box-shadow: 0 0 5px rgba(0,0,0,0.3);
}

input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  background: #4a5568;
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
  border-radius: 5px;
}

input[type="range"]:hover {
  opacity: 1;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #4299e1;
  cursor: pointer;
  border-radius: 50%;
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #4299e1;
  cursor: pointer;
  border-radius: 50%;
}

.quantity-control {
  width: 100%;
}

.input-wrapper {
  width: 100%;
  max-width: 120px;
  margin: 0 auto;
}

@media (max-width: 640px) {
  .card-quantities {
    flex-direction: column;
  }

  .quantity-control {
    margin-bottom: 0.5rem;
  }
}

/* New styles for color labels */
.text-white {
  color: white;
}
.text-blue-500 {
  color: #4299e1; /* Tailwind CSS blue-500 */
}
.text-black {
  color: black;
}
.text-red-500 {
  color: #f56565; /* Tailwind CSS red-500 */
}
.text-green-500 {
  color: #48bb78; /* Tailwind CSS green-500 */
}
</style>
