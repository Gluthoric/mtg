<template>
  <div class="container">
    <div v-if="set" class="set-info text-center mb-6">
      <img :src="set.icon_svg_uri" :alt="set.name" class="set-icon w-24 h-24 mx-auto mb-4">
      <h1 class="text-2xl font-bold mb-2">{{ set.name }}</h1>
      <p class="mb-1">Code: {{ set.code }}</p>
      <p class="mb-1">Released: {{ new Date(set.released_at).toLocaleDateString() }}</p>
      <p class="mb-1">Card Count: {{ set.card_count }}</p>
      <p>Set Type: {{ set.set_type }}</p>
    </div>

    <h2 class="text-xl font-bold text-center mb-4">Cards in this Set</h2>
    <div class="filters grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
      <input v-model="filters.name" placeholder="Search by card name" @input="fetchCards" class="w-full p-2">
      <select v-model="filters.rarity" @change="fetchCards" class="w-full p-2">
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
          <h3 class="text-lg font-semibold mb-2">{{ card.name }}</h3>
          <p class="mb-1"><span class="font-medium">Rarity:</span> {{ card.rarity }}</p>
          <p class="mb-1"><span class="font-medium">Collector Number:</span> {{ card.collector_number }}</p>
          <p v-if="card.collection" class="mb-1"><span class="font-medium">In Collection:</span> {{ card.collection.quantity_regular + card.collection.quantity_foil }}</p>
          <p v-if="card.kiosk"><span class="font-medium">In Kiosk:</span> {{ card.kiosk.quantity_regular + card.kiosk.quantity_foil }}</p>
        </div>
      </div>
    </div>

    <div class="pagination text-center mt-6">
      <button @click="changePage(-1)" :disabled="currentPage === 1" class="px-4 py-2 mr-2">Previous</button>
      <span class="px-4 py-2 bg-secondary rounded">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="changePage(1)" :disabled="currentPage === totalPages" class="px-4 py-2 ml-2">Next</button>
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