<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-primary text-white py-3">
            <h4 class="mb-0 fw-bold"><i class="bi-briefcase-fill me-2"></i>{{ isEdit ? 'Edit Drive' : 'Post New Job Drive' }}</h4>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="submitForm">
              <div class="mb-3">
                <label class="form-label fw-bold">Job Title / Role</label>
                <input v-model="job.title" class="form-control" placeholder="e.g. Software Engineer" required />
              </div>
              <div class="mb-3">
                <label class="form-label fw-bold">Job Description</label>
                <textarea v-model="job.description" class="form-control" rows="3" placeholder="Describe the role comprehensively..." required></textarea>
              </div>
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-bold">Location</label>
                  <input v-model="job.location" class="form-control" placeholder="e.g. Mumbai / Remote" required />
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-bold">Salary Package</label>
                  <input v-model="job.salary" class="form-control" placeholder="e.g. 12 LPA" required />
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label fw-bold">Job Type</label>
                  <select v-model="job.type" class="form-select" required>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
              </div>
              <div class="mb-4">
                <label class="form-label fw-bold">Requirements / Qualifications</label>
                <textarea v-model="job.requirements" class="form-control" rows="3" placeholder="List required skills (e.g. React, Python, 8.0 CGPA minimum)"></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-4">
                  <label class="form-label fw-bold"><i class="bi-person-badge me-1"></i>Min CGPA Required</label>
                  <input v-model.number="job.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="e.g. 7.5" required />
                </div>
                <div class="col-md-6 mb-4">
                  <label class="form-label fw-bold"><i class="bi-building me-1"></i>Required Branch</label>
                  <input v-model="job.required_branch" class="form-control" placeholder="e.g. CS / IT / All" required />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-4">
                  <label class="form-label fw-bold"><i class="bi-calendar-event me-1"></i>Application Deadline</label>
                  <input v-model="job.deadline" type="datetime-local" class="form-control" required />
                </div>
                <div class="col-md-3 mb-4">
                  <label class="form-label fw-bold"><i class="bi-mortarboard me-1"></i>Required Batch</label>
                  <input v-model="job.required_batch" class="form-control" placeholder="e.g. 2024 or All" required />
                </div>
                <div class="col-md-3 mb-4">
                  <label class="form-label fw-bold"><i class="bi-people me-1"></i>Vacancies</label>
                  <input v-model.number="job.spots" type="number" min="1" class="form-control" required />
                </div>
              </div>
              
              <div class="d-flex justify-content-end pt-3 border-top">
                <router-link to="/company" class="btn btn-outline-secondary me-3 px-4">Cancel</router-link>
                <button type="submit" class="btn btn-success px-4 fw-bold">{{ isEdit ? 'Update Drive Details' : 'Submit for Admin Approval' }}</button>
              </div>
            </form>
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
      isEdit: false,
      editId: null,
      job: {
        title: '',
        description: '',
        location: '',
        salary: '',
        type: 'Full-time',
        requirements: '',
        spots: 1,
        min_cgpa: 0,
        required_branch: 'All',
        required_batch: 'All',
        deadline: ''
      }
    }
  },
  mounted() {
    const id = this.$route.query.edit
    if (id) {
      this.isEdit = true;
      this.editId = id;
      const prefill = sessionStorage.getItem('editJob');
      if (prefill) {
        this.job = JSON.parse(prefill);
      }
    }
  },
  methods: {
    async submitForm() {
      this.job.salary = String(this.job.salary)

      // Salary constraint validation
      if (this.job.type !== 'Internship' && (parseFloat(this.job.salary) <= 0 || isNaN(parseFloat(this.job.salary)))) {
        alert("Only Internships can have a 0 dollar salary. Please provide a valid salary for this job type.")
        return
      }

      try {
        if (this.isEdit) {
          await axios.put(`http://127.0.0.1:5000/api/company/edit_job/${this.editId}`, this.job, { withCredentials: true })
        } else {
          await axios.post('http://127.0.0.1:5000/api/company/create_job', this.job, { withCredentials: true })
        }
        sessionStorage.removeItem('editJob')
        this.$router.push('/company')
      } catch (err) {
        console.error(err)
        alert('Failed to save job drive.')
      }
    }
  }
}
</script>
