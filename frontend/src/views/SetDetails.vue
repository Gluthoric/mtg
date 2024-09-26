<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white min-h-screen">
    <div v-if="set" class="set-info text-center mb-6 pt-6">
      <img :src="set.icon_svg_uri" :alt="set.name" class="set-icon w-24 h-24 mx-auto mb-4">
      <h1 class="text-3xl font-bold mb-2 text-primary">{{ set.name }}</h1>
      <p class="mb-1 text-gray-light">Code: {{ set.code }}</p>
      <p class="mb-1 text-gray-light">Released: {{ new Date(set.released_at).toLocaleDateString() }}</p>
      <p class="mb-1 text-gray-light">Card Count: {{ set.card_count }}</p>
      <p class="text-gray-light">Set Type: {{ set.set_type }}</p>
    </div>

    <h2 class="text-2xl font-bold text-center mb-6 text-primary">Cards in this Set</h2>
    <div class="filters grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <input
        v-model="filters.name"
        placeholder="Search by card name"
        @input="fetchCards"
        class="w-full p-3 bg-dark-100 text-white placeholder-gray-medium border border-dark-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
      >
      <select
        v-model="filters.rarity"
        @change="fetchCards"
        class="w-full p-3 bg-dark-100 text-white border border-dark-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="">All Rarities</option>
        <option value="common">Common</option>
        <option value="uncommon">Uncommon</option>
        <option value="rare">Rare</option>
        <option value="mythic">Mythic</option>
      </select>
    </div>

    <div class="card-list grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div v-for="card in cards" :key="card.id" class="card bg-dark-200 rounded-lg overflow-hidden shadow-lg">
        <img :src="card.image_uris.small" :alt="card.name" class="w-full">
        <div class="card-details p-4">
          <h3 class="text-lg font-semibold mb-2 text-primary">{{ card.name }}</h3>
          <p class="mb-1"><span class="font-medium text-gray-medium">Rarity:</span> {{ card.rarity }}</p>
          <p class="mb-1"><span class="font-medium text-gray-medium">Collector Number:</span> {{ card.collector_number }}</p>
          <p v-if="card.quantity_regular + card.quantity_foil > 0" class="mb-1">
            <span class="font-medium text-gray-medium">In Collection:</span>
            {{ card.quantity_regular + card.quantity_foil }}
          </p>
          <p v-if="card.quantity_kiosk_regular + card.quantity_kiosk_foil > 0">
            <span class="font-medium text-gray-medium">In Kiosk:</span>
            {{ card.quantity_kiosk_regular + card.quantity_kiosk_foil }}
          </p>
        </div>
      </div>
    </div>

    <div class="pagination text-center mt-8 mb-8">
      <button
        @click="changePage(-1)"
        :disabled="currentPage === 1"
        class="px-4 py-2 mr-2 bg-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>
      <span class="px-4 py-2 bg-dark-100 text-white rounded-lg">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        @click="changePage(1)"
        :disabled="currentPage === totalPages"
        class="px-4 py-2 ml-2 bg-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'SetDetails',
  props: {
    setCode: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const set = ref(null)
    const cards = ref([])
    const filters = ref({ name: '', rarity: '' })
    const currentPage = ref(1)
    const totalPages = ref(1)

    const fetchSet = async () => {
      try {
        const response = await axios.get(`/api/sets/${props.setCode}`)
        set.value = response.data
      } catch (error) {
        console.error('Error fetching set details:', error)
      }
    }

    const fetchCards = async () => {
      try {
        const response = await axios.get(`/api/sets/${props.setCode}/cards`, {
          params: {
            ...filters.value,
            page: currentPage.value
          }
        })
        cards.value = response.data.cards
        totalPages.value = response.data.pages
      } catch (error) {
        console.error('Error fetching set cards:', error)
      }
    }

    const changePage = (delta) => {
      currentPage.value += delta
      fetchCards()
    }

    onMounted(() => {
      fetchSet()
      fetchCards()
    })

    return {
      set,
      cards,
      filters,
      currentPage,
      totalPages,
      fetchCards,
      changePage
    }
  }
}
</script>