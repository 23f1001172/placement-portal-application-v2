import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import CompanyDashboard from './views/CompanyDashboard.vue'
import StudentDashboard from './views/StudentDashboard.vue'
import CreateJob from './views/CreateJob.vue'

const routes = [
  { path: '/', component: Login },
  { path: '/register', component: Register },
  { path: '/admin', component: AdminDashboard },
  { path: '/company', component: CompanyDashboard },
  { path: '/company/create-job', component: CreateJob },
  { path: '/student', component: StudentDashboard }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
