<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">
      {{ setName }} - Kiosk Inventory
    </h1>
    <div v-if="loading" class="loading text-center mt-4">Loading...</div>
    <div v-else-if="error" class="error text-center mt-4 text-red-500">
      {{ error }}
    </div>
    <div v-else>
      <CardListControls
        :filters="filters"
        :cardsPerRow="cardsPerRow"
        @update-filters="updateFilters"
        @update-cards-per-row="updateCardsPerRow"
      />

      <!-- Cards Grid -->
      <div class="card-grid grid gap-6" :style="gridStyle">
        <div
          v-for="card in filteredAndSortedCards"
          :key="card.id"
          class="card bg-dark-200 shadow-md rounded-lg overflow-hidden relative flex flex-col"
        >
          <div class="card-info p-2 z-10 bg-dark-200 bg-opacity-80">
            <h3 class="text-base font-semibold truncate text-primary">
              {{ card.name }}
            </h3>
          </div>
          <div class="image-container">
            <img
              v-if="getImageUrl(card)"
              :src="getImageUrl(card)"
              :alt="card.name"
              class="w-full h-full object-contain"
              @error="handleImageError($event, card)"
            />
            <div
              v-else
              class="w-full h-full flex items-center justify-center bg-dark-100 text-gray-medium"
            >
              No image available
            </div>
          </div>
          <div class="card-info p-2 flex flex-col">
            <div class="flex justify-between items-center mb-2">
              <p class="text-xs text-gray-light">
                CN: {{ card.collector_number }}
              </p>
              <p class="text-xs text-gray-light">{{ card.rarity }}</p>
            </div>
            <div class="card-quantities flex flex-col space-y-2">
              <!-- Regular Quantity Control -->
              <div class="quantity-control">
                <label
                  :for="'regular-' + card.id"
                  class="quantity-label text-xs font-semibold text-gray-light block mb-1"
                >
                  Regular
                </label>
                <div
                  class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden"
                >
                  <button
                    @click="updateQuantity(card, 'regular', -1)"
                    class="btn decrement-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Regular Quantity"
                    :disabled="card.quantity_kiosk_regular === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'regular-' + card.id"
                    v-model.number="card.quantity_regular"
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
                <div class="price text-xs text-gray-light mt-1">
                  Price: ${{ card.prices?.usd || "N/A" }}
                </div>
              </div>

              <!-- Foil Quantity Control -->
              <div class="quantity-control">
                <label
                  :for="'foil-' + card.id"
                  class="quantity-label text-xs font-semibold text-gray-light block mb-1"
                >
                  Foil
                </label>
                <div
                  class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden"
                >
                  <button
                    @click="updateQuantity(card, 'foil', -1)"
                    class="btn decrement-btn flex items-center justify-center bg-dark-300 hover:bg-dark-400"
                    aria-label="Decrement Foil Quantity"
                    :disabled="card.quantity_kiosk_foil === 0"
                  >
                    –
                  </button>
                  <input
                    :id="'foil-' + card.id"
                    v-model.number="card.quantity_foil"
                    type="number"
                    min="0"
                    class="quantity-input text-center border-none outline-none bg-input-background text-white text-sm"
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
                <div class="price text-xs text-gray-light mt-1">
                  Price: ${{ card.prices?.usd_foil || "N/A" }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Handle No Cards Matching Filters -->
      <div
        v-if="filteredAndSortedCards.length === 0"
        class="text-center text-gray-light"
      >
        No cards match the selected filters.
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import CardListControls from "../components/CardListControls.vue";

export default {
  name: "KioskSetCards",
  components: {
    CardListControls,
  },
  setup() {
    const route = useRoute();
    const setCode = ref(route.params.setCode);
    const setName = ref("");
    const cards = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const filters = ref({
      name: "",
      rarity: "",
      colors: [],
      missing: false,
    });
    const cardsPerRow = ref(6);

    const fetchCards = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get(
          `/api/kiosk/sets/${setCode.value}/cards`,
          {
            params: {
              per_page: 1000, // Request a large number of cards
            },
          },
        );
        cards.value = response.data.cards;
        setName.value = response.data.set_name;
      } catch (err) {
        console.error("Error fetching kiosk set cards:", err);
        error.value = "Failed to load kiosk set cards";
      } finally {
        loading.value = false;
      }
    };

    const updateFilters = (newFilters) => {
      filters.value = { ...filters.value, ...newFilters };
    };

    const updateCardsPerRow = (newCardsPerRow) => {
      cardsPerRow.value = newCardsPerRow;
    };

    const updateQuantity = async (card, type, delta = 0) => {
      let newQuantity;
      if (type === "regular") {
        newQuantity = card.quantity_regular + delta;
        if (newQuantity < 0) return;
      } else if (type === "foil") {
        newQuantity = card.quantity_foil + delta;
        if (newQuantity < 0) return;
      } else {
        return;
      }

      try {
        const payload =
          type === "regular"
            ? {
                quantity_regular: newQuantity,
                quantity_foil: card.quantity_foil,
              }
            : {
                quantity_regular: card.quantity_regular,
                quantity_foil: newQuantity,
              };
        const response = await axios.put(`/api/kiosk/${card.id}`, payload);
        Object.assign(card, response.data); // Update card data
      } catch (err) {
        console.error("Error updating quantity:", err);
        alert("Failed to update quantity. Please try again.");
      }
    };

    const gridStyle = computed(() => ({
      gridTemplateColumns: `repeat(${cardsPerRow.value}, 1fr)`,
    }));

    const getImageUrl = (card) => {
      const imageSizes = [
        "normal",
        "large",
        "small",
        "png",
        "art_crop",
        "border_crop",
      ];

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

      console.warn("No image URL found for card:", card.name);
      return null;
    };

    const handleImageError = (event, card) => {
      console.error(
        "Image failed to load for card:",
        card.name,
        "URL:",
        event.target.src,
      );
      event.target.style.display = "none";
      const noImageDiv = event.target.parentNode.querySelector(".bg-dark-100");
      if (noImageDiv) {
        noImageDiv.style.display = "flex";
      }
    };

    const filteredAndSortedCards = computed(() => {
      return cards.value
        .filter((card) => {
          const nameMatch = card.name
            .toLowerCase()
            .includes(filters.value.name.toLowerCase());
          const rarityMatch =
            !filters.value.rarity || card.rarity === filters.value.rarity;
          const colorMatch =
            filters.value.colors.length === 0 ||
            (card.colors &&
              card.colors.some((color) =>
                filters.value.colors.includes(color),
              ));
          const missingMatch =
            !filters.value.missing ||
            (card.quantity_regular === 0 && card.quantity_foil === 0);
          return nameMatch && rarityMatch && colorMatch && missingMatch;
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

    onMounted(() => {
      fetchCards();
    });

    return {
      setName,
      cards,
      loading,
      error,
      filters,
      updateFilters,
      updateQuantity,
      cardsPerRow,
      updateCardsPerRow,
      gridStyle,
      getImageUrl,
      handleImageError,
      filteredAndSortedCards,
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
  aspect-ratio: 5 / 7;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.card:hover {
  transform: scale(1.02);
}

.card-quantities {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quantity-control {
  width: 100%;
}

.quantity-label {
  font-size: 0.75rem;
}

.input-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.quantity-input {
  flex: 1;
  text-align: center;
  border: none;
  outline: none;
  background-color: var(--input-background);
  color: var(--text-color);
}

.btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--button-background);
  color: var(--text-color);
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn:hover:not(:disabled) {
  background-color: var(--button-hover-background);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .card-quantities {
    flex-direction: column;
  }

  .quantity-control {
    margin-bottom: 0.5rem;
  }
}
</style>
