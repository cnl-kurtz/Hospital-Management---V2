<script setup>
import { ref, onMounted } from 'vue'
import AdminNavBar from '../../components/AdminNavBar.vue'

// State
const staffList = ref([]) 
const editingId = ref(null) // ID of doctor being edited (null = Add Mode)
const isLoading = ref(false)
const departments = ref([])
const imagePreview = ref(null)

// Form Data
const doctor = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  department: '',
  contact: '',
  bio: '',
  fee: '', 
  timings: '', 
  days: '',
  image: null,
  blacklisted: false
})

// --- DATA FETCHING ---
const fetchDepartments = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/departments')
    const data = await response.json()
    departments.value = data.map(d => d.name)
  } catch (error) { console.error("Error loading departments:", error) }
}

const fetchDoctors = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/doctors', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if(response.ok) {
        staffList.value = await response.json()
    }
  } catch (error) { console.error("Error fetching doctors:", error) }
}

onMounted(() => {
  fetchDoctors()
  fetchDepartments()
})

// --- ACTIONS ---

const handleSubmit = async () => {
  const token = localStorage.getItem('token')
  if (!token) return alert("Please login first.")

  isLoading.value = true
  const isEdit = editingId.value !== null
  
  const url = isEdit 
    ? `http://127.0.0.1:5000/api/admin/update_doctor/${editingId.value}`
    : 'http://127.0.0.1:5000/api/admin/add_doctor'
  
  const method = isEdit ? 'PUT' : 'POST'

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify(doctor.value)
    })

    const result = await response.json()
    if (!response.ok) throw new Error(result.error || 'Operation failed')

    alert(isEdit ? 'Doctor Updated Successfully!' : 'Doctor Added Successfully!')
    resetForm()
    fetchDoctors() 

  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}

const editDoctor = (docData) => {
  editingId.value = docData.id
  doctor.value = {
    name: docData.name,
    username: docData.username,
    email: docData.email,
    password: '', 
    department: docData.department,
    contact: docData.contact,
    bio: docData.bio,
    fee: docData.fee,
    timings: docData.timings || '09:00 AM - 05:00 PM',
    days: docData.days || 'Mon - Fri',
    image: null 
  }
  imagePreview.value = null 
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const toggleBlacklist = async (staff) => {
  const action = staff.is_blacklisted ? "Restore" : "Blacklist"
  if(!confirm(`Are you sure you want to ${action} access for Dr. ${staff.name}?`)) return

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/blacklist_doctor/${staff.id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) {
        fetchDoctors() 
    } else {
        alert("Action failed.")
    }
  } catch (error) {
    alert(error.message)
  }
}

const deleteDoctor = async (id) => {
  if(!confirm("Are you sure? This will delete the doctor's login and profile.")) return

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/delete_doctor/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) {
        alert("Doctor deleted.")
        fetchDoctors()
    } else {
        alert("Failed to delete.")
    }
  } catch (error) {
    alert(error.message)
  }
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    doctor.value.image = file.name 
    imagePreview.value = URL.createObjectURL(file)
  }
}

const resetForm = () => {
  doctor.value = { 
    name: '', username: '', email: '', password: '', department: '', 
    contact: '', bio: '', fee: '', timings: '09:00 AM - 05:00 PM', 
    days: 'Mon - Fri', image: null 
  }
  editingId.value = null
  imagePreview.value = null
}
</script>

<template>
  <div class="bg-light min-vh-100">
    
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Staff Management</h2>
        <p class="text-white-50 mb-0">Register new doctors and manage staff members</p>
      </div>
    </div>
    
    <div class="container mt-n5 pb-5">
      <div class="row g-4">
        
        <div class="col-lg-5">
          <div class="card border-0 shadow-sm sticky-top" style="top: 20px; z-index: 1020;">
            <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
              <h5 class="fw-bold text-primary mb-0">
                <i class="bi" :class="editingId ? 'bi-pencil-square' : 'bi-person-plus-fill'"></i>
                {{ editingId ? 'Edit Doctor Details' : 'Add New Doctor' }}
              </h5>
              <button v-if="editingId" @click="resetForm" class="btn btn-sm btn-light text-muted">Cancel</button>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="handleSubmit">
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Full Name</label>
                    <input type="text" class="form-control" v-model="doctor.name" placeholder="Dr. Name" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Username</label>
                    <input type="text" class="form-control" v-model="doctor.username" placeholder="Login ID" required>
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Email</label>
                    <input type="email" class="form-control" v-model="doctor.email" placeholder="mail@hplus.com" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Password</label>
                    <input type="password" class="form-control" v-model="doctor.password" :placeholder="editingId ? 'Unchanged' : '******'" :required="!editingId">
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Department</label>
                    <select class="form-select" v-model="doctor.department" required>
                      <option value="" disabled>Select Dept</option>
                      <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Fee ($)</label>
                    <input type="number" class="form-control" v-model="doctor.fee" placeholder="0.00" required>
                  </div>
                </div>

                <div class="row mb-3">
                   <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Timings</label>
                    <input type="text" class="form-control" v-model="doctor.timings" placeholder="09:00 AM - 05:00 PM">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Days</label>
                    <input type="text" class="form-control" v-model="doctor.days" placeholder="Mon - Fri">
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Office Contact</label>
                    <input type="tel" class="form-control" v-model="doctor.contact" placeholder="Ext or Phone">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Experience (Years)</label>
                    <input type="number" class="form-control" v-model="doctor.experience" placeholder="e.g., 5">
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label small fw-bold text-muted">Bio</label>
                  <textarea class="form-control" v-model="doctor.bio" rows="2"></textarea>
                </div>

                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Profile Image</label>
                  <div class="d-flex align-items-center gap-3">
                    <div v-if="imagePreview" class="rounded-circle bg-light border" 
                         style="width: 50px; height: 50px; background-size: cover; background-position: center;"
                         :style="{ backgroundImage: `url(${imagePreview})` }">
                    </div>
                    <input type="file" class="form-control" @change="handleFileChange" accept="image/*">
                  </div>
                </div>

                <button class="btn w-100 fw-bold" :class="editingId ? 'btn-warning text-white' : 'btn-primary'" :disabled="isLoading">
                  {{ isLoading ? 'Processing...' : (editingId ? 'Update Doctor' : 'Register Doctor') }}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-7">
          <div class="card border-0 shadow-sm">
             <div class="card-header bg-white border-0 pt-4 px-4">
               <h5 class="fw-bold text-secondary mb-0">Medical Staff Directory</h5>
             </div>
             <div class="card-body p-4">
              
              <div class="row g-3">
                <div v-for="staff in staffList" :key="staff.id" class="col-md-6">
                  <div class="card border-0 bg-lightc h-100 hover-card" :class="{'opacity-75': staff.is_blacklisted}">
                    <div class="card-body">
                      <div class="d-flex align-items-start gap-3">
                        
                        <div class="rounded-circle bg-white d-flex align-items-center justify-content-center flex-shrink-0 shadow-sm" 
                             :class="staff.is_blacklisted ? 'text-secondary' : 'text-primary'"
                             style="width: 50px; height: 50px; font-weight: bold; font-size: 1.2rem;">
                           {{ staff.name.charAt(4) || 'D' }}
                        </div>

                        <div class="flex-grow-1 overflow-hidden">
                           <h6 class="fw-bold mb-1 text-truncate" :class="{'text-decoration-line-through': staff.is_blacklisted}">
                             Dr. {{ staff.name }}
                           </h6>
                           <span class="badge bg-primary-subtle text-primary border border-primary-subtle mb-2">
                             {{ staff.department }}
                           </span>
                           <div class="small text-muted text-truncate" title="Timings">
                             <i class="bi bi-clock me-1"></i>{{ staff.timings }}
                           </div>
                           <div class="small text-muted text-truncate" :title="staff.email">
                             <i class="bi bi-envelope me-1"></i>{{ staff.email }}
                           </div>
                        </div>

                        <div class="d-flex flex-column gap-2">
                          <button @click="editDoctor(staff)" class="btn btn-link text-secondary p-0" title="Edit">
                            <i class="bi bi-pencil-square"></i>
                          </button>
                          
                          <button @click="toggleBlacklist(staff)" class="btn btn-link p-0" 
                                  :class="staff.is_blacklisted ? 'text-success' : 'text-warning'"
                                  :title="staff.is_blacklisted ? 'Restore Access' : 'Blacklist'">
                            <i class="bi" :class="staff.is_blacklisted ? 'bi-check-circle' : 'bi-slash-circle'"></i>
                          </button>

                          <button @click="deleteDoctor(staff.id)" class="btn btn-link text-danger p-0" title="Delete">
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>

                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="staffList.length === 0" class="col-12 text-center py-5 text-muted">
                  <i class="bi bi-people display-4 opacity-25"></i>
                  <p class="mt-2">No doctors found. Use the form to add one.</p>
                </div>
              </div>

            </div>
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

.sticky-top { transition: top 0.3s; }

/* Interactive Card Effects */
.bg-lightc { background-color: #ecf1f5; }
.hover-card:hover { 
  transform: translateY(-3px); 
  transition: all 0.2s; 
  background-color: #e9ecef !important; 
}
</style>