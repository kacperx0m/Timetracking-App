import { ref } from 'vue'
import { schedule_api } from './Schedule'

const DEFAULT_BULK_DATA = {
    day_type: 'WORK',
    time_start: '08:00',
    time_end: '16:00'
}

export function use_bulk_operations(selected_items, onSuccess) {
    const show_bulk_form = ref(false)
    const bulk_form_data = ref({ ...DEFAULT_BULK_DATA }) // ... means copy
    const loading = ref(false)
    const error = ref(null)


    function open_bulk_edit() {
        show_bulk_form.value = true
        bulk_form_data.value = {...DEFAULT_BULK_DATA}
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    function cancel_bulk_form() {
        show_bulk_form.value = false
        bulk_form_data.value = {...DEFAULT_BULK_DATA}
    }

    async function save_bulk_edit() {
        try {
            loading.value = true
            error.value = null
        
        const time_start = bulk_form_data.value.day_type === 'WORK' 
            ? bulk_form_data.value.time_start 
            : null
        const time_end = bulk_form_data.value.day_type === 'WORK' 
            ? bulk_form_data.value.time_end 
            : null
        
        await schedule_api.update_schedule_days(
            selected_items.value,
            bulk_form_data.value.day_type,
            time_start,
            time_end
        )
        
        console.log(`Updated ${selected_items.value.length} schedules`)
        
        show_bulk_form.value = false
        
        // TODO: uncomment?
        // selected_items.value = []
        // await fetch_schedules()

        if (onSuccess) {
            await onSuccess()
        }
        
        } catch (err) {
            error.value = 'Bulk update error: ' + err.message
            console.error('Error:', err)
        } finally {
            loading.value = false
        }
    }

    async function confirm_bulk_delete() {
        const confirmed = confirm(
        `Are you sure you want to delete ${selected_items.value.length} schedules?\n\n` +
        `This action cannot be undone.`
        )
        
        if (!confirmed) return
        
        try {
            loading.value = true
            error.value = null
            
            await schedule_api.delete_schedule_days(selected_items.value)
            
            console.log(`Deleted ${selected_items.value.length} schedules`)
            
            if (onSuccess) {
                await onSuccess()
            }

            // TODO: uncomment
            // selected_items.value = []
            // await fetch_schedules()
            if (onSuccess) {
            await onSuccess()
        }
        
        } catch (err) {
            error.value = 'Bulk delete error: ' + err.message
            console.error('Error:', err)
        } finally {
            loading.value = false
        }
    }

    return {
        show_bulk_form,
        bulk_form_data,
        loading,
        error,
        open_bulk_edit,
        cancel_bulk_form,
        save_bulk_edit,
        confirm_bulk_delete
    }
}