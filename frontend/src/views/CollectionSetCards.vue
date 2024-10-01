<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <nav class="mb-4 flex justify-center space-x-4">
      <router-link to="/" class="text-primary hover:underline">Home</router-link>
      <router-link to="/collection" class="text-primary hover:underline">Collection</router-link>
      <router-link to="/kiosk" class="text-primary hover:underline">Kiosk</router-link>
      <router-link to="/import" class="text-primary hover:underline">Import</router-link>
    </nav>
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">{{ setName }}</h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">{{ error }}</div>
    <div v-else>
      <CardListControls
        :filters="filters"
        :cardsPerRow="cardsPerRow"
        @update-filters="updateFilters"
        @update-cards-per-row="updateCardsPerRow"
      />

      <!-- Set Statistics -->
      <div class="set-stats bg-dark-200 p-4 rounded-lg mb-4">
        <h2 class="text-lg font-semibold mb-2">Set Statistics</h2>
        <p>Total Cards in Set: {{ totalCardsInSet }}</p>
        <p>Cards in Collection: {{ cardsInCollection }}</p>
        <p>Completion: {{ completionPercentage }}%</p>
        <p>Total Value: ${{ totalValue.toFixed(2) }}</p>
      </div>

      <!-- New Statistics Sections -->
      <div v-if="statistics" class="mb-6">
        <!-- Frame Effects -->
        <div class="mb-4">
          <h2 class="text-xl font-semibold text-primary mb-2">Frame Effects</h2>
          <ul>
            <li v-for="(count, effect) in statistics.frame_effects" :key="effect">
              {{ effect }}: {{ count }}
            </li>
          </ul>
        </div>
        
        <!-- Promo Types -->
        <div class="mb-4">
          <h2 class="text-xl font-semibold text-primary mb-2">Promo Types</h2>
          <ul>
            <li v-for="(count, promo) in statistics.promo_types" :key="promo">
              {{ promo }}: {{ count }}
            </li>
          </ul>
        </div>
        
        <!-- Other Attributes -->
        <div>
          <h2 class="text-xl font-semibold text-primary mb-2">Other Attributes</h2>
          <ul>
            <li v-for="(count, attribute) in statistics.other_attributes" :key="attribute">
              {{ attribute }}: {{ count }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Cards Grid -->
      <div class="card-grid grid gap-4" :style="gridStyle">
        <div
          v-for="card in cards"
          :key="card.id"
          class="card bg-dark-200 shadow-md rounded-lg overflow-hidden relative flex flex-col"
          :class="{ 'border-2 border-red-500': isMissing(card) }"
          :style="{ width: '100%' }"
        >
          <div class="card-info p-2 z-10 bg-dark-200 bg-opacity-80">
            <h3 class="text-base font-semibold truncate text-primary">{{ card.name }}</h3>
          </div>
          <div class="image-container">
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
                    class="btn decrement-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Regular Quantity"
                    :disabled="card.quantity_collection_regular === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'regular-' + card.id"
                    v-model.number="card.quantity_collection_regular"
                    type="number"
                    min="0"
                    class="quantity-input text-center border-none outline-none bg-input-background text-white text-sm"
                    @input="onInput(card, 'regular')"
                  />
                  <button
                    @click="increment(card, 'regular')"
                    class="btn increment-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
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
                    :disabled="card.quantity_collection_foil === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'foil-' + card.id"
                    v-model.number="card.quantity_collection_foil"
                    type="number"
                    min="0"
                    class="quantity-input text-center border-none outline-none bg-input-background text-white text-sm"
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
            <!-- Card Details -->
            <div class="card-details mt-2 text-xs text-gray-light">
              <p><span class="font-semibold">Type:</span> {{ card.type_line || 'N/A' }}</p>
              <p><span class="font-semibold">Mana Cost:</span> {{ card.mana_cost || 'N/A' }}</p>
              <p><span class="font-semibold">Set:</span> {{ setName }}</p>
              <p><span class="font-semibold">Rarity:</span> {{ card.rarity }}</p>
              <p v-if="card.frame_effects"><span class="font-semibold">Frame Effects:</span> {{ card.frame_effects.join(', ') }}</p>
              <p v-if="card.promo_types"><span class="font-semibold">Promo Types:</span> {{ card.promo_types.join(', ') }}</p>
            </div>
          </div>
          <div v-if="isMissing(card)" class="missing-indicator absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded text-xs font-bold shadow">
            Missing
          </div>
        </div>
      </div>

      <!-- Handle No Cards Matching Filters -->
      <div v-if="cards.length === 0" class="text-center text-gray-light mt-4">
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
import CardListControls from '../components/CardListControls.vue';

export default {
  name: 'CollectionSetCards',
  components: {
    CardListControls
  },
  setup() {
    const route = useRoute();
    const setCode = ref(route.params.setCode);
    const setName = ref('');
    const cards = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const filters = ref({
      name: '',
      rarities: [],
      colors: [],
      missing: false,
      types: [],
      keyword: ''
    });
    const cardsPerRow = ref(6);
    const statistics = ref(null);

    // Computed properties for set statistics
    const totalCardsInSet = computed(() => cards.value.length);
    const cardsInCollection = computed(() => cards.value.filter(card => card.quantity_collection_regular > 0 || card.quantity_collection_foil > 0).length);
    const completionPercentage = computed(() => ((cardsInCollection.value / totalCardsInSet.value) * 100).toFixed(2));
    const totalValue = computed(() => {
      return cards.value.reduce((total, card) => {
        const regularValue = (card.prices?.usd || 0) * card.quantity_collection_regular;
        const foilValue = (card.prices?.usd_foil || 0) * card.quantity_collection_foil;
        return total + regularValue + foilValue;
      }, 0);
    });

    const fetchSetDetails = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get(`/api/collection/sets/${setCode.value}`);
        setName.value = response.data.set.name;
        cards.value = response.data.cards;
        statistics.value = response.data.statistics;
      } catch (err) {
        console.error('Error fetching set details:', err);
        error.value = 'Failed to load set details';
      } finally {
        loading.value = false;
      }
    };

    const updateFilters = (newFilters) => {
      filters.value = { ...filters.value, ...newFilters };
      fetchSetDetails();
    };

    const updateCardsPerRow = (newCardsPerRow) => {
      cardsPerRow.value = newCardsPerRow;
    };

    watch(
      () => route.params.setCode,
      (newSetCode) => {
        setCode.value = newSetCode;
        fetchSetDetails();
      }
    );

    onMounted(() => {
      fetchSetDetails();
    });

    const isMissing = (card) => {
      return card.quantity_collection_regular + card.quantity_collection_foil === 0;
    };

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

    const updateQuantity = async (card, type, delta = 0) => {
      let newQuantity;
      if (type === 'regular') {
        newQuantity = card.quantity_collection_regular + delta;
        if (newQuantity < 0) return;
      } else if (type === 'foil') {
        newQuantity = card.quantity_collection_foil + delta;
        if (newQuantity < 0) return;
      } else {
        return;
      }

      try {
        const payload = type === 'regular'
          ? { quantity_regular: newQuantity, quantity_foil: card.quantity_collection_foil }
          : { quantity_regular: card.quantity_collection_regular, quantity_foil: newQuantity };
        const response = await axios.put(`/api/collection/${card.id}`, payload);
        Object.assign(card, response.data); // Update card data
      } catch (err) {
        console.error('Error updating quantity:', err);
        alert('Failed to update quantity. Please try again.');
      }
    };

    const increment = (card, type) => {
      updateQuantity(card, type, 1);
    };

    const decrement = (card, type) => {
      updateQuantity(card, type, -1);
    };

    const onInput = (card, type) => {
      if (type === 'regular') {
        card.quantity_collection_regular = Math.max(0, parseInt(card.quantity_collection_regular) || 0);
      } else if (type === 'foil') {
        card.quantity_collection_foil = Math.max(0, parseInt(card.quantity_collection_foil) || 0);
      }
      // Immediately update the backend
      updateQuantity(card, type);
    };

    const gridStyle = computed(() => ({
      gridTemplateColumns: `repeat(${cardsPerRow.value}, 1fr)`,
    }));

    return {
      setName,
      cards,
      loading,
      error,
      filters,
      updateFilters,
      isMissing,
      getImageUrl,
      handleImageError,
      increment,
      decrement,
      onInput,
      cardsPerRow,
      updateCardsPerRow,
      gridStyle,
      totalCardsInSet,
      cardsInCollection,
      completionPercentage,
      totalValue,
      statistics
    };
  },
};
</script>

<style scoped>
/* Styles remain unchanged */
</style>
