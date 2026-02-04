import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// Admin Views
import AdminDashboard from '../views/Admin/AdminDashboard.vue'
import Departments from '../views/Admin/Departments.vue'
import AddDoctor from '../views/Admin/AddDoctor.vue'
import AppointmentsView from '../views/Admin/AppointmentsView.vue'
import MedicalRecords from '../views/Admin/MedicalRecords.vue'

// Doctor Views
import DoctorDashboard from '../views/Doctor/DoctorDashboard.vue'
import DoctorProfile from '../views/Doctor/DoctorProfile.vue'
import DoctorPatients from '../views/Doctor/DoctorPatients.vue'

// Patient Views
import PatientDashboard from '../views/Patient/PatientDashboard.vue'
import ViewDoctors from '../views/Patient/ViewDoctors.vue'
import PatientProfile from '../views/Patient/PatientProfile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- PUBLIC ROUTES ---
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { hideNavbar: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { hideNavbar: true }
    },

    // --- ADMIN ROUTES ---
    {
      path: '/admindashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/departments',
      name: 'departments',
      component: Departments,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/staff',
      name: 'staff', // This points to AddDoctor.vue
      component: AddDoctor,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/appointmentsview',
      name: 'appointments',
      component: AppointmentsView,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/medical-records',
      name: 'medical-records',
      component: MedicalRecords,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },

    // --- DOCTOR ROUTES ---
    {
      path: '/doctor-dashboard',
      name: 'doctor-dashboard',
      component: DoctorDashboard,
      meta: { requiresAuth: true, role: 'doctor', hideNavbar: true }
    },
    {
      path: '/doctor-profile',
      name: 'doctor-profile',
      component: DoctorProfile,
      meta: { requiresAuth: true, role: 'doctor', hideNavbar: true }
    },
    {
      path: '/doctor-patients',
      name: 'doctor-patients',
      component: DoctorPatients,
      meta: { requiresAuth: true, role: 'doctor', hideNavbar: true }
    },

    // --- PATIENT ROUTES ---
    {
      path: '/patient-dashboard',
      name: 'patient-dashboard',
      component: PatientDashboard,
      meta: { requiresAuth: true, role: 'patient', hideNavbar: true }
    },
    {
      path: '/view-doctors',
      name: 'view-doctors',
      component: ViewDoctors,
      meta: { requiresAuth: true, role: 'patient', hideNavbar: true }
    },
    {
      path: '/patient-profile',
      name: 'patient-profile',
      component: PatientProfile,
      meta: { requiresAuth: true, role: 'patient', hideNavbar: true }
    }
  ]
})

// --- GLOBAL SECURITY GUARD ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // 1. Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!token) {
      // User is not logged in
      alert("Please log in to access this page.")
      return next('/login')
    }

    // 2. Check if route requires a specific role
    if (to.meta.role && to.meta.role !== role) {
      alert(`Unauthorized Access! You are logged in as a ${role}, but this page is for ${to.meta.role}s.`)
      
      // Redirect them to their safe home based on their role
      if (role === 'admin') return next('/admindashboard')
      if (role === 'doctor') return next('/doctor-dashboard')
      if (role === 'patient') return next('/patient-dashboard')
      
      return next('/login') // Fallback
    }
  }

  // 3. Prevent logged-in users from visiting Login/Register pages
  if ((to.path === '/login' || to.path === '/register') && token) {
    if (role === 'admin') return next('/admindashboard')
    if (role === 'doctor') return next('/doctor-dashboard')
    if (role === 'patient') return next('/patient-dashboard')
  }

  next() // All checks passed, proceed
})

export default router