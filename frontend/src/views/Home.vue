<template>
  <div class="bg-background text-foreground min-h-screen">
    <nav class="mb-4 flex justify-center space-x-4 p-4">
      <router-link v-for="link in navLinks" :key="link.to" :to="link.to" class="text-primary hover:underline">
        {{ link.text }}
      </router-link>
    </nav>
    <div class="px-4 md:px-6 lg:px-8">
      <h1 class="text-center mb-6 text-3xl font-bold text-primary">MTG Collection Kiosk</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link v-for="link in mainLinks" :key="link.to" :to="link.to" class="block">
          <div class="bg-card hover:bg-card-hover text-card-foreground rounded-lg shadow-md p-6 transition-all duration-300 ease-in-out transform hover:scale-105">
            <h2 class="text-xl font-semibold mb-2">{{ link.text }}</h2>
            <p class="text-muted-foreground">{{ link.description }}</p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
const navLinks = [
  { to: '/', text: 'Home' },
  { to: '/collection', text: 'Collection' },
  { to: '/kiosk', text: 'Kiosk' },
  { to: '/import', text: 'Import' }
];

const mainLinks = [
  { to: '/collection', text: 'My Collection', description: 'View and manage your MTG card collection' },
  { to: '/kiosk', text: 'Kiosk Mode', description: 'Quick card entry for new acquisitions' },
  { to: '/import', text: 'Import Cards', description: 'Import cards from various sources' }
];
</script>