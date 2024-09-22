<template>
  <div class="controls">
    <div class="filter-section">
      <input
        v-model="localFilters.name"
        @input="emitFilters"
        placeholder="Search by name"
        class="input"
      />
      <select v-model="localFilters.set_type" @change="emitFilters" class="select">
        <option value="">All Types</option>
        <option v-for="type in setTypes" :key="type" :value="type">{{ capitalize(type) }}</option>
      </select>
    </div>
    <div class="sort-section">
      <label for="sortBy">Sort By:</label>
      <select v-model="localSorting.sortBy" @change="emitSorting" id="sortBy" class="select">
        <option value="released_at">Release Date</option>
        <option value="name">Name</option>
        <option value="collection_count">Collection Count</option>
      </select>
      <select v-model="localSorting.sortOrder" @change="emitSorting" class="select">
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>
    </div>
    <div class="pagination-section">
      <label for="perPage">Per Page:</label>
      <select v-model="localPerPage" @change="emitPerPage" id="perPage" class="select">
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
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-section,
.sort-section,
.pagination-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-background);
  color: var(--text-color);
}

.select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-background);
  color: var(--text-color);
}

button {
  background-color: var(--primary-color);
  color: var(--text-color);
}

button:hover {
  background-color: var(--link-color);
}
</style>