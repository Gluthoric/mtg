<!-- KioskSetCards.vue -->
<template>
  <div class="container">
    <h1 class="text-center mb-4">{{ setName }} - Kiosk Inventory</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4">{{ error }}</div>
    <div v-else>
      <div class="filters grid grid-cols-1 md:grid-cols-3 gap-2 mb-4">
        <input v-model="filters.name" placeholder="Search by name" @input="fetchCards" class="w-full">
        <select v-model="filters.rarity" @change="fetchCards" class="w-full">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="mythic">Mythic</option>
        </select>
        <select v-model="sorting.sortBy" @change="fetchCards" class="w-full">
          <option value="name">Name</option>
          <option value="rarity">Rarity</option>
          <option value="collector_number">Collector Number</option>
        </select>
      </div>
      <div class="card-list grid grid-cols-auto gap-4">
        <div v-for="card in cards" :key="card.id" class="card">
          <img :src="card.image_uris.small" :alt="card.name" class="w-full mb-2">
          <div class="card-details p-2">
            <h3 class="mb-2 text-lg font-bold">{{ card.name }}</h3>
            <p class="mb-1"><span class="font-semibold">Rarity:</span> {{ card.rarity }}</p>
            <div class="quantity-controls mb-2">
              <div class="quantity-row">
                <span class="font-semibold">Regular:</span>
                <button @click="updateQuantity(card, 'regular', -1)" class="quantity-btn">-</button>
                <input v-model.number="card.quantity.quantity_regular" @change="updateQuantity(card, 'regular')" type="number" min="0" class="quantity-input">
                <button @click="updateQuantity(card, 'regular', 1)" class="quantity-btn">+</button>
              </div>
              <div class="quantity-row">
                <span class="font-semibold">Foil:</span>
                <button @click="updateQuantity(card, 'foil', -1)" class="quantity-btn">-</button>
                <input v-model.number="card.quantity.quantity_foil" @change="updateQuantity(card, 'foil')" type="number" min="0" class="quantity-input">
                <button @click="updateQuantity(card, 'foil', 1)" class="quantity-btn">+</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="pagination text-center mt-4">
        <button @click="changePage(-1)" :disabled="currentPage === 1" class="mr-2">Previous</button>
        <span class="px-2 py-1 bg-secondary rounded">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="changePage(1)" :disabled="currentPage === totalPages" class="ml-2">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
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
    const sorting = ref({ sortBy: 'name', sortOrder: 'asc' })
    const currentPage = ref(1)
    const totalPages = ref(1)

    const fetchCards = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await axios.get(`/api/kiosk/sets/${setCode}/cards`, {
          params: {
            ...filters.value,
            ...sorting.value,
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

    onMounted(() => {
      fetchCards()
    })

    return {
      setName,
      cards,
      loading,
      error,
      filters,
      sorting,
      currentPage,
      totalPages,
      fetchCards,
      changePage,
      updateQuantity
    }
  }
}
</script>

<style scoped>
.quantity-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quantity-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.quantity-input {
  width: 40px;
  text-align: center;
}
</style>