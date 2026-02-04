<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PatientNavBar from '../../components/PatientNavBar.vue'

const route = useRoute()
const router = useRouter()
const deptName = route.query.dept ? route.query.dept : 'General'

// --- STATE ---
const doctors = ref([])
const deptDescription = ref('') // Reactive state for description
const isLoading = ref(true)

// Booking State
const showBookModal = ref(false)
const selectedDoctor = ref(null)
const bookingForm = ref({ date: '', slot: '', symptoms: '' })
const minDate = new Date().toISOString().split('T')[0]
const dynamicSlots = ref([]) 
const isCheckingSlots = ref(false)
const slotError = ref('') 

// --- 1. FETCH DATA (Doctors + Description Fallback) ---
onMounted(async () => {
  try {
    // A. Handle Description
    // First, check if the Dashboard passed the description via Router State (Optimization)
    if (history.state && history.state.deptDescription) {
      deptDescription.value = history.state.deptDescription
    } else {
      // If user refreshed the page, Router State is lost. Fetch from API.
      const deptRes = await fetch('http://127.0.0.1:5000/api/departments')
      if (deptRes.ok) {
        const allDepts = await deptRes.json()
        const currentDept = allDepts.find(d => d.name === deptName)
        deptDescription.value = currentDept ? currentDept.desc : `Specialized treatments in ${deptName}.`
      }
    }

    // B. Fetch Doctors
    const docRes = await fetch('http://127.0.0.1:5000/api/doctors')
    if (docRes.ok) {
      const allDoctors = await docRes.json()
      doctors.value = allDoctors.filter(d => d.dept === deptName)
    }

  } catch (error) { 
    console.error("Error loading data:", error)
  } finally { 
    isLoading.value = false 
  }
})

// --- 2. SLOT LOGIC (Watch for Date Changes) ---
watch(() => bookingForm.value.date, async (newDate) => {
  if (!newDate || !selectedDoctor.value) return
  
  // Reset UI
  bookingForm.value.slot = '' 
  isCheckingSlots.value = true
  dynamicSlots.value = [] 
  slotError.value = ''

  try {
    const response = await fetch('http://127.0.0.1:5000/api/appointments/available_slots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doctor_id: selectedDoctor.value.id, date: newDate })
    })
    
    const data = await response.json()
    if (data.error) slotError.value = data.error
    else dynamicSlots.value = data

  } catch (error) {
    console.error("Error fetching slots", error)
    slotError.value = "Unable to load schedule."
  } finally {
    isCheckingSlots.value = false
  }
})

// --- ACTIONS ---
const openBooking = (doc) => {
  selectedDoctor.value = doc
  bookingForm.value = { date: '', slot: '', symptoms: '' }
  dynamicSlots.value = [] 
  slotError.value = ''
  showBookModal.value = true
}

const confirmBooking = async () => {
  if (!bookingForm.value.date || !bookingForm.value.slot) {
    alert("Please select date and time.")
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/book_appointment', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        doctor_id: selectedDoctor.value.id,
        date: bookingForm.value.date,
        slot: bookingForm.value.slot,
        symptoms: bookingForm.value.symptoms
      })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.error || "Booking failed.")
    }

    alert("Appointment Confirmed Successfully!")
    showBookModal.value = false
    router.push('/patient-dashboard')
  } catch (error) { alert(error.message) }
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section">
      <PatientNavBar />
      <div class="container pt-4 pb-5">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb mb-2">
            <li class="breadcrumb-item">
              <router-link to="/patient-dashboard" class="text-white-50 text-decoration-none">
                <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
              </router-link>
            </li>
          </ol>
        </nav>
        <h2 class="display-5 fw-bold text-white mb-0">{{ deptName }} Specialists</h2>
      </div>
    </div>

    <div class="bg-white border-bottom shadow-sm" style="position: relative; z-index: 10;">
      <div class="container py-4">
        <div class="row">
          <div class="col-lg-8">
            <h6 class="text-primary fw-bold text-uppercase small mb-2" style="letter-spacing: 1px;">About Department</h6>
            <p class="text-secondary lead fs-6 mb-0 lh-base">
              {{ deptDescription || 'Loading department details...' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-3">
      
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else class="row g-4">
        
        <div v-for="doc in doctors" :key="doc.id" class="col-md-6 col-lg-4">
          <div class="card border-0 shadow-sm h-100 p-3 d-flex flex-column hover-lift">
            
            <div class="d-flex align-items-center gap-3 border-bottom pb-3 mb-3">
              <div class="flex-shrink-0">
                <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold fs-4" 
                     style="width: 60px; height: 60px;">
                  <span v-if="doc.name">{{ doc.name.charAt(0) }}</span>
                </div>
              </div>
              <div class="flex-grow-1">
                <h5 class="fw-bold text-dark mb-1 text-truncate">Dr. {{ doc.name }}</h5>
                <span class="badge bg-light text-primary border border-primary-subtle">
                   {{ doc.dept }}
                </span>
              </div>
            </div>

            <div class="d-flex justify-content-between px-3 mb-3">
               <div class="d-flex align-items-center">
                 <i class="bi bi-briefcase text-muted me-2"></i>
                 <div>
                   <div class="fw-bold small">{{ doc.exp }} Years</div>
                   <div class="text-muted" style="font-size: 0.7rem;">Experience</div>
                 </div>
               </div>
               <div class="vr opacity-25"></div>
               <div class="d-flex align-items-center">
                 <i class="bi bi-cash text-muted me-2"></i>
                 <div>
                   <div class="fw-bold small">₹ {{ doc.fee }}</div>
                   <div class="text-muted" style="font-size: 0.7rem;">Cons. Fee</div>
                 </div>
               </div>
            </div>

            <div class="bio-container mb-4 flex-grow-1 bg-light rounded p-2">
               <p class="text-bold small mb-0 bio-text text-muted">
                 {{ doc.bio }}
               </p>
            </div>

            <div class="text-center mt-auto">
              <button @click="openBooking(doc)" class="btn btn-cstmbtn rounded-pill px-5 fw-bold shadow-sm w-100">
                Book Appointment
              </button>
            </div>

          </div>
        </div>

        <div v-if="doctors.length === 0" class="col-12 text-center py-5 text-muted">
          <div class="p-5 bg-white rounded shadow-sm">
            <i class="bi bi-person-x display-1 text-secondary opacity-25"></i>
            <h5 class="mt-3 fw-bold">No Specialists Found</h5>
            <p>We currently don't have any doctors available in <strong>{{ deptName }}</strong>.</p>
            <router-link to="/patient-dashboard" class="btn btn-outline-primary rounded-pill px-4">Browse other departments</router-link>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showBookModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded shadow-lg p-4" style="max-width: 500px; width: 90%;">
        
        <div class="d-flex align-items-center gap-3 border-bottom pb-3 mb-3">
          <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 50px; height: 50px;">
             <span v-if="selectedDoctor.name">{{ selectedDoctor.name.charAt(4) }}</span>
          </div>
          <div>
            <h5 class="fw-bold mb-0">{{ selectedDoctor.name }}</h5>
            <small class="text-muted">{{ selectedDoctor.dept }}</small>
          </div>
        </div>

        <div class="mb-4 p-3 bg-light rounded border border-light-subtle d-flex align-items-center justify-content-around">
           <div class="text-center">
             <small class="text-muted text-uppercase fw-bold" style="font-size: 0.65rem; letter-spacing: 1px;">Daily Hours</small>
             <div class="fw-bold text-dark small mt-1">
               <i class="bi bi-clock me-1 text-primary"></i> {{ selectedDoctor.timings }}
             </div>
           </div>
           <div class="vr text-secondary opacity-25"></div>
           <div class="text-center">
             <small class="text-muted text-uppercase fw-bold" style="font-size: 0.65rem; letter-spacing: 1px;">Working Days</small>
             <div class="mt-1">
               <span class="badge bg-white text-primary border shadow-sm fw-bold">
                 <i class="bi bi-calendar-week me-1"></i> {{ selectedDoctor.days }}
               </span>
             </div>
           </div>
        </div>

        <form @submit.prevent="confirmBooking">
          <div class="mb-3">
            <label class="form-label small fw-bold text-muted">Select Date</label>
            <input type="date" class="form-control" v-model="bookingForm.date" :min="minDate" required>
          </div>

          <div class="mb-3">
            <label class="form-label small fw-bold text-muted">Available Slots</label>
            
            <div v-if="isCheckingSlots" class="text-center py-4 text-muted small">
              <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
              Checking availability...
            </div>

            <div v-else-if="slotError" class="alert alert-warning border-0 d-flex align-items-center small py-2 mb-2">
              <i class="bi bi-calendar-x me-2 fs-5"></i>
              <div>{{ slotError }}</div>
            </div>

            <div v-else-if="bookingForm.date && dynamicSlots.length === 0" class="text-danger small py-2">
              <i class="bi bi-x-circle me-1"></i> Fully booked for this date.
            </div>

            <div v-else class="d-flex flex-wrap gap-2">
              <div v-for="slotObj in dynamicSlots" :key="slotObj.time">
                <input 
                  type="radio" 
                  class="btn-check" 
                  :id="slotObj.time" 
                  :value="slotObj.time" 
                  v-model="bookingForm.slot" 
                  :disabled="slotObj.is_booked"
                  required
                >
                <label 
                  class="btn btn-sm rounded-pill" 
                  :class="slotObj.is_booked ? 'btn-light text-muted text-decoration-line-through border' : 'btn-outline-success'"
                  :for="slotObj.time"
                >
                  {{ slotObj.time }}
                </label>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label small fw-bold text-muted">Symptoms / Reason (Optional)</label>
            <textarea class="form-control" v-model="bookingForm.symptoms" rows="2" placeholder="Briefly describe your issue..."></textarea>
          </div>

          <div class="d-flex gap-2">
            <button type="button" @click="showBookModal = false" class="btn btn-light flex-grow-1">Cancel</button>
            <button type="submit" class="btn btn-primary fw-bold flex-grow-1" :disabled="!bookingForm.slot">Confirm Appointment</button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #022032 0%, #265790 100%); }
.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1050; }
.modal-content-custom { position: relative; z-index: 1060; }
.bio-container { max-height: 120px; overflow-y: auto; border: 1px solid #f0f0f0; }
.hover-lift { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.btn-cstmbtn { background-color: #2c629e; color: #fff; }
.btn-cstmbtn:hover { background-color: #649ad1; color: #fff; }
.hover-lift:hover { transform: translateY(-3px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
</style>