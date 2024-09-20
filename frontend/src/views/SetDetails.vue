<template>
  <div class="set-details">
    <div v-if="set" class="set-info">
      <img :src="set.icon_svg_uri" :alt="set.name" class="set-icon">
      <h1>{{ set.name }}</h1>
      <p>Code: {{ set.code }}</p>
      <p>Released: {{ new Date(set.released_at).toLocaleDateString() }}</p>
      <p>Card Count: {{ set.card_count }}</p>
      <p>Set Type: {{ set.set_type }}</p>
    </div>

    <h2>Cards in this Set</h2>
    <div class="filters">
      <input v-model="filters.name" placeholder="Search by card name" @input="fetchCards">
      <select v-model="filters.rarity" @change="fetchCards">
        <option value="">All Rarities</option>
        <option value="common">Common</option>
        <option value="uncommon">Uncommon</option>
        <option value="rare">Rare</option>
        <option value="mythic">Mythic</option>
      </select>
    </div>

    <div class="card-list">
      <div v-for="card in cards" :key="card.id" class="card-item">
        <img :src="card.image_uris.small" :alt="card.name">
        <div class="card-details">
          <h3>{{ card.name }}</h3>
          <p>Rarity: {{ card.rarity }}</p>
          <p>Collector Number: {{ card.collector_number }}</p>
          <p v-if="card.collection">In Collection: {{ card.collection.quantity_regular + card.collection.quantity_foil }}</p>
          <p v-if="card.kiosk">In Kiosk: {{ card.kiosk.quantity_regular + card.kiosk.quantity_foil }}</p>
        </div>
      </div>
    </div>

    <div class="pagination">
      <button @click="changePage(-1)" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="changePage(1)" :disabled="currentPage === totalPages">Next</button>
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

<style scoped>
.set-info {
  text-align: center;
  margin-bottom: 2rem;
}

.set-icon {
  width: 100px;
  height: 100px;
}

.filters {
  margin-bottom: 1rem;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.card-item {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.5rem;
}

.card-item img {
  width: 100%;
  height: auto;
}

.pagination {
  margin-top: 1rem;
}
</style>