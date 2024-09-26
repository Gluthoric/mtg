<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">{{ setName }} - Kiosk Inventory</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <!-- Name Filter -->
        <input
          v-model="filters.name"
          @input="debouncedFetchCards"
          placeholder="Filter by name"
          class="p-2 border rounded bg-dark-100 text-white placeholder-gray-medium w-full"
        />

        <!-- Rarity Filter -->
        <select v-model="filters.rarity" @change="fetchCards" class="p-2 border rounded bg-dark-100 text-white w-full">
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
                @change="fetchCards"
                class="mr-1"
              />
              <span :class="colorClass(color)" class="capitalize">{{ color }}</span>
            </label>
          </div>
        </div>
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
          v-for="card in cards"
          :key="card.id"
          class="card bg-dark-200 shadow-md rounded-lg overflow-hidden relative flex flex-col"
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
                    @click="updateQuantity(card, 'regular', -1)"
                    class="btn decrement-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Regular Quantity"
                    :disabled="card.quantity.quantity_regular === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'regular-' + card.id"
                    v-model.number="card.quantity.quantity_regular"
                    type="number"
                    min="0"
                    class="quantity-input text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="updateQuantity(card, 'regular')"
                  />
                  <button
                    @click="updateQuantity(card, 'regular', 1)"
                    class="btn increment-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Increment Regular Quantity"
                  >
                    +
                  </button>
                </div>
              </div>

              <!-- Foil Quantity Control -->
              <div class="quantity-control">
                <label :for="'foil-' + card.id" class="quantity-label text-xs font-semibold text-gray-light block mb-1">
                  Foil
                </label>
                <div class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden">
                  <button
                    @click="updateQuantity(card, 'foil', -1)"
                    class="btn decrement-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Foil Quantity"
                    :disabled="card.quantity.quantity_foil === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'foil-' + card.id"
                    v-model.number="card.quantity.quantity_foil"
                    type="number"
                    min="0"
                    class="quantity-input text-center border-none outline-none bg-dark-100 text-white text-sm"
                    @input="updateQuantity(card, 'foil')"
                  />
                  <button
                    @click="updateQuantity(card, 'foil', 1)"
                    class="btn increment-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Increment Foil Quantity"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination text-center mt-6">
        <button @click="changePage(-1)" :disabled="currentPage === 1" class="px-4 py-2 mr-2">Previous</button>
        <span class="px-4 py-2 bg-secondary rounded">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="changePage(1)" :disabled="currentPage === totalPages" class="px-4 py-2 ml-2">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'KioskSetCards',
  setup() {
    const route = useRoute()
    const setCode = route.params.setCode
    const setName = ref('')
    const cards = ref([])
    const loading = ref(true)
    const error = ref(null)
    const filters = ref({ name: '', rarity: '' })
    const colorFilters = ref([])
    const sorting = ref({ sortBy: 'name', sortOrder: 'asc' })
    const currentPage = ref(1)
    const totalPages = ref(1)
    const cardsPerRow = ref(6)
    const cardSize = 180
    const availableColors = ['W', 'U', 'B', 'R', 'G']

    const fetchCards = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get(`/api/kiosk/sets/${setCode}/cards`, {
          params: {
            ...filters.value,
            ...sorting.value,
            colors: colorFilters.value,
            page: currentPage.value
          }
        })
        cards.value = response.data.cards
        setName.value = response.data.set_name
        totalPages.value = response.data.pages
        currentPage.value = response.data.current_page
      } catch (err) {
        console.error('Error fetching kiosk set cards:', err)
        error.value = 'Failed to load kiosk set cards'
      } finally {
        loading.value = false
      }
    }

    const debouncedFetchCards = debounce(fetchCards, 300)

    const updateQuantity = async (card, type, delta = 0) => {
      const newQuantity = type === 'regular'
        ? card.quantity.quantity_regular + delta
        : card.quantity.quantity_foil + delta

      if (newQuantity < 0) return

      try {
        await axios.put(`/api/kiosk/${card.id}`, {
          quantity_regular: type === 'regular' ? newQuantity : card.quantity.quantity_regular,
          quantity_foil: type === 'foil' ? newQuantity : card.quantity.quantity_foil
        })

        if (type === 'regular') {
          card.quantity.quantity_regular = newQuantity
        } else {
          card.quantity.quantity_foil = newQuantity
        }
      } catch (err) {
        console.error('Error updating card quantity:', err)
        error.value = 'Failed to update card quantity'
      }
    }

    const changePage = (delta) => {
      const newPage = currentPage.value + delta
      if (newPage >= 1 && newPage <= totalPages.value) {
        currentPage.value = newPage
        fetchCards()
      }
    }

    const gridStyle = computed(() => ({
      gridTemplateColumns: `repeat(${cardsPerRow.value}, 1fr)`,
    }))

    const getImageUrl = (card) => {
      const imageSizes = ['normal', 'large', 'small', 'png', 'art_crop', 'border_crop']

      if (card.image_uris) {
        for (const size of imageSizes) {
          if (card.image_uris[size]) {
            return card.image_uris[size]
          }
        }
      }

      if (card.card_faces && card.card_faces[0].image_uris) {
        for (const size of imageSizes) {
          if (card.card_faces[0].image_uris[size]) {
            return card.card_faces[0].image_uris[size]
          }
        }
      }

      console.warn('No image URL found for card:', card.name)
      return null
    }

    const handleImageError = (event, card) => {
      console.error('Image failed to load for card:', card.name, 'URL:', event.target.src)
      event.target.style.display = 'none'
      const noImageDiv = event.target.parentNode.querySelector('.bg-dark-100')
      if (noImageDiv) {
        noImageDiv.style.display = 'flex'
      }
    }

    const colorClass = (color) => {
      const colorMap = {
        W: 'text-white',
        U: 'text-blue-500',
        B: 'text-black',
        R: 'text-red-500',
        G: 'text-green-500',
      }
      return colorMap[color] || 'text-gray-500'
    }

    function debounce(func, wait) {
      let timeout
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout)
          func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    }

    onMounted(() => {
      fetchCards()
    })

    watch([filters, colorFilters, sorting], () => {
      currentPage.value = 1
      fetchCards()
    })

    return {
      setName,
      cards,
      loading,
      error,
      filters,
      colorFilters,
      sorting,
      currentPage,
      totalPages,
      fetchCards,
      debouncedFetchCards,
      changePage,
      updateQuantity,
      cardsPerRow,
      gridStyle,
      getImageUrl,
      handleImageError,
      availableColors,
      colorClass,
      cardSize,
    }
  }
}
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

.card:hover {
  transform: scale(1.02);
}

.quantity-control {
  width: 100%;
}

.input-wrapper {
  width: 100%;
  max-width: 120px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
}

.quantity-input {
  flex: 1;
  min-width: 0;
}

.btn {
  flex-shrink: 0;
  width: 24px;
  min-width: 24px;
}

@media (max-width: 640px) {
  .card-quantities {
    flex-direction: column;
  }

  .quantity-control {
    margin-bottom: 0.5rem;
  }
}
</style>