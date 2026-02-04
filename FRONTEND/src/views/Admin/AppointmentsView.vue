<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const router = useRouter()
const route = useRoute()

// State
const appointments = ref([])
const isLoading = ref(true)

// --- FETCH DATA ---
const fetchAppointments = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/appointments', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      appointments.value = await response.json()
    }
  } catch (error) {
    console.error("Error fetching appointments:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAppointments()
})

// --- LOGIC ---
const isHighlighted = (patientName) => {
  const query = route.query.search
  if (!query) return false
  return patientName.toLowerCase().includes(query.toLowerCase())
}

const getStatusClass = (status) => {
  switch (status) {
    case 'Completed': return 'bg-success text-white cursor-pointer hover-scale shadow-sm'
    case 'Upcoming': 
    case 'Scheduled': return 'bg-primary-subtle text-primary border border-primary-subtle'
    case 'Cancelled': return 'bg-danger-subtle text-danger border border-danger-subtle'
    default: return 'bg-secondary-subtle text-secondary'
  }
}

const handleStatusClick = (appt) => {
  if (appt.status === 'Completed') {
    router.push({ name: 'medical-records', query: { search: appt.patient } })
  }
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5"> <h2 class="fw-bold text-white mb-1">Appointments</h2>
        <p class="text-white-50 mb-0">Manage patient visits and scheduling</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else class="card border-0 shadow-sm">
        <div class="card-body p-5 pt-3 px-4">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="bg-light">
                <tr>
                  <th class="ps-4 py-3 text-secondary small">Patient Name</th>
                  <th class="py-3 text-secondary small">Doctor</th>
                  <th class="py-3 text-secondary small">Department</th>
                  <th class="py-3 text-secondary small">Date & Time</th>
                  <th class="pe-4 text-end text-secondary small">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="appt in appointments" 
                  :key="appt.id"
                  :class="isHighlighted(appt.patient) ? 'bg-warning-subtle' : ''"
                >
                  <td class="ps-4 fw-medium">
                    {{ appt.patient }}
                    <span v-if="isHighlighted(appt.patient)" class="badge bg-warning text-dark ms-2 small">
                      Result
                    </span>
                  </td>
                  <td>
                    <div class="d-flex align-items-center gap-2">
                      <div class="avatar-circle bg-light text-primary fw-bold">
                        {{ appt.doctor.charAt(4) || 'D' }}
                      </div>
                      <span class="small">{{ appt.doctor }}</span>
                    </div>
                  </td>
                  <td><span class="text-muted small">{{ appt.dept }}</span></td>
                  <td class="small">
                    <div class="fw-bold">{{ appt.date }}</div>
                    <div class="text-muted">{{ appt.time }}</div>
                  </td>
                  <td class="text-end pe-4">
                    <span 
                      class="badge rounded-pill px-3 py-2 fw-normal" 
                      :class="getStatusClass(appt.status)"
                      @click="handleStatusClick(appt)"
                      :title="appt.status === 'Completed' ? 'View Medical Record' : ''"
                    >
                      {{ appt.status }}
                      <i v-if="appt.status === 'Completed'" class="bi bi-arrow-right-short ms-1"></i>
                    </span>
                  </td>
                </tr>
                
                <tr v-if="appointments.length === 0">
                  <td colspan="5" class="text-center py-5 text-muted">
                    No appointments found in the system.
                  </td>
                </tr>

              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section {
  background: linear-gradient(90deg, #022032 0%, #265790 100%);
  padding-bottom: 4rem !important;
}

.mt-n5 { margin-top: -4rem !important; }

.avatar-circle {
  width: 30px; height: 30px; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; font-size: 0.8rem;
}
.cursor-pointer { cursor: pointer; }
.hover-scale { transition: transform 0.2s; }
.hover-scale:hover { transform: scale(1.05); }
.bg-warning-subtle { background-color: #fff3cd !important; }
</style>