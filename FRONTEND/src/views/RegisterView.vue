<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
// Removed BackButton import to use a simple HTML button instead

const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')

const form = ref({
  name: '',
  username: '',
  email: '',
  dob: '',
  phone: '',
  password: ''
})

const handleRegister = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('http://127.0.0.1:5000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed')
    }

    alert('Account created successfully! Please log in.')
    router.push('/login')

  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="brand-gradient min-vh-100 d-flex align-items-center justify-content-center position-relative py-5"> 
    
    <button 
      @click="$router.push('/')" 
      class="btn btn-link text-white text-decoration-none position-absolute top-0 start-0 m-4 fw-bold opacity-75"
      style="z-index: 10;"
    >
      <i class="bi bi-arrow-left me-1"></i> Back
    </button>

    <div class="container">
      <div class="row justify-content-center">
        
        <div class="col-12 col-md-8 col-lg-6 col-xl-6">
          
          <div class="card border-0 shadow-lg rounded-4 p-4 p-md-5">
            
            <div class="text-center mb-3">
              <div class="d-inline-flex align-items-center gap-2 mb-2">
                <span class="bg-primary text-white rounded px-2 py-1 fw-bold">H+</span>
                <span class="h5 mb-0 text-dark fw-bold">HealthCare</span>
              </div>
              <h2 class="fw-bold text-dark fs-3">Create Account</h2>
              <p class="text-muted small">Join us to manage your medical records.</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center small py-2" role="alert">
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              <div>{{ errorMessage }}</div>
            </div>
            
            <form @submit.prevent="handleRegister">
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg bg-light fs-6" 
                    v-model="form.name" 
                    placeholder="John Doe" 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">Username</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg bg-light fs-6" 
                    v-model="form.username" 
                    placeholder="johndoe123" 
                    required
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">Email Address</label>
                <input 
                  type="email" 
                  class="form-control form-control-lg bg-light fs-6" 
                  v-model="form.email" 
                  placeholder="name@example.com" 
                  required
                >
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">Phone</label>
                  <input 
                    type="tel" 
                    class="form-control form-control-lg bg-light fs-6" 
                    v-model="form.phone" 
                    placeholder="+91..." 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">Date of Birth</label>
                  <input 
                    type="date" 
                    class="form-control form-control-lg bg-light fs-6" 
                    v-model="form.dob" 
                    required
                  >
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small text-muted fw-bold">Password</label>
                <input 
                  type="password" 
                  class="form-control form-control-lg bg-light fs-6" 
                  v-model="form.password" 
                  placeholder="******" 
                  required
                >
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 fw-bold rounded-pill" :disabled="isLoading">
                {{ isLoading ? 'Creating Account...' : 'Sign Up' }}
              </button>

              <div class="text-center mt-3">
                <p class="text-muted small mb-0">
                  Already have an account? 
                  <router-link to="/login" class="text-primary text-decoration-none fw-bold">Log in</router-link>
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
/* Exact match to LoginView gradient */
.brand-gradient {
  background: linear-gradient(90deg, #022032 0%, #265790 100%);
}

/* Consistent Input Styling */
.form-control {
  border: 1px solid #e2e8f0;
}

.form-control:focus {
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1);
  border-color: #0d6efd;
  background-color: #fff;
}

/* Primary Button Hover Effects */
.btn-primary {
  background-color: #0d6efd;
  border: none;
  transition: transform 0.3s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
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