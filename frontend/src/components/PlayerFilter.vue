<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  filter: ReturnType<typeof usePlayerFilter>
}>()

const emit = defineEmits<{
  changed: []
}>()

const open = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const selectedSet = computed(() => props.filter.selected.value)
const sortedSelected = computed(() => Array.from(selectedSet.value).sort())
const allCount = computed(() => props.filter.sortedPlayers.value.length)
const isAll = computed(() => selectedSet.value.size === 0 || selectedSet.value.size === allCount.value)

const visibleBadges = computed(() => sortedSelected.value.slice(0, 5))
const remainingCount = computed(() => Math.max(0, sortedSelected.value.length - 5))

function toggleDropdown(e: MouseEvent) {
  e.stopPropagation()
  open.value = !open.value
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
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div class="player-filter" ref="dropdownRef">
    <span class="filter-label">{{ t('common.filterPlayers') }}</span>
    <div class="filter-select" :class="{ open }">
      <div class="select-display" @click="toggleDropdown">
        <div class="badge-area">
          <template v-if="isAll">
            <span class="badge badge-all">{{ t('common.allPlayers') }}</span>
          </template>
          <template v-else>
            <span v-for="p in visibleBadges" :key="p" class="badge">
              {{ p }}
              <button class="badge-remove" @click.stop="removePlayer(p, $event)">×</button>
            </span>
            <span v-if="remainingCount > 0" class="badge badge-more">+{{ remainingCount }}</span>
          </template>
        </div>
        <span class="material-symbols-outlined select-arrow">expand_more</span>
      </div>
      <div v-if="open" class="select-dropdown" @click.stop>
        <div class="dropdown-actions">
          <button class="action-btn" @click="handleSelectAll">{{ t('common.selectAll') }}</button>
          <button class="action-btn" @click="handleDeselectAll">{{ t('common.deselectAll') }}</button>
        </div>
        <div class="dropdown-list">
          <label v-for="p in filter.sortedPlayers.value" :key="p" class="dropdown-item" :class="{ selected: selectedSet.has(p) }">
            <input type="checkbox" :checked="selectedSet.has(p)" @change="togglePlayer(p)" />
            <span>{{ p }}</span>
            <span v-if="selectedSet.has(p)" class="material-symbols-outlined check-icon">check</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.player-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.filter-label {
  font-weight: 500;
  font-size: 14px;
  color: var(--md-sys-color-on-surface-variant);
  white-space: nowrap;
}
.filter-select {
  position: relative;
  flex: 1;
  max-width: 600px;
}
.select-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-low);
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 44px;
  gap: 8px;
}
.filter-select.open .select-display {
  border-color: var(--md-sys-color-primary);
}
.badge-area {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
  white-space: nowrap;
  line-height: 1.4;
}
.badge-all {
  background: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-on-surface-variant);
}
.badge-more {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}
.badge-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--md-sys-color-on-secondary-container);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
}
.badge-remove:hover {
  background: rgba(0,0,0,0.12);
}
.select-arrow {
  font-size: 20px;
  color: var(--md-sys-color-on-surface-variant);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.filter-select.open .select-arrow {
  transform: rotate(180deg);
}
.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  z-index: 200;
  overflow: hidden;
}
.dropdown-actions {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}
.action-btn {
  font-size: 12px;
  color: var(--md-sys-color-primary);
  padding: 4px 10px;
  border-radius: 8px;
  background: var(--md-sys-color-primary-container);
}
.action-btn:hover {
  opacity: 0.85;
}
.dropdown-list {
  max-height: 260px;
  overflow-y: scroll;
  padding: 4px 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.dropdown-list::-webkit-scrollbar {
  display: none;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 14px;
  color: var(--md-sys-color-on-surface);
  transition: background 0.15s;
}
.dropdown-item:hover {
  background: var(--md-sys-color-surface-container-highest);
}
.dropdown-item.selected {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}
.dropdown-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--md-sys-color-primary);
  cursor: pointer;
}
.check-icon {
  font-size: 18px;
  color: var(--md-sys-color-primary);
  margin-left: auto;
}
</style>
