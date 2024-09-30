<template>
  <div id="app" class="bg-dark-300 min-h-screen">
    <nav class="bg-dark-200 p-4">
      <div class="container mx-auto flex justify-center space-x-4">
        <router-link to="/" class="text-white hover:text-primary">Home</router-link>
        <router-link to="/collection" class="text-white hover:text-primary">Collection</router-link>
        <router-link to="/kiosk" class="text-white hover:text-primary">Kiosk</router-link>
        <router-link to="/sets" class="text-white hover:text-primary">Sets</router-link>
        <router-link to="/import" class="text-white hover:text-primary">Import</router-link>
      </div>
    </nav>
    <router-view class="container mx-auto p-4"/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Styles are now handled in main.css */
</style>
