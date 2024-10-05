<template>
  <div class="bg-background text-foreground min-h-screen">
    <nav class="mb-4 flex justify-center space-x-4 p-4">
      <router-link
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="text-primary hover:underline"
      >
        {{ link.text }}
      </router-link>
    </nav>
    <div class="px-4 md:px-6 lg:px-8">
      <h1 class="text-center mb-4 text-2xl font-bold text-primary">
        {{ setName }}
      </h1>
      <div v-if="loading" class="loading text-center mt-4" role="status">
        <span class="sr-only">Loading...</span>
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"
        ></div>
      </div>
      <div
        v-else-if="error"
        class="error text-center mt-4 text-destructive"
        role="alert"
      >
        {{ error }}
      </div>
      <div v-else>
        <CardListControls
          v-model="filters"
          v-model:modelCardsPerRow="cardsPerRow"
          class="controls bg-card p-4 rounded-lg shadow-md mb-4"
        />

        <!-- Set Statistics -->
        <div class="set-stats bg-card p-4 rounded-lg mb-4">
          <h2 class="text-lg font-semibold mb-2">Set Statistics</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p class="text-sm text-muted-foreground">Total Cards in Set</p>
              <p class="text-xl font-bold">{{ totalCardsInSet }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Cards in Collection</p>
              <p class="text-xl font-bold">{{ cardsInCollection }}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Completion</p>
              <p class="text-xl font-bold">{{ completionPercentage }}%</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Total Value</p>
              <p class="text-xl font-bold">${{ totalValue.toFixed(2) }}</p>
            </div>
          </div>
        </div>

        <!-- Detailed Statistics -->
        <div
          v-if="statistics"
          class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
        >
          <!-- Frame Effects -->
          <div class="bg-card p-4 rounded-lg">
            <h2 class="text-xl font-semibold text-primary mb-2">
              Frame Effects
            </h2>
            <ul
              v-if="Object.keys(statistics.frame_effects).length"
              class="space-y-1"
            >
              <li
                v-for="(count, effect) in statistics.frame_effects"
                :key="effect"
                class="flex justify-between"
              >
                <span>{{ effect }}</span>
                <span class="font-semibold">{{ count }}</span>
              </li>
            </ul>
            <p v-else class="text-muted-foreground">
              No frame effects in this set
            </p>
          </div>

          <!-- Promo Types -->
          <div class="bg-card p-4 rounded-lg">
            <h2 class="text-xl font-semibold text-primary mb-2">Promo Types</h2>
            <ul
              v-if="Object.keys(statistics.promo_types).length"
              class="space-y-1"
            >
              <li
                v-for="(count, promo) in statistics.promo_types"
                :key="promo"
                class="flex justify-between"
              >
                <span>{{ promo }}</span>
                <span class="font-semibold">{{ count }}</span>
              </li>
            </ul>
            <p v-else class="text-muted-foreground">
              No promo types in this set
            </p>
          </div>

          <!-- Other Attributes -->
          <div class="bg-card p-4 rounded-lg">
            <h2 class="text-xl font-semibold text-primary mb-2">
              Other Attributes
            </h2>
            <ul
              v-if="Object.keys(statistics.other_attributes).length"
              class="space-y-1"
            >
              <li
                v-for="(count, attribute) in statistics.other_attributes"
                :key="attribute"
                class="flex justify-between"
              >
                <span>{{ attribute }}</span>
                <span class="font-semibold">{{ count }}</span>
              </li>
            </ul>
            <p v-else class="text-muted-foreground">
              No other attributes in this set
            </p>
          </div>
        </div>

        <!-- Cards Grid -->
        <div class="card-grid grid gap-4" :style="gridStyle">
          <div
            v-for="card in sortedCards"
            :key="card.id"
            class="card bg-card shadow-md rounded-lg overflow-hidden relative flex flex-col"
            :class="{ 'border-2 border-destructive': isMissing(card) }"
          >
            <div class="card-info p-2 z-10 bg-card bg-opacity-80">
              <h3 class="text-base font-semibold truncate text-primary">
                {{ card.name }}
              </h3>
            </div>
            <div class="image-container aspect-w-3 aspect-h-4">
              <img
                v-if="getImageUrl(card)"
                :src="getImageUrl(card)"
                :alt="card.name"
                class="w-full h-full object-contain"
                @error="handleImageError($event, card)"
              />
              <div
                v-else
                class="w-full h-full flex items-center justify-center bg-muted text-muted-foreground"
              >
                No image available
              </div>
            </div>
            <div class="card-info p-2 flex flex-col">
              <div class="flex justify-between items-center mb-2">
                <p class="text-xs text-muted-foreground">
                  CN: {{ card.collector_number }}
                </p>
                <p class="text-xs text-muted-foreground">{{ card.rarity }}</p>
              </div>
              <div class="card-quantities flex flex-col space-y-2">
                <!-- Regular Quantity Control -->
                <div class="quantity-control">
                  <label
                    :for="'regular-' + card.id"
                    class="quantity-label text-xs font-semibold text-muted-foreground block mb-1"
                  >
                    Regular
                  </label>
                  <div
                    class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden"
                  >
                    <button
                      @click="decrement(card, 'regular')"
                      class="btn decrement-btn flex items-center justify-center bg-secondary hover:bg-secondary-hover"
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
                      class="quantity-input text-center border-none outline-none bg-input text-black text-sm"
                      @input="onInput(card, 'regular')"
                    />
                    <button
                      @click="increment(card, 'regular')"
                      class="btn increment-btn flex items-center justify-center bg-secondary hover:bg-secondary-hover"
                      aria-label="Increment Regular Quantity"
                    >
                      +
                    </button>
                  </div>
                  <div class="price text-xs text-muted-foreground mt-1">
                    Price: ${{ card.prices?.usd || "N/A" }}
                  </div>
                </div>

                <!-- Foil Quantity Control -->
                <div class="quantity-control">
                  <label
                    :for="'foil-' + card.id"
                    class="quantity-label text-xs font-semibold text-muted-foreground block mb-1"
                  >
                    Foil
                  </label>
                  <div
                    class="input-wrapper flex items-center justify-center border rounded-md overflow-hidden"
                  >
                    <button
                      @click="decrement(card, 'foil')"
                      class="btn decrement-btn w-8 h-8 flex items-center justify-center bg-secondary hover:bg-secondary-hover"
                      aria-label="Decrement Foil Quantity"
                      :disabled="card.quantity_collection_foil === 0"
                    >
                      –
                    </button>
                    <input
                      :id="'foil-' + card.id"
                      v-model.number="card.quantity_foil"
                      type="number"
                      min="0"
                      class="quantity-input text-center border-none outline-none bg-input text-black text-sm"
                      @input="onInput(card, 'foil')"
                    />
                    <button
                      @click="increment(card, 'foil')"
                      class="btn increment-btn w-8 h-8 flex items-center justify-center bg-secondary hover:bg-secondary-hover"
                      aria-label="Increment Foil Quantity"
                    >
                      +
                    </button>
                  </div>
                  <div class="price text-xs text-muted-foreground mt-1">
                    Price: ${{ card.prices?.usd_foil || "N/A" }}
                  </div>
                </div>
              </div>
              <!-- Card Details -->
              <div class="card-details mt-2 text-xs text-muted-foreground">
                <p>
                  <span class="font-semibold">Type:</span>
                  {{ card.type_line || "N/A" }}
                </p>
                <p>
                  <span class="font-semibold">Mana Cost:</span>
                  {{ card.mana_cost || "N/A" }}
                </p>
                <p><span class="font-semibold">Set:</span> {{ setName }}</p>
                <p>
                  <span class="font-semibold">Rarity:</span> {{ card.rarity }}
                </p>
                <p v-if="card.frame_effects">
                  <span class="font-semibold">Frame Effects:</span>
                  {{ card.frame_effects.join(", ") }}
                </p>
                <p v-if="card.promo_types">
                  <span class="font-semibold">Promo Types:</span>
                  {{ card.promo_types.join(", ") }}
                </p>
              </div>
            </div>
            <div
              v-if="isMissing(card)"
              class="missing-indicator absolute top-1 right-1 bg-destructive text-destructive-foreground px-2 py-1 rounded text-xs font-bold shadow"
            >
              Missing
            </div>
          </div>
        </div>

        <!-- Handle No Cards Matching Filters -->
        <div
          v-if="sortedCards.length === 0"
          class="text-center text-muted-foreground mt-4"
        >
          No cards match the selected filters.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import CardListControls from "../components/CardListControls.vue";
import {
  fetchSetDetails as fetchSetDetailsUtil,
  applyFilters as applyFiltersUtil,
} from "../utils/setUtils";

const route = useRoute();
const setCode = ref(route.params.setCode);
const setName = ref("");
const cards = ref([]);
const originalCards = ref([]);
const loading = ref(true);
const error = ref(null);
const filters = ref({
  name: "",
  rarities: [],
  colors: [],
  missing: false,
  types: [],
  keyword: "",
});
const cardsPerRow = ref(6);
const statistics = ref(null);

const navLinks = [
  { to: "/", text: "Home" },
  { to: "/collection", text: "Collection" },
  { to: "/kiosk", text: "Kiosk" },
  { to: "/import", text: "Import" },
];

// Computed properties for set statistics
const totalCardsInSet = computed(() => originalCards.value.length);
const cardsInCollection = computed(
  () =>
    originalCards.value.filter(
      (card) => card.quantity_regular > 0 || card.quantity_foil > 0,
    ).length,
);
const completionPercentage = computed(() =>
  ((cardsInCollection.value / totalCardsInSet.value) * 100).toFixed(2),
);
const totalValue = computed(() => {
  return originalCards.value.reduce((total, card) => {
    const regularValue = (card.prices?.usd || 0) * (card.quantity_regular || 0);
    const foilValue = (card.prices?.usd_foil || 0) * (card.quantity_foil || 0);
    return total + regularValue + foilValue;
  }, 0);
});

const fetchSetDetails = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetchSetDetailsUtil(setCode.value);
    console.log("API response:", JSON.stringify(response, null, 2));
    if (response) {
      setName.value = response.set?.name || "";
      originalCards.value = response.cards || [];
      statistics.value = response.set?.statistics || {};
      console.log(
        "Statistics value:",
        JSON.stringify(statistics.value, null, 2),
      );
      console.log("Statistics keys:", Object.keys(statistics.value));
      applyFilters();
    } else {
      throw new Error("Invalid response format");
    }
  } catch (err) {
    console.error("Error fetching set details:", err);
    error.value = "Failed to load set details";
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  cards.value = applyFiltersUtil(originalCards.value, filters.value);
};

watch(
  () => route.params.setCode,
  (newSetCode) => {
    setCode.value = newSetCode;
    fetchSetDetails();
  },
);

watch(
  filters,
  () => {
    applyFilters();
  },
  { deep: true },
);

onMounted(() => {
  console.log("Component mounted");
  fetchSetDetails();
});

const isMissing = (card) => {
  return card.quantity_regular + card.quantity_foil === 0;
};

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
  const noImageDiv = event.target.parentNode.querySelector(".bg-muted");
  if (noImageDiv) {
    noImageDiv.style.display = "flex";
  }
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
    const response = await axios.put(`/api/collection/${card.id}`, payload);
    const updatedCard = response.data;
    // Update card data in originalCards
    const index = originalCards.value.findIndex((c) => c.id === card.id);
    if (index !== -1) {
      originalCards.value[index] = updatedCard;
    }
    applyFilters(); // Re-apply filters to update the displayed cards
  } catch (err) {
    console.error("Error updating quantity:", err);
    alert("Failed to update quantity. Please try again.");
  }
};

const increment = (card, type) => {
  updateQuantity(card, type, 1);
};

const decrement = (card, type) => {
  updateQuantity(card, type, -1);
};

const onInput = (card, type) => {
  if (type === "regular") {
    card.quantity_regular = Math.max(0, parseInt(card.quantity_regular) || 0);
  } else if (type === "foil") {
    card.quantity_foil = Math.max(0, parseInt(card.quantity_foil) || 0);
  }
  // Immediately update the backend
  updateQuantity(card, type);
};

const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${cardsPerRow.value}, 1fr)`,
}));

const sortedCards = computed(() => {
  return [...cards.value].sort((a, b) => {
    const aNum = parseInt(a.collector_number.replace(/\D/g, ""));
    const bNum = parseInt(b.collector_number.replace(/\D/g, ""));
    return aNum - bNum;
  });
});
</script>

<style scoped>
.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: scale(1.02);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.btn {
  @apply w-8 h-8 text-lg font-bold;
}

.quantity-input {
  @apply w-12 h-8;
}

/* Remove default number input arrows */
.quantity-input::-webkit-outer-spin-button,
.quantity-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.quantity-input[type="number"] {
  -moz-appearance: textfield;
}
</style>
