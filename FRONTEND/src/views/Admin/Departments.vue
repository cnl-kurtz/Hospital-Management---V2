<script setup>
import { ref, onMounted } from 'vue'
import AdminNavBar from '../../components/AdminNavBar.vue'

// State
const departments = ref([])
const deptName = ref('')
const deptDesc = ref('')
const isLoading = ref(false)

// Edit Mode State
const isEditing = ref(false)
const editingId = ref(null)

// 1. Fetch Departments
const fetchDepartments = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/departments')
    departments.value = await response.json()
  } catch (error) { console.error("Error fetching departments:", error) }
}

// 2. Handle Form Submit (Add OR Update)
const handleFormSubmit = async () => {
  if (!deptName.value) return alert("Name is required")
  
  isLoading.value = true
  
  const url = isEditing.value 
    ? `http://127.0.0.1:5000/api/admin/update_department/${editingId.value}`
    : 'http://127.0.0.1:5000/api/admin/add_department'
    
  const method = isEditing.value ? 'PUT' : 'POST'

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ 
        name: deptName.value, 
        desc: deptDesc.value,
        icon: 'bi-hospital' 
      })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error)
    }

    alert(isEditing.value ? "Department Updated!" : "Department Added!")
    resetForm()
    fetchDepartments() 
  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}

// 3. Prepare Edit
const startEdit = (dept) => {
  isEditing.value = true
  editingId.value = dept.id
  deptName.value = dept.name
  deptDesc.value = dept.desc || ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 4. Reset
const resetForm = () => {
  isEditing.value = false
  editingId.value = null
  deptName.value = ''
  deptDesc.value = ''
}

// 5. Delete Department
const deleteDepartment = async (id) => {
  if(!confirm("Are you sure? This might affect doctors in this department.")) return

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/delete_department/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) fetchDepartments()
    else alert("Failed to delete")
  } catch (error) { alert(error.message) }
}

onMounted(() => { fetchDepartments() })
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Departments Management</h2>
        <p class="text-white-50 mb-0">Add and manage hospital departments</p>
      </div>
    </div>
    
    <div class="container mt-n5 pb-5">
      <div class="row g-4">
        
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm h-100 sticky-top" style="top: 20px;">
            <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
              <h5 class="fw-bold text-primary mb-0">
                {{ isEditing ? 'Edit Department' : 'Add New Department' }}
              </h5>
              <button v-if="isEditing" @click="resetForm" class="btn btn-sm btn-outline-secondary">Cancel</button>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="handleFormSubmit">
                <div class="mb-3">
                  <label class="form-label small fw-bold text-muted">Department Name</label>
                  <input type="text" class="form-control" v-model="deptName" placeholder="e.g. Dermatology" required>
                </div>
                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Description</label>
                  <textarea class="form-control" v-model="deptDesc" rows="4" placeholder="Brief description..."></textarea>
                </div>
                <button class="btn btn-cstmbtn w-100 fw-bold" :disabled="isLoading">
                  {{ isLoading ? 'Processing...' : (isEditing ? 'Update Department' : 'Create Department') }}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0 pt-4 px-4">
               <h5 class="fw-bold text-secondary mb-0">Existing Departments</h5>
            </div>
            <div class="card-body p-4">
              
              <div class="row g-3">
                <div v-for="dept in departments" :key="dept.id" class="col-md-6">
                  <div class="card border-0 bg-lightc h-100 hover-card">
                    <div class="card-body d-flex align-items-start gap-3">
                      
                      <div class="rounded-circle bg-white text-primary shadow-sm d-flex align-items-center justify-content-center flex-shrink-0" style="width: 50px; height: 50px;">
                        <i :class="['bi fs-4', dept.icon || 'bi-building']"></i>
                      </div>
                      
                      <div class="flex-grow-1 overflow-hidden"> 
                        <h6 class="fw-bold mb-1">{{ dept.name }}</h6>
                        <p class="text-muted small mb-0 text-clamp">{{ dept.desc }}</p>
                      </div>

                      <div class="d-flex flex-column gap-2">
                         <button @click="startEdit(dept)" class="btn btn-link text-secondary p-0" title="Edit">
                          <i class="bi bi-pencil-square"></i>
                        </button>
                        <button @click="deleteDepartment(dept.id)" class="btn btn-link text-danger p-0" title="Remove">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>

                    </div>
                  </div>
                </div>

                <div v-if="departments.length === 0" class="col-12 text-center py-5 text-muted">
                  No departments found.
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
.btn-cstmbtn { background-color: #2c629e; color: #fff; }
.btn-cstmbtn:hover { background-color: #649ad1; color: #fff; }

.header-section { 
  background: linear-gradient(90deg, #022032 0%, #265790 100%); 
  padding-bottom: 4rem !important;
}
.mt-n5 { margin-top: -4rem !important; }


.bg-lightc { background-color: #ecf1f5; }

.hover-card:hover { 
  transform: translateY(-3px); 
  transition: all 0.2s; 
  background-color: #e0e1e3 !important; /* Slightly darker grey on hover */
}

.text-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>