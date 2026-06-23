<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed, inject, ref, onMounted, onBeforeUnmount, nextTick, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Settings, Menu, Server, ChevronDown } from 'lucide-vue-next'
import { useAppStore } from '@/stores/app'
import { useDataStore } from '@/stores/data'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const app = useAppStore()
const data = useDataStore()

const toggleSidebar = inject<() => void>('toggleSidebar', () => {})

const isSettingsPage = computed(() => route.path === '/settings')

const breadcrumbMap: Record<string, string> = {
  '/': 'nav.dashboard',
  '/map': 'nav.mapStats',
  '/players': 'nav.playerStats',
  '/battle': 'nav.battleStats',
  '/craft': 'nav.craftStats',
  '/items': 'nav.itemStats',
  '/activity': 'nav.activity',
  '/data-manage': 'nav.dataManage',
  '/settings': 'nav.settings',
}

const subtitleMap: Record<string, string> = {
  '/': 'dashboard.subtitle',
  '/map': 'map.subtitle',
  '/players': 'playerStats.subtitle',
  '/battle': 'battle.subtitle',
  '/craft': 'craft.subtitle',
  '/items': 'item.subtitle',
  '/activity': 'activity.subtitle',
  '/data-manage': 'dataManage.subtitle',
  '/settings': 'settings.subtitle',
}

const currentLabel = computed(() => t(breadcrumbMap[route.path] || 'nav.dashboard'))
const currentSubtitle = computed(() => {
  const key = subtitleMap[route.path]
  return key ? t(key) : ''
})

function goToSettings() {
  router.push('/settings')
}

const serverDropdownOpen = ref(false)
const serverDropdownRef = ref<HTMLElement | null>(null)
const serverBtnRef = ref<HTMLElement | null>(null)
const dropdownStyle = ref<Record<string, string>>({})

function updateDropdownPosition() {
  if (!serverBtnRef.value) return
  const rect = serverBtnRef.value.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    right: `${window.innerWidth - rect.right}px`,
    minWidth: `${Math.max(rect.width, 140)}px`,
  }
}

async function toggleServerDropdown() {
  serverDropdownOpen.value = !serverDropdownOpen.value
  if (serverDropdownOpen.value) {
    await nextTick()
    updateDropdownPosition()
  }
}

async function switchServer(name: string) {
  serverDropdownOpen.value = false
  if (name === app.currentServer) return
  app.setCurrentServer(name)
  await data.reload()
}

function handleClickOutside(e: MouseEvent) {
  if (serverDropdownOpen.value) {
    const target = e.target as Node
    if (serverBtnRef.value && serverBtnRef.value.contains(target)) return
    if (serverDropdownRef.value && serverDropdownRef.value.contains(target)) return
    serverDropdownOpen.value = false
  }
}

function handleScroll() {
  if (serverDropdownOpen.value) {
    updateDropdownPosition()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside, true)
  window.addEventListener('scroll', handleScroll, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside, true)
  window.removeEventListener('scroll', handleScroll, true)
})
</script>

<template>
  <div class="bg-white/60 dark:bg-slate-900/80 backdrop-blur-xl border-b border-brand/10 dark:border-brand/20 shadow-sm">
    <div class="px-4 md:px-8 py-4 md:py-5 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <button
          class="md:hidden p-2 -ml-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          @click="toggleSidebar"
        >
          <Menu class="w-5 h-5" />
        </button>
        <div class="min-w-0">
          <h1 class="text-lg md:text-xl font-semibold text-slate-800 dark:text-slate-100 truncate">{{ currentLabel }}</h1>
          <p v-if="currentSubtitle" class="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-0.5 truncate">{{ currentSubtitle }}</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative" v-if="app.servers.length > 0">
          <button
            ref="serverBtnRef"
            @click="toggleServerDropdown"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all duration-200 hover:bg-white/80 dark:hover:bg-slate-800/80 text-slate-600 dark:text-slate-400 hover:text-brand dark:hover:text-brand-light"
          >
            <Server class="w-4 h-4" />
            <span class="max-w-[120px] truncate">{{ app.currentServer }}</span>
            <ChevronDown class="w-3 h-3 transition-transform duration-200" :class="serverDropdownOpen ? 'rotate-180' : ''" />
          </button>
        </div>

        <button
          class="p-2 rounded-lg transition-all duration-300 group"
          :class="isSettingsPage
            ? 'bg-brand/15 text-brand dark:text-brand-light'
            : 'hover:bg-white/80 dark:hover:bg-slate-800/80'"
          @click="goToSettings"
        >
          <Settings
            class="w-5 h-5 transition-all duration-300"
            :class="isSettingsPage
              ? 'text-brand dark:text-brand-light'
              : 'text-slate-600 dark:text-slate-400 group-hover:text-brand group-hover:rotate-90'"
          />
        </button>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="serverDropdownOpen && app.servers.length > 0"
      ref="serverDropdownRef"
      :style="dropdownStyle"
      class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-2xl z-[9999] overflow-hidden"
    >
      <button
        v-for="s in app.servers"
        :key="s"
        class="w-full px-4 py-2 text-left text-sm transition-all"
        :class="s === app.currentServer ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light font-medium' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'"
        @click="switchServer(s)"
      >
        {{ s }}
      </button>
    </div>
  </Teleport>
</template>
