<template>
  <aside :class="['sidebar bg-secondary text-white overflow-y-auto', { 'w-64': isOpen, 'w-16': !isOpen }]">
    <div class="logo p-4 flex items-center justify-between">
      <span v-if="isOpen" class="font-bold text-xl truncate">MTG Collection</span>
      <button @click="toggleSidebar" class="text-white focus:outline-none" aria-label="Toggle Sidebar">
        <MenuIcon v-if="!isOpen" class="h-6 w-6" />
        <XIcon v-else class="h-6 w-6" />
      </button>
    </div>
    <nav class="mt-4">
      <SidebarLink to="/" icon="HomeIcon">Home</SidebarLink>
      <SidebarLink to="/collection" icon="CollectionIcon">Collection</SidebarLink>
      
      <!-- Dropdown for Sets -->
      <Menu as="div" class="relative">
        <div>
          <Menu.Button class="flex items-center w-full px-4 py-2 text-gray-light hover:text-white focus:outline-none">
            <TableCellsIcon class="w-5 h-5 mr-2" />
            <span v-if="isOpen">Sets</span>
            <ChevronDownIcon v-if="isOpen" class="w-4 h-4 ml-1" />
          </Menu.Button>
        </div>

        <Transition
          enter="transition ease-out duration-200"
          enter-from="transform opacity-0 scale-95"
          enter-to="transform opacity-100 scale-100"
          leave="transition ease-in duration-150"
          leave-from="transform opacity-100 scale-100"
          leave-to="transform opacity-0 scale-95"
        >
          <Menu.Items class="absolute left-full top-0 mt-0 ml-2 w-48 origin-top-left bg-secondary border border-gray-700 rounded-md shadow-lg focus:outline-none z-50">
            <div class="py-1">
              <Menu.Item>
                {({ active }) => (
                  <router-link
                    to="/sets"
                    :class="[
                      active ? 'bg-primary text-white' : 'text-gray-light',
                      'block px-4 py-2 text-sm flex items-center'
                    ]"
                  >
                    <ViewGridIcon class="w-5 h-5 mr-2" />
                    All Sets
                  </router-link>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <router-link
                    to="/sets/special"
                    class={`${
                      active ? 'bg-primary text-white' : 'text-gray-light'
                    } block px-4 py-2 text-sm flex items-center`}
                  >
                    <StarIcon class="w-5 h-5 mr-2" />
                    Special Sets
                  </router-link>
                )}
              </Menu.Item>
            </div>
          </Menu.Items>
        </Transition>
      </Menu>
      
      <SidebarLink to="/kiosk" icon="DesktopComputerIcon">Kiosk</SidebarLink>
      <SidebarLink to="/import" icon="UploadIcon">Import</SidebarLink>
    </nav>

    <Transition name="fade">
      <div v-if="isOpen" class="filters mt-4 p-4">
        <component
          :is="currentFilterComponent"
          v-bind="currentFilterProps"
          @update-filters="handleUpdateFilters"
          @update-sorting="handleUpdateSorting"
          @update-per-page="handleUpdatePerPage"
          @update-cards-per-row="handleUpdateCardsPerRow"
        />
      </div>
    </Transition>
  </aside>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Menu, Transition } from '@headlessui/vue'
import { 
  MenuIcon, 
  XIcon, 
  TableCellsIcon, 
  ViewGridIcon, 
  StarIcon, 
  HomeIcon, 
  CollectionIcon, 
  DesktopComputerIcon, 
  UploadIcon,
  ChevronDownIcon
} from '@heroicons/vue/outline'
import SidebarLink from './SidebarLink.vue'
import SetListControls from './SetListControls.vue'
import CardListControls from './CardListControls.vue'

export default {
  name: 'Sidebar',
  components: {
    Menu,
    Transition,
    MenuIcon,
    XIcon,
    TableCellsIcon,
    ViewGridIcon,
    StarIcon,
    HomeIcon,
    CollectionIcon,
    DesktopComputerIcon,
    UploadIcon,
    ChevronDownIcon,
    SidebarLink,
    SetListControls,
    CardListControls
  },
  setup() {
    const isOpen = ref(true)
    const route = useRoute()

    const toggleSidebar = () => {
      isOpen.value = !isOpen.value
    }

    const currentPath = computed(() => route.path)

    const currentFilterComponent = computed(() => {
      if (['/collection', '/sets'].includes(currentPath.value)) {
        return SetListControls
      } else if (['/collection/sets', '/kiosk/sets'].some(path => currentPath.value.startsWith(path))) {
        return CardListControls
      }
      return null
    })

    const currentFilterProps = computed(() => {
      if (currentFilterComponent.value === SetListControls) {
        return {
          setTypes: ['core', 'expansion', 'masters', 'draft_innovation', 'commander', 'starter', 'box', 'promo', 'token', 'memorabilia'],
          totalPages: 1
        }
      } else if (currentFilterComponent.value === CardListControls) {
        return {
          filters: {
            name: '',
            rarities: [],
            colors: [],
            missing: false,
            types: [],
            keyword: ''
          },
          cardsPerRow: 6
        }
      }
      return {}
    })

    const handleUpdateFilters = (newFilters) => {
      // Emit event to parent component
    }

    const handleUpdateSorting = (newSorting) => {
      // Emit event to parent component
    }

    const handleUpdatePerPage = (newPerPage) => {
      // Emit event to parent component
    }

    const handleUpdateCardsPerRow = (newCardsPerRow) => {
      // Emit event to parent component
    }

    return {
      isOpen,
      toggleSidebar,
      currentFilterComponent,
      currentFilterProps,
      handleUpdateFilters,
      handleUpdateSorting,
      handleUpdatePerPage,
      handleUpdateCardsPerRow
    }
  }
}
</script>

<style scoped>
.sidebar {
  transition: width 0.3s ease;
  height: 100vh;
  overflow-y: auto;
}

.logo {
  background-color: var(--primary-color);
}

.filters {
  background-color: var(--secondary-color);
  border-top: 1px solid var(--border-color);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    z-index: 50;
    top: 0;
    left: 0;
    bottom: 0;
  }
}

@media (max-width: 640px) {
  .sidebar {
    width: 100%;
  }
}
</style>
