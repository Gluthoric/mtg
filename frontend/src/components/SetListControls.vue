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
        <select 
          v-model="localFilters.set_type" 
          @change="emitFilters"
          class="w-full mt-2 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Types</option>
          <option v-for="type in setTypes" :key="type" :value="type">{{ capitalize(type.replace('_', ' ')) }}</option>
        </select>
      </div>
      <div class="sort-section">
        <label for="sortBy" class="block mb-1">Sort By:</label>
        <div class="flex space-x-2">
          <select 
            v-model="localSorting.sortBy" 
            @change="emitSorting" 
            id="sortBy"
            class="w-1/2 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="released_at">Release Date</option>
            <option value="name">Name</option>
            <option value="collection_count">Collection Count</option>
          </select>
          <select 
            v-model="localSorting.sortOrder" 
            @change="emitSorting"
            class="w-1/2 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
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
        set_type: ''
      },
      localSorting: {
        sortBy: 'released_at',
        sortOrder: 'desc'
      },
      localPerPage: 20,
      perPageOptions: [10, 20, 50, 100]
    }
  },
  methods: {
    emitFilters() {
      this.$emit('update-filters', { ...this.localFilters })
    },
    emitSorting() {
      this.$emit('update-sorting', { ...this.localSorting })
    },
    emitPerPage() {
      this.$emit('update-per-page', this.localPerPage)
    },
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1)
    }
  }
}
</script>

<style scoped>
.controls label {
  margin-right: 0.5rem;
}
</style>
