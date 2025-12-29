<!-- frontend/src/components/TimeEventRegister.vue -->
<template>
  <div class="register-event">
    <h2>Register event</h2>
    <form @submit.prevent="registerEvent">
      <select v-model="form.employee">
        <option v-for="emp in employees" :key="emp.id" :value="emp.id">
          {{ emp.name }} {{ emp.surname }}
        </option>
      </select>
      
      <select v-model="form.event_type">
        <option value="CHECK_IN">Check in</option>
        <option value="CHECK_OUT">Check out</option>
        <option value="BREAK_START">Break start</option>
        <option value="BREAK_END">Break end</option>
      </select>
      
      <button type="submit">Submit</button>
    </form>
    
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../api/client'

const employees = ref([])
const form = ref({
  employee: null,
  event_type: 'CHECK_IN'
})
const error = ref(null)

onMounted(async () => {
  const response = await apiClient.get('/employees/')
  employees.value = response.data
})

const registerEvent = async () => {
  try {
    error.value = null
    const response = await apiClient.post('/time-events/register/', {
      employee: form.value.employee,
      event_type: form.value.event_type,
      device: 1
    })
    alert('Event registered!')
    console.log(response.data)
  } catch (err) {
    error.value = err.response?.data?.error || 'Registering error'
  }
}
</script>

<style scoped>
.error {
  color: red;
  margin-top: 10px;
}
</style>
