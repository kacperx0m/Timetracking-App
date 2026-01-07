<!-- frontend/src/views/LoginView.vue -->
<template>
  <div class="login-view">
    <h1>Login</h1>
    
    <!-- prevents from reloading page -->
    <form @submit.prevent="login">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" required />
      </div>
      
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>
      
      <button type="submit">Login</button>
    </form>
    
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const password = ref('')
const error = ref(null)
const router = useRouter()

async function login() {
  try {
    error.value = null
    
    const response = await axios.post('http://127.0.0.1:8000/api-token-auth/', {
      username: username.value,
      password: password.value
    })
    
    const token = response.data.token
    localStorage.setItem('auth_token', token)
    
    console.log('Logged in! Token:', token)
    
    // Przekieruj do schedule
    router.push('/schedule')
    
  } catch (err) {
    error.value = 'Bad login or password'
    console.error('Login error:', err)
  }
}
</script>

<style scoped>
.login-view {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
}

form > div {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #0056b3;
}
</style>
