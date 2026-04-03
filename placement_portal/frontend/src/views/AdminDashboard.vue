<template>
  <div class="container mt-4">
    <h2>Admin Dashboard</h2>

    <div class="row mt-3">
      <div class="col">Students: {{ stats.students }}</div>
      <div class="col">Companies: {{ stats.companies }}</div>
      <div class="col">Jobs: {{ stats.jobs }}</div>
      <div class="col">Applications: {{ stats.applications }}</div>
    </div>

    <h4 class="mt-4">Companies</h4>
    <table class="table">
      <tr v-for="c in companies" :key="c.id">
        <td>{{ c.name }}</td>
        <td>{{ c.industry }}</td>
        <td>
          <button v-if="!c.approved" @click="approveCompany(c.id)" class="btn btn-success btn-sm">Approve</button>
          <button @click="removeCompany(c.id)" class="btn btn-danger btn-sm">Remove</button>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      stats: {},
      companies: []
    }
  },
  async mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      const stats = await axios.get('http://127.0.0.1:5000/api/admin/dashboard', { withCredentials: true })
      this.stats = stats.data

      const companies = await axios.get('http://127.0.0.1:5000/api/admin/companies', { withCredentials: true })
      this.companies = companies.data
    },

    async approveCompany(id) {
      await axios.post(`http://127.0.0.1:5000/api/admin/approve_company/${id}`, {}, { withCredentials: true })
      this.fetchData()
    },

    async removeCompany(id) {
      await axios.delete(`http://127.0.0.1:5000/api/admin/remove_company/${id}`, { withCredentials: true })
      this.fetchData()
    }
  }
}
</script>
