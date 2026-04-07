<template>
  <div class="container mt-5">
    <h3>Login</h3>

    <input v-model="email" placeholder="Email" class="form-control mb-2" />
    <input v-model="password" type="password" placeholder="Password" class="form-control mb-2" />

    <button @click="login" class="btn btn-primary">Login</button>
    <div class="mt-3">
      <router-link to="/register">Register as a company or student</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/login', {
          email: this.email,
          password: this.password
        }, { withCredentials: true })

        const role = res.data.role

        if (role === 'admin') this.$router.push('/admin')
        else if (role === 'company') this.$router.push('/company')
        else this.$router.push('/student')

      } catch (err) {
        alert(err.response.data.message)
      }
    }
  }
}
</script>
