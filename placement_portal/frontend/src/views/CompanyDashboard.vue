<template>
  <div class="container mt-4">
    <h2>Company Dashboard</h2>

    <p>Total Jobs: {{ stats.jobs }}</p>
    <p>Total Applications: {{ stats.applications }}</p>

    <h4>Create Job</h4>
    <input v-model="job.title" placeholder="Title" class="form-control mb-2" />
    <input v-model="job.location" placeholder="Location" class="form-control mb-2" />
    <button @click="createJob" class="btn btn-primary">Post Job</button>

    <h4 class="mt-4">Jobs</h4>
    <ul>
      <li v-for="j in jobs" :key="j.id">
        {{ j.title }} - {{ j.status }}
        <button @click="closeJob(j.id)">Close</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      stats: {},
      jobs: [],
      job: { title: '', location: '' }
    }
  },
  async mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      const stats = await axios.get('http://127.0.0.1:5000/api/company/dashboard', { withCredentials: true })
      this.stats = stats.data

      const jobs = await axios.get('http://127.0.0.1:5000/api/company/jobs', { withCredentials: true })
      this.jobs = jobs.data
    },

    async createJob() {
      await axios.post('http://127.0.0.1:5000/api/company/create_job', this.job, { withCredentials: true })
      this.fetchData()
    },

    async closeJob(id) {
      await axios.post(`http://127.0.0.1:5000/api/company/close_job/${id}`, {}, { withCredentials: true })
      this.fetchData()
    }
  }
}
</script>
