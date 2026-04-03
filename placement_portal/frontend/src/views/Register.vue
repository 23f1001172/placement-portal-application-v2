<template>
  <div class="container mt-5">
    <h3>Register</h3>

    <input v-model="name" placeholder="Name" class="form-control mb-2" />
    <input v-model="email" placeholder="Email" class="form-control mb-2" />
    <input v-model="password" type="password" placeholder="Password" class="form-control mb-2" />

    <select v-model="role" class="form-control mb-2">
      <option value="student">Student</option>
      <option value="company">Company</option>
    </select>

    <button @click="register" class="btn btn-success">Register</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      role: 'student'
    }
  },
  methods: {
    async register() {
      try {
        await axios.post('http://127.0.0.1:5000/api/register', {
          name: this.name,
          email: this.email,
          password: this.password,
          role: this.role
        })

        alert("Registered successfully")
        this.$router.push('/')
      } catch (err) {
        alert(err.response.data.message)
      }
    }
  }
}
</script>
