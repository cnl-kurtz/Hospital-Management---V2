<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import PatientNavBar from '../../components/PatientNavBar.vue'

const router = useRouter()
const userName = ref('Patient')

// --- STATE ---
const departments = ref([]) 
const allAppointments = ref([]) 
const isLoading = ref(true)

// Removed: showDeptModal, selectedDept (No longer needed)
const showHistoryModal = ref(false)
const showDetailsModal = ref(false)
const selectedAppt = ref(null)

// --- COMPUTED LISTS ---
const upcomingAppts = computed(() => {
  return allAppointments.value.filter(a => a.status === 'Scheduled')
})

const pastAppts = computed(() => {
  let list = allAppointments.value.filter(a => a.status !== 'Scheduled')
  return list.sort((a, b) => {
    if (a.status === 'Completed' && b.status !== 'Completed') return -1
    if (a.status !== 'Completed' && b.status === 'Completed') return 1
    return b.id - a.id
  })
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const options = { month: 'short', day: 'numeric', year: 'numeric' }
  return new Date(dateStr).toLocaleDateString('en-US', options)
}

// --- FETCH DATA ---
const loadDashboard = async () => {
  try {
    const token = localStorage.getItem('token')
    
    // Fetch Departments (Real Data from DB)
    const deptRes = await fetch('http://127.0.0.1:5000/api/departments')
    departments.value = await deptRes.json()

    // Fetch Appointments
    const apptRes = await fetch('http://127.0.0.1:5000/api/my_appointments', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (apptRes.ok) {
      allAppointments.value = await apptRes.json()
    }

  } catch (error) { console.error(error) } 
  finally { isLoading.value = false }
}

onMounted(() => {
  const storedName = localStorage.getItem('name')
  if (storedName) userName.value = storedName.split(' ')[0] 
  loadDashboard()
})

// --- ACTIONS ---
const openDepartment = (dept) => {
  router.push({ 
    name: 'view-doctors', 
    query: { dept: dept.name },
    state: { deptDescription: dept.desc } 
  })
}

const cancelAppointment = async (id) => {
  if(!confirm("Are you sure you want to cancel this appointment?")) return
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/cancel_appointment/${id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (!response.ok) throw new Error("Failed to cancel")
    alert("Appointment Cancelled.")
    loadDashboard() 
  } catch (error) { alert(error.message) }
}

const openDetails = (appt) => {
  selectedAppt.value = appt
  showDetailsModal.value = true
}

const requestDiagnosisEmail = (appt) => {
  alert(`Diagnosis for visit on ${appt.date} has been requested.`)
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5">
      <PatientNavBar />
      <div class="container pt-4 pb-5">
        <h1 class="display-5 fw-bold text-white">Hello, {{ userName }}!</h1>
        <p class="lead text-white-50">Manage your appointments and medical history.</p>
      </div>
    </div>

    <div class="container mt-n5">
      <div class="row g-4">
        
        <div class="col-lg-8">
          <h5 class="fw-bold mb-3 text-white">Explore Departments</h5>
          <div v-if="isLoading" class="text-center py-5 card border-0 shadow-sm rounded-2">
            <div class="spinner-border text-primary mx-auto" role="status"></div>
            <p class="text-muted mt-2">Loading...</p>
          </div>
          <div v-else class="row g-3">
            <div v-for="dept in departments" :key="dept.id" class="col-md-6">
              <div class="card border-0 shadow-sm h-100 hover-card cursor-pointer rounded-2" @click="openDepartment(dept)">
                <div class="card-body d-flex align-items-center gap-3 p-4">
                  <div class="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center flex-shrink-0" style="width: 60px; height: 60px;">
                    <i :class="['bi fs-3', dept.icon || 'bi-hospital']"></i>
                  </div>
                  <div>
                    <h5 class="fw-bold mb-1 text-dark">{{ dept.name }}</h5>
                    <small class="text-muted">View Doctors & Services</small>
                  </div>
                  <i class="bi bi-arrow-right ms-auto text-primary"></i>
                </div>
              </div>
            </div>
             <div v-if="departments.length === 0" class="col-12 text-center text-white-50">
               No departments found.
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <h5 class="fw-bold mb-3 text-white">Your Upcoming Visits</h5>
          <div class="card border-0 shadow-sm mb-4 rounded-4">
            <div class="card-body p-0">
              <div v-if="upcomingAppts.length === 0" class="p-4 text-center text-muted">No upcoming appointments.</div>
              <div v-else class="list-group list-group-flush rounded-2 overflow-hidden">
                <div v-for="appt in upcomingAppts" :key="appt.id" class="list-group-item border-0 p-3">
                  <div class="d-flex w-100 justify-content-between align-items-center mb-2">
                    <h6 class="mb-0 fw-bold text-primary">{{ appt.doctor }}</h6>
                    <small class="text-muted fw-bold">{{ formatDate(appt.date) }}</small>
                  </div>
                  <div class="mb-3">
                    <span class="badge bg-info text-dark border rounded-pill">{{ appt.dept }}</span>
                    <span class="small text-muted ms-2"><i class="bi bi-clock me-1"></i>{{ appt.time }}</span>
                  </div>
                  <button @click="cancelAppointment(appt.id)" class="btn btn-sm btn-light text-muted w-100 hover-danger rounded-pill fw-bold" style="font-size: 0.85rem;">
                    Cancel Appointment
                  </button>
                </div>
              </div>
            </div>
          </div>

          <h5 class="fw-bold mb-3 text-secondary">Recent History</h5>
          <div class="card border-0 shadow-sm rounded-2">
            <div class="card-body p-0">
              <div class="list-group list-group-flush rounded-2 overflow-hidden">
                <div v-for="appt in pastAppts.slice(0, 3)" :key="appt.id" class="list-group-item border-0 p-3 cursor-pointer list-group-item-action" @click="openDetails(appt)">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-0 fw-bold text-dark">{{ appt.doctor }}</h6>
                      <small class="text-muted">{{ formatDate(appt.date) }}</small>
                    </div>
                    <span class="badge rounded-pill" :class="appt.status === 'Completed' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">{{ appt.status }}</span>
                  </div>
                  <div v-if="appt.status === 'Completed'" class="mt-2">
                    <button @click.stop="requestDiagnosisEmail(appt)" class="btn btn-sm btn-light text-primary fw-bold w-100 rounded-pill">
                      <i class="bi bi-envelope-paper me-2"></i>Email Diagnosis
                    </button>
                  </div>
                </div>
              </div>
              <div class="p-2 border-top">
                <button @click="showHistoryModal = true" class="btn btn-link text-decoration-none w-100 fw-bold small">View All Past Appointments</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div v-if="showDetailsModal && selectedAppt" class="modal-backdrop-custom d-flex align-items-center justify-content-center" style="z-index: 1100;">
      <div class="modal-content-custom bg-white rounded-2 shadow-lg p-4" style="max-width: 500px; width: 90%;">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Visit Details</h5>
          <button @click="showDetailsModal = false" class="btn-close"></button>
        </div>
        <div class="mb-3"><label class="small text-muted fw-bold">Doctor</label><div class="fw-bold fs-5">{{ selectedAppt.doctor }}</div></div>
        <div class="row mb-3">
           <div class="col-6"><label class="small text-muted fw-bold">Date</label><div>{{ formatDate(selectedAppt.date) }}</div></div>
           <div class="col-6"><label class="small text-muted fw-bold">Status</label><div><span class="badge rounded-pill" :class="selectedAppt.status === 'Completed' ? 'bg-success' : 'bg-danger'">{{ selectedAppt.status }}</span></div></div>
        </div>
        <div class="mb-4 bg-light p-3 rounded-2"><label class="small text-muted fw-bold d-block mb-1">Remarks / Notes</label><p class="mb-0 text-dark">{{ selectedAppt.remarks || 'No additional remarks provided.' }}</p></div>
        <div class="d-grid"><button @click="showDetailsModal = false" class="btn btn-primary fw-bold rounded-pill">Close</button></div>
      </div>
    </div>
    
    <div v-if="showHistoryModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded-2 shadow-lg p-0 overflow-hidden" style="max-width: 600px; width: 90%; max-height: 80vh;">
        <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-light"><h5 class="fw-bold mb-0 m-0">Appointment History</h5><button @click="showHistoryModal = false" class="btn-close"></button></div>
        <div class="overflow-auto p-0" style="max-height: 60vh;">
          <div class="list-group list-group-flush">
            <div v-for="appt in pastAppts" :key="appt.id" class="list-group-item p-3 list-group-item-action cursor-pointer" @click="openDetails(appt)">
              <div class="d-flex justify-content-between align-items-center mb-2"><div><h6 class="mb-0 fw-bold">{{ appt.doctor }}</h6><small class="text-muted">{{ formatDate(appt.date) }}</small></div><span class="badge rounded-pill" :class="appt.status === 'Completed' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">{{ appt.status }}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #022032 0%, #265790 100%); }
.mt-n5 { margin-top: -80px; }
.cursor-pointer { cursor: pointer; }
.hover-card:hover { transform: translateY(-3px); transition: all 0.2s; box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1050; }
.modal-content-custom { position: relative; z-index: 1060; }
.hover-danger:hover { background-color: #dc3545 !important; color: white !important; transition: all 0.2s ease; }
</style>