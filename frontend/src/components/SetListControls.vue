<template>
  <div class="controls bg-secondary p-4 rounded-lg shadow-md">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="filter-section">
        <input
          v-model="localFilters.name"
          @input="emitFilters"
          placeholder="Search by name"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      <!-- Set Types Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Set Types</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="type in setTypes"
            :key="type"
            @click="toggleSetType(type)"
            :class="[
              'px-3 py-1 rounded-full capitalize text-sm',
              isSetTypeSelected(type) ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              'hover:bg-primary hover:text-white transition-colors duration-200'
            ]"
          >
            {{ capitalize(type.replace('_', ' ')) }}
          </button>
        </div>
      </div>

      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Digital</label>
        <select 
          v-model="localFilters.digital" 
          @change="emitFilters"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All</option>
          <option value="true">Digital Only</option>
          <option value="false">Physical Only</option>
        </select>
      </div>
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Foil Only</label>
        <select 
          v-model="localFilters.foil_only" 
          @change="emitFilters"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All</option>
          <option value="true">Foil Only Sets</option>
          <option value="false">Include Non-Foil Sets</option>
        </select>
      </div>
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Released From</label>
        <input
          type="date"
          v-model="localFilters.released_from"
          @change="emitFilters"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Released To</label>
        <input
          type="date"
          v-model="localFilters.released_to"
          @change="emitFilters"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      <!-- Sort Options -->
      <div class="sort-section">
        <label class="block text-sm font-medium mb-2">Sort By</label>
        <select
          v-model="selectedSortOption"
          @change="updateSorting"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <div class="pagination-section">
        <label for="perPage" class="block mb-1">Per Page:</label>
        <select 
          v-model="localPerPage" 
          @change="emitPerPage" 
          id="perPage"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option v-for="option in perPageOptions" :key="option" :value="option">{{ option }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SetListControls',
  props: {
    setTypes: {
      type: Array,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      localFilters: {
        name: '',
        set_types: [],
        digital: '',
        foil_only: '',
        released_from: '',
        released_to: ''
      },
      selectedSortOption: 'released_at-desc',
      sortOptions: [
        { value: 'released_at-desc', label: 'Release Date (Newest)' },
        { value: 'released_at-asc', label: 'Release Date (Oldest)' },
        { value: 'name-asc', label: 'Name (A-Z)' },
        { value: 'name-desc', label: 'Name (Z-A)' },
        { value: 'collection_count-desc', label: 'Collection Count (High to Low)' },
        { value: 'collection_count-asc', label: 'Collection Count (Low to High)' },
      ],
      localPerPage: 20,
      perPageOptions: [10, 20, 50, 100]
    }
  },
  methods: {
    emitFilters() {
      this.$emit('update-filters', { ...this.localFilters })
    },
    updateSorting() {
      const [sortBy, sortOrder] = this.selectedSortOption.split('-')
      this.$emit('update-sorting', { sortBy, sortOrder })
    },
    emitPerPage() {
      this.$emit('update-per-page', this.localPerPage)
    },
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1)
    },
    toggleSetType(type) {
      const index = this.localFilters.set_types.indexOf(type)
      if (index > -1) {
        this.localFilters.set_types.splice(index, 1)
      } else {
        this.localFilters.set_types.push(type)
      }
      this.emitFilters()
    },
    isSetTypeSelected(type) {
      return this.localFilters.set_types.includes(type)
    }
  }
}
</script>

<style scoped>
.controls label {
  margin-right: 0.5rem;
}
</style>
