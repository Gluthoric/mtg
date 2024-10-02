<template>
  <div id="app" class="flex flex-col min-h-screen bg-theme-dark-300 text-white">
    <Header />
    <main class="flex-1 overflow-x-hidden overflow-y-auto p-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import Header from "./components/Header.vue";

export default defineComponent({
  name: "App",
  components: {
    Header,
  },
});
</script>

<style>
#app {
  font-family: Arial, sans-serif;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--theme-dark-300);
  color: white;
}
</style>
