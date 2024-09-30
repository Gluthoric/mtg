<template>
  <header class="bg-white dark:bg-theme-dark-200 p-4 flex items-center justify-between">
    <!-- Logo or Brand Name -->
    <div class="flex items-center">
      <router-link to="/" class="text-xl font-bold text-primary hover:text-black dark:hover:text-white">
        MTG Collection
      </router-link>
    </div>

    <!-- Navigation Links for Medium and Larger Screens -->
    <nav class="hidden md:flex space-x-6">
      <!-- ... (keep existing navigation links) ... -->

      <!-- Dark Mode Toggle Button -->
      <button @click="$emit('toggle-dark-mode')" class="text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white">
        <SunIcon v-if="isDarkMode" class="w-5 h-5" />
        <MoonIcon v-else class="w-5 h-5" />
      </button>
    </nav>

    <!-- Mobile Menu Button -->
    <div class="md:hidden">
      <!-- ... (keep existing mobile menu) ... -->
    </div>
  </header>
</template>

<script>
import { Menu, Transition } from '@headlessui/vue'
import { useRoute } from 'vue-router'
import { 
  HomeIcon, 
  CollectionIcon, 
  DesktopComputerIcon, 
  TableCellsIcon, 
  ChevronDownIcon, 
  ViewGridIcon, 
  StarIcon, 
  UploadIcon,
  MenuIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/outline'

export default {
  name: 'Header',
  components: { 
    Menu, 
    Transition, 
    HomeIcon, 
    CollectionIcon, 
    DesktopComputerIcon, 
    TableCellsIcon,
    ChevronDownIcon,
    ViewGridIcon,
    StarIcon,
    UploadIcon,
    MenuIcon,
    SunIcon,
    MoonIcon
  },
  props: {
    isDarkMode: {
      type: Boolean,
      required: true
    }
  },
  emits: ['toggle-dark-mode'],
  setup() {
    const route = useRoute()

    // Function to check if the route is active
    const isActive = (path) => route.path === path

    return { isActive }
  },
}
</script>

<style scoped>
/* ... (keep existing styles) ... */
</style>
