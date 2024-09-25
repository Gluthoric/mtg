<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">{{ setName }}</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <input
          v-model="nameFilter"
          @input="debouncedApplyFilters"
          placeholder="Filter by name"
          class="p-2 border rounded bg-dark-100 text-white placeholder-gray-medium w-full"
        />
        <select v-model="rarityFilter" @change="applyFilters" class="p-2 border rounded bg-dark-100 text-white w-full">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
      </div>

      <div class="mb-4">
        <label for="card-size-slider" class="block text-sm font-medium mb-2 text-gray-light">Card Size</label>
        <input
          id="card-size-slider"
          type="range"
          v-model="cardSize"
          min="150"
          max="300"
          class="w-full bg-dark-100"
        />
      </div>

      <div class="card-grid grid gap-4" :style="gridStyle">
        <div
          v-for="card in sortedCards"
          :key="card.id"
          class="card bg-dark-200 shadow-md rounded-lg overflow-hidden relative"
          :class="{ 'border-2 border-red-500': isMissing(card) }"
          :style="{ width: `${cardSize}px` }"
        >
          <div class="image-container" :style="{ height: `${cardSize}px` }">
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
          <div class="card-info p-4">
            <h3 class="text-lg font-semibold mb-2 truncate text-primary">{{ card.name }}</h3>
            <p class="text-sm mb-1 text-gray-light">Collector Number: {{ card.collector_number }}</p>
            <p class="text-sm mb-2 text-gray-light">Rarity: {{ card.rarity }}</p>
            <div class="card-quantities grid grid-cols-2 gap-2">
              <div class="quantity-control flex flex-col">
                <label :for="'regular-' + card.id" class="quantity-label mb-1 text-xs font-semibold text-gray-light">
                  Regular
                </label>
                <div class="input-wrapper flex border rounded-md overflow-hidden">
                  <input
                    :id="'regular-' + card.id"
                    v-model.number="card.quantity_regular"
                    type="number"
                    min="0"
                    class="quantity-input flex-1 p-1 text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="onInput(card, 'regular')"
                  />
                  <div class="buttons flex flex-col bg-dark-200 border-l border-dark-400">
                    <button
                      @click="increment(card, 'regular')"
                      class="btn increment-btn px-1 py-0.5 text-xs bg-dark-300 hover:bg-dark-400"
                      aria-label="Increment Regular Quantity"
                    >
                      ▲
                    </button>
                    <button
                      @click="decrement(card, 'regular')"
                      class="btn decrement-btn px-1 py-0.5 text-xs bg-dark-300 hover:bg-dark-400"
                      aria-label="Decrement Regular Quantity"
                      :disabled="card.quantity_regular === 0"
                    >
                      ▼
                    </button>
                  </div>
                </div>
              </div>
              <div class="quantity-control flex flex-col">
                <label :for="'foil-' + card.id" class="quantity-label mb-1 text-xs font-semibold text-gray-light">
                  Foil
                </label>
                <div class="input-wrapper flex border rounded-md overflow-hidden">
                  <input
                    :id="'foil-' + card.id"
                    v-model.number="card.quantity_foil"
                    type="number"
                    min="0"
                    class="quantity-input flex-1 p-1 text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="onInput(card, 'foil')"
                  />
                  <div class="buttons flex flex-col bg-dark-200 border-l border-dark-400">
                    <button
                      @click="increment(card, 'foil')"
                      class="btn increment-btn px-1 py-0.5 text-xs bg-dark-300 hover:bg-dark-400"
                      aria-label="Increment Foil Quantity"
                    >
                      ▲
                    </button>
                    <button
                      @click="decrement(card, 'foil')"
                      class="btn decrement-btn px-1 py-0.5 text-xs bg-dark-300 hover:bg-dark-400"
                      aria-label="Decrement Foil Quantity"
                      :disabled="card.quantity_foil === 0"
                    >
                      ▼
                    </button>
                  </div>
                </div>
              </div>
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
    const cardSize = ref(200);
    let debounceTimer = null;

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
      debouncedApplyFilters,
      isMissing,
      sortedCards,
      getImageUrl,
      handleImageError,
      increment,
      decrement,
      onInput,
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
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: scale(1.02);
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
</style>