<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import { ChevronDown, X, Check, Users, Search } from 'lucide-vue-next'

const DROPDOWN_CLOSE_EVENT = 'close-other-dropdowns'

const { t } = useI18n()

const props = defineProps<{
  filter: ReturnType<typeof usePlayerFilter>
}>()

const emit = defineEmits<{
  changed: []
}>()

const open = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)

const filteredPlayers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.filter.sortedPlayers.value
  return props.filter.sortedPlayers.value.filter(p => p.toLowerCase().includes(q))
})

const selectedSet = computed(() => props.filter.selected.value)
const sortedSelected = computed(() => Array.from(selectedSet.value).sort())
const allCount = computed(() => props.filter.sortedPlayers.value.length)
const isAll = computed(() => selectedSet.value.size === 0 || selectedSet.value.size === allCount.value)

const visibleBadges = computed(() => sortedSelected.value.slice(0, 5))
const remainingCount = computed(() => Math.max(0, sortedSelected.value.length - 5))

function toggleDropdown(e: MouseEvent) {
  e.stopPropagation()
  open.value = !open.value
  if (!open.value) {
    searchQuery.value = ''
  } else {
    window.dispatchEvent(new CustomEvent(DROPDOWN_CLOSE_EVENT, { detail: 'player-filter' }))
    nextTick(() => searchInputRef.value?.focus())
  }
}

function handleCloseOtherDropdowns(e: Event) {
  const detail = (e as CustomEvent).detail
  if (detail !== 'player-filter') {
    open.value = false
    searchQuery.value = ''
  }
}

function removePlayer(p: string, e: MouseEvent) {
  e.stopPropagation()
  props.filter.remove(p)
  emit('changed')
}

function togglePlayer(p: string) {
  props.filter.toggle(p)
  emit('changed')
}

function handleSelectAll() {
  props.filter.selectAll()
  emit('changed')
}

function handleDeselectAll() {
  props.filter.deselectAll()
  emit('changed')
}

function handleClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    open.value = false
    searchQuery.value = ''
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener(DROPDOWN_CLOSE_EVENT, handleCloseOtherDropdowns)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener(DROPDOWN_CLOSE_EVENT, handleCloseOtherDropdowns)
})
</script>

<template>
  <div ref="dropdownRef" class="flex items-center gap-3" @click="open && (open = false, searchQuery = '')">
    <div class="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 whitespace-nowrap">
      <Users class="w-4 h-4 text-brand dark:text-brand-light" />
      <span>{{ t('common.filterPlayers') }}</span>
    </div>
    <div class="relative flex-1 max-w-[600px]">
      <div
        class="flex items-center justify-between px-3 py-2 rounded-xl border bg-white/80 dark:bg-slate-800/80 cursor-pointer transition-all min-h-[44px] gap-2"
        :class="open ? 'border-brand/40 ring-2 ring-brand/20' : 'border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500'"
        @click.stop="toggleDropdown"
      >
        <div class="flex flex-wrap gap-1.5 flex-1 min-w-0">
          <template v-if="isAll">
            <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">{{ t('common.allPlayers') }}</span>
          </template>
          <template v-else>
            <span v-for="p in visibleBadges" :key="p" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light">
              {{ p }}
              <button class="hover:bg-brand/20 dark:hover:bg-brand/30 rounded-full p-0.5 transition-colors" @click.stop="removePlayer(p, $event)">
                <X class="w-3 h-3" />
              </button>
            </span>
            <span v-if="remainingCount > 0" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-brand text-white">
              +{{ remainingCount }}
            </span>
          </template>
        </div>
        <ChevronDown class="w-4 h-4 text-slate-400 dark:text-slate-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': open }" />
      </div>

      <div v-if="open" class="absolute top-full mt-1 left-0 right-0 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-600 rounded-xl shadow-xl z-50 overflow-hidden" @click.stop>
        <div class="flex gap-2 p-3 border-b border-slate-100 dark:border-slate-700">
          <button class="px-3 py-1.5 bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light rounded-lg text-xs font-medium hover:bg-brand/20 dark:hover:bg-brand/30 transition-all" @click="handleSelectAll">{{ t('common.selectAll') }}</button>
          <button class="px-3 py-1.5 bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light rounded-lg text-xs font-medium hover:bg-brand/20 dark:hover:bg-brand/30 transition-all" @click="handleDeselectAll">{{ t('common.deselectAll') }}</button>
        </div>
        <div class="p-2 border-b border-slate-100 dark:border-slate-700">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-700/50">
            <Search class="w-4 h-4 text-slate-400 dark:text-slate-500 flex-shrink-0" />
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              :placeholder="t('common.searchPlayer')"
              class="flex-1 bg-transparent text-sm text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 outline-none"
              @click.stop
            />
            <button v-if="searchQuery" class="p-0.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors" @click.stop="searchQuery = ''">
              <X class="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
            </button>
          </div>
        </div>
        <div class="max-h-[260px] overflow-y-auto hide-scrollbar">
          <div
            v-for="p in filteredPlayers"
            :key="p"
            class="flex items-center gap-3 px-3 py-2 cursor-pointer transition-all text-sm"
            :class="selectedSet.has(p) ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'"
            @click="togglePlayer(p)"
          >
            <span class="flex-1">{{ p }}</span>
            <Check v-if="selectedSet.has(p)" class="w-4 h-4 text-brand dark:text-brand-light" />
          </div>
          <div v-if="filteredPlayers.length === 0" class="px-3 py-4 text-center text-sm text-slate-400 dark:text-slate-500">
            {{ t('common.noResults') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>