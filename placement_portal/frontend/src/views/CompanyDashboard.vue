<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Company Dashboard</h2>
      <button @click="logout" class="btn btn-danger">Logout</button>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-info text-dark fw-bold py-2 d-flex justify-content-between align-items-center">
        <span><i class="bi-building"></i> Company Profile</span>
        <button @click="toggleEditProfile" class="btn btn-sm btn-outline-dark">{{ isEditingProfile ? 'Cancel' : 'Edit Profile' }}</button>
      </div>
      <div class="card-body">
        <div v-if="!isEditingProfile">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Company Name:</strong> {{ profile.name || 'Not set' }}</p>
              <p><strong>Industry:</strong> {{ profile.industry || 'Not set' }}</p>
              <p><strong>Location:</strong> {{ profile.location || 'Not set' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Contact Email:</strong> {{ profile.email || 'Not set' }}</p>
              <p><strong>Website:</strong> <a v-if="profile.website" :href="profile.website" target="_blank">{{ profile.website }}</a><span v-else>Not set</span></p>
              <p><strong>Description:</strong> {{ profile.description || 'Not set' }}</p>
            </div>
          </div>
        </div>
        <div v-else>
          <form @submit.prevent="saveProfile">
            <div class="row">
              <div class="col-md-6 mb-2"><label class="fw-bold">Company Name</label><input v-model="profileEdit.name" class="form-control" required /></div>
              <div class="col-md-6 mb-2"><label class="fw-bold">Industry</label><input v-model="profileEdit.industry" class="form-control" /></div>
              <div class="col-md-6 mb-2"><label class="fw-bold">Location</label><input v-model="profileEdit.location" class="form-control" /></div>
              <div class="col-md-6 mb-2"><label class="fw-bold">Contact Email</label><input v-model="profileEdit.email" class="form-control" type="email" /></div>
              <div class="col-md-6 mb-2"><label class="fw-bold">Website URL</label><input v-model="profileEdit.website" class="form-control" placeholder="https://..." /></div>
              <div class="col-12 mb-2"><label class="fw-bold">Description</label><textarea v-model="profileEdit.description" class="form-control" rows="2"></textarea></div>
            </div>
            <button type="submit" class="btn btn-success btn-sm px-4">Save Profile</button>
          </form>
        </div>
      </div>
    </div>

    <div class="row mb-4">
      <div class="col"><div class="card shadow-sm text-center py-3 bg-light border-start border-4 border-primary"><div class="fw-bold fs-3">{{ stats.drives_created || 0 }}</div><div class="text-muted fw-bold">DRIVES CREATED</div></div></div>
      <div class="col"><div class="card shadow-sm text-center py-3 bg-light border-start border-4 border-success"><div class="fw-bold fs-3 text-success">{{ stats.drives_accepted || 0 }}</div><div class="text-muted fw-bold">DRIVES ACCEPTED</div></div></div>
      <div class="col"><div class="card shadow-sm text-center py-3 bg-light border-start border-4 border-info"><div class="fw-bold fs-3">{{ stats.total_applications || 0 }}</div><div class="text-muted fw-bold">TOTAL APPLICATIONS</div></div></div>
      <div class="col"><div class="card shadow-sm text-center py-3 bg-light border-start border-4 border-warning"><div class="fw-bold fs-3 text-warning">{{ stats.candidates_selected || 0 }}</div><div class="text-muted fw-bold">HIRED CANDIDATES</div></div></div>
    </div>

    <div class="d-flex justify-content-between mb-4">
      <router-link to="/company/create-job" class="btn btn-success fw-bold px-4">
        <i class="bi-plus-circle"></i> Post New Drive
      </router-link>
      <button @click="exportData" class="btn btn-warning fw-bold px-4">
        <i class="bi-download"></i> Export Applications Report
      </button>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-dark text-white fw-bold py-3 d-flex justify-content-between align-items-center">
        <span><i class="bi-briefcase"></i> Active Drives</span>
        <input v-model="searchDrives" placeholder="Search your drives..." class="form-control form-control-sm w-25" />
      </div>
      <div class="card-body bg-white">
        <table class="table table-hover align-middle" v-if="activeDrives.length">
          <thead class="table-light">
            <tr><th>Drive Title</th><th>Status</th><th class="text-end">Management Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="j in activeDrives" :key="j.id">
              <td class="fw-semibold">{{ j.title }}</td>
              <td>
                <span class="badge"
                  :class="{
                    'bg-warning text-dark': j.status === 'pending',
                    'bg-success': j.status === 'approved'
                  }"
                >{{ j.status.toUpperCase() }}</span>
              </td>
              <td class="text-end">
                <button @click="viewDriveDetails(j)" class="btn btn-outline-info btn-sm me-2">View Details</button>
                <button @click="viewApplicants(j)" class="btn btn-outline-primary btn-sm me-2">View Applicants</button>
                <button 
                  v-if="j.status === 'pending'"
                  @click="editJob(j)" 
                  class="btn btn-info btn-sm me-2">
                  Edit Drive
                </button>
                <button 
                  v-if="j.status !== 'closed'"
                  @click="closeJob(j.id)" 
                  class="btn btn-danger btn-sm">
                  Close Drive
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted">No active drives.</div>
      </div>
    </div>

    <div class="card shadow-sm mb-5 border-0">
      <div class="card-header bg-secondary text-white fw-bold py-3">
        <span><i class="bi-archive"></i> Past / Rejected Drives</span>
      </div>
      <div class="card-body bg-white">
        <table class="table table-hover align-middle" v-if="pastDrives.length">
          <thead class="table-light">
            <tr><th>Drive Title</th><th>Status</th><th class="text-end">Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="j in pastDrives" :key="j.id">
              <td class="fw-semibold">{{ j.title }}</td>
              <td>
                <span class="badge"
                  :class="{
                    'bg-danger': j.status === 'rejected',
                    'bg-dark': j.status === 'blacklisted',
                    'bg-secondary': j.status === 'closed'
                  }"
                >{{ j.status.toUpperCase() }}</span>
              </td>
              <td class="text-end">
                <button @click="viewDriveDetails(j)" class="btn btn-outline-info btn-sm me-2">View Details</button>
                <button @click="viewApplicants(j)" class="btn btn-outline-primary btn-sm me-2">View Applicants</button>
                <button
                  v-if="j.status === 'rejected'"
                  @click="editJob(j)" 
                  class="btn btn-warning btn-sm me-2">
                  Edit &amp; Resubmit
                </button>
                <button
                  v-if="j.status === 'closed'"
                  @click="reopenJob(j.id)"
                  class="btn btn-outline-success btn-sm">
                  Reopen Drive
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-muted">No rejected or closed drives.</div>
      </div>
    </div>

    <div v-if="activeJobForApplicants" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold">Applicants for {{ activeJobForApplicants.title }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="activeJobForApplicants = null"></button>
          </div>
          <div class="modal-body p-4">
            
            <div class="row">
              <div class="col-md-5 border-end">
                <input v-model="searchApplicants" placeholder="Search applicants by name..." class="form-control mb-3" />
                <div class="list-group" style="max-height: 400px; overflow-y: auto;">
                  <button 
                    v-for="app in filteredApplicants"
                    :key="app.application_id"
                    @click="selectedApplicant = app"
                    class="list-group-item list-group-item-action"
                    :class="{ 'active': selectedApplicant && selectedApplicant.application_id === app.application_id }"
                  >
                    <div class="d-flex justify-content-between align-items-center">
                      <span class="fw-bold">{{ app.student_name }}</span>
                      <span class="badge"
                        :class="{
                          'bg-secondary': app.status === 'applied',
                          'bg-info': app.status === 'shortlisted' || app.status === 'interview',
                          'bg-success': app.status === 'selected',
                          'bg-danger': app.status === 'rejected'
                        }"
                      >{{ app.status }}</span>
                    </div>
                    <div class="small" :class="{ 'text-light': selectedApplicant && selectedApplicant.application_id === app.application_id, 'text-muted': !(selectedApplicant && selectedApplicant.application_id === app.application_id) }">
                      Applied: {{ app.date }}
                    </div>
                  </button>
                  <div v-if="!filteredApplicants.length" class="text-muted p-3 text-center">No applicants found.</div>
                </div>
              </div>

              <div class="col-md-7">
                <div v-if="selectedApplicant" class="p-3 bg-light rounded h-100">
                  <h4 class="fw-bold border-bottom pb-2 mb-3">{{ selectedApplicant.student_name }}'s Profile</h4>
                  <p><strong>Email:</strong> {{ selectedApplicant.student_email }}</p>
                  <p><strong>Roll Number:</strong> {{ selectedApplicant.student_roll_number }}</p>
                  <p><strong>Batch:</strong> {{ selectedApplicant.student_batch }}</p>
                  <p><strong>Department:</strong> {{ selectedApplicant.student_department }}</p>
                  <p><strong>Education:</strong> {{ selectedApplicant.education }}</p>
                  <p><strong>Skills:</strong> {{ selectedApplicant.skills }}</p>
                  <p><strong>Resume Link:</strong> 
                    <a v-if="selectedApplicant.resume !== 'N/A'" :href="selectedApplicant.resume" target="_blank">View Resume</a>
                    <span v-else>N/A</span>
                  </p>

                  <div class="card mt-4 border-info">
                    <div class="card-header bg-info text-dark fw-bold d-flex justify-content-between align-items-center">
                      <span>Update Candidate Status</span>
                      <span class="badge bg-dark">Current: {{ selectedApplicant.status }}</span>
                    </div>
                    <div class="card-body">
                      <div class="d-flex gap-2 flex-wrap">
                        <button v-if="selectedApplicant.status !== 'shortlisted'" @click="updateAppStatus(selectedApplicant.application_id, 'shortlisted')" class="btn btn-outline-primary btn-sm flex-fill">Shortlist</button>
                        <button v-if="selectedApplicant.status !== 'interview'" @click="updateAppStatus(selectedApplicant.application_id, 'interview')" class="btn btn-outline-warning btn-sm flex-fill">Call Interview</button>
                        <button v-if="selectedApplicant.status !== 'selected'" @click="updateAppStatus(selectedApplicant.application_id, 'selected')" class="btn btn-success btn-sm flex-fill">Hire (Selected)</button>
                        <button v-if="selectedApplicant.status !== 'rejected'" @click="updateAppStatus(selectedApplicant.application_id, 'rejected')" class="btn btn-danger btn-sm flex-fill">Reject</button>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="d-flex justify-content-center align-items-center h-100 text-muted">
                  Select an applicant from the list to view their full profile.
                </div>
              </div>
            </div>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary px-4" @click="activeJobForApplicants = null">Close Viewer</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedDrive" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">{{ selectedDrive.title }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedDrive = null"></button>
          </div>
          <div class="modal-body p-4">
            <div class="row mb-3">
              <div class="col-sm-6"><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</div>
              <div class="col-sm-6"><strong>Salary:</strong> {{ selectedDrive.salary || 'N/A' }}</div>
            </div>
           
            <div class="row mb-3 p-2 rounded" style="background:#f8f9fa;">
              <div class="col-sm-4 text-center">
                <div class="fw-bold fs-4 text-primary">{{ selectedDrive.spots || 1 }}</div>
                <div class="text-muted small">Open Spots</div>
              </div>
              <div class="col-sm-4 text-center">
                <div class="fw-bold fs-4 text-secondary">{{ selectedDrive.total_applicants || 0 }}</div>
                <div class="text-muted small">Applied</div>
              </div>
              <div class="col-sm-4 text-center">
                <div class="fw-bold fs-4" :class="(selectedDrive.total_selected || 0) >= (selectedDrive.spots || 1) ? 'text-success' : 'text-dark'">{{ selectedDrive.total_selected || 0 }} / {{ selectedDrive.spots || 1 }}</div>
                <div class="text-muted small">Selected</div>
              </div>
            </div>
            <div class="mb-3">
              <strong>Job Type:</strong> <span class="badge bg-primary">{{ selectedDrive.type || 'N/A' }}</span>
              <span class="badge ms-2" :class="{ 'bg-success': selectedDrive.status === 'approved', 'bg-warning text-dark': selectedDrive.status === 'pending', 'bg-danger': selectedDrive.status === 'rejected' }">{{ selectedDrive.status }}</span>
            </div>
            <div class="mb-3">
              <strong class="d-block border-bottom pb-1 mb-2">Description</strong>
              <div style="white-space: pre-wrap">{{ selectedDrive.description || 'Not provided' }}</div>
            </div>
            <div class="mb-3">
              <strong class="d-block border-bottom pb-1 mb-2">Requirements</strong>
              <div style="white-space: pre-wrap">{{ selectedDrive.requirements || 'Not provided' }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedDrive = null">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      stats: {},
      jobs: [],
      profile: {},
      profileEdit: {},
      isEditingProfile: false,
      selectedDrive: null,
      searchDrives: '',
      searchApplicants: '',
      activeJobForApplicants: null,
      applicants: [],
      selectedApplicant: null
    }
  },
  computed: {
    activeDrives() {
      const q = this.searchDrives.toLowerCase();
      const active = this.jobs.filter(j => j.status === 'pending' || j.status === 'approved');
      if (!q) return active;
      return active.filter(j => j.title && j.title.toLowerCase().includes(q));
    },
    pastDrives() {
      return this.jobs.filter(j => j.status === 'rejected' || j.status === 'blacklisted' || j.status === 'closed');
    },
    filteredApplicants() {
      const q = this.searchApplicants.toLowerCase()
      if (!q) return this.applicants
      return this.applicants.filter(a => a.student_name && a.student_name.toLowerCase().includes(q))
    }
  },
  async mounted() {
    this.fetchData()
    this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      try {
        const res = await axios.get('http://127.0.0.1:5000/api/company/profile', { withCredentials: true })
        this.profile = res.data
      } catch (e) { console.error(e) }
    },
    toggleEditProfile() {
      this.isEditingProfile = !this.isEditingProfile
      if (this.isEditingProfile) {
        this.profileEdit = { ...this.profile }
      }
    },
    async saveProfile() {
      try {
        await axios.post('http://127.0.0.1:5000/api/company/profile', this.profileEdit, { withCredentials: true })
        this.isEditingProfile = false
        this.fetchProfile()
        this.fetchData()
        alert('Profile saved successfully!')
      } catch (e) {
        alert('Failed to save profile.')
      }
    },
    viewDriveDetails(j) {
      this.selectedDrive = j
    },
    async fetchData() {
      try {
        const stats = await axios.get('http://127.0.0.1:5000/api/company/dashboard', { withCredentials: true })
        this.stats = stats.data

        const jobs = await axios.get('http://127.0.0.1:5000/api/company/jobs', { withCredentials: true })
        this.jobs = jobs.data
      } catch (e) {
        if (e.response && e.response.status === 401) this.$router.push('/')
      }
    },
    editJob(j) {
      sessionStorage.setItem('editJob', JSON.stringify(j));
      this.$router.push({ path: '/company/create-job', query: { edit: j.id } });
    },
    async closeJob(id) {
      if (confirm('Are you sure you want to completely close this job drive?')) {
        await axios.post(`http://127.0.0.1:5000/api/company/close_job/${id}`, {}, { withCredentials: true })
        this.fetchData()
      }
    },
    async viewApplicants(job) {
      this.activeJobForApplicants = job
      this.selectedApplicant = null
      this.searchApplicants = ''
      await this.fetchApplicants(job.id)
    },
    async fetchApplicants(jobId) {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/company/applications/${jobId}`, { withCredentials: true })
        this.applicants = res.data
        // Auto-update selected applicant if they are currently being viewed to refresh status
        if (this.selectedApplicant) {
            this.selectedApplicant = this.applicants.find(a => a.application_id === this.selectedApplicant.application_id)
        }
      } catch (err) {
        console.error(err)
      }
    },
    async updateAppStatus(appId, status) {
      try {
        await axios.post(`http://127.0.0.1:5000/api/company/update_application/${appId}`, { status }, { withCredentials: true })
        // Show success popup then deselect applicant and refresh list
        const label = { shortlisted: 'Shortlisted', interview: 'Called for Interview', selected: 'Hired / Selected', rejected: 'Rejected' }[status] || status
        alert(`✅ Candidate has been marked as: ${label}`)
        this.selectedApplicant = null
        await this.fetchApplicants(this.activeJobForApplicants.id)
        this.fetchData() // Refresh stats in background
      } catch (err) {
        // Show specific backend error (e.g. spots limit hit)
        alert(err.response?.data?.message || 'Failed to update status')
      }
    },
    async reopenJob(id) {
      if (confirm('Reopen this drive? It will go back to Admin for approval.')) {
        try {
          await axios.post(`http://127.0.0.1:5000/api/company/reopen_job/${id}`, {}, { withCredentials: true })
          alert('Drive resubmitted for admin approval!')
          this.fetchData()
        } catch (err) {
          alert(err.response?.data?.message || 'Failed to reopen drive')
        }
      }
    },
    async exportData() {
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/company/export', {}, { withCredentials: true })
        if (res.data.task_id) {
          alert("Batch job submitted to queue. You will be alerted when complete.")
          this.pollExportTask(res.data.task_id)
        }
      } catch (e) {
        console.error(e)
      }
    },
    pollExportTask(taskId) {
      const interval = setInterval(async () => {
        try {
          const res = await axios.get(`http://127.0.0.1:5000/api/company/export/status/${taskId}`, { withCredentials: true })
          if (res.data.status === 'SUCCESS') {
            clearInterval(interval)
            alert("Export processing complete! The batch system has securely saved your Report to the system root's export folder.")
          } else if (res.data.status === 'FAILURE') {
            clearInterval(interval)
            alert("Export background task failed.")
          }
        } catch (e) {
            clearInterval(interval)
        }
      }, 2000)
    },
    async logout() {
      try {
        await axios.get('http://127.0.0.1:5000/api/logout', { withCredentials: true })
      } catch (e) {
        console.error(e)
      } finally {
        this.$router.push('/')
      }
    }
  }
}
</script>
