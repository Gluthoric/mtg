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
        My Collection
      </h1>
      <SetListControls
        :setTypes="setTypes"
        :totalPages="totalPages"
        @update-filters="handleUpdateFilters"
        @update-sorting="handleUpdateSorting"
        @update-per-page="handleUpdatePerPage"
        class="controls bg-card p-4 rounded-lg shadow-md mb-4"
      />
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
      <div v-else-if="sets.length === 0" class="text-center mt-4">
        <p>No sets found in your collection.</p>
      </div>
      <TransitionGroup
        v-else
        name="set-list"
        tag="div"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4"
      >
        <div
          v-for="set in sets"
          :key="set.code"
          class="card p-4 rounded-lg shadow-md transition-all duration-300 ease-in-out hover:scale-105"
          :style="{
            backgroundColor: set.background_color || '#333333',
            color: set.text_color || '#ffffff',
          }"
        >
          <router-link
            :to="{ name: 'CollectionSetCards', params: { setCode: set.code } }"
            class="block"
          >
            <div class="flex items-center mb-2">
              <img
                :src="set.icon_svg_uri"
                :alt="set.name"
                loading="lazy"
                class="w-8 h-8 mr-2"
              />
              <h3 class="text-sm font-semibold truncate">{{ set.name }}</h3>
            </div>
            <div class="text-xs opacity-75 mb-1">
              {{ formatDate(set.released_at) }}
            </div>
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs"
                >{{ set.collection_count || 0 }} / {{ set.card_count }}</span
              >
              <span class="text-xs font-semibold"
                >{{ Math.round(set.collection_percentage || 0) }}%</span
              >
            </div>
            <div
              class="progress-container bg-opacity-30 bg-black rounded-full overflow-hidden"
            >
              <div
                class="progress-bar h-1 transition-all duration-300 ease-in-out bg-white"
                :style="{ width: `${set.collection_percentage}%` }"
                role="progressbar"
                :aria-valuenow="Math.round(set.collection_percentage)"
                aria-valuemin="0"
                aria-valuemax="100"
              ></div>
            </div>
            <div class="text-xs mt-2">
              <span class="font-semibold">Value:</span>
              {{ formatCurrency(set.total_value) }}
            </div>
          </router-link>
        </div>
      </TransitionGroup>
      <div class="pagination flex justify-center items-center mt-4 space-x-4">
        <button
          @click="changePage(-1)"
          :disabled="currentPage === 1"
          class="px-4 py-2 bg-primary text-primary-foreground rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <span class="text-lg font-semibold"
          >Page {{ currentPage }} of {{ totalPages }}</span
        >
        <button
          @click="changePage(1)"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 bg-primary text-primary-foreground rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import SetListControls from "../components/SetListControls.vue";

const sets = ref([]);
const loading = ref(true);
const error = ref(null);
const filters = ref({
  name: "",
  set_type: [
    "core",
    "expansion",
    "masters",
    "draft_innovation",
    "funny",
    "commander",
  ],
});
const sorting = ref({ sortBy: "released_at", sortOrder: "desc" });
const currentPage = ref(1);
const totalPages = ref(1);
const perPage = ref(50);
const setTypes = ref([
  "core",
  "expansion",
  "masters",
  "draft_innovation",
  "commander",
  "starter",
  "box",
  "promo",
  "token",
  "memorabilia",
]);

const navLinks = [
  { to: "/", text: "Home" },
  { to: "/collection", text: "Collection" },
  { to: "/kiosk", text: "Kiosk" },
  { to: "/import", text: "Import" },
];

const fetchSets = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get("/api/collection/sets", {
      params: {
        ...filters.value,
        sort_by: sorting.value.sortBy,
        sort_order: sorting.value.sortOrder,
        page: currentPage.value,
        per_page: perPage.value,
      },
    });
    sets.value = response.data.sets;
    totalPages.value = response.data.pages;
    currentPage.value = response.data.current_page;
  } catch (err) {
    console.error("Error fetching collection sets:", err);
    error.value = "Failed to load collection sets";
  } finally {
    loading.value = false;
  }
};

const handleUpdateFilters = (newFilters) => {
  filters.value = { ...filters.value, ...newFilters };
  if (newFilters.set_types) {
    filters.value.set_type =
      newFilters.set_types.length > 0 ? newFilters.set_types : undefined;
  }
  currentPage.value = 1;
  fetchSets();
};

const handleUpdateSorting = (newSorting) => {
  sorting.value = { ...newSorting };
  fetchSets();
};

const handleUpdatePerPage = (newPerPage) => {
  perPage.value = newPerPage;
  currentPage.value = 1;
  fetchSets();
};

const changePage = (delta) => {
  const newPage = currentPage.value + delta;
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage;
    fetchSets();
  }
};

const formatDate = (dateString) => {
  return dateString ? new Date(dateString).getFullYear() : "N/A";
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
};

onMounted(fetchSets);
</script>

<style scoped>
.set-list-enter-active,
.set-list-leave-active {
  transition: all 0.5s ease;
}
.set-list-enter-from,
.set-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: scale(1.05);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.progress-container {
  background-color: rgba(0, 0, 0, 0.3);
}

.progress-bar {
  transition: width 0.3s ease;
}
</style>
