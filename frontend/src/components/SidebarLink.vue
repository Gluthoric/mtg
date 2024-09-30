<template>
  <router-link
    :to="to"
    class="flex items-center py-2.5 px-4 rounded transition duration-200 hover:bg-primary hover:text-white"
    :class="{ 'bg-primary text-white font-semibold': isActive }"
  >
    <component :is="icon" class="h-5 w-5 mr-2" />
    <span v-if="$parent.isOpen">
      <slot></slot>
    </span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  to: { type: [String, Object], required: true },
  icon: { type: String, required: true }
})

const route = useRoute()
const isActive = computed(() => {
  if (typeof props.to === 'string') {
    return route.path === props.to
  }
  return route.path === props.to.path
})
</script>
