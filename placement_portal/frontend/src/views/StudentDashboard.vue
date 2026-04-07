<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Student Dashboard</h2>
      <button @click="logout" class="btn btn-danger">Logout</button>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-info text-white fw-bold py-2">
        <i class="bi-person-circle"></i> My Profile
      </div>
      <div class="card-body">
        <div v-if="!isEditingProfile">
          <p><strong>Name:</strong> {{ profile.name }}</p>
          <p><strong>Email:</strong> {{ profile.email }}</p>
          <p><strong>Roll Number:</strong> {{ profile.roll_number || 'Not set' }}</p>
          <p><strong>Batch:</strong> {{ profile.batch || 'Not set' }}</p>
          <p><strong>Department:</strong> {{ profile.department || 'Not set' }}</p>
          <p><strong>Education:</strong> {{ profile.education || 'Not set' }}</p>
          <p><strong>Skills:</strong> {{ profile.skills || 'Not set' }}</p>
          <p><strong>Current CGPA:</strong> <span class="badge bg-secondary">{{ profile.cgpa || '0.0' }}</span></p>
          <p><strong>Resume:</strong> 
            <a v-if="profile.resume && profile.resume !== 'Not set'" :href="profile.resume" target="_blank" class="btn btn-sm btn-outline-primary">View My Submitted PDF</a>
            <span v-else class="text-muted">No PDF Uploaded</span>
          </p>
          <button @click="editProfile" class="btn btn-sm btn-primary mt-2">Edit Profile Details</button>
        </div>
        <div v-else>
          <form @submit.prevent="updateProfile" enctype="multipart/form-data">
            <div class="mb-2"><label class="fw-bold">Roll Number</label><input v-model="profileEdit.roll_number" class="form-control" placeholder="E.g. 23F1001172" /></div>
            <div class="mb-2"><label class="fw-bold">Batch (Graduation Year)</label><input v-model.number="profileEdit.batch" type="number" min="2000" max="2100" class="form-control" placeholder="E.g. 2025" required /></div>
            <div class="mb-2"><label class="fw-bold">Department</label><input v-model="profileEdit.department" class="form-control" placeholder="E.g. Computer Science" /></div>
            <div class="mb-2"><label class="fw-bold">Education</label><input v-model="profileEdit.education" class="form-control" required /></div>
            <div class="mb-2"><label class="fw-bold">Skills / Tech Stack</label><input v-model="profileEdit.skills" class="form-control" required /></div>
            <div class="mb-2"><label class="fw-bold">Current CGPA (0.00 - 10.00)</label><input v-model.number="profileEdit.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" required /></div>
            <div class="mb-3">
                <label class="fw-bold d-block">Upload PDF Resume</label>
                <input type="file" class="form-control" accept=".pdf" @change="handleFileUpload" />
                <small class="text-muted">Uploading a new file overrides your previous resume.</small>
            </div>
            <button type="submit" class="btn btn-success btn-sm me-2">Save Changes</button>
            <button type="button" @click="isEditingProfile = false" class="btn btn-secondary btn-sm">Cancel</button>
          </form>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white fw-bold py-2">
        <i class="bi-briefcase"></i> Available Job Drives
      </div>
      <div class="card-body">
        <div class="d-flex mb-3">
          <input v-model="search" @input="filterJobs" placeholder="Search jobs by role or company..." class="form-control me-2" style="max-width: 400px;" />
          <button @click="filterJobs" class="btn btn-dark">Search</button>
        </div>

        <table class="table table-hover">
          <thead class="table-light">
            <tr><th>Role</th><th>Company</th><th>Location</th><th>Salary</th><th>Spots</th><th>Applicants</th><th>Selected</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="j in availableJobs" :key="j.id">
              <td class="fw-bold">{{ j.title }}</td>
              <td>{{ j.company }}</td>
              <td>{{ j.location }}</td>
              <td>{{ j.salary }}</td>
              <td><span class="badge bg-primary">{{ j.spots }}</span></td>
              <td><span class="badge bg-secondary">{{ j.total_applicants }}</span></td>
              <td><span class="badge bg-success">{{ j.total_selected }}</span></td>
              <td>
                <button @click="viewJobDetails(j)" class="btn btn-sm btn-outline-info me-2">View Details</button>
                <button @click="apply(j.id)" class="btn btn-sm btn-success">Apply Now</button>
              </td>
            </tr>
            <tr v-if="!availableJobs.length"><td colspan="8" class="text-center text-muted">No available drives. Check your Applications below.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-secondary text-white fw-bold py-2 d-flex justify-content-between align-items-center">
        <span><i class="bi-file-earmark-check"></i> My Applications</span>
        <button @click="exportData" class="btn btn-sm btn-warning fw-bold">Export Status Report <i class="bi-download"></i></button>
      </div>
      <div class="card-body">
        <table class="table">
          <thead>
            <tr><th>Role</th><th>Company</th><th>Applied On</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in applications" :key="a.job_id">
              <td class="fw-bold">{{ a.job }}</td>
              <td>{{ a.company }}</td>
              <td>{{ a.date }}</td>
              <td>
                <span class="badge"
                  :class="{
                    'bg-warning text-dark': a.status === 'applied' || a.status === 'pending',
                    'bg-info text-dark': a.status === 'shortlisted' || a.status === 'interview',
                    'bg-success': a.status === 'selected',
                    'bg-danger': a.status === 'rejected',
                  }"
                >{{ a.status }}</span>
              </td>
              <td>
                <button @click="viewAppliedJobDetails(a.job_id)" class="btn btn-sm btn-outline-secondary">View Drive</button>
              </td>
            </tr>
            <tr v-if="!applications.length"><td colspan="5" class="text-center text-muted">You haven't applied to any drives yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedJob" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">{{ selectedJob.title }} at {{ selectedJob.company }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedJob = null"></button>
          </div>
          <div class="modal-body p-4">
            <div class="row mb-3">
              <div class="col-sm-6"><strong>Location:</strong> {{ selectedJob.location }}</div>
              <div class="col-sm-6"><strong>Salary Package:</strong> {{ selectedJob.salary }}</div>
            </div>
            <div class="row mb-3">
              <div class="col-sm-4"><strong>Open Spots:</strong> <span class="badge bg-primary">{{ selectedJob.spots }}</span></div>
              <div class="col-sm-4"><strong>Applicants:</strong> <span class="badge bg-secondary">{{ selectedJob.total_applicants }}</span></div>
              <div class="col-sm-4"><strong>Selected:</strong> <span class="badge bg-success">{{ selectedJob.total_selected }}</span></div>
            </div>
            <div class="row mb-3 border-top pt-2">
              <div class="col-sm-3"><strong>Min CGPA:</strong> <span class="badge bg-warning text-dark">{{ selectedJob.min_cgpa }}</span></div>
              <div class="col-sm-3"><strong>Branch:</strong> <span class="badge bg-info text-dark">{{ selectedJob.required_branch }}</span></div>
              <div class="col-sm-3"><strong>Batch:</strong> <span class="badge bg-primary">{{ selectedJob.required_batch }}</span></div>
              <div class="col-sm-3"><strong>Deadline:</strong> <span class="badge bg-danger">{{ formatDate(selectedJob.deadline) }}</span></div>
            </div>
            <div class="mb-3 d-flex gap-3">
              <div><strong>Job Type:</strong> <span class="badge bg-primary">{{ selectedJob.type }}</span></div>
              <div v-if="selectedJob.status && selectedJob.status !== 'approved'">
                <strong>Drive Status:</strong>
                <span class="badge" :class="{ 'bg-danger': selectedJob.status === 'rejected' || selectedJob.status === 'blacklisted', 'bg-secondary': selectedJob.status === 'closed' }">
                  {{ selectedJob.status.toUpperCase() }}
                </span>
              </div>
            </div>
            <div class="mb-3">
              <strong class="d-block border-bottom pb-1 mb-2">Job Description</strong>
              <div style="white-space: pre-wrap">{{ selectedJob.description }}</div>
            </div>
            <div class="mb-3">
              <strong class="d-block border-bottom pb-1 mb-2">Requirements</strong>
              <div style="white-space: pre-wrap">{{ selectedJob.requirements }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedJob = null">Close</button>
            <button v-if="!isAlreadyApplied(selectedJob.id)" type="button" class="btn btn-success" @click="applyAndClose(selectedJob.id)">Apply Now</button>
            <span v-else class="badge bg-secondary p-2">Already Applied</span>
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
      jobs: [],
      applications: [],
      search: '',
      searchFilter: '',
      profile: {},
      isEditingProfile: false,
      profileEdit: {},
      selectedJob: null,
      selectedFile: null
    }
  },
  computed: {
    availableJobs() {
      if (!this.jobs) return [];
      const appliedJobIds = this.applications.map(a => a.job_id);
      const available = this.jobs.filter(j => !appliedJobIds.includes(j.id));
      if (!this.searchFilter) return available;
      const q = this.searchFilter.toLowerCase();
      return available.filter(j =>
        (j.title && j.title.toLowerCase().includes(q)) ||
        (j.company && j.company.toLowerCase().includes(q))
      );
    }
  },
  async mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const profileReq = await axios.get('http://127.0.0.1:5000/api/student/profile', { withCredentials: true })
        this.profile = profileReq.data

        const jobsReq = await axios.get('http://127.0.0.1:5000/api/student/jobs', { withCredentials: true })
        this.jobs = jobsReq.data

        const appsReq = await axios.get('http://127.0.0.1:5000/api/student/applications', { withCredentials: true })
        this.applications = appsReq.data
      } catch (e) {
        console.error(e)
        if (e.response && e.response.status === 401) this.$router.push('/')
      }
    },

    editProfile() {
      this.profileEdit = {
        roll_number: this.profile.roll_number !== 'Not set' ? this.profile.roll_number : '',
        batch: this.profile.batch !== 'Not set' ? this.profile.batch : '',
        department: this.profile.department !== 'Not set' ? this.profile.department : '',
        education: this.profile.education !== 'Not set' ? this.profile.education : '',
        skills: this.profile.skills !== 'Not set' ? this.profile.skills : '',
        cgpa: this.profile.cgpa || 0.0
      }
      this.selectedFile = null
      this.isEditingProfile = true
    },

    handleFileUpload(event) {
      this.selectedFile = event.target.files[0]
    },

    async updateProfile() {
      try {
        // Sensible Validation
        if (this.profileEdit.cgpa < 0 || this.profileEdit.cgpa > 10) {
          alert("Please enter a sensible CGPA between 0 and 10.");
          return;
        }
        if (this.profileEdit.batch < 1900 || this.profileEdit.batch > 2100) {
          alert("Please enter a sensible Graduation Year (e.g., 2025).");
          return;
        }

        const formData = new FormData()
        formData.append('roll_number', this.profileEdit.roll_number)
        formData.append('batch', this.profileEdit.batch || '')
        formData.append('department', this.profileEdit.department)
        formData.append('education', this.profileEdit.education)
        formData.append('skills', this.profileEdit.skills)
        formData.append('cgpa', this.profileEdit.cgpa)
        if (this.selectedFile) {
            formData.append('resume', this.selectedFile)
        }

        await axios.post('http://127.0.0.1:5000/api/student/update_profile', formData, { 
            withCredentials: true,
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.isEditingProfile = false
        this.fetchData()
      } catch (err) {
        console.error(err)
        if(err.response && err.response.data.message) {
          alert(err.response.data.message)
        } else {
          alert('Failed to update profile.')
        }
      }
    },

    viewJobDetails(job) {
      this.selectedJob = job;
    },

    viewAppliedJobDetails(jobId) {
      // Search full jobs list (includes closed drives, not just available ones)
      const found = this.jobs.find(j => j.id === jobId);
      if (found) {
        this.selectedJob = found;
      } else {
        // Drive not in main list at all — fetch directly from backend
        axios.get(`http://127.0.0.1:5000/api/student/job/${jobId}`, { withCredentials: true })
          .then(res => { this.selectedJob = res.data })
          .catch(() => alert('Drive details could not be loaded.'))
      }
    },

    isAlreadyApplied(jobId) {
      return this.applications.some(a => a.job_id === jobId);
    },

    async apply(id) {
      try {
        await axios.post(`http://127.0.0.1:5000/api/student/apply/${id}`, {}, { withCredentials: true })
        alert("Applied successfully!")
        this.fetchData()
      } catch (err) {
        if(err.response && err.response.data.message) {
          alert(err.response.data.message)
        }
      }
    },

    async applyAndClose(id) {
      await this.apply(id)
      this.selectedJob = null
    },

    filterJobs() {
      this.searchFilter = this.search;
    },

    async searchJobs() {
      this.filterJobs();
    },

    async exportData() {
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/student/export', {}, { withCredentials: true })
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
          const res = await axios.get(`http://127.0.0.1:5000/api/student/export/status/${taskId}`, { withCredentials: true })
          if (res.data.status === 'SUCCESS') {
            clearInterval(interval)
            alert("Export processing complete! The batch system has securely saved your .csv to the system root's export folder.")
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
    },
    formatDate(dateStr) {
      if (!dateStr) return "No deadline set";
      const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateStr).toLocaleString(undefined, options);
    }
  }
}
</script>
