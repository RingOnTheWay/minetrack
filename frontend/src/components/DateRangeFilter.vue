<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Calendar, X } from 'lucide-vue-next'
import DatePickerPopup from './DatePickerPopup.vue'

const DROPDOWN_CLOSE_EVENT = 'close-other-dropdowns'

const { t } = useI18n()

const props = defineProps<{
  startDate: string
  endDate: string
  hasFilter: boolean
  availableDates: string[]
}>()

const emit = defineEmits<{
  'update:start': [value: string]
  'update:end': [value: string]
  'clear': []
}>()

const showPicker = ref(false)
const inputRef = ref<HTMLElement | null>(null)
const popupStyle = ref({ top: '0px', left: '0px' })

function updatePopupPosition() {
  if (!inputRef.value) return
  const rect = inputRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top
  if (spaceBelow < 300 && spaceAbove > spaceBelow) {
    popupStyle.value = {
      top: `${rect.top - 308}px`,
      left: `${rect.left}px`,
    }
  } else {
    popupStyle.value = {
      top: `${rect.bottom + 8}px`,
      left: `${rect.left}px`,
    }
  }
}

function openPicker() {
  if (showPicker.value) {
    showPicker.value = false
    return
  }
  showPicker.value = true
  window.dispatchEvent(new CustomEvent(DROPDOWN_CLOSE_EVENT, { detail: 'date-range' }))
  nextTick(() => updatePopupPosition())
}

function handleCloseOtherDropdowns(e: Event) {
  const detail = (e as CustomEvent).detail
  if (detail !== 'date-range') showPicker.value = false
}

function handleSelectRange(start: string, end: string) {
  emit('update:start', start)
  emit('update:end', end)
  if (start && end) showPicker.value = false
}

function handleClear() {
  emit('clear')
}

function handleClearFromInput(e: MouseEvent) {
  e.stopPropagation()
  emit('clear')
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.date-range-trigger') && !target.closest('.date-picker-popup')) {
    showPicker.value = false
  }
}

function handleScroll() {
  if (showPicker.value) updatePopupPosition()
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('scroll', handleScroll, true)
  window.addEventListener(DROPDOWN_CLOSE_EVENT, handleCloseOtherDropdowns)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('scroll', handleScroll, true)
  window.removeEventListener(DROPDOWN_CLOSE_EVENT, handleCloseOtherDropdowns)
})
</script>

<template>
  <div class="flex items-center gap-3" @click="showPicker && (showPicker = false)">
    <div class="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 whitespace-nowrap">
      <Calendar class="w-4 h-4 text-brand dark:text-brand-light" />
      <span>{{ t('dateRange.timeFilter') }}</span>
    </div>
    <div class="relative flex-1 max-w-[600px]">
      <div
        ref="inputRef"
        class="date-range-trigger flex items-center justify-between px-3 py-2 rounded-xl border bg-white/80 dark:bg-slate-800/80 cursor-pointer transition-all min-h-[44px] gap-2"
        @click.stop="openPicker"
        :class="showPicker ? 'border-brand/40 ring-2 ring-brand/20' : 'border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500'"
      >
        <div class="flex flex-wrap gap-1.5 flex-1 min-w-0">
          <template v-if="!hasFilter">
            <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">{{ t('dateRange.allDates') }}</span>
          </template>
          <template v-else>
            <span v-if="startDate" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light">{{ startDate }}</span>
            <span v-if="startDate && endDate" class="text-xs text-slate-400 self-center">~</span>
            <span v-if="endDate" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light">{{ endDate }}</span>
            <span v-if="startDate && !endDate" class="text-xs text-slate-400 self-center">~ ...</span>
          </template>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          <button
            v-if="hasFilter"
            class="p-1 text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-all"
            @click="handleClearFromInput"
          >
            <X class="w-3.5 h-3.5" />
          </button>
          <svg class="w-4 h-4 text-slate-400 dark:text-slate-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': showPicker }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </div>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <DatePickerPopup
      :visible="showPicker"
      :available-dates="availableDates"
      mode="range"
      color-scheme="brand"
      :range-start="startDate"
      :range-end="endDate"
      :popup-style="popupStyle"
      @select-range="handleSelectRange"
      @clear="handleClear"
    />
  </Teleport>
</template>
