<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const router = useRouter()

// State for Dashboard Numbers
const stats = ref({
  patients: 0,
  appointments: 0,
  doctors: 0,
  departments: 0
})

const isLoading = ref(true)

// Quick Access Items
const quickAccess = [
  { title: 'Staff Management', desc: 'Manage doctors & nurses', icon: 'bi-person-badge-fill', color: 'text-warning', bg: 'bg-warning-subtle', route: '/staff' },
  { title: 'Departments', desc: 'Organize hospital resources', icon: 'bi-building-fill', color: 'text-info', bg: 'bg-info-subtle', route: '/departments' },
  { title: 'Appointments', desc: 'Schedule & manage visits', icon: 'bi-calendar-check-fill', color: 'text-success', bg: 'bg-success-subtle', route: '/appointmentsview' },
  { title: 'Medical Records', desc: 'Access patient history securely', icon: 'bi-file-earmark-medical-fill', color: 'text-danger', bg: 'bg-danger-subtle', route: '/medical-records' },
  { title: 'Reports & Analytics', desc: 'View hospital performance', icon: 'bi-graph-up-arrow', color: 'text-secondary', bg: 'bg-secondary-subtle', route: '/admindashboard' },
]

const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

// --- FETCH REAL STATS ---
const fetchStats = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/stats', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) {
      stats.value = await response.json()
    }
  } catch (error) {
    console.error("Error loading stats:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
})

const navigateTo = (path) => {
  router.push(path)
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5">
      <AdminNavBar />
      
      <div class="container pb-5 mb-5">
        <div class="row pt-4">
          <div class="col-md-8 text-white">
            <span class="badge bg-white text-primary mb-2">{{ today }}</span>
            <h1 class="display-5 fw-bold">Welcome, Admin!</h1>
            <p class="lead opacity-75">Manage your hospital operations efficiently.</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-n5">
      
      <div class="row g-4 mb-5">
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-primary">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Total Patients</h6>
                <h3 class="fw-bold mb-0">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                  <span v-else>{{ stats.patients }}</span>
                </h3>
              </div>
              <div class="icon-box bg-primary-subtle text-primary"><i class="bi bi-people-fill fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-success">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Appointments</h6>
                <h3 class="fw-bold mb-0">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                  <span v-else>{{ stats.appointments }}</span>
                </h3>
              </div>
              <div class="icon-box bg-success-subtle text-success"><i class="bi bi-calendar-check fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-purple">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Medical Staff</h6>
                <h3 class="fw-bold mb-0">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                  <span v-else>{{ stats.doctors }}</span>
                </h3>
              </div>
              <div class="icon-box bg-purple-subtle text-purple"><i class="bi bi-person-badge fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-warning">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Departments</h6>
                <h3 class="fw-bold mb-0">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                  <span v-else>{{ stats.departments }}</span>
                </h3>
              </div>
              <div class="icon-box bg-warning-subtle text-warning"><i class="bi bi-building fs-4"></i></div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <h4 class="fw-bold mb-4">Quick Access</h4>
          
          <div class="row g-4">
            <div v-for="(item, index) in quickAccess" :key="index" class="col-md-6 col-lg-3">
              <div @click="navigateTo(item.route)" class="card border-0 shadow-sm h-100 hover-card text-center py-4">
                <div class="card-body">
                  <div class="mb-3 rounded-circle d-inline-flex align-items-center justify-content-center" 
                       :class="item.bg" 
                       style="width: 60px; height: 60px;">
                    <i :class="['bi fs-4', item.icon, item.color]"></i>
                  </div>
                  <h5 class="fw-bold text-dark mt-2">{{ item.title }}</h5>
                  <p class="text-muted mb-0 small">{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
      
      <div class="pb-5"></div>

    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #022032 0%, #265790 100%); }
.mt-n5 { margin-top: -80px; }
.icon-box { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.hover-card { transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.hover-card:hover { transform: translateY(-5px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
.border-purple { border-color: #6f42c1 !important; }
.text-purple { color: #6f42c1 !important; }
.bg-purple-subtle { background-color: #e2d9f3 !important; }
</style>