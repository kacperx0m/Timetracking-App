import { ref } from 'vue'
import { schedule_api } from './Schedule'
import { format_date, generate_days_array } from './DateFormatter'

const DEFAULT_WORK_HOURS = {
  start: '08:00',
  end: '16:00'
}

export function use_schedule_form(onSuccess) {
    const show_form = ref(false)
    const editing_schedule = ref(null)
    const form_data = ref(create_empty_form())
    const loading = ref(false)
    const error = ref(null)

    const bulk_add = ref(false)

    function create_empty_form(employee_id = null) {
        return {
            employee: employee_id,
            date: '',
            date_start: '',
            date_end: '',
            day_type: 'WORK',
            time_start: DEFAULT_WORK_HOURS.start,
            time_end: DEFAULT_WORK_HOURS.end
        }
    }

    function open_bulk_form(employee_id = null) {
        show_form.value = true
        editing_schedule.value = null
        bulk_add.value = true
        form_data.value = create_empty_form(employee_id)
        error.value = null
    }

    function open_add_form(employee_id) {
        show_form.value = true
        editing_schedule.value = null
        bulk_add.value = false
        form_data.value = create_empty_form(employee_id)
    }

    function edit_schedule(schedule) {
        show_form.value = true
        editing_schedule.value = schedule
        form_data.value = {
            employee: schedule.employee,
            date: schedule.date,
            day_type: schedule.day_type,
            time_start: schedule.time_start || DEFAULT_WORK_HOURS.start,
            time_end: schedule.time_end || DEFAULT_WORK_HOURS.end
        }
        
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    function cancel_form() {
        show_form.value = false
        editing_schedule.value = null
        form_data.value = create_empty_form()
    }

    async function save_schedule() {
        try {
        loading.value = true
        error.value = null
        
        const data = {
            employee: form_data.value.employee,
            date: form_data.value.date,
            day_type: form_data.value.day_type,
            time_start: form_data.value.day_type === 'WORK' ? form_data.value.time_start : null,
            time_end: form_data.value.day_type === 'WORK' ? form_data.value.time_end : null
        }
        
        if (editing_schedule.value) {
            await schedule_api.update_schedule(editing_schedule.value.id, data)
            console.log('Schedule updated')
        } 
        else if (bulk_add.value) {
            console.log('=== CREATE MULTIPLE START ===')
            console.log('date_start:', form_data.value.date_start)
            console.log('date_end:', form_data.value.date_end)
            const days = generate_days_array(form_data.value.date_start, form_data.value.date_end)
            console.log('Generated days:', days)
            const data = {
                employee_id: form_data.value.employee,
                days: days,
                day_type: form_data.value.day_type,
                time_start: form_data.value.day_type === 'WORK' ? form_data.value.time_start : null,
                time_end: form_data.value.day_type === 'WORK' ? form_data.value.time_end : null
            }
        
            console.log(data)
            await schedule_api.create_schedule_days(data)
            console.log('Multiple schedules created')
        }
        else {
            console.log(data)
            await schedule_api.create_schedule(data)
            console.log('Schedule created')
        }
        
        show_form.value = false
        
        if (onSuccess) {
            await onSuccess()
        }

        } catch (err) {
            error.value = 'Save error: ' + err.message + '\nFor more information check console.'
            alert(error.value)
            console.error('Error:', err)
        } finally {
            loading.value = false
        }
    }


    async function confirm_delete_schedule(schedule) {
        const employee_name = schedule.employee_name || `ID ${schedule.employee}`
        const confirmed = confirm(
        `Are you sure you want to delete this schedule?\n\n` +
        `Date: ${format_date(schedule.date)}\n` +
        `Employee: ${employee_name}\n` +
        `Type: ${schedule.day_type}`
        )
        
        if (!confirmed) return

        try {
            loading.value = true
            error.value = null
        
            await schedule_api.delete_schedule(schedule.id)
            console.log('Schedule deleted')
        
            // TODO: uncomment?
            // await fetch_schedules()
        
            if (onSuccess) {
            await onSuccess()
        }

        } catch (err) {
            error.value = 'Delete error: ' + err.message
            console.error('Error:', err)
        } finally {
            loading.value = false
        }
    }

    return {
            show_form,
            editing_schedule,
            form_data,
            loading,
            error,
            bulk_add,
            open_bulk_form,
            open_add_form,
            edit_schedule,
            cancel_form,
            save_schedule,
            confirm_delete_schedule
        }
}