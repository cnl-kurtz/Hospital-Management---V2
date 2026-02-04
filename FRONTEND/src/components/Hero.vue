<script setup>
import { ref, onMounted } from 'vue'

const isLoggedIn = ref(false)
const userRole = ref('')
const userName = ref('')

onMounted(() => {
  // Check if token exists
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    userRole.value = localStorage.getItem('role')
    userName.value = localStorage.getItem('username')
  }
})

// Helper to determine where the dashboard button points
const getDashboardLink = () => {
  if (userRole.value === 'admin') return '/dashboard'
  if (userRole.value === 'doctor') return '/doctor-dashboard'
  return '/patient-dashboard'
}

// Logic to clear session and refresh UI
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('username')
  window.location.reload() // Reloads page to show "Get Started" state
}
</script>

<template>
  <div>
    <div class="header-section text-white">
      <slot name="navbar"></slot> 
      
      <div class="container pt-5 pb-5 mb-5 text-center">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <h1 class="display-4 fw-bold mb-3">Manage HealthCare Effortlessly</h1>
            <p class="lead opacity-75 mb-5">Welcome to H+ HealthCare. The modern, secure way to manage medical records, appointments, and hospital staff.</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="row g-0 font-poppins">
              
              <div class="col-md-7 p-5 d-flex flex-column justify-content-center bg-white">
                
                <div v-if="isLoggedIn">
                   <h3 class="fw-bold text-primary mb-4">Welcome back, {{ userName }}!</h3>
                   <p class="text-muted mb-5">You are currently signed in as a <strong>{{ userRole }}</strong>. Continue to your dashboard to manage your account.</p>
                   <div class="d-flex gap-2 align-items-center">
                      <router-link :to="getDashboardLink()" class="btn btn-primary btn-lg rounded-pill px-5 fw-bold">
                        Go to Dashboard <i class="bi bi-arrow-right ms-2"></i>
                      </router-link>
                      
                      <button @click="handleLogout" class="btn btn-outline-danger btn-lg rounded-pill px-4 fw-bold ms-2">
                        Logout
                      </button>
                   </div>
                </div>

                <div v-else>
                  <h3 class="fw-bold text-primary mb-4">Get Started Today</h3>
                  <p class="text-muted mb-5">Are you a patient looking to book an appointment? Please sign in or create an account to continue.</p>
                  <div class="d-flex gap-3 flex-wrap">
                    <router-link to="/login" class="btn btn-cstmbtn btn-lg rounded-pill px-5 fw-bold d-flex align-items-center gap-2">
                      <i class="bi bi-box-arrow-in-right"></i> Login
                    </router-link>
                    <router-link to="/register" class="btn btn-outline-primary btn-lg rounded-pill px-5 fw-bold d-flex align-items-center gap-2">
                      <i class="bi bi-person-plus"></i> Register
                    </router-link>
                  </div>
                </div>

              </div>

              <div class="col-md-5 bg-primary-subtle d-none d-md-flex align-items-center justify-content-center p-5">
                 <div class="text-center text-primary opacity-50">
                   <i class="bi bi-hospital display-1"></i>
                   <h5 class="fw-bold mt-3">H+ HealthCare</h5>
                 </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* The same gradient used in all dashboards */
.header-section {
  background: linear-gradient(90deg, #022032 0%, #265790 100%);
  padding-bottom: 70px; /* Extra padding for the overlap */
}

/* Pulls the card up to overlap the header */
.mt-n5 {
  margin-top: -150px;
}

.rounded-4 {
  border-radius: 1rem !important;
}

.btn-cstmbtn { background-color: #2c629e; color: #fff; }
.btn-cstmbtn:hover { background-color: #649ad1; color: #fff; }
</style>