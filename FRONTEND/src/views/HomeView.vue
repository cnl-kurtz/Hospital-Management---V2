<script setup>
import NavBar from '../components/NavBar.vue'
import Hero from '../components/Hero.vue'
</script>

<template>
  <div class="home">
    <Hero>
      <template #navbar>
        <NavBar />
      </template>
    </Hero>
  </div>
</template>