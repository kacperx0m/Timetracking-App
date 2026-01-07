import { ref } from 'vue'
import { schedule_api } from './Schedule'
import { get_today_date_before_days, get_today_date_after_days } from './DateFormatter'

export function use_schedule_filters() {
    const selected_employee = ref(null)
    const start_date = ref(get_today_date_before_days(14))
    const end_date = ref(get_today_date_after_days(14))
    const schedules = ref([])
    const loading = ref(false)
    const error = ref(null)
  

    async function fetch_schedules() {
        try {
        loading.value = true
        error.value = null
        
        if (selected_employee.value && start_date.value && end_date.value) {
            console.log('Filtering:', {
            employee: selected_employee.value,
            start: start_date.value,
            end: end_date.value
            })
            
            const response = await schedule_api.get_employee_schedule_range(
            selected_employee.value,
            start_date.value,
            end_date.value
            )
            
            schedules.value = response.data
        } 
        else if (selected_employee.value) {
            console.log('Filtering:', {
            employee: selected_employee.value,
            })
            
            const response = await schedule_api.get_employee_schedule_range(
            selected_employee.value,
            start_date.value,
            end_date.value
            )
            
            schedules.value = response.data
        } 
        else if (start_date.value && end_date.value) {
            console.log('Filtering:', {
            start: start_date.value,
            end: end_date.value
            })
            
            const response = await schedule_api.get_employee_schedule_range(
            selected_employee.value,
            start_date.value,
            end_date.value
            )

            schedules.value = response.data
        }
        else {
            const response = await schedule_api.get_schedule_days()
            schedules.value = response.data
        }
        
        console.log('Obtained schedules:', schedules.value)
        
        } catch (err) {
        error.value = 'Error obtaining data: ' + err.message
        console.error('Error:', err)
        } finally {
        loading.value = false
        }
    }

    return {
        selected_employee,
        start_date,
        end_date,
        schedules,
        loading,
        error,
        fetch_schedules,
    }
}