<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/') 
}
</script>

<template>
  <button @click="goHome" class="img-back-btn" title="Back to Home">
    <img src="/back-arrow.png" alt="Back" width="32" height="32">
  </button>
</template>

<style scoped>
.img-back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  
  /* Reset default button styles */
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  
  /* Simple hover effect */
  transition: opacity 0.2s;
}

.img-back-btn:hover {
  opacity: 0.7;
}
</style>