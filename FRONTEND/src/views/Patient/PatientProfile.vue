<script setup>
import { ref, onMounted } from 'vue'
import PatientNavBar from '../../components/PatientNavBar.vue'

const profile = ref({
  name: '',
  username: '',
  email: '',
  phone: '',
  dob: '',
  password: '' 
})
const isLoading = ref(false)

// 1. Fetch Profile on Load
onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/patient/profile', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      const data = await response.json()
      profile.value = data
    }
  } catch (error) {
    console.error("Error fetching profile", error)
  }
})

// 2. Update Profile
const saveProfile = async () => {
  isLoading.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/api/patient/profile', {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(profile.value)
    })

    if (!response.ok) throw new Error("Failed to update")

    alert("Profile updated successfully!")
    localStorage.setItem('name', profile.value.name)
    
  } catch (error) {
    alert("Error updating profile")
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <PatientNavBar />
      <div class="container pt-3 pb-5"> <div class="d-flex align-items-center justify-content-between">
          <div>
            <h2 class="fw-bold text-white mb-1">Account Settings</h2>
            <p class="text-white-50 mb-0">Manage your personal information and security</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-n5 pb-5"> 
      <div class="row g-4">
        
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm text-center h-80">
            <div class="card-body p-4">
              <div class="mb-3 mx-auto bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold display-5 border border-4 border-white shadow-sm" 
                   style="width: 120px; height: 120px; margin-top: -60px; background-color: #e3f2fd;">
                {{ profile.name.charAt(0) || 'U' }}
              </div>
              
              <h5 class="fw-bold text-dark mb-1">{{ profile.name }}</h5>
              <p class="text-muted small mb-3">@{{ profile.username }}</p>
              
              <span class="badge bg-primary px-3 py-2 rounded-pill">Patient Account</span>

              <hr class="my-4 text-muted opacity-25">

              <div class="text-start px-2">
                <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">Contact Information</small>
                <div class="d-flex align-items-center mt-3">
                  <i class="bi bi-envelope text-primary me-3"></i>
                  <div class="text-truncate">{{ profile.email }}</div>
                </div>
                <div class="d-flex align-items-center mt-3">
                  <i class="bi bi-telephone text-primary me-3"></i>
                  <div>{{ profile.phone }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0 py-3 px-4">
              <h6 class="fw-bold text-dark mb-0">Edit Details</h6>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="saveProfile">
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Full Name</label>
                    <input type="text" class="form-control" v-model="profile.name" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Username</label>
                    <input type="text" class="form-control bg-light text-muted" v-model="profile.username" disabled>
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Date of Birth</label>
                    <input type="date" class="form-control" v-model="profile.dob" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Phone Number</label>
                    <input type="tel" class="form-control" v-model="profile.phone" required>
                  </div>
                </div>

                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Email Address</label>
                  <input type="email" class="form-control" v-model="profile.email" required>
                </div>

                <hr class="text-muted opacity-25 my-4">

                <div class="d-flex justify-content-end gap-2">
                  <button type="button" class="btn btn-light text-muted fw-bold" @click="$router.push('/patient-dashboard')">Cancel</button>
                  <button type="submit" class="btn btn-primary px-4 fw-bold shadow-sm" :disabled="isLoading">
                    {{ isLoading ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Matching the dashboard gradient exactly */
.header-section { 
  background: linear-gradient(90deg, #022032 0%, #265790 100%); 
}

/* Negative margin to pull the container up. 
   mt-n5 is a Bootstrap utility, but we can enforce it here if needed.
*/
.mt-n5 { margin-top: -3rem !important; }
</style>