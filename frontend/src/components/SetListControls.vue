<template>
  <div class="controls grid grid-cols-1 md:grid-cols-3 gap-1 mb-2">
    <div class="filter-section">
      <input
        v-model="localFilters.name"
        @input="emitFilters"
        placeholder="Search by name"
      />
      <select v-model="localFilters.set_type" @change="emitFilters">
        <option value="">All Types</option>
        <option v-for="type in setTypes" :key="type" :value="type">{{ capitalize(type) }}</option>
      </select>
    </div>
    <div class="sort-section">
      <label for="sortBy">Sort By:</label>
      <select v-model="localSorting.sortBy" @change="emitSorting" id="sortBy">
        <option value="released_at">Release Date</option>
        <option value="name">Name</option>
        <option value="collection_count">Collection Count</option>
      </select>
      <select v-model="localSorting.sortOrder" @change="emitSorting">
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>
    </div>
    <div class="pagination-section">
      <label for="perPage">Per Page:</label>
      <select v-model="localPerPage" @change="emitPerPage" id="perPage">
        <option v-for="option in perPageOptions" :key="option" :value="option">{{ option }}</option>
      </select>
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