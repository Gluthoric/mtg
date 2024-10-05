<template>
  <div
    class="controls bg-gray-100 dark:bg-gray-800 p-6 rounded-lg shadow-md mb-6"
  >
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Name Filter -->
      <div class="filter-section">
        <input
          v-model="filters.name"
          placeholder="Search by name"
          class="w-full p-3 border border-gray-300 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
        />
      </div>

      <!-- Rarity Filter -->
      <div class="filter-section">
        <label
          class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >Rarities</label
        >
        <div class="flex flex-wrap gap-2">
          <button
            v-for="rarity in availableRarities"
            :key="rarity"
            @click="toggleRarity(rarity)"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200',
              isRaritySelected(rarity)
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600',
              'border border-gray-300 dark:border-gray-600',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400',
            ]"
          >
            {{ rarity }}
          </button>
        </div>
      </div>

      <!-- Color Filter -->
      <div class="filter-section">
        <label
          class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >Colors</label
        >
        <div class="flex flex-wrap gap-2">
          <button
            v-for="color in availableColors"
            :key="color"
            @click="toggleColor(color)"
            :class="[
              'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200',
              colorClass(color),
              isColorSelected(color)
                ? 'ring-2 ring-offset-2 ring-blue-500 dark:ring-blue-400'
                : 'opacity-70 hover:opacity-100',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400',
            ]"
          >
            <span class="sr-only">{{ getColorName(color) }}</span>
          </button>
        </div>
      </div>

      <!-- Type Line Filter -->
      <div class="filter-section">
        <label
          class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >Types</label
        >
        <div class="flex flex-wrap gap-2">
          <button
            v-for="type in availableTypes"
            :key="type"
            @click="toggleType(type)"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200',
              isTypeSelected(type)
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600',
              'border border-gray-300 dark:border-gray-600',
              'focus:outline-none focus:ring-2 focus:ring-green-500 dark:focus:ring-green-400',
            ]"
          >
            {{ type }}
          </button>
        </div>
      </div>

      <!-- Keywords Filter -->
      <div class="filter-section relative" ref="keywordDropdownRef">
        <label
          class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >Keywords</label
        >
        <div class="relative">
          <input
            type="text"
            v-model="keywordSearch"
            @focus="showKeywordDropdown = true"
            @input="filterKeywords"
            placeholder="Select keyword"
            class="w-full p-3 border border-gray-300 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
          />
          <ul
            v-if="showKeywordDropdown"
            class="absolute z-10 w-full mt-1 max-h-60 overflow-auto bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg"
          >
            <li
              v-for="keyword in filteredKeywords"
              :key="keyword"
              @click="selectKeyword(keyword)"
              class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer text-gray-700 dark:text-gray-300"
            >
              {{ keyword }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Cards Per Row Slider -->
      <div class="filter-section">
        <label
          for="cards-per-row-slider"
          class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Cards per row
        </label>
        <input
          id="cards-per-row-slider"
          type="range"
          v-model="cardsPerRow"
          min="5"
          max="12"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
        />
        <div class="text-sm mt-2 text-gray-600 dark:text-gray-400">
          {{ cardsPerRow }} cards per row
        </div>
      </div>

      <!-- Missing Filter Toggle -->
      <div class="filter-section flex items-center">
        <label class="flex items-center cursor-pointer">
          <div class="relative">
            <input type="checkbox" v-model="filters.missing" class="sr-only" />
            <div class="w-10 h-6 bg-gray-200 rounded-full shadow-inner"></div>
            <div
              class="dot absolute w-6 h-6 bg-white rounded-full shadow -left-1 -top-1 transition"
            ></div>
          </div>
          <div class="ml-3 text-gray-700 dark:text-gray-300 font-medium">
            Show Missing Cards
          </div>
        </label>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from "vue";
import { onClickOutside } from "@vueuse/core";

interface Filters {
  name: string;
  rarities: string[];
  colors: string[];
  missing: boolean;
  types: string[];
  keyword: string;
}

export default defineComponent({
  name: "CardListControls",
  props: {
    modelValue: {
      type: Object as () => Filters,
      required: true,
    },
    modelCardsPerRow: {
      type: Number,
      default: 6,
    },
  },
  emits: ["update:modelValue", "update:modelCardsPerRow"],
  setup(props, { emit }) {
    const filters = ref<Filters>({
      name: props.modelValue.name || "",
      rarities: props.modelValue.rarities || [],
      colors: props.modelValue.colors || [],
      missing: props.modelValue.missing || false,
      types: props.modelValue.types || [],
      keyword: props.modelValue.keyword || "",
    });
    const cardsPerRow = ref(props.modelCardsPerRow);

    const availableColors = ["W", "U", "B", "R", "G", "C"];
    const availableRarities = ["common", "uncommon", "rare", "mythic"];
    const availableTypes = [
      "Creature",
      "Artifact",
      "Enchantment",
      "Instant",
      "Sorcery",
      "Planeswalker",
      "Land",
    ];
    const availableKeywords = [
      "Flying",
      "Haste",
      "First strike",
      "Trample",
      "Vigilance",
    ];

    const keywordSearch = ref("");
    const showKeywordDropdown = ref(false);
    const filteredKeywords = ref(availableKeywords);

    const isRaritySelected = computed(
      () => (rarity: string) => filters.value.rarities.includes(rarity),
    );

    const isColorSelected = computed(
      () => (color: string) => filters.value.colors.includes(color),
    );

    const isTypeSelected = computed(
      () => (type: string) => filters.value.types.includes(type),
    );

    const colorClass = (color: string) => {
      const colorMap: Record<string, string> = {
        W: "bg-white text-black",
        U: "bg-blue-500 text-white",
        B: "bg-black text-white",
        R: "bg-red-500 text-white",
        G: "bg-green-500 text-white",
        C: "bg-gray-500 text-white",
      };
      return colorMap[color] || "bg-gray-500 text-white";
    };

    const getColorName = (color: string) => {
      const colorNames: Record<string, string> = {
        W: "White",
        U: "Blue",
        B: "Black",
        R: "Red",
        G: "Green",
        C: "Colorless",
      };
      return colorNames[color] || color;
    };

    const toggleRarity = (rarity: string) => {
      const index = filters.value.rarities.indexOf(rarity);
      if (index > -1) {
        filters.value.rarities.splice(index, 1);
      } else {
        filters.value.rarities.push(rarity);
      }
    };

    const toggleColor = (color: string) => {
      const index = filters.value.colors.indexOf(color);
      if (index > -1) {
        filters.value.colors.splice(index, 1);
      } else {
        filters.value.colors.push(color);
      }
    };

    const toggleType = (type: string) => {
      const index = filters.value.types.indexOf(type);
      if (index > -1) {
        filters.value.types.splice(index, 1);
      } else {
        filters.value.types.push(type);
      }
    };

    const filterKeywords = () => {
      const search = keywordSearch.value.toLowerCase();
      filteredKeywords.value = availableKeywords.filter((kw) =>
        kw.toLowerCase().includes(search),
      );
    };

    const selectKeyword = (keyword: string) => {
      filters.value.keyword = keyword;
      keywordSearch.value = keyword;
      showKeywordDropdown.value = false;
    };

    watch(
      filters,
      (newFilters) => {
        emit("update:modelValue", newFilters);
      },
      { deep: true },
    );

    watch(cardsPerRow, (newCardsPerRow) => {
      emit("update:modelCardsPerRow", newCardsPerRow);
    });

    const keywordDropdownRef = ref(null);
    onClickOutside(keywordDropdownRef, () => {
      showKeywordDropdown.value = false;
    });

    return {
      filters,
      cardsPerRow,
      availableColors,
      availableRarities,
      availableTypes,
      keywordSearch,
      showKeywordDropdown,
      filteredKeywords,
      isRaritySelected,
      isColorSelected,
      isTypeSelected,
      colorClass,
      getColorName,
      toggleRarity,
      toggleColor,
      toggleType,
      filterKeywords,
      selectKeyword,
      keywordDropdownRef,
    };
  },
});
</script>

<style scoped>
input:checked ~ .dot {
  transform: translateX(100%);
  background-color: #48bb78;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #48bb78;
  cursor: pointer;
  border-radius: 50%;
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #48bb78;
  cursor: pointer;
  border-radius: 50%;
}
</style>
