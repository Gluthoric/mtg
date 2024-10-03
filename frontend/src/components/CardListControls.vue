<template>
  <div class="controls bg-secondary p-4 rounded-lg shadow-md mb-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Name Filter -->
      <div class="filter-section">
        <input
          v-model="filters.name"
          placeholder="Search by name"
          class="w-full p-2 border rounded-md bg-input-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
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
              isRaritySelected(rarity)
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary-foreground text-secondary hover:bg-secondary-hover',
              'hover:text-secondary-foreground transition-colors duration-200',
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
              isColorSelected(color)
                ? 'ring-2 ring-offset-2 ring-primary'
                : 'opacity-50 hover:opacity-75',
              'hover:opacity-100 transition-opacity duration-200',
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
              isTypeSelected(type)
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary-foreground text-secondary hover:bg-secondary-hover',
              'hover:bg-primary hover:text-primary-foreground transition-colors duration-200',
            ]"
          >
            {{ type }}
          </button>
        </div>
      </div>

      <!-- Keywords Filter -->
      <div class="filter-section relative" ref="keywordDropdownRef">
        <label class="block text-sm font-medium mb-2">Keywords</label>
        <div class="relative">
          <input
            type="text"
            v-model="keywordSearch"
            @focus="showKeywordDropdown = true"
            @input="filterKeywords"
            placeholder="Select keyword"
            class="w-full p-2 border rounded-md bg-input-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <ul
            v-if="showKeywordDropdown"
            class="absolute z-10 bg-background text-foreground w-full mt-1 max-h-40 overflow-auto border rounded-md"
          >
            <li
              v-for="keyword in filteredKeywords"
              :key="keyword"
              @click="selectKeyword(keyword)"
              class="px-4 py-2 hover:bg-secondary cursor-pointer"
            >
              {{ keyword }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Cards Per Row Slider -->
      <div class="filter-section">
        <label for="cards-per-row-slider" class="block text-sm font-medium mb-2"
          >Cards per row</label
        >
        <input
          id="cards-per-row-slider"
          type="range"
          v-model="cardsPerRow"
          min="5"
          max="12"
          step="1"
          class="w-full"
        />
        <div class="text-sm mt-1">{{ cardsPerRow }} cards per row</div>
      </div>

      <!-- Missing Filter Toggle -->
      <div class="filter-section flex items-center">
        <label class="flex items-center relative">
          <span class="mr-2 text-sm font-medium">Show Missing Cards</span>
          <div class="toggle-slot">
            <div class="toggle-button"></div>
            <input
              type="checkbox"
              v-model="filters.missing"
              class="toggle-checkbox"
            />
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
.toggle-checkbox {
  position: absolute;
  top: 0;
  left: 0;
  width: 40px;
  height: 20px;
  opacity: 0;
  cursor: pointer;
  margin: 0;
  padding: 0;
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
.toggle-checkbox:checked + .toggle-button {
  transform: translateX(20px);
}
.toggle-checkbox:checked ~ .toggle-slot {
  background-color: #4299e1;
}

input[type="range"]::-webkit-slider-thumb {
  background: #4299e1;
}
input[type="range"]::-moz-range-thumb {
  background: #4299e1;
}
</style>
