<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps<{
  visible: boolean
  availableDates: string[]
  mode: 'single' | 'range'
  colorScheme: 'brand' | 'accent'
  selectedDate?: string
  rangeStart?: string
  rangeEnd?: string
  popupStyle: { top: string; left: string }
}>()

const emit = defineEmits<{
  'select': [date: string]
  'select-range': [start: string, end: string]
  'clear': []
}>()

const pickerView = ref<'day' | 'month' | 'year'>('day')
const pickerYear = ref(new Date().getFullYear())
const pickerMonth = ref(new Date().getMonth())
const yearRangeStart = ref(new Date().getFullYear() - 5)
const selectingEnd = ref(false)

const MONTH_NAMES_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
const MONTH_NAMES_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const monthNames = computed(() => t('lang.switchTo') === '中文' ? MONTH_NAMES_EN : MONTH_NAMES_ZH)

const selectedClass = computed(() => props.colorScheme === 'brand' ? 'dp-selected-brand' : 'dp-selected-accent')
const inRangeClass = computed(() => props.colorScheme === 'brand' ? 'dp-in-range-brand' : 'dp-in-range')
const hoverClass = computed(() => props.colorScheme === 'brand' ? 'dp-hover-brand' : 'dp-hover-accent')
const headerHoverClass = computed(() => props.colorScheme === 'brand' ? 'hover:text-brand dark:hover:text-brand-light' : 'hover:text-red-500 dark:hover:text-red-400')
const clearBtnClass = computed(() => props.colorScheme === 'brand' ? 'text-brand dark:text-brand-light' : 'text-red-500 dark:text-red-400')

const yearRangeEnd = computed(() => yearRangeStart.value + 11)
const yearRangeLabel = computed(() => `${yearRangeStart.value} - ${yearRangeEnd.value}`)

watch(() => props.visible, (val) => {
  if (val) {
    pickerView.value = 'day'
    selectingEnd.value = false
    const ref = props.mode === 'single' ? props.selectedDate : props.rangeStart
    if (ref) {
      const parts = ref.split('-')
      if (parts.length === 3) {
        pickerYear.value = parseInt(parts[0])
        pickerMonth.value = parseInt(parts[1]) - 1
      }
    }
  }
})

function getDaysInMonth(year: number, month: number) { return new Date(year, month + 1, 0).getDate() }
function getFirstDayOfWeek(year: number, month: number) { return new Date(year, month, 1).getDay() }

function pickerDayDates(year: number, month: number) {
  const days = getDaysInMonth(year, month)
  const result: (string | null)[] = []
  for (let d = 1; d <= days; d++) {
    const mm = String(month + 1).padStart(2, '0')
    const dd = String(d).padStart(2, '0')
    result.push(`${year}-${mm}-${dd}`)
  }
  return result
}

function monthHasData(year: number, month: number) {
  const prefix = `${year}-${String(month + 1).padStart(2, '0')}`
  return props.availableDates.some(d => d.startsWith(prefix))
}

function yearHasData(year: number) {
  return props.availableDates.some(d => d.startsWith(`${year}-`))
}

function handleHeaderPrev() {
  if (pickerView.value === 'day') {
    if (pickerMonth.value === 0) { pickerMonth.value = 11; pickerYear.value-- } else { pickerMonth.value-- }
  } else if (pickerView.value === 'month') {
    pickerYear.value--
  } else {
    yearRangeStart.value -= 12
  }
}

function handleHeaderNext() {
  if (pickerView.value === 'day') {
    if (pickerMonth.value === 11) { pickerMonth.value = 0; pickerYear.value++ } else { pickerMonth.value++ }
  } else if (pickerView.value === 'month') {
    pickerYear.value++
  } else {
    yearRangeStart.value += 12
  }
}

function switchToYearView() { pickerView.value = 'year' }
function switchToMonthView() { pickerView.value = 'month' }

function selectYear(year: number) {
  pickerYear.value = year
  pickerView.value = 'month'
}

function selectMonth(month: number) {
  pickerMonth.value = month
  pickerView.value = 'day'
}

function isInRange(date: string) {
  if (!props.rangeStart || !props.rangeEnd) return false
  return date >= props.rangeStart && date <= props.rangeEnd
}

function getDayClass(date: string | null) {
  if (!date) return ''
  if (props.mode === 'single') {
    if (date === props.selectedDate) return selectedClass.value
    return props.availableDates.includes(date) ? `dp-has-data ${hoverClass.value}` : 'dp-no-data pointer-events-none'
  }
  if (date === props.rangeStart || date === props.rangeEnd) return selectedClass.value
  if (isInRange(date)) return inRangeClass.value
  return props.availableDates.includes(date) ? `dp-has-data ${hoverClass.value}` : 'dp-no-data pointer-events-none'
}

function getMonthClass(month: number) {
  const hasData = monthHasData(pickerYear.value, month)
  const prefix = `${pickerYear.value}-${String(month + 1).padStart(2, '0')}`
  const isCurrentMonth = pickerMonth.value === month && props.availableDates.some(d => d.startsWith(prefix))
  if (isCurrentMonth) return selectedClass.value
  return hasData ? `dp-has-data ${hoverClass.value}` : 'dp-no-data pointer-events-none'
}

function getYearClass(year: number) {
  const hasData = yearHasData(year)
  if (year === pickerYear.value) return selectedClass.value
  return hasData ? `dp-has-data ${hoverClass.value}` : 'dp-no-data pointer-events-none'
}

function selectDate(date: string) {
  if (props.mode === 'single') {
    emit('select', date)
    return
  }
  if (props.rangeStart && props.rangeEnd) {
    emit('select-range', date, '')
    selectingEnd.value = false
  } else if (!props.rangeStart || selectingEnd.value) {
    if (!props.rangeStart || date < props.rangeStart) {
      emit('select-range', date, '')
      selectingEnd.value = false
    } else {
      emit('select-range', props.rangeStart, date)
      selectingEnd.value = true
    }
  } else {
    if (date < props.rangeStart) {
      emit('select-range', date, '')
      selectingEnd.value = false
    } else {
      emit('select-range', props.rangeStart, date)
      selectingEnd.value = true
    }
  }
}

function handleClear() {
  selectingEnd.value = false
  emit('clear')
}

const hasSelection = computed(() => {
  if (props.mode === 'single') return !!props.selectedDate
  return !!(props.rangeStart || props.rangeEnd)
})

const rangeLabel = computed(() => {
  if (props.mode === 'single') return props.selectedDate || ''
  if (props.rangeStart && props.rangeEnd) return `${props.rangeStart} ~ ${props.rangeEnd}`
  if (props.rangeStart) return `${props.rangeStart} ~ ...`
  return ''
})

const selectHint = computed(() => {
  if (props.mode === 'single') return ''
  if (props.rangeStart && !props.rangeEnd) return t('dateRange.selectEndDate')
  return t('dateRange.selectStartDate')
})
</script>

<template>
  <div v-if="visible" class="date-picker-popup dark:bg-slate-800 dark:border-slate-700" :style="popupStyle" @click.stop>
    <div class="flex items-center justify-between mb-2">
      <button class="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all" @click="handleHeaderPrev">
        <ChevronLeft class="w-4 h-4 text-slate-600 dark:text-slate-400" />
      </button>
      <div class="flex items-center gap-1">
        <button class="text-sm font-semibold text-slate-700 dark:text-slate-300 transition-colors px-1 rounded" :class="headerHoverClass" @click="switchToYearView">{{ pickerView === 'year' ? yearRangeLabel : pickerYear }}</button>
        <button v-if="pickerView !== 'year'" class="text-sm font-semibold text-slate-700 dark:text-slate-300 transition-colors px-1 rounded" :class="headerHoverClass" @click="switchToMonthView">{{ monthNames[pickerMonth] }}</button>
      </div>
      <button class="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all" @click="handleHeaderNext">
        <ChevronRight class="w-4 h-4 text-slate-600 dark:text-slate-400" />
      </button>
    </div>

    <template v-if="pickerView === 'day'">
      <div v-if="selectHint" class="text-xs text-slate-400 mb-2 text-center">{{ selectHint }}</div>
      <div class="grid grid-cols-7 gap-1 text-center">
        <div v-for="d in ['日', '一', '二', '三', '四', '五', '六']" :key="d" class="text-xs text-slate-400 py-1 font-medium">{{ d }}</div>
        <div v-for="n in getFirstDayOfWeek(pickerYear, pickerMonth)" :key="'e'+n" class="py-1" />
        <button
          v-for="date in pickerDayDates(pickerYear, pickerMonth)"
          :key="date || 'null'"
          class="py-1.5 text-xs rounded-lg transition-all"
          :class="getDayClass(date)"
          @click="date && availableDates.includes(date) && selectDate(date)"
        >
          {{ date ? date.slice(8) : '' }}
        </button>
      </div>
    </template>

    <template v-if="pickerView === 'month'">
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="(name, i) in monthNames"
          :key="i"
          class="py-2 text-xs rounded-lg transition-all"
          :class="getMonthClass(i)"
          @click="monthHasData(pickerYear, i) && selectMonth(i)"
        >
          {{ name }}
        </button>
      </div>
    </template>

    <template v-if="pickerView === 'year'">
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="y in 12"
          :key="y"
          class="py-2 text-xs rounded-lg transition-all"
          :class="getYearClass(yearRangeStart + y - 1)"
          @click="yearHasData(yearRangeStart + y - 1) && selectYear(yearRangeStart + y - 1)"
        >
          {{ yearRangeStart + y - 1 }}
        </button>
      </div>
    </template>

    <div v-if="hasSelection" class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
      <span class="text-xs text-slate-500 dark:text-slate-400">{{ rangeLabel }}</span>
      <button class="text-xs hover:underline" :class="clearBtnClass" @click="handleClear">{{ t('dateRange.clear') }}</button>
    </div>
  </div>
</template>
