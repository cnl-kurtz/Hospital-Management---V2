<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const identifier = ref('') 
const password = ref('')
const rememberMe = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: identifier.value, password: password.value })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Login failed')
    }

    localStorage.setItem('token', data.token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('username', data.username)
    localStorage.setItem('name', data.name)

    if (data.role === 'admin') router.push('/admindashboard')
    else if (data.role === 'doctor') router.push('/doctor-dashboard')
    else router.push('/patient-dashboard')

  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="brand-gradient min-vh-100 d-flex align-items-center justify-content-center position-relative"> 
    
    <button 
      @click="$router.push('/')" 
      class="btn btn-link text-white text-decoration-none position-absolute top-0 start-0 m-4 fw-bold opacity-75"
      style="z-index: 10;"
    >
      <i class="bi bi-arrow-left me-1"></i> Back
    </button>

    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-md-6 col-lg-5 col-xl-5">
          
          <div class="card border-0 shadow-lg rounded-4 p-4 p-md-5">
            
            <div class="text-center mb-4">
              <div class="d-inline-flex align-items-center gap-2 mb-3">
                <span class="bg-primary text-white rounded px-2 py-1 fw-bold">H+</span>
                <span class="h5 mb-0 text-dark fw-bold">HealthCare</span>
              </div>
              <h2 class="fw-bold text-dark">Welcome Back</h2>
              <p class="text-muted small">Please enter your details to sign in.</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center small py-2" role="alert">
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              <div>{{ errorMessage }}</div>
            </div>

            <form @submit.prevent="handleLogin">
              
              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">Email or Username</label>
                <input 
                  type="text" 
                  class="form-control form-control-lg bg-light fs-6" 
                  v-model="identifier" 
                  placeholder="name@example.com"
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">Password</label>
                <input 
                  type="password" 
                  class="form-control form-control-lg bg-light fs-6" 
                  v-model="password" 
                  placeholder="••••••••"
                  required
                >
              </div>

              <div class="d-flex justify-content-between align-items-center mb-4">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="rememberMe" v-model="rememberMe">
                  <label class="form-check-label text-muted small" for="rememberMe">
                    Remember me
                  </label>
                </div>
                <a href="#" class="text-decoration-none small text-primary fw-bold">Forgot password?</a>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 fw-bold rounded-pill" :disabled="isLoading">
                {{ isLoading ? 'Signing In...' : 'Sign In' }}
              </button>

              <div class="text-center mt-4">
                <p class="text-muted small mb-0">
                  Don't have an account? 
                  <router-link to="/register" class="text-primary text-decoration-none fw-bold">Sign Up</router-link>
                </p>
              </div>

            </form>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.brand-gradient {
  background: linear-gradient(70deg, #022032 0%, #265790 100%);
}

.form-control {
  border: 1px solid #e2e8f0; /* Very subtle border */
}

.form-control:focus {
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1); /* Soft glow instead of harsh outline */
  border-color: #0d6efd;
  background-color: #fff;
}

.btn-primary {
  background-color: #0d6efd; /* Bootstrap Primary Blue */
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px); /* Subtle lift effect */
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}

.card {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>