<template>
  <div class="container mx-auto px-4 bg-dark-300 text-white">
    <nav class="mb-4 flex justify-center space-x-4">
      <router-link to="/" class="text-primary hover:underline"
        >Home</router-link
      >
      <router-link to="/collection" class="text-primary hover:underline"
        >Collection</router-link
      >
      <router-link to="/kiosk" class="text-primary hover:underline"
        >Kiosk</router-link
      >
      <router-link to="/import" class="text-primary hover:underline"
        >Import</router-link
      >
    </nav>
    <h1 class="text-center mb-4 text-2xl font-bold text-primary">
      Kiosk Inventory
    </h1>
    <SetListControls
      :setTypes="setTypes"
      :totalPages="totalPages"
      @update-filters="updateFilters"
      @update-sorting="updateSorting"
      @update-per-page="updatePerPage"
      class="controls bg-secondary p-4 rounded-lg shadow-md mb-4"
    />
    <div v-if="loading" class="loading text-center mt-1">Loading...</div>
    <div v-else-if="error" class="error text-center mt-1">{{ error }}</div>
    <div
      v-else-if="sets && sets.length > 0"
      class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
    >
      <div
        v-for="set in sets"
        :key="set.code"
        class="card bg-secondary p-4 rounded-lg shadow-md transition-transform hover:scale-105"
      >
        <router-link
          :to="{ name: 'KioskSetCards', params: { setCode: set.code } }"
        >
          <!-- Set icon displayed at the top -->
          <div class="set-icon">
            <img
              :src="set.icon_svg_uri"
              :alt="set.name"
              loading="lazy"
              class="w-24 h-24 mx-auto mb-4"
            />
          </div>

          <!-- Set code and name in a compact format -->
          <h3 class="text-center">
            {{ set.code.toUpperCase() }} - {{ set.name }}
          </h3>

          <!-- Display the Kiosk card count -->
          <p class="text-center">Kiosk: {{ set.kiosk_count }}</p>

          <!-- Display the total value of cards in the set -->
          <p class="text-center">
            Value: ${{
              set.total_value !== null && set.total_value !== undefined
                ? set.total_value.toFixed(2)
                : "N/A"
            }}
          </p>
        </router-link>
      </div>
    </div>
    <div v-else-if="!loading && sets.length === 0" class="text-center mt-1">
      <p>No sets found in your kiosk inventory.</p>
    </div>
    <div class="pagination flex justify-center items-center mt-4 space-x-4">
      <button
        @click="changePage(-1)"
        :disabled="currentPage === 1"
        class="px-4 py-2 bg-primary text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>
      <span class="text-lg font-semibold"
        >Page {{ currentPage }} of {{ totalPages }}</span
      >
      <button
        @click="changePage(1)"
        :disabled="currentPage === totalPages"
        class="px-4 py-2 bg-primary text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import SetListControls from "../components/SetListControls.vue";

export default {
  name: "Kiosk",
  components: {
    SetListControls,
  },
  setup() {
    const sets = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const filters = ref({});
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

    const fetchSets = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get("/api/kiosk/sets", {
          params: {
            ...filters.value,
            ...sorting.value,
            page: currentPage.value,
            per_page: perPage.value,
          },
        });
        sets.value = response.data.sets;
        totalPages.value = response.data.pages;
        currentPage.value = response.data.current_page;
      } catch (err) {
        console.error("Error fetching kiosk sets:", err);
        error.value = "Failed to load kiosk sets";
      } finally {
        loading.value = false;
      }
    };

    const updateFilters = (newFilters) => {
      filters.value = { ...filters.value, ...newFilters };
      currentPage.value = 1;
      fetchSets();
    };

    const updateSorting = (newSorting) => {
      sorting.value = { ...newSorting };
      fetchSets();
    };

    const updatePerPage = (newPerPage) => {
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

    onMounted(() => {
      fetchSets();
    });

    return {
      sets,
      loading,
      error,
      filters,
      sorting,
      currentPage,
      totalPages,
      perPage,
      setTypes,
      updateFilters,
      updateSorting,
      updatePerPage,
      changePage,
    };
  },
};
</script>

<style scoped>
.controls {
  background-color: var(--secondary-color);
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

input,
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
}

input:focus,
select:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
}

.set-types-container {
  margin-top: 1rem;
}

.set-types-container h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.set-types-container .grid {
  grid-template-columns: repeat(2, 1fr);
}

@media (min-width: 768px) {
  .set-types-container .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .set-types-container .grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

.set-types-container label {
  display: flex;
  align-items: center;
}

.set-types-container input[type="checkbox"] {
  margin-right: 0.5rem;
}

.set-types-container span {
  text-transform: capitalize;
}

.card {
  padding: 1rem;
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: scale(1.02);
}

.set-icon {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
}

.set-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
