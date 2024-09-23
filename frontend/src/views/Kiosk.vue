<template>
  <div class="container">
    <h1 class="text-center mb-4">Kiosk Inventory</h1>
    <div class="filters grid grid-cols-1 md:grid-cols-3 gap-2 mb-4">
      <input v-model="filters.name" placeholder="Search by name" @input="fetchCards" class="w-full">
      <select v-model="filters.set" @change="fetchCards" class="w-full">
        <option value="">All Sets</option>
        <option v-for="set in sets" :key="set.code" :value="set.code">{{ set.name }}</option>
      </select>
      <select v-model="filters.rarity" @change="fetchCards" class="w-full">
        <option value="">All Rarities</option>
        <option value="common">Common</option>
        <option value="uncommon">Uncommon</option>
        <option value="rare">Rare</option>
        <option value="mythic">Mythic</option>
      </select>
    </div>
    <div class="card-list grid grid-cols-auto gap-4">
      <div v-for="card in cards" :key="card.id" class="card">
        <img :src="card.image_uris.small" :alt="card.name" class="w-full mb-2">
        <div class="card-details p-2">
          <h3 class="mb-2 text-lg font-bold">{{ card.name }}</h3>
          <p class="mb-1"><span class="font-semibold">Set:</span> {{ card.set_name }}</p>
          <p class="mb-1"><span class="font-semibold">Rarity:</span> {{ card.rarity }}</p>
          <p class="mb-1"><span class="font-semibold">Regular:</span> {{ card.quantity.quantity_regular }}</p>
          <p class="mb-2"><span class="font-semibold">Foil:</span> {{ card.quantity.quantity_foil }}</p>
          <button @click="openEditModal(card)" class="w-full">Edit</button>
        </div>
      </div>
    </div>
    <div class="pagination text-center mt-4">
      <button @click="changePage(-1)" :disabled="currentPage === 1" class="mr-2">Previous</button>
      <span class="px-2 py-1 bg-secondary rounded">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="changePage(1)" :disabled="currentPage === totalPages" class="ml-2">Next</button>
    </div>
    <!-- Edit Modal (implement later) -->
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Kiosk',
  setup() {
    const cards = ref([])
    const sets = ref([])
    const filters = ref({ name: '', set: '', rarity: '' })
    const currentPage = ref(1)
    const totalPages = ref(1)

    const fetchCards = async () => {
      try {
        const response = await axios.get('/api/kiosk', {
          params: {
            ...filters.value,
            page: currentPage.value
          }
        })
        cards.value = response.data.kiosk
        totalPages.value = response.data.pages
      } catch (error) {
        console.error('Error fetching kiosk cards:', error)
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
      console.log('Edit kiosk card:', card)
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