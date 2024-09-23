<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/collection">Collection</router-link>
      <router-link to="/kiosk">Kiosk</router-link>
      <router-link to="/sets">Sets</router-link>
      <router-link to="/import">Import</router-link>
    </nav>
    <router-view/>
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