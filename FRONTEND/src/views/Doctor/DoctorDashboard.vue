<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DoctorNavBar from '../../components/DoctorNavBar.vue'

const router = useRouter()

// --- STATE ---
const scheduledAppts = ref([]) 
const completedAppts = ref([])
const doctorName = ref('Doctor')
const doctorId = ref(null) 
const doctorTimings = ref('') // NEW: Store Timings
const doctorDays = ref('')    // NEW: Store Days
const isLoading = ref(true)

// Modal Logic
const showActionModal = ref(false)
const showDetailsModal = ref(false)
const modalActionType = ref('') 
const selectedAppt = ref(null)
const actionReason = ref('')

// Reschedule Logic
const rescheduleForm = ref({ date: '', slot: '' })
const dynamicSlots = ref([]) 
const isCheckingSlots = ref(false)
const minDate = new Date().toISOString().split('T')[0]

// --- 1. INITIAL FETCH ---
const fetchDashboardData = async () => {
  try {
    const token = localStorage.getItem('token')
    
    // 1. Fetch Profile to get Doctor Details
    const profileRes = await fetch('http://127.0.0.1:5000/api/doctor/profile', {
       headers: { 'Authorization': `Bearer ${token}` }
    })
    if (profileRes.ok) {
      const profile = await profileRes.json()
      doctorName.value = profile.name
      doctorId.value = profile.id
      
      // Store timings and days to display in header
      doctorTimings.value = profile.timings
      doctorDays.value = profile.days
    }

    // 2. Fetch Appointments
    const response = await fetch('http://127.0.0.1:5000/api/doctor/appointments', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      scheduledAppts.value = data.scheduled
      completedAppts.value = data.completed
    }
  } catch (error) {
    console.error("Error fetching data:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

// --- 2. WATCH RESCHEDULE DATE ---
watch(() => rescheduleForm.value.date, async (newDate) => {
  if (!newDate || modalActionType.value !== 'reschedule') return
  if (!doctorId.value) return 

  rescheduleForm.value.slot = ''
  isCheckingSlots.value = true
  dynamicSlots.value = []
  
  try {
    const response = await fetch('http://127.0.0.1:5000/api/appointments/available_slots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doctor_id: doctorId.value, date: newDate })
    })
    
    if (response.ok) {
      dynamicSlots.value = await response.json()
    }
  } catch (error) {
    console.error(error)
  } finally {
    isCheckingSlots.value = false
  }
})

// --- 3. ACTIONS ---

const handleComplete = (appt) => {
  router.push({ name: 'doctor-patients', query: { patient: appt.patient, appt_id: appt.id } })
}

const openActionModal = (type, appt) => {
  modalActionType.value = type
  selectedAppt.value = appt
  showActionModal.value = true
  if (type === 'reschedule') {
    rescheduleForm.value = { date: '', slot: '' }
    dynamicSlots.value = []
  }
  actionReason.value = ''
}

const confirmAction = async () => {
  const token = localStorage.getItem('token')
  
  // A. CANCEL LOGIC
  if (modalActionType.value === 'cancel') {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/doctor/cancel_appointment/${selectedAppt.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ reason: actionReason.value }) 
      })
      if (!response.ok) throw new Error("Failed to cancel")
      alert("Appointment Cancelled")
      scheduledAppts.value = scheduledAppts.value.filter(a => a.id !== selectedAppt.value.id)
    } catch (e) { alert(e.message) }

  // B. RESCHEDULE LOGIC
  } else if (modalActionType.value === 'reschedule') {
    if (!rescheduleForm.value.date || !rescheduleForm.value.slot) {
      alert("Please select a new date and time.")
      return
    }
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/doctor/reschedule_appointment/${selectedAppt.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          date: rescheduleForm.value.date,
          slot: rescheduleForm.value.slot,
          reason: actionReason.value 
        })
      })
      if (!response.ok) throw new Error("Failed to reschedule")
      alert("Appointment Rescheduled Successfully!")
      fetchDashboardData()
    } catch (e) { alert(e.message) }
  }
  showActionModal.value = false
  selectedAppt.value = null
}

const viewCompletedDetails = (appt) => {
  selectedAppt.value = appt
  showDetailsModal.value = true
}

const goToProfile = () => {
  router.push('/doctor-profile')
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5">
      <DoctorNavBar />
      <div class="container pt-4 pb-5">
        <div class="row align-items-center">
          <div class="col-md-7 text-white">
            <h1 class="display-5 fw-bold">Welcome, {{ doctorName }}!</h1>
            <p class="lead opacity-75">You have <span class="fw-bold">{{ scheduledAppts.length }}</span> upcoming appointments.</p>
          </div>
          
          <div class="col-md-5 d-flex justify-content-md-end mt-3 mt-md-0">
            <div @click="goToProfile" class="d-inline-flex align-items-center gap-2 bg-white bg-opacity-25 text-white px-3 py-1 rounded-pill cursor-pointer hover-card shadow-sm" style="backdrop-filter: blur(10px);">
              <i class="bi bi-clock fs-5"></i>
              <span class="fw-bold">
                <span v-if="doctorTimings || doctorDays">
                  {{ doctorTimings }} <span v-if="doctorTimings && doctorDays">|</span> {{ doctorDays }}
                </span>
                <span v-else>Manage Availability</span>
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div class="container mt-n5">
      <div v-if="isLoading" class="text-center py-5 card border-0 shadow-sm mb-4">
        <div class="spinner-border text-primary mx-auto" role="status"></div>
      </div>

      <div v-else>
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3 px-4 border-bottom-0">
            <h5 class="mb-0 fw-bold text-primary"><i class="bi bi-calendar-event me-2"></i>Scheduled Appointments</h5>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-4 py-3 text-secondary small">Date & Time</th>
                    <th class="py-3 text-secondary small">Patient Name</th>
                    <th class="py-3 text-secondary small">Reason</th>
                    <th class="pe-4 text-end text-secondary small">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appt in scheduledAppts" :key="appt.id">
                    <td class="ps-4">
                      <div class="fw-bold text-primary">{{ appt.time }}</div>
                      <div class="small text-muted">{{ appt.date }}</div>
                    </td>
                    <td class="fw-medium">{{ appt.patient }}</td>
                    <td><span class="badge bg-warning-subtle text-dark">{{ appt.reason }}</span></td>
                    <td class="text-end pe-4">
                      <button class="btn btn-sm btn-success text-white fw-bold me-2" @click="handleComplete(appt)">Complete</button>
                      <button class="btn btn-sm btn-outline-primary fw-bold me-2" @click="openActionModal('reschedule', appt)">Reschedule</button>
                      <button class="btn btn-sm btn-outline-danger fw-bold" @click="openActionModal('cancel', appt)">Cancel</button>
                    </td>
                  </tr>
                  <tr v-if="scheduledAppts.length === 0">
                    <td colspan="4" class="text-center py-5 text-muted">No upcoming appointments.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3 px-4 border-bottom-0">
            <h5 class="mb-0 fw-bold text-success"><i class="bi bi-check-circle-fill me-2"></i>Completed Appointments</h5>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-4 py-3 text-secondary small">Date</th>
                    <th class="py-3 text-secondary small">Patient Name</th>
                    <th class="py-3 text-secondary small">Diagnosis</th>
                    <th class="pe-4 text-end text-secondary small">View</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appt in completedAppts" :key="appt.id" @click="viewCompletedDetails(appt)" class="cursor-pointer">
                    <td class="ps-4 text-muted small">{{ appt.date }}</td>
                    <td class="fw-medium">{{ appt.patient }}</td>
                    <td>{{ appt.diagnosis }}</td>
                    <td class="text-end pe-4"><button class="btn btn-sm btn-light rounded-circle"><i class="bi bi-eye"></i></button></td>
                  </tr>
                  <tr v-if="completedAppts.length === 0">
                    <td colspan="4" class="text-center py-4 text-muted">No completed appointments yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="pb-5"></div>

    <div v-if="showActionModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded shadow-lg p-4" style="max-width: 400px; width: 90%;">
        <h5 class="fw-bold text-capitalize mb-3">{{ modalActionType }} Appointment</h5>
        
        <div v-if="modalActionType === 'reschedule'" class="mb-3">
          <label class="form-label small fw-bold text-muted">New Date</label>
          <input type="date" class="form-control mb-2" v-model="rescheduleForm.date" :min="minDate">
          <label class="form-label small fw-bold text-muted">New Slot</label>
          <div v-if="isCheckingSlots" class="text-center py-2 text-muted small"><div class="spinner-border spinner-border-sm text-primary me-2"></div>Loading...</div>
          <div v-else-if="rescheduleForm.date && dynamicSlots.length === 0" class="small text-danger">No slots available.</div>
          <div v-else class="d-flex flex-wrap gap-2">
            <div v-for="slotObj in dynamicSlots" :key="slotObj.time">
              <input type="radio" class="btn-check" :id="'res-'+slotObj.time" :value="slotObj.time" v-model="rescheduleForm.slot" :disabled="slotObj.is_booked">
              <label class="btn btn-sm rounded-pill" :class="slotObj.is_booked ? 'btn-light text-muted text-decoration-line-through border' : 'btn-outline-primary'" :for="'res-'+slotObj.time">{{ slotObj.time }}</label>
            </div>
          </div>
        </div>

        <p class="small text-muted mb-2 mt-3">Remarks / Reason</p>
        <textarea class="form-control mb-3" v-model="actionReason" rows="3" :placeholder="modalActionType === 'cancel' ? 'Reason for cancellation...' : 'Reason for rescheduling...'"></textarea>
        <div class="d-flex justify-content-end gap-2">
          <button @click="showActionModal = false" class="btn btn-light">Back</button>
          <button @click="confirmAction" class="btn btn-primary text-capitalize">Confirm {{ modalActionType }}</button>
        </div>
      </div>
    </div>

    <div v-if="showDetailsModal && selectedAppt" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded shadow-lg p-4" style="max-width: 500px; width: 90%;">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Record Details</h5>
          <button @click="showDetailsModal = false" class="btn-close"></button>
        </div>
        <div class="mb-3"><label class="small text-muted fw-bold">Patient</label><div class="fw-bold fs-5">{{ selectedAppt.patient }}</div></div>
        <div class="mb-3"><label class="small text-muted fw-bold">Diagnosis</label><div>{{ selectedAppt.diagnosis }}</div></div>
        <div class="mb-3"><label class="small text-muted fw-bold">Tests Conducted</label><div>{{ selectedAppt.tests }}</div></div>
        <div class="mb-4"><label class="small text-muted fw-bold">Prescription</label><div class="p-2 bg-light rounded">{{ selectedAppt.prescription }}</div></div>
        <div class="d-grid"><button class="btn btn-outline-danger fw-bold">Export PDF</button></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #022032 0%, #265790 100%); }
.mt-n5 { margin-top: -60px; }
.cursor-pointer { cursor: pointer; }
.hover-card { transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.hover-card:hover { transform: translateY(-2px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1050; }
.modal-content-custom { position: relative; z-index: 1060; }
</style>