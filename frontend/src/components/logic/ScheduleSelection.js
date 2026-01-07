import { ref, computed } from 'vue'

export function use_schedule_selection(schedules) {
    const selected_items = ref([])
    const all_selected = computed(() => {
        return schedules.value.length > 0 && 
            selected_items.value.length === schedules.value.length
    })
    // const has_selection = computed(() => {
    //     return selectedItems.value.length > 0
    // })

    function is_selected(schedule_id) {
        return selected_items.value.includes(schedule_id)
    }

    function toggle_selection(schedule_id) {
        const index = selected_items.value.indexOf(schedule_id)
        if (index > -1) {
            selected_items.value.splice(index, 1)
        } else {
            selected_items.value.push(schedule_id)
        }
    }

    function toggle_select_all() {
        if (all_selected.value) {
            selected_items.value = []
        } else {
            selected_items.value = schedules.value.map(s => s.id)
        }
    }

    function clear_selection() {
        selected_items.value = []
    }

    return {
        selected_items,
        all_selected,
        // has_selection,
        is_selected,
        toggle_selection,
        toggle_select_all,
        clear_selection
    }
}