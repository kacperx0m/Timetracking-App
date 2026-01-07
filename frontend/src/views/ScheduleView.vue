<template>
  <div class="schedule-view">
    <h1>Schedule list</h1>
    
    <div class="filters">
      <div class="filter-group">
        <label>Employee:</label>
        <select v-model="selected_employee">
          <option :value="null">-- All --</option>
          <option v-for="emp in employees" :key="emp.id" :value="emp.id">
            {{ emp.name }} {{ emp.surname }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Date since:</label>
        <input type="date" v-model="start_date" />
      </div>

      <div class="filter-group">
        <label>Date untill:</label>
        <input type="date" v-model="end_date" />
      </div>

      <button @click="fetch_schedules" :disabled="loading">
        {{ loading ? 'Loading...' : 'Filter' }}
      </button>
  </div>

  <p v-if="loading">Loading...</p>

  <p v-if="error" style="color: red">{{ error }}</p>

  <div v-if="show_form" class="form-container">
      <h2>{{ editing_schedule ? 'Edit Schedule' : (bulk_add ? 'Add Multiple Schedules' : 'Add New Schedule') }}</h2>
      
      <form @submit.prevent="save_schedule">
        <div class="form-row">
          <div class="form-group">
            <label>Employee: *</label>
            <select v-model="form_data.employee" required>
              <option :value="null">-- Select --</option>
              <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                {{ emp.name }} {{ emp.surname }}
              </option>
            </select>
          </div>

          <div v-if="!bulk_add" class="form-group">
            <label>Date: *</label>
            <input type="date" v-model="form_data.date" required />
          </div>

          <div v-if="bulk_add" class="form-group">
            <label>Date since: *</label>
            <input type="date" v-model="form_data.date_start" required />
          </div>

          <div v-if="bulk_add" class="form-group">
            <label>Date to: *</label>
            <input type="date" v-model="form_data.date_end" required />
          </div>

          <div class="form-group">
            <label>Day Type: *</label>
            <select v-model="form_data.day_type" required>
              <option value="WORK">Work</option>
              <option value="OFF">Off</option>
              <option value="LEAVE">Leave</option>
            </select>
          </div>
        </div>

        <div class="form-row" v-if="form_data.day_type === 'WORK'">
          <div class="form-group">
            <label>Start Time:</label>
            <input type="time" v-model="form_data.time_start" />
          </div>

          <div class="form-group">
            <label>End Time:</label>
            <input type="time" v-model="form_data.time_end" />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-save">
            {{ editing_schedule ? 'Save Changes' : 'Add' }}
          </button>
          <button type="button" @click="cancel_form" class="btn-cancel">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <div v-if="show_bulk_form && selected_items.length > 0" class="form-container bulk-form">
      <h2>Edit Multiple Schedules ({{ selected_items.length }} selected)</h2>
      
      <form @submit.prevent="save_bulk_edit">
        <div class="form-row">
          <div class="form-group">
            <label>Day Type: *</label>
            <select v-model="bulk_form_data.day_type" required>
              <option value="WORK">Work</option>
              <option value="OFF">Off</option>
              <option value="LEAVE">Leave</option>
            </select>
          </div>

          <div class="form-group" v-if="bulk_form_data.day_type === 'WORK'">
            <label>Start Time:</label>
            <input type="time" v-model="bulk_form_data.time_start" />
          </div>

          <div class="form-group" v-if="bulk_form_data.day_type === 'WORK'">
            <label>End Time:</label>
            <input type="time" v-model="bulk_form_data.time_end" />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-save">
            Update {{ selected_items.length }} Schedules
          </button>
          <button type="button" @click="cancel_bulk_form" class="btn-cancel">
            Cancel
          </button>
        </div>
      </form>
    </div>

  <div v-if="!show_form && !loading" class="add-section">
      <button @click="open_add_form" class="btn-add">
        ➕ Add New Schedule
      </button>

      <button @click="open_bulk_form" class="btn-bulk-add">
        ➕ Add Multiple Schedules
      </button>
      
      <div v-if="selected_items.length > 0" class="bulk-actions">
        <span class="selection-info">{{ selected_items.length }} selected</span>
        <button @click="open_bulk_edit" class="btn-bulk-edit">
          ✏️ Edit Selected
        </button>
        <button @click="confirm_bulk_delete" class="btn-bulk-delete">
          🗑️ Delete Selected
        </button>
        <button @click="clear_selection" class="btn-clear">
          Clear Selection
        </button>
      </div>
    </div>


  <div v-if="!loading && schedules.length > 0">
    <h2>Days List ({{ schedules.length }})</h2>
      
    <div class="select-all">
      <label>
        <input 
          type="checkbox" 
          :checked="all_selected"
          @change="toggle_select_all"
        />
        Select All
      </label>
    </div>
      
    <ul class="schedule-list">
      <li 
        v-for="schedule in schedules" 
        :key="schedule.id" 
        class="schedule-item"
        :class="{ selected: is_selected(schedule.id) }"
      >
        <div class="schedule-checkbox">
          <input 
            type="checkbox" 
            :checked="is_selected(schedule.id)"
            @change="toggle_selection(schedule.id)"
          />
        </div>
        
        <div class="schedule-info">
          <strong>{{ format_date(schedule.date) }}</strong> - 
          {{ schedule.day_type }} 
          <span v-if="schedule.time_start">
            ({{ schedule.time_start }} - {{ schedule.time_end }})
          </span>
          <span v-if="schedule.employee" class="employee-badge">
            {{ employees[schedule.employee-1].name }}
            {{ employees[schedule.employee-1].surname }}
          </span>
        </div>
        
        <div class="schedule-actions">
          <button @click="edit_schedule(schedule)" class="btn-edit" title="Edit">
            ✏️
          </button>
          <button @click="confirm_delete_schedule(schedule)" class="btn-delete" title="Delete">
            🗑️
          </button>
        </div>
      </li>
    </ul>

  </div>

  <p v-if="schedules.length === 0">No available schedules</p>
  
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { 
    get_employees, 
  } from '@/components/logic/Schedule'
  import { format_date } from '@/components/logic/DateFormatter'
  import { use_schedule_filters } from '@/components/logic/ScheduleFilters'
  import { use_schedule_form } from '@/components/logic/ScheduleForm'
  import { use_bulk_operations } from '@/components/logic/ScheduleBulkOperations'
  import { use_schedule_selection } from '@/components/logic/ScheduleSelection'

  const employees = ref([])

  const {
    selected_employee,
    start_date,
    end_date,
    schedules,
    loading: filters_loading,
    error: filters_error,
    fetch_schedules,
  } = use_schedule_filters()

  const {
    show_form,
    editing_schedule,
    form_data,
    loading: form_loading,
    error: form_error,
    bulk_add,
    open_bulk_form,
    open_add_form,
    edit_schedule,
    cancel_form,
    save_schedule,
    confirm_delete_schedule
  } = use_schedule_form(async () => {
    await fetch_schedules()
  })

  const {
    selected_items,
    all_selected,
    is_selected,
    toggle_selection,
    toggle_select_all,
    clear_selection
  } = use_schedule_selection(schedules)

  const {
    show_bulk_form,
    bulk_form_data,
    loading: bulk_loading,
    error: bulk_error,
    open_bulk_edit,
    cancel_bulk_form,
    save_bulk_edit,
    confirm_bulk_delete
  } = use_bulk_operations(selected_items, async () => {
    clear_selection()
    await fetch_schedules()
  })

  const loading = ref(false)
  const error = ref(null)

  onMounted(async () => {
    try {
      // loading.value = true
      const emp_esponse = await get_employees()
      employees.value = emp_esponse.data
      await fetch_schedules()
    } catch (err) {
      error.value = "Error loading schedule data: " + err.message
      console.log("Error: ", err)
    }
  })
</script>



<style scoped>
.schedule-view {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

/* Filters */
.filters {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-group label {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 14px;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

button {
  padding: 8px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Forms */
.form-container {
  background: #fff;
  border: 2px solid #007bff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.bulk-form {
  border-color: #ffc107;
  background: #fffbf0;
}

.form-container h2 {
  margin-top: 0;
  color: #007bff;
}

.bulk-form h2 {
  color: #ffc107;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 14px;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-save {
  background: #28a745;
}

.btn-save:hover {
  background: #218838;
}

.btn-cancel {
  background: #6c757d;
}

.btn-cancel:hover {
  background: #5a6268;
}

/* Add section and bulk actions */
.add-section {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.btn-add {
  background: #28a745;
  padding: 12px 30px;
  font-size: 16px;
}

.btn-add:hover {
  background: #218838;
}

.btn-add-range {
  background: #17a2b8;
  padding: 12px 30px;
  font-size: 16px;
}

.btn-add-range:hover {
  background: #138496;
}

.bulk-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 15px;
  background: #fff3cd;
  border-radius: 6px;
  flex: 1;
}

.selection-info {
  font-weight: 600;
  color: #856404;
  margin-right: 10px;
}

.btn-bulk-edit {
  background: #ffc107;
  color: #000;
}

.btn-bulk-edit:hover {
  background: #e0a800;
}

.btn-bulk-delete {
  background: #dc3545;
}

.btn-bulk-delete:hover {
  background: #c82333;
}

.btn-clear {
  background: #6c757d;
}

.btn-clear:hover {
  background: #5a6268;
}

/* Select all */
.select-all {
  padding: 10px 15px;
  background: #e9ecef;
  border-radius: 4px;
  margin-bottom: 10px;
}

.select-all label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  cursor: pointer;
}

.select-all input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Schedule list */
.schedule-list {
  list-style: none;
  padding: 0;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  margin: 8px 0;
  background: #f9f9f9;
  border-left: 4px solid #007bff;
  border-radius: 4px;
  transition: background 0.2s;
}

.schedule-item.selected {
  background: #e7f3ff;
  border-left-color: #ffc107;
}

.schedule-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.schedule-info {
  flex: 1;
}

.schedule-info strong {
  color: #333;
}

.employee-badge {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 10px;
}

.schedule-actions {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  padding: 6px 12px;
  font-size: 16px;
  background: transparent;
  border: 1px solid #ccc;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #ffc107;
  border-color: #ffc107;
}

.btn-delete:hover {
  background: #dc3545;
  border-color: #dc3545;
}
</style>