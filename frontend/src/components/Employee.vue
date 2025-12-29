<!-- frontend/src/views/EmployeeList.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const employees = ref([])

onMounted(async () => {
  try {
    const response = await apiClient.get('/employees/')
    employees.value = response.data
  } catch (error) {
    console.error('Error downloading employees:', error)
  }
})
</script>

<template>
  <div>
    <h2>Employees</h2>
    <ul>
      <li v-for="emp in employees" :key="emp.id">
        {{ emp.name }} {{ emp.surname }}
      </li>
    </ul>
  </div>
</template>
