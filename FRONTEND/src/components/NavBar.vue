<script setup>
// No script logic needed for now
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent px-4 py-3">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold d-flex align-items-center gap-2" href="#">
        <span class="bg-white text-primary rounded px-2 py-0 fw-bolder">H+</span>
        HealthCare
      </a>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav gap-3">
          <li class="nav-item">
            <router-link class="nav-link active fw-bold" to="/">Home</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#">About</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#">Contact</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* Removed the custom gradient class, Bootstrap handles the rest */
.nav-link {
  color: rgba(255, 255, 255, 0.85) !important;
}
.nav-link:hover, .nav-link.active {
  color: #fff !important;
}
</style>