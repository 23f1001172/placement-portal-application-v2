<template>
  <div class="container mt-4">
    <h2>Student Dashboard</h2>

    <input v-model="search" placeholder="Search jobs" class="form-control mb-3" />
    <button @click="searchJobs" class="btn btn-secondary mb-3">Search</button>

    <h4>Available Jobs</h4>
    <ul>
      <li v-for="j in jobs" :key="j.id">
        {{ j.title }} - {{ j.company }}
        <button @click="apply(j.id)" class="btn btn-sm btn-primary">Apply</button>
      </li>
    </ul>

    <h4 class="mt-4">My Applications</h4>
    <button @click="exportData" class="btn btn-warning mb-3">
      Export Applications
    </button>
    <ul>
      <li v-for="a in applications" :key="a.job">
        {{ a.job }} - {{ a.company }}
        <br />
        Status: <b>{{ a.status }}</b> | Applied on: {{ a.date }}
      </li>

    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      jobs: [],
      applications: [],
      search: ''
    }
  },
  async mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      const jobs = await axios.get('http://127.0.0.1:5000/api/student/jobs', { withCredentials: true })
      this.jobs = jobs.data

      const apps = await axios.get('http://127.0.0.1:5000/api/student/applications', { withCredentials: true })
      this.applications = apps.data
    },

    async apply(id) {
      await axios.post(`http://127.0.0.1:5000/api/student/apply/${id}`, {}, { withCredentials: true })
      this.fetchData()
    },

    async searchJobs() {
      const res = await axios.get(`http://127.0.0.1:5000/api/student/search?q=${this.search}`, { withCredentials: true })
      this.jobs = res.data
    },

    async exportData() {
     await axios.post(
        'http://127.0.0.1:5000/api/student/export',
    {},
    { withCredentials: true }
    )
    alert("Export started. Check exports folder later.")
    }
  }
}
</script>
