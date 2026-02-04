<script setup>
import { useRoute } from 'vue-router'
// REMOVED NavBar import
import AppFooter from './components/AppFooter.vue'
import { RouterView } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="d-flex flex-column min-vh-100">
    
    <main class="flex-grow-1">
      <RouterView />
    </main>
    
    <AppFooter v-if="!route.meta.hideNavbar" />
    
  </div>
</template>

<style>
/* Global styles remain */
</style>