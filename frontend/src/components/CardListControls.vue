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
          <button
            v-for="rarity in availableRarities"
            :key="rarity"
            @click="toggleRarity(rarity)"
            :class="[
              'px-3 py-1 rounded-full capitalize text-sm',
              isRaritySelected(rarity) ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              'hover:bg-primary hover:text-white transition-colors duration-200'
            ]"
          >
            {{ rarity }}
          </button>
        </div>
      </div>

      <!-- Color Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Colors</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="color in availableColors"
            :key="color"
            @click="toggleColor(color)"
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center',
              colorClass(color),
              isColorSelected(color) ? 'ring-2 ring-offset-2 ring-primary' : 'opacity-50 hover:opacity-75',
              'hover:opacity-100 transition-opacity duration-200'
            ]"
          >
            <span class="sr-only">{{ getColorName(color) }}</span>
          </button>
        </div>
      </div>

      <!-- Type Line Filter -->
      <div class="filter-section">
        <label class="block text-sm font-medium mb-2">Types</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="type in availableTypes"
            :key="type"
            @click="toggleType(type)"
            :class="[
              'px-3 py-1 rounded-full capitalize text-sm',
              isTypeSelected(type) ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              'hover:bg-primary hover:text-white transition-colors duration-200'
            ]"
          >
            {{ type }}
          </button>
        </div>
      </div>

      <!-- Keywords Filter -->
      <div class="filter-section relative" v-click-outside="() => showKeywordDropdown = false">
        <label class="block text-sm font-medium mb-2">Keywords</label>
        <div class="relative">
          <input
            type="text"
            v-model="keywordSearch"
            @focus="showKeywordDropdown = true"
            @input="filterKeywords"
            placeholder="Select keyword"
            class="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <ul v-if="showKeywordDropdown" class="absolute z-10 bg-white text-black w-full mt-1 max-h-40 overflow-auto border rounded-md">
            <li
              v-for="keyword in filteredKeywords"
              :key="keyword"
              @click="selectKeyword(keyword)"
              class="px-4 py-2 hover:bg-gray-200 cursor-pointer"
            >
              {{ keyword }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Missing Filter Toggle -->
      <div class="filter-section flex items-center">
        <label class="flex items-center">
          <span class="mr-2 text-sm font-medium">Show Missing Cards</span>
          <input
            type="checkbox"
            v-model="localFilters.missing"
            @change="emitFilters"
            class="toggle-checkbox"
          />
          <div class="toggle-slot">
            <div class="toggle-button"></div>
          </div>
        </label>
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
      availableKeywords: ['Flying', 'Haste', 'First strike', 'Trample', 'Vigilance'],
      keywordSearch: '',
      showKeywordDropdown: false,
      filteredKeywords: [],
    }
  },
  created() {
    this.debouncedEmitFilters = debounce(() => {
      this.$emit('update-filters', { ...this.localFilters })
    }, 300)
    this.filteredKeywords = this.availableKeywords
  },
  methods: {
    emitFilters() {
      this.debouncedEmitFilters()
    },
    emitCardsPerRow() {
      this.$emit('update-cards-per-row', this.localCardsPerRow)
    },
    toggleRarity(rarity) {
      const index = this.localFilters.rarities.indexOf(rarity)
      if (index > -1) {
        this.localFilters.rarities.splice(index, 1)
      } else {
        this.localFilters.rarities.push(rarity)
      }
      this.emitFilters()
    },
    isRaritySelected(rarity) {
      return this.localFilters.rarities.includes(rarity)
    },
    toggleColor(color) {
      const index = this.localFilters.colors.indexOf(color)
      if (index > -1) {
        this.localFilters.colors.splice(index, 1)
      } else {
        this.localFilters.colors.push(color)
      }
      this.emitFilters()
    },
    isColorSelected(color) {
      return this.localFilters.colors.includes(color)
    },
    colorClass(color) {
      const colorMap = {
        W: 'bg-white text-black',
        U: 'bg-blue-500 text-white',
        B: 'bg-black text-white',
        R: 'bg-red-500 text-white',
        G: 'bg-green-500 text-white',
        C: 'bg-gray-500 text-white',
      }
      return colorMap[color] || 'bg-gray-500 text-white'
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
    toggleType(type) {
      const index = this.localFilters.types.indexOf(type)
      if (index > -1) {
        this.localFilters.types.splice(index, 1)
      } else {
        this.localFilters.types.push(type)
      }
      this.emitFilters()
    },
    isTypeSelected(type) {
      return this.localFilters.types.includes(type)
    },
    filterKeywords() {
      const search = this.keywordSearch.toLowerCase()
      this.filteredKeywords = this.availableKeywords.filter(kw => kw.toLowerCase().includes(search))
    },
    selectKeyword(keyword) {
      this.localFilters.keyword = keyword
      this.keywordSearch = keyword
      this.showKeywordDropdown = false
      this.emitFilters()
    },
  },
  beforeUnmount() {
    this.debouncedEmitFilters.cancel()
  },
  directives: {
    clickOutside: {
      beforeMount(el, binding) {
        el.clickOutsideEvent = function(event) {
          if (!(el == event.target || el.contains(event.target))) {
            binding.value(event)
          }
        }
        document.body.addEventListener('click', el.clickOutsideEvent)
      },
      unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent)
      },
    },
  },
}
</script>

<style scoped>
.toggle-checkbox {
  opacity: 0;
  position: absolute;
}
.toggle-slot {
  position: relative;
  width: 40px;
  height: 20px;
  border-radius: 10px;
  background-color: #ccc;
  transition: background-color 0.3s ease;
}
.toggle-button {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: white;
  transition: transform 0.3s ease;
}
.toggle-checkbox:checked + .toggle-slot {
  background-color: #4299e1;
}
.toggle-checkbox:checked + .toggle-slot .toggle-button {
  transform: translateX(20px);
}

input[type="range"]::-webkit-slider-thumb {
  background: #4299e1;
}
input[type="range"]::-moz-range-thumb {
  background: #4299e1;
}
</style>
