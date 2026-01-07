export function format_date(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('pl-PL', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

export function get_today_date_after_days(days) {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

export function get_today_date_before_days(days) {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().split('T')[0]
}

export function generate_days_array(start_date, end_date) {
  const days = []
  const start = new Date(start_date)
  const end = new Date(end_date)
  
  if (start > end) {
    throw new Error("Start date can't be later than end date")
  }
  
  const current = new Date(start)
  
  while (current <= end) {
    days.push(current.toISOString().split('T')[0])
    current.setDate(current.getDate() + 1)
  }
  
  return days
}