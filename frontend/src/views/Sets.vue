<template>
  <div class="container">
    <h1 class="text-center text-2xl font-bold mb-4">
      Magic: The Gathering Sets
    </h1>
    <div v-if="loading" class="text-center text-lg">Loading sets...</div>
    <div v-else-if="error" class="error text-center text-lg text-error">
      Error: {{ error }}
    </div>
    <div v-else-if="sets.length === 0" class="text-center text-lg">
      No sets found.
    </div>
    <div v-else>
      <p class="text-center mb-4">Total sets: {{ sets.length }}</p>
      <div class="set-grid grid grid-cols-auto gap-4">
        <div v-for="set in sets" :key="set.code" class="card p-4">
          <router-link
            :to="{ name: 'SetDetails', params: { setCode: set.code } }"
            class="block"
          >
            <img
              v-lazy="set.icon_svg_uri"
              :alt="set.name"
              class="w-12 h-12 mx-auto mb-2"
            />
            <h2 class="text-lg font-semibold mb-2">{{ set.name }}</h2>
            <p class="mb-2">Released: {{ formatDate(set.released_at) }}</p>
            <div class="progress-container mb-2">
              <div
                class="progress-bar"
                :style="{
                  width: `${set.collection_percentage}%`,
                  backgroundColor: getProgressColor(set.collection_percentage),
                }"
              ></div>
            </div>
            <p class="collection-status font-bold">
              {{ formatCollectionProgress(set) }}
            </p>
          </router-link>
        </div>
      </div>
      <div class="pagination text-center mt-6">
        <button
          @click="changePage(-1)"
          :disabled="currentPage === 1"
          class="px-4 py-2 mr-2"
        >
          Previous
        </button>
        <span class="px-4 py-2 bg-secondary rounded"
          >Page {{ currentPage }} of {{ totalPages }}</span
        >
        <button
          @click="changePage(1)"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 ml-2"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";

export default {
  name: "Sets",
  setup() {
    const sets = ref([]);
    const filters = ref({ name: "", set_type: "" });
    const currentPage = ref(1);
    const totalPages = ref(1);
    const loading = ref(true);
    const error = ref(null);

    const fetchSets = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get("/api/sets", {
          params: {
            ...filters.value,
            page: currentPage.value,
          },
        });
        sets.value = response.data.sets;
        totalPages.value = response.data.pages;
      } catch (err) {
        console.error("Error fetching sets:", err);
        error.value = "Failed to load sets";
      } finally {
        loading.value = false;
      }
    };

    const changePage = (delta) => {
      currentPage.value += delta;
      fetchSets();
    };

    const formatDate = (dateString) => {
      return dateString ? new Date(dateString).toLocaleDateString() : "N/A";
    };

    const formatCollectionProgress = (set) => {
      if (set.collection_count === 0) {
        return "Not Started (0%)";
      } else if (set.collection_count === set.card_count) {
        return "Complete (100%)";
      } else {
        return `${set.collection_count}/${set.card_count} (${set.collection_percentage.toFixed(2)}%)`;
      }
    };

    const getProgressColor = (percentage) => {
      if (percentage === 0) return "#95a5a6";
      if (percentage < 25) return "#e74c3c";
      if (percentage < 50) return "#e67e22";
      if (percentage < 75) return "#f1c40f";
      if (percentage < 100) return "#2ecc71";
      return "#3498db";
    };

    onMounted(fetchSets);

    return {
      sets,
      filters,
      currentPage,
      totalPages,
      loading,
      error,
      fetchSets,
      changePage,
      formatDate,
      formatCollectionProgress,
      getProgressColor,
    };
  },
};
</script>
