<template>
  <div class="controls bg-secondary p-4 rounded-lg shadow-md">
    <div class="max-w-3xl mx-auto">
      <div class="space-y-6">
        <div class="filter-section">
          <label for="name-filter" class="sr-only">Search by name</label>
          <input
            id="name-filter"
            v-model="localFilters.name"
            @input="emitFilters"
            placeholder="Search by name"
            class="w-full p-2 border rounded-md bg-input-background text-white focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div class="filter-section">
          <label class="block text-sm font-medium mb-2 text-center"
            >Set Types</label
          >
          <div class="flex flex-wrap justify-center gap-2">
            <button
              v-for="type in setTypes"
              :key="type"
              @click="toggleSetType(type)"
              :class="[
                'px-3 py-1 rounded-full capitalize text-sm',
                isSetTypeSelected(type)
                  ? 'bg-primary text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
                'hover:bg-primary hover:text-white transition-colors duration-200',
              ]"
            >
              {{ capitalize(type.replace("_", " ")) }}
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sort-section">
            <label for="sort-select" class="block text-sm font-medium mb-2"
              >Sort By</label
            >
            <select
              id="sort-select"
              v-model="selectedSortOption"
              @change="updateSorting"
              class="w-full p-2 border rounded-md bg-input-background text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option
                v-for="option in sortOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <div class="pagination-section">
            <label for="per-page-select" class="block text-sm font-medium mb-2"
              >Per Page</label
            >
            <select
              id="per-page-select"
              v-model="localPerPage"
              @change="emitPerPage"
              class="w-full p-2 border rounded-md bg-input-background text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option
                v-for="option in perPageOptions"
                :key="option"
                :value="option"
              >
                {{ option }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import debounce from "lodash.debounce";

export default {
  name: "SetListControls",
  props: {
    setTypes: {
      type: Array,
      required: true,
    },
    totalPages: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      localFilters: {
        name: "",
        set_types: [],
      },
      localSorting: {
        sortBy: "released_at",
        sortOrder: "desc",
      },
      sortOptions: [
        { value: "released_at-desc", label: "Release Date (Newest)" },
        { value: "released_at-asc", label: "Release Date (Oldest)" },
        { value: "name-asc", label: "Name (A-Z)" },
        { value: "name-desc", label: "Name (Z-A)" },
        {
          value: "collection_count-desc",
          label: "Collection Count (High to Low)",
        },
        {
          value: "collection_count-asc",
          label: "Collection Count (Low to High)",
        },
      ],
      localPerPage: 50,
      perPageOptions: [20, 50, 100, 200],
    };
  },
  computed: {
    selectedSortOption: {
      get() {
        return `${this.localSorting.sortBy}-${this.localSorting.sortOrder}`;
      },
      set(value) {
        const [sortBy, sortOrder] = value.split("-");
        this.localSorting = { sortBy, sortOrder };
        this.emitChanges();
      },
    },
  },
  created() {
    this.debouncedEmitChanges = debounce(this.emitChanges, 300);
  },
  methods: {
    emitChanges() {
      this.$emit("update-filters", { ...this.localFilters });
      this.$emit("update-sorting", { ...this.localSorting });
    },
    emitPerPage() {
      this.$emit("update-per-page", this.localPerPage);
    },
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    toggleSetType(type) {
      const index = this.localFilters.set_types.indexOf(type);
      if (index === -1) {
        this.localFilters.set_types.push(type);
      } else {
        this.localFilters.set_types.splice(index, 1);
      }
      this.emitChanges();
    },
    isSetTypeSelected(type) {
      return this.localFilters.set_types.includes(type);
    },
  },
  watch: {
    "localFilters.name": {
      handler() {
        this.debouncedEmitChanges();
      },
    },
  },
};
</script>

<style scoped>
/* Add any additional styles here if needed */
</style>
