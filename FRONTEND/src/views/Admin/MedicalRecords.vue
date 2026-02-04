<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const route = useRoute()
const searchQuery = ref('')
const records = ref([])
const isLoading = ref(true)

// Modal State
const showModal = ref(false)
const selectedRecord = ref(null)

// --- FETCH DATA ---
onMounted(async () => {
  if (route.query.search) {
    searchQuery.value = route.query.search
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/medical_records', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      records.value = await response.json()
    }
  } catch (error) {
    console.error("Error fetching records:", error)
  } finally {
    isLoading.value = false
  }
})

// --- FILTER LOGIC ---
const filteredRecords = computed(() => {
  if (!searchQuery.value) return records.value
  const q = searchQuery.value.toLowerCase()
  return records.value.filter(rec => 
    rec.patient.toLowerCase().includes(q) ||
    rec.id.toLowerCase().includes(q) ||
    rec.diagnosis.toLowerCase().includes(q)
  )
})

const viewRecord = (rec) => {
  selectedRecord.value = rec
  showModal.value = true
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5"> <h2 class="fw-bold text-white mb-1">Medical Records</h2>
        <p class="text-white-50 mb-0">Access patient history and past diagnoses</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      
      <div class="row justify-content-center mb-4">
        <div class="col-md-6">
          <div class="input-group shadow-sm">
            <span class="input-group-text bg-white border-0 ps-3"><i class="bi bi-search text-muted"></i></span>
            <input 
              type="text" 
              class="form-control border-0 py-3" 
              v-model="searchQuery" 
              placeholder="Search by Name, Diagnosis or ID..."
            >
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="bg-light">
                <tr>
                  <th class="ps-4 py-3 text-secondary small">Record ID</th>
                  <th class="py-3 text-secondary small">Patient Name</th>
                  <th class="py-3 text-secondary small">Doctor</th>
                  <th class="py-3 text-secondary small">Date</th>
                  <th class="py-3 text-secondary small">Diagnosis</th>
                  <th class="pe-4 text-end text-secondary small">Details</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rec in filteredRecords" :key="rec.id">
                  <td class="ps-4 text-primary fw-bold small">{{ rec.id }}</td>
                  <td class="fw-medium">
                    {{ rec.patient }} 
                    <span class="text-muted small ms-1">({{ rec.age }} yrs)</span>
                  </td>
                  <td>
                    <div class="d-flex flex-column" style="line-height: 1.2;">
                      <span>{{ rec.doctor }}</span>
                      <small class="text-muted" style="font-size: 0.75rem;">{{ rec.dept }}</small>
                    </div>
                  </td>
                  <td>{{ rec.date }}</td>
                  <td><span class="badge bg-secondary-subtle text-dark border">{{ rec.diagnosis }}</span></td>
                  <td class="text-end pe-4">
                    <button @click="viewRecord(rec)" class="btn btn-sm btn-outline-primary fw-bold">View Full Record</button>
                  </td>
                </tr>
                <tr v-if="filteredRecords.length === 0">
                  <td colspan="6" class="text-center py-5 text-muted">
                    No medical records found matching "{{ searchQuery }}"
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <div v-if="showModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded shadow-lg p-4" style="max-width: 600px; width: 90%;">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
          <div>
            <h5 class="fw-bold mb-0">Medical Record Details</h5>
            <small class="text-muted">{{ selectedRecord.id }} • {{ selectedRecord.date }}</small>
          </div>
          <button @click="showModal = false" class="btn-close"></button>
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label class="small text-muted fw-bold">Patient</label>
            <div class="fs-5 fw-bold">{{ selectedRecord.patient }}</div>
          </div>
          <div class="col-md-6">
            <label class="small text-muted fw-bold">Attending Doctor</label>
            <div>{{ selectedRecord.doctor }}</div>
            <small class="text-muted">{{ selectedRecord.dept }}</small>
          </div>
        </div>

        <div class="p-3 bg-light rounded mb-3">
          <label class="small text-muted fw-bold d-block mb-1">Diagnosis</label>
          <div class="fw-bold text-primary">{{ selectedRecord.diagnosis }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-12">
             <label class="small text-muted fw-bold">Prescription</label>
             <div>{{ selectedRecord.prescription }}</div>
          </div>
        </div>

        <div class="row mb-3" v-if="selectedRecord.tests">
          <div class="col-12">
             <label class="small text-muted fw-bold">Recommended Tests</label>
             <div>{{ selectedRecord.tests }}</div>
          </div>
        </div>

        <div class="row mb-4" v-if="selectedRecord.notes">
          <div class="col-12">
             <label class="small text-muted fw-bold">Doctor's Notes</label>
             <div class="text-muted small fst-italic">"{{ selectedRecord.notes }}"</div>
          </div>
        </div>

        <div class="d-flex justify-content-end">
          <button @click="showModal = false" class="btn btn-primary fw-bold px-4">Close</button>
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