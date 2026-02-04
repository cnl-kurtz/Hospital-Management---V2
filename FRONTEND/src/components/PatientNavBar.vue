<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userName = ref('Patient')
const searchQuery = ref('')
const searchResults = ref(null)
const showResults = ref(false)
let debounceTimer = null

// --- SEARCH LOGIC ---
const handleSearch = () => {
  clearTimeout(debounceTimer)
  
  if (searchQuery.value.length < 2) {
    searchResults.value = null
    showResults.value = false
    return
  }

  debounceTimer = setTimeout(async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/patient/global_search?q=${searchQuery.value}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        searchResults.value = await response.json()
        showResults.value = true
      }
    } catch (error) {
      console.error("Search failed", error)
    }
  }, 300)
}

const closeSearch = () => {
  setTimeout(() => { showResults.value = false }, 200)
}

// --- NAVIGATION ---
const goToDoctor = (doc) => {
  // Navigate to the doctor's department so they appear in the list
  router.push({ name: 'view-doctors', query: { dept: doc.dept } })
  showResults.value = false
}

const goToDept = (deptName) => {
  router.push({ name: 'view-doctors', query: { dept: deptName } })
  showResults.value = false
}

onMounted(() => {
  const storedName = localStorage.getItem('name')
  if (storedName) userName.value = storedName
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent px-4 py-3">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold d-flex align-items-center gap-2" to="/patient-dashboard">
        <span class="bg-white text-primary rounded px-2 py-0 fw-bolder">H+</span>
        HealthCare <span class="badge bg-white text-primary ms-2 small" style="font-size: 0.7rem;">PATIENT</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#patNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="patNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-4 gap-3">
          <li class="nav-item">
            <router-link class="nav-link fw-bold" to="/patient-dashboard" active-class="active">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/patient-profile" active-class="fw-bold active">My Profile</router-link>
          </li>
        </ul>

        <div class="d-flex align-items-center gap-3 position-relative">
          
          <div class="d-none d-md-block position-relative">
            <div class="input-group">
              <span class="input-group-text bg-primary border-0 text-white"><i class="bi bi-search"></i></span>
              <input 
                type="text" 
                class="form-control bg-primary border-0 text-white placeholder-white" 
                placeholder="Search for Doctors..." 
                style="--bs-bg-opacity: .5; min-width: 250px;"
                v-model="searchQuery"
                @input="handleSearch"
                @blur="closeSearch"
                @focus="handleSearch"
                autocomplete="on"
              >
            </div>

            <div v-if="showResults && searchResults" class="dropdown-menu show shadow border-0 p-0 mt-2 w-100" style="position: absolute; top: 100%; left: 0;">
              
              <div v-if="searchResults.doctors?.length > 0">
                <h6 class="dropdown-header text-uppercase small fw-bold bg-light py-2">Doctors</h6>
                <a v-for="doc in searchResults.doctors" :key="doc.id" href="#" class="dropdown-item d-flex justify-content-between" @click.prevent="goToDoctor(doc)">
                  <span>{{ doc.name }}</span>
                  <small class="text-muted">{{ doc.dept }}</small>
                </a>
              </div>

              <div v-if="searchResults.departments?.length > 0">
                <h6 class="dropdown-header text-uppercase small fw-bold bg-light py-2">Departments</h6>
                <a v-for="dept in searchResults.departments" :key="dept.id" href="#" class="dropdown-item" @click.prevent="goToDept(dept.name)">
                  {{ dept.name }}
                </a>
              </div>

              <div v-if="!searchResults.doctors?.length && !searchResults.departments?.length" class="p-3 text-center text-muted small">
                No doctors found.
              </div>
            </div>
          </div>

          <div class="vr text-white opacity-50 mx-2"></div>

          <div class="dropdown">
            <a class="nav-link dropdown-toggle text-white d-flex align-items-center gap-2" href="#" role="button" data-bs-toggle="dropdown">
              <div class="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <i class="bi bi-person-fill"></i>
              </div>
              <span class="d-none d-md-block text-white small">{{ userName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow border-0">
              <li><router-link class="dropdown-item" to="/patient-profile">Profile</router-link></li>
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
::placeholder { color: rgba(255, 255, 255, 0.7) !important; font-size: 14px; }
.router-link-active { color: white !important; opacity: 1 !important; }
.dropdown-menu { max-height: 400px; overflow-y: auto; }
</style>