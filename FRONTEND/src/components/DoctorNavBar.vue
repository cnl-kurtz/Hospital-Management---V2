<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const doctorName = ref('Doctor')

onMounted(() => {
  const storedName = localStorage.getItem('name')
  if (storedName) {
    doctorName.value = storedName
  }
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent px-4 py-3">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold d-flex align-items-center gap-2" to="/doctor-dashboard">
        <span class="bg-white text-primary rounded px-2 py-0 fw-bolder">H+</span>
        HealthCare <span class="badge bg-white text-primary ms-2 small" style="font-size: 0.7rem;">DOCTOR</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#docNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="docNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-4 gap-3">
          <li class="nav-item">
            <router-link class="nav-link fw-bold" to="/doctor-dashboard" active-class="active">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/doctor-patients" active-class="fw-bold active">Patients</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/doctor-profile" active-class="fw-bold active">My Profile</router-link>
          </li>
        </ul>

        <div class="d-flex align-items-center gap-3">
          <div class="dropdown">
            <a class="nav-link dropdown-toggle text-white d-flex align-items-center gap-2" href="#" role="button" data-bs-toggle="dropdown">
              <div class="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <i class="bi bi-person-fill"></i>
              </div>
              <span class="d-none d-md-block text-white small">{{ doctorName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow">
              <li><router-link class="dropdown-item" to="/doctor-profile">Profile</router-link></li>
              <li><hr class="dropdown-divider"></li>
              <li><button class="dropdown-item text-danger" @click="logout">Logout</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.router-link-active {
  color: white !important;
  opacity: 1 !important;
}
</style>