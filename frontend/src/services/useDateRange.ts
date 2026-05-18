import { ref, computed } from 'vue'

export function useDateRange(allDates: () => string[]) {
  const startDate = ref('')
  const endDate = ref('')

  const filteredDates = computed(() => {
    const dates = allDates()
    if (!startDate.value && !endDate.value) return dates
    return dates.filter(d => {
      if (startDate.value && d < startDate.value) return false
      if (endDate.value && d > endDate.value) return false
      return true
    })
  })

  function setDateRange(start: string, end: string) {
    startDate.value = start
    endDate.value = end
  }

  function clearDateRange() {
    startDate.value = ''
    endDate.value = ''
  }

  const hasFilter = computed(() => !!startDate.value || !!endDate.value)

  return {
    startDate,
    endDate,
    filteredDates,
    setDateRange,
    clearDateRange,
    hasFilter,
  }
}
