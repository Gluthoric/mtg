<template>
  <div class="controls bg-secondary p-4 rounded-lg shadow-md mb-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Name Filter -->
      <div class="filter-section">
        <input
          v-model="localFilters.name"
          @input="emitFilters"
          placeholder="Search by name"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      <!-- Rarity Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Rarities</label>
        <div class="flex flex-wrap gap-2">
          <label v-for="rarity in availableRarities" :key="rarity" class="flex items-center">
            <input
              type="checkbox"
              :value="rarity"
              v-model="localFilters.rarities"
              @change="emitFilters"
              class="mr-1"
            />
            <span class="capitalize">{{ rarity }}</span>
          </label>
        </div>
      </div>

      <!-- Color Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Colors</label>
        <div class="flex flex-wrap gap-2">
          <label v-for="color in availableColors" :key="color" class="flex items-center">
            <input
              type="checkbox"
              :value="color"
              v-model="localFilters.colors"
              @change="emitFilters"
              class="mr-1"
            />
            <span :class="colorClass(color)" class="capitalize">{{ getColorName(color) }}</span>
          </label>
        </div>
      </div>

      <!-- Type Line Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Types</label>
        <div class="flex flex-wrap gap-2">
          <label v-for="type in availableTypes" :key="type" class="flex items-center">
            <input
              type="checkbox"
              :value="type"
              v-model="localFilters.types"
              @change="emitFilters"
              class="mr-1"
            />
            <span class="capitalize">{{ type }}</span>
          </label>
        </div>
      </div>

      <!-- Keywords Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Keywords</label>
        <select
          v-model="localFilters.keyword"
          @change="emitFilters"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Keywords</option>
          <option v-for="keyword in availableKeywords" :key="keyword" :value="keyword">
            {{ keyword }}
          </option>
        </select>
      </div>

      <!-- Missing Filter Button -->
      <div class="filter-section">
        <button
          @click="toggleMissingFilter"
          class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          :class="{ 'bg-blue-600': localFilters.missing }"
        >
          {{ localFilters.missing ? 'Show All Cards' : 'Show Missing Cards' }}
        </button>
      </div>

      <!-- Cards Per Row Slider -->
      <div class="filter-section">
        <label for="cards-per-row-slider" class="block text-sm font-medium mb-2">Cards per row</label>
        <input
          id="cards-per-row-slider"
          type="range"
          v-model="localCardsPerRow"
          min="5"
          max="12"
          step="1"
          class="w-full"
          @input="emitCardsPerRow"
        />
        <div class="text-sm mt-1">{{ localCardsPerRow }} cards per row</div>
      </div>
    </div>
  </div>
</template>

<script>
import debounce from 'lodash.debounce'

export default {
  name: 'CardListControls',
  props: {
    filters: {
      type: Object,
      default: () => ({
        name: '',
        rarities: [],
        colors: [],
        missing: false,
        types: [],
        keyword: ''
      })
    },
    cardsPerRow: {
      type: Number,
      default: 6
    }
  },
  data() {
    return {
      localFilters: { ...this.filters },
      localCardsPerRow: this.cardsPerRow,
      availableColors: ['W', 'U', 'B', 'R', 'G', 'C'],
      availableRarities: ['common', 'uncommon', 'rare', 'mythic'],
      availableTypes: ['Creature', 'Artifact', 'Enchantment', 'Instant', 'Sorcery', 'Planeswalker', 'Land'],
      availableKeywords: ['Flying', 'Haste', 'First strike', 'Trample', 'Vigilance']
    }
  },
  created() {
    // Create a debounced version of emitFilters with a 300ms delay
    this.debouncedEmitFilters = debounce(() => {
      this.$emit('update-filters', { ...this.localFilters })
    }, 300)
  },
  methods: {
    emitFilters() {
      this.debouncedEmitFilters()
    },
    emitCardsPerRow() {
      this.$emit('update-cards-per-row', this.localCardsPerRow)
    },
    toggleMissingFilter() {
      this.localFilters.missing = !this.localFilters.missing
      this.emitFilters()
    },
    colorClass(color) {
      const colorMap = {
        W: 'text-white',
        U: 'text-blue-500',
        B: 'text-black',
        R: 'text-red-500',
        G: 'text-green-500',
        C: 'text-gray-500',
      }
      return colorMap[color] || 'text-gray-500'
    },
    getColorName(color) {
      const colorNames = {
        'W': 'White',
        'U': 'Blue',
        'B': 'Black',
        'R': 'Red',
        'G': 'Green',
        'C': 'Colorless',
      };
      return colorNames[color] || color;
    },
  },
  beforeUnmount() {
    // Cancel any pending debounced calls when the component is unmounted
    this.debouncedEmitFilters.cancel()
  }
}
</script>

<style scoped>
/* Add any additional styles here */
</style>
