import axios from 'axios'
import api from 'axios'

const API_BASE_URL = "http://127.0.0.1:8000"

const api_client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

api_client.interceptors.request.use(config => {
    const token = localStorage.getItem("auth_token")
    if (token) {
        config.headers.Authorization = `Token ${token}`
    }
    return config
})

api_client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 400) {
      const errorData = error.response.data
      const errorStr = JSON.stringify(errorData).toLowerCase()
      
      if (errorStr.includes('already exists') || errorStr.includes('does exist')) {
        error.message = 'Schedule for this employee already exists'
      }
    }
    
    return Promise.reject(error)
  }
)

export const schedule_api = {
    get_schedule_days() {
        return api_client.get(`${API_BASE_URL}/schedule/`)
    },

    get_employee_schedule_range(employee_id, start_date, end_date) {
        return api_client.get(`${API_BASE_URL}/schedule/get_employee_schedule_range/`,
            {params: {
                employee_id: employee_id,
                start_date: start_date,
                end_date: end_date
            }}
        )
    },

    create_schedule(data) {
        return api_client.post(`${API_BASE_URL}/schedule/`, data)
    },

    create_schedule_days(data) {
        return api_client.post(`${API_BASE_URL}/schedule/create_multiple/`, data)
    },

    update_schedule(id, data) {
        return api_client.put(`${API_BASE_URL}/schedule/${id}/`, data)
    },

    update_schedule_days(ids, day_type, time_start, time_end) {
        return api_client.post(`${API_BASE_URL}/schedule/update_multiple/`, 
            {schedule_ids: ids,
            day_type: day_type,
            time_start: time_start,
            time_end: time_end}
        )
    },

    delete_schedule(id) {
        return api_client.delete(`${API_BASE_URL}/schedule/${id}/`)
    },

    delete_schedule_days(ids) {
        return api_client.post(`${API_BASE_URL}/schedule/delete_multiple/`, {
            schedule_ids: ids})
    },
}

export function get_employees() {
    return api_client.get(`${API_BASE_URL}/employees/`)
}