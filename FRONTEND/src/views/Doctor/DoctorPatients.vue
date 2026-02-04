<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DoctorNavBar from '../../components/DoctorNavBar.vue'

const route = useRoute()
const router = useRouter()

// Form Data
const diagnosisForm = ref({
  appointment_id: null,
  patientName: '',
  diagnosis: '',
  prescription: '',
  tests: '',
  notes: ''
})

const isLoading = ref(false)
const pastRecords = ref([]) 
const searchQuery = ref('')
const selectedRecord = ref(null)

// --- FETCH & PREFILL ---
onMounted(async () => {
  if (route.query.patient) {
    diagnosisForm.value.patientName = route.query.patient
  }
  if (route.query.appt_id) {
    diagnosisForm.value.appointment_id = route.query.appt_id
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/doctor/appointments', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      const data = await response.json()
      pastRecords.value = data.completed
    }
  } catch (error) {
    console.error("Error loading history", error)
  }
})

// --- FILTERED HISTORY ---
const filteredRecords = computed(() => {
  if (!searchQuery.value) return pastRecords.value
  const q = searchQuery.value.toLowerCase()
  return pastRecords.value.filter(r => 
    r.patient.toLowerCase().includes(q) || 
    r.diagnosis.toLowerCase().includes(q)
  )
})

// --- SUBMIT DIAGNOSIS ---
const submitDiagnosis = async () => {
  if (!diagnosisForm.value.appointment_id) {
    alert("Error: No appointment selected. Please start from the Dashboard.")
    return
  }

  isLoading.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/api/doctor/complete_appointment', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(diagnosisForm.value)
    })

    if (!response.ok) throw new Error("Failed to save diagnosis")

    alert("Diagnosis Saved & Appointment Completed!")
    router.push('/doctor-dashboard')

  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}

const openRecordModal = (record) => {
  selectedRecord.value = record
}

const exportPDF = () => {
  alert("PDF generation started...")
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5 pt-4">
      <DoctorNavBar />
      <div class="container pt-3 pb-5"> 
        <h2 class="fw-bold text-white mb-1">Patient Diagnosis</h2>
        <p class="text-white-50 mb-0">Diagnose patients and view medical history</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      <div class="row g-4">
        
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0 py-3 px-4">
              <h5 class="fw-bold text-primary mb-0"><i class="bi bi-clipboard-pulse me-2"></i>Write Diagnosis</h5>
            </div>
            <div class="card-body p-4">
              
              <div v-if="!diagnosisForm.appointment_id" class="alert alert-warning small">
                <i class="bi bi-exclamation-circle me-2"></i> No active appointment selected. Please go back to Dashboard.
              </div>

              <form @submit.prevent="submitDiagnosis">
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Patient Name</label>
                    <input type="text" class="form-control bg-light" v-model="diagnosisForm.patientName" readonly>
                  </div>
                  <div class="col-md-6">
                     <label class="form-label small fw-bold text-muted">Diagnosis</label>
                     <input type="text" class="form-control" v-model="diagnosisForm.diagnosis" placeholder="e.g. Acute Migraine" required>
                  </div>
                </div>

                <div class="mb-3">
                   <label class="form-label small fw-bold text-muted">Tests</label>
                   <input type="text" class="form-control" v-model="diagnosisForm.tests" placeholder="e.g. Blood Panel">
                </div>

                <div class="mb-3">
                   <label class="form-label small fw-bold text-muted">Prescription</label>
                   <textarea class="form-control" v-model="diagnosisForm.prescription" rows="2" placeholder="e.g. Paracetamol 500mg" required></textarea>
                </div>

                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Additional Notes</label>
                  <textarea class="form-control" v-model="diagnosisForm.notes" rows="2" placeholder="Private notes..."></textarea>
                </div>

                <hr class="text-muted opacity-25 my-3">

                <div class="d-flex justify-content-end">
                   <button class="btn btn-primary fw-bold px-4 py-2" :disabled="isLoading || !diagnosisForm.appointment_id">
                    <i class="bi bi-check-circle me-2"></i>
                    {{ isLoading ? 'Saving...' : 'Save & Complete' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-0 py-3 px-4">
              <h5 class="fw-bold text-secondary mb-0">Past Records</h5>
            </div>
            <div class="card-body p-3">
              <div class="input-group mb-3">
                <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" class="form-control bg-light border-start-0" v-model="searchQuery" placeholder="Search history...">
              </div>

              <div v-if="pastRecords.length === 0" class="text-center text-muted small py-4">
                No past records found.
              </div>

              <div v-else class="list-group list-group-flush overflow-auto" style="max-height: 400px;">
                <button 
                  v-for="rec in filteredRecords" 
                  :key="rec.id" 
                  class="list-group-item list-group-item-action border-0 py-3 rounded mb-1"
                  @click="openRecordModal(rec)"
                >
                  <div class="d-flex w-100 justify-content-between align-items-center">
                    <h6 class="mb-1 fw-bold text-dark">{{ rec.patient }}</h6>
                    <small class="text-muted">{{ rec.date }}</small>
                  </div>
                  <p class="mb-1 small text-primary">{{ rec.diagnosis }}</p>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div v-if="selectedRecord" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded shadow-lg p-4" style="max-width: 500px; width: 90%;">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Diagnosis Record</h5>
          <button @click="selectedRecord = null" class="btn-close"></button>
        </div>
        
        <div class="mb-3">
          <label class="small text-muted fw-bold">Patient</label>
          <div class="fw-bold fs-5">{{ selectedRecord.patient }}</div>
        </div>
        <div class="mb-3">
          <label class="small text-muted fw-bold">Diagnosis</label>
          <div>{{ selectedRecord.diagnosis }}</div>
        </div>
        <div class="mb-3">
          <label class="small text-muted fw-bold">Tests</label>
          <div>{{ selectedRecord.tests }}</div>
        </div>
        <div class="mb-4">
          <label class="small text-muted fw-bold">Prescription</label>
          <div class="p-2 bg-light rounded">{{ selectedRecord.prescription }}</div>
        </div>

        <div class="d-grid">
          <button @click="exportPDF" class="btn btn-outline-danger fw-bold">
            <i class="bi bi-file-earmark-pdf me-2"></i>Export as PDF
          </button>
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
.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1050; }
.modal-content-custom { position: relative; z-index: 1060; }
</style>