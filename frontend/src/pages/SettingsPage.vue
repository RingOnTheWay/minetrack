<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore, themePresets } from '@/stores/app'
import { useDataStore } from '@/stores/data'
import type { NavKey } from '@/stores/app'
import { apiGet, apiPost } from '@/services/api'
import { Palette, User, Code, ExternalLink, Check, Scale, Calendar, LayoutList, Lock, BarChart3, Filter, X, Plus, Shield, ShieldOff, Clock, Pickaxe, UserCheck, Search, FolderSync, FolderOpen, RefreshCw, AlertCircle, CheckCircle2, Play, HardDrive, ArrowLeft, Folder, Loader2, Trophy } from 'lucide-vue-next'
import {
  LayoutDashboard, Map, Users, Swords, Hammer, Package, TrendingUp,
  Database,
} from 'lucide-vue-next'

const { t } = useI18n()
const app = useAppStore()
const data = useDataStore()

const buildDate = __BUILD_DATE__ as string

const amOrder = ['Rose', 'Emerald', 'Sky', 'Amber', 'Teal']
const kbOrder = ['Gold', 'Navy', 'Crimson', 'HotPink']

const colorGroups = computed(() => [
  { label: 'AM', colors: amOrder.map(name => themePresets.find(p => p.name === name)!) },
  { label: 'KB', colors: kbOrder.map(name => themePresets.find(p => p.name === name)!) },
])

function selectTheme(primary: string) {
  app.setThemeColor(primary)
}

function isActive(primary: string) {
  return app.themeColorPrimary === primary
}

const navItems = computed(() => [
  { icon: LayoutDashboard, label: t('nav.dashboard'), key: '/' as NavKey },
  { icon: Map, label: t('nav.mapStats'), key: '/map' as NavKey },
  { icon: Users, label: t('nav.playerStats'), key: '/players' as NavKey },
  { icon: Swords, label: t('nav.battleStats'), key: '/battle' as NavKey },
  { icon: Hammer, label: t('nav.craftStats'), key: '/craft' as NavKey },
  { icon: Package, label: t('nav.itemStats'), key: '/items' as NavKey },
  { icon: Pickaxe, label: t('nav.blockStats'), key: '/blocks' as NavKey },
  { icon: TrendingUp, label: t('nav.activity'), key: '/activity' as NavKey },
  { icon: Trophy, label: t('nav.honor'), key: '/honor' as NavKey },
  { icon: Database, label: t('nav.dataManage'), key: '/data-manage' as NavKey },
])

function isNavDisabled(key: NavKey) {
  return key === '/data-manage' && app.isStatic
}

function toggleNav(key: NavKey) {
  if (isNavDisabled(key)) return
  app.toggleNavVisibility(key)
}

const whitelistInput = ref('')
const blacklistInput = ref('')
const whitelistInputRef = ref<HTMLInputElement | null>(null)
const blacklistInputRef = ref<HTMLInputElement | null>(null)
const maxLegendPlayers = ref(app.maxLegendPlayers)
const defaultSelectedInput = ref('')
const defaultSelectedDropdownOpen = ref(false)
const defaultSelectedSearch = ref('')
const defaultSelectedDropdownRef = ref<HTMLElement | null>(null)
const defaultSelectedSearchRef = ref<HTMLInputElement | null>(null)

const sortedAllPlayers = computed(() => Array.from(data.allPlayers).sort())

const filteredDefaultPlayers = computed(() => {
  const q = defaultSelectedSearch.value.trim().toLowerCase()
  if (!q) return sortedAllPlayers.value
  return sortedAllPlayers.value.filter(p => p.toLowerCase().includes(q))
})

const defaultSelectedSet = computed(() => new Set(app.defaultSelectedPlayers))

function addDefaultSelected(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return
  if (app.defaultSelectedPlayers.includes(trimmed)) return
  app.setDefaultSelectedPlayers([...app.defaultSelectedPlayers, trimmed])
  defaultSelectedInput.value = ''
}

function removeDefaultSelected(name: string) {
  app.setDefaultSelectedPlayers(app.defaultSelectedPlayers.filter(p => p !== name))
}

function toggleDefaultSelectedFromDropdown(p: string) {
  if (defaultSelectedSet.value.has(p)) {
    removeDefaultSelected(p)
  } else {
    addDefaultSelected(p)
  }
}

function clearDefaultSelected() {
  app.setDefaultSelectedPlayers([])
}

function toggleDefaultSelectedDropdown(e: MouseEvent) {
  e.stopPropagation()
  defaultSelectedDropdownOpen.value = !defaultSelectedDropdownOpen.value
  if (defaultSelectedDropdownOpen.value) {
    defaultSelectedSearch.value = ''
    nextTick(() => defaultSelectedSearchRef.value?.focus())
  }
}

function handleClickOutsideDefaultDropdown(e: MouseEvent) {
  if (defaultSelectedDropdownRef.value && !defaultSelectedDropdownRef.value.contains(e.target as Node)) {
    defaultSelectedDropdownOpen.value = false
    defaultSelectedSearch.value = ''
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutsideDefaultDropdown)
  loadAutoScanStatus()
})

function toggleFilterEnabled() {
  app.setFilterEnabled(!app.filterEnabled)
}

function onMinPlaytimeChange() {
  if (app.minPlaytimeHours < 0) app.setMinPlaytimeHours(0)
}

function onMaxLegendPlayersChange() {
  if (maxLegendPlayers.value < 1) maxLegendPlayers.value = 1
  if (maxLegendPlayers.value > 100) maxLegendPlayers.value = 100
  app.setMaxLegendPlayers(maxLegendPlayers.value)
}

function addToWhitelist(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return
  if (app.whitelist.includes(trimmed)) return
  const newWhitelist = [...app.whitelist, trimmed]
  const newBlacklist = app.blacklist.filter(p => p !== trimmed)
  app.setWhitelist(newWhitelist)
  app.setBlacklist(newBlacklist)
  whitelistInput.value = ''
}

function removeFromWhitelist(name: string) {
  app.setWhitelist(app.whitelist.filter(p => p !== name))
}

function addToBlacklist(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return
  if (app.blacklist.includes(trimmed)) return
  const newBlacklist = [...app.blacklist, trimmed]
  const newWhitelist = app.whitelist.filter(p => p !== trimmed)
  app.setBlacklist(newBlacklist)
  app.setWhitelist(newWhitelist)
  blacklistInput.value = ''
}

function removeFromBlacklist(name: string) {
  app.setBlacklist(app.blacklist.filter(p => p !== name))
}

function onWhitelistKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addToWhitelist(whitelistInput.value)
  }
}

function onBlacklistKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addToBlacklist(blacklistInput.value)
  }
}

const autoScanFolderInput = ref(app.autoScanFolder)
const autoScanSyncing = ref(false)
const autoScanLastStatus = ref<{
  last_scan_time: string | null
  last_scan_success: boolean | null
  last_scan_date: string | null
  last_scan_error: string | null
  last_scan_result: any
} | null>(null)
const autoScanTriggering = ref(false)
const autoScanTriggerResult = ref<any>(null)
const autoScanTriggerError = ref('')

async function loadAutoScanStatus() {
  try {
    const data = await apiGet<any>('/api/auto_scan/config')
    autoScanLastStatus.value = {
      last_scan_time: data.last_scan_time,
      last_scan_success: data.last_scan_success,
      last_scan_date: data.last_scan_date,
      last_scan_error: data.last_scan_error,
      last_scan_result: data.last_scan_result,
    }
    if (data.enabled !== app.autoScanEnabled) {
      app.setAutoScanEnabled(data.enabled)
    }
    if (data.folder && data.folder !== app.autoScanFolder) {
      app.setAutoScanFolder(data.folder)
      autoScanFolderInput.value = data.folder
    }
  } catch {}
}

async function toggleAutoScan() {
  const newVal = !app.autoScanEnabled
  autoScanSyncing.value = true
  try {
    await apiPost('/api/auto_scan/config', {
      enabled: newVal,
      folder: app.autoScanFolder,
    })
    app.setAutoScanEnabled(newVal)
  } catch {
    app.setAutoScanEnabled(!newVal)
  } finally {
    autoScanSyncing.value = false
  }
}

async function saveAutoScanFolder() {
  const folder = autoScanFolderInput.value.trim()
  autoScanSyncing.value = true
  try {
    await apiPost('/api/auto_scan/config', {
      enabled: app.autoScanEnabled,
      folder: folder,
    })
    app.setAutoScanFolder(folder)
  } catch {
    autoScanFolderInput.value = app.autoScanFolder
  } finally {
    autoScanSyncing.value = false
  }
}

function onAutoScanFolderKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    saveAutoScanFolder()
  }
}

async function triggerAutoScan() {
  autoScanTriggering.value = true
  autoScanTriggerResult.value = null
  autoScanTriggerError.value = ''
  try {
    const result = await apiPost<any>('/api/auto_scan/trigger', {})
    autoScanTriggerResult.value = result
    await loadAutoScanStatus()
    await data.reload()
  } catch (e: any) {
    autoScanTriggerError.value = e.message || t('dataManage.operationFailed')
  } finally {
    autoScanTriggering.value = false
  }
}

function formatScanTime(isoStr: string | null): string {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    return d.toLocaleString()
  } catch {
    return isoStr
  }
}

const showFolderBrowser = ref(false)
const folderBrowserPath = ref('')
const folderBrowserParent = ref('')
const folderBrowserDirs = ref<{name: string; path: string; accessible: boolean}[]>([])
const folderBrowserIsRoot = ref(false)
const folderBrowserLoading = ref(false)
const folderBrowserError = ref('')

async function openFolderBrowser() {
  folderBrowserError.value = ''
  showFolderBrowser.value = true
  await browseTo('')
}

async function browseTo(path: string) {
  folderBrowserLoading.value = true
  folderBrowserError.value = ''
  try {
    const params: Record<string, string> = { _: String(Date.now()) }
    if (path) params.path = path
    const data = await apiGet<any>('/api/browse', params)
    folderBrowserPath.value = data.path
    folderBrowserParent.value = data.parent
    folderBrowserIsRoot.value = data.is_root
    if (data.is_root) {
      folderBrowserDirs.value = data.dirs.map((d: string) => ({ name: d, path: d, accessible: true }))
    } else {
      folderBrowserDirs.value = data.dirs
    }
  } catch (e: any) {
    folderBrowserError.value = e.message || t('dataManage.operationFailed')
  } finally {
    folderBrowserLoading.value = false
  }
}

function selectFolderAndClose() {
  autoScanFolderInput.value = folderBrowserPath.value
  saveAutoScanFolder()
  showFolderBrowser.value = false
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div
      v-motion-slide-bottom
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <Palette class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.themeColor') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.themeColorDesc') }}</p>
          </div>
        </div>

        <div class="space-y-6">
          <div v-for="group in colorGroups" :key="group.label">
            <p class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3">{{ group.label }}</p>
            <div class="flex flex-wrap gap-3">
              <button
                v-for="color in group.colors"
                :key="color.primary"
                class="group relative w-14 h-14 rounded-xl transition-all duration-300 hover:scale-110 hover:-translate-y-1 active:scale-95 focus:outline-none"
                :class="isActive(color.primary) ? 'ring-2 ring-offset-2 ring-brand dark:ring-offset-slate-800 shadow-lg' : 'shadow-sm hover:shadow-md'"
                :style="{ backgroundColor: color.primary }"
                @click="selectTheme(color.primary)"
              >
                <div
                  v-if="isActive(color.primary)"
                  class="absolute inset-0 flex items-center justify-center"
                >
                  <Check class="w-5 h-5 text-white drop-shadow-md" />
                </div>
                <div
                  v-else
                  class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <div class="w-3 h-3 rounded-full bg-white/60" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="50"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <LayoutList class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.navItems') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.navItemsDesc') }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <div
            v-for="item in navItems"
            :key="item.key"
            class="flex items-center justify-between p-3 rounded-xl transition-colors"
            :class="isNavDisabled(item.key) ? 'bg-slate-50/50 dark:bg-slate-800/30' : 'bg-slate-100/80 dark:bg-slate-700/50 hover:bg-slate-200/60 dark:hover:bg-slate-700/70'"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center"
                :class="isNavDisabled(item.key) ? 'bg-slate-200/50 dark:bg-slate-600/30' : 'bg-brand/10 dark:bg-brand/20'"
              >
                <component
                  :is="item.icon"
                  class="w-4 h-4"
                  :class="isNavDisabled(item.key) ? 'text-slate-400 dark:text-slate-500' : 'text-brand dark:text-brand-light'"
                />
              </div>
              <span
                class="text-sm font-medium"
                :class="isNavDisabled(item.key) ? 'text-slate-400 dark:text-slate-500' : 'text-slate-700 dark:text-slate-200'"
              >{{ item.label }}</span>
              <Lock
                v-if="isNavDisabled(item.key)"
                class="w-3.5 h-3.5 text-slate-400 dark:text-slate-500"
              />
            </div>

            <button
              class="relative w-10 h-6 rounded-full transition-all duration-300"
              :class="[
                isNavDisabled(item.key)
                  ? 'bg-slate-200 dark:bg-slate-600 cursor-not-allowed'
                  : app.isNavVisible(item.key)
                    ? 'bg-brand'
                    : 'bg-slate-300 dark:bg-slate-600'
              ]"
              :disabled="isNavDisabled(item.key)"
              @click="toggleNav(item.key)"
            >
              <div
                class="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-300"
                :class="app.isNavVisible(item.key) ? 'left-5' : 'left-1'"
              />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="75"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
              <BarChart3 class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.chartTotal') }}</h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.chartTotalDesc') }}</p>
            </div>
          </div>

          <button
            class="relative w-12 h-7 rounded-full transition-all duration-300"
            :class="app.showChartTotal ? 'bg-brand' : 'bg-slate-300 dark:bg-slate-600'"
            @click="app.toggleChartTotal()"
          >
            <div
              class="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-all duration-300"
              :class="app.showChartTotal ? 'left-5.5' : 'left-0.5'"
            />
          </button>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="81"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <Users class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.maxLegendPlayers') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.maxLegendPlayersDesc') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <input
              v-model.number="maxLegendPlayers"
              type="number"
              min="1"
              max="100"
              class="w-24 px-4 py-2.5 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              @change="onMaxLegendPlayersChange"
            />
            <span class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.players') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="87"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm"
      :class="defaultSelectedDropdownOpen ? 'z-50' : ''"
    >
      <div class="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
        <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />
      </div>

      <div class="relative">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <UserCheck class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.defaultSelectedPlayers') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.defaultSelectedPlayersDesc') }}</p>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex flex-wrap gap-2 min-h-[2rem]">
            <span
              v-for="name in app.defaultSelectedPlayers"
              :key="'ds-'+name"
              class="inline-flex items-center gap-1 px-2.5 py-1 bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light text-xs font-medium rounded-lg border border-brand/20 dark:border-brand/30"
            >
              {{ name }}
              <button class="hover:bg-brand/20 dark:hover:bg-brand/30 rounded-full p-0.5 transition-colors" @click="removeDefaultSelected(name)">
                <X class="w-3 h-3" />
              </button>
            </span>
            <span v-if="app.defaultSelectedPlayers.length === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">{{ t('settings.defaultSelectedEmpty') }}</span>
          </div>

          <div ref="defaultSelectedDropdownRef" class="relative" @click="defaultSelectedDropdownOpen && (defaultSelectedDropdownOpen = false, defaultSelectedSearch = '')">
            <div class="flex gap-2">
              <input
                v-model="defaultSelectedInput"
                type="text"
                :placeholder="t('settings.addPlayerPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown.enter.prevent="addDefaultSelected(defaultSelectedInput)"
              />
              <button
                class="px-3 py-2 bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light hover:bg-brand/20 dark:hover:bg-brand/30 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="!defaultSelectedInput.trim()"
                @click="addDefaultSelected(defaultSelectedInput)"
              >
                <Plus class="w-4 h-4" />
              </button>
              <button
                class="px-3 py-2 bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700/70 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="app.defaultSelectedPlayers.length === 0"
                @click="clearDefaultSelected"
              >
                {{ t('settings.clearAll') }}
              </button>
            </div>

            <div class="mt-2">
              <button
                class="flex items-center gap-2 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-500 transition-all w-full"
                @click.stop="toggleDefaultSelectedDropdown"
              >
                <Search class="w-4 h-4" />
                <span>{{ t('settings.selectFromPlayers') }}</span>
                <span class="ml-auto text-xs text-slate-400">{{ app.defaultSelectedPlayers.length }}/{{ sortedAllPlayers.length }}</span>
              </button>

              <div v-if="defaultSelectedDropdownOpen" class="absolute top-full mt-1 left-0 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-xl z-50 overflow-hidden" @click.stop>
                <div class="p-2 border-b border-slate-100 dark:border-slate-700">
                  <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-700/50">
                    <Search class="w-4 h-4 text-slate-400 dark:text-slate-500 flex-shrink-0" />
                    <input
                      ref="defaultSelectedSearchRef"
                      v-model="defaultSelectedSearch"
                      type="text"
                      :placeholder="t('common.searchPlayer')"
                      class="flex-1 bg-transparent text-sm text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 outline-none"
                      @click.stop
                    />
                  </div>
                </div>
                <div class="max-h-[260px] overflow-y-auto hide-scrollbar">
                  <div
                    v-for="p in filteredDefaultPlayers"
                    :key="p"
                    class="flex items-center gap-3 px-3 py-2 cursor-pointer transition-all text-sm"
                    :class="defaultSelectedSet.has(p) ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'"
                    @click="toggleDefaultSelectedFromDropdown(p)"
                  >
                    <span class="flex-1">{{ p }}</span>
                    <Check v-if="defaultSelectedSet.has(p)" class="w-4 h-4 text-brand dark:text-brand-light" />
                  </div>
                  <div v-if="filteredDefaultPlayers.length === 0" class="px-3 py-4 text-center text-sm text-slate-400 dark:text-slate-500">
                    {{ t('common.noResults') }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <p class="text-xs text-slate-400 dark:text-slate-500">{{ t('settings.defaultSelectedHint') }}</p>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="93"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center justify-between" :class="app.filterEnabled ? 'mb-8' : ''">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
              <Filter class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.playerFilter') }}</h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.playerFilterDesc') }}</p>
            </div>
          </div>

          <button
            class="relative w-12 h-7 rounded-full transition-all duration-300"
            :class="app.filterEnabled ? 'bg-brand' : 'bg-slate-300 dark:bg-slate-600'"
            @click="toggleFilterEnabled"
          >
            <div
              class="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-all duration-300"
              :class="app.filterEnabled ? 'left-5.5' : 'left-0.5'"
            />
          </button>
        </div>

        <div v-if="app.filterEnabled" class="space-y-6">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <Clock class="w-4 h-4 text-brand dark:text-brand-light" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.minPlaytime') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.minPlaytimeDesc') }}</p>
            <div class="flex items-center gap-3">
              <input
                :value="app.minPlaytimeHours"
                @input="app.setMinPlaytimeHours(parseFloat(($event.target as HTMLInputElement).value) || 0)"
                type="number"
                min="0"
                step="0.5"
                class="w-32 px-4 py-2.5 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                @change="onMinPlaytimeChange"
              />
              <span class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.hours') }}</span>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-2 mb-3">
              <Shield class="w-4 h-4 text-emerald-500" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.whitelist') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.whitelistDesc') }}</p>
            <div class="flex flex-wrap gap-2 mb-2 min-h-[2rem]">
              <span
                v-for="name in app.whitelist"
                :key="'w-'+name"
                class="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-medium rounded-lg border border-emerald-200 dark:border-emerald-800/50"
              >
                {{ name }}
                <button class="hover:text-emerald-900 dark:hover:text-emerald-200 transition-colors" @click="removeFromWhitelist(name)">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span v-if="app.whitelist.length === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">{{ t('settings.emptyList') }}</span>
            </div>
            <div class="flex gap-2">
              <input
                ref="whitelistInputRef"
                v-model="whitelistInput"
                type="text"
                :placeholder="t('settings.addPlayerPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown="onWhitelistKeydown"
              />
              <button
                class="px-3 py-2 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="!whitelistInput.trim()"
                @click="addToWhitelist(whitelistInput)"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-2 mb-3">
              <ShieldOff class="w-4 h-4 text-red-500" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.blacklist') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.blacklistDesc') }}</p>
            <div class="flex flex-wrap gap-2 mb-2 min-h-[2rem]">
              <span
                v-for="name in app.blacklist"
                :key="'b-'+name"
                class="inline-flex items-center gap-1 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-medium rounded-lg border border-red-200 dark:border-red-800/50"
              >
                {{ name }}
                <button class="hover:text-red-900 dark:hover:text-red-200 transition-colors" @click="removeFromBlacklist(name)">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span v-if="app.blacklist.length === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">{{ t('settings.emptyList') }}</span>
            </div>
            <div class="flex gap-2">
              <input
                ref="blacklistInputRef"
                v-model="blacklistInput"
                type="text"
                :placeholder="t('settings.addPlayerPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown="onBlacklistKeydown"
              />
              <button
                class="px-3 py-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="!blacklistInput.trim()"
                @click="addToBlacklist(blacklistInput)"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="93"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center justify-between" :class="app.autoScanEnabled ? 'mb-8' : ''">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
              <FolderSync class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.autoScan') }}</h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.autoScanDesc') }}</p>
            </div>
          </div>

          <button
            class="relative w-12 h-7 rounded-full transition-all duration-300"
            :class="app.autoScanEnabled ? 'bg-brand' : 'bg-slate-300 dark:bg-slate-600'"
            @click="toggleAutoScan"
          >
            <div
              class="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-all duration-300"
              :class="app.autoScanEnabled ? 'left-5.5' : 'left-0.5'"
            />
          </button>
        </div>

        <div v-if="app.autoScanEnabled" class="space-y-6">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <FolderOpen class="w-4 h-4 text-brand dark:text-brand-light" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.autoScanFolder') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.autoScanFolderDesc') }}</p>
            <div class="flex gap-2">
              <input
                v-model="autoScanFolderInput"
                type="text"
                :placeholder="t('settings.autoScanFolderPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown="onAutoScanFolderKeydown"
                @blur="saveAutoScanFolder"
              />
              <button class="px-3 py-2 bg-brand/10 dark:bg-brand/20 hover:bg-brand/20 dark:hover:bg-brand/30 text-brand dark:text-brand-light rounded-lg transition-all flex items-center gap-2" @click="openFolderBrowser">
                <FolderOpen class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-2 mb-3">
              <Clock class="w-4 h-4 text-brand dark:text-brand-light" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.autoScanSchedule') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ t('settings.autoScanScheduleDesc') }}</p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <RefreshCw class="w-4 h-4 text-brand dark:text-brand-light" />
                <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.autoScanManualTrigger') }}</label>
              </div>
              <button
                class="btn-brand inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all"
                :disabled="autoScanTriggering || !app.autoScanFolder"
                @click="triggerAutoScan"
              >
                <RefreshCw v-if="autoScanTriggering" class="w-3.5 h-3.5 animate-spin" />
                <Play v-else class="w-3.5 h-3.5" />
                {{ autoScanTriggering ? t('common.loading') : t('settings.autoScanTriggerNow') }}
              </button>
            </div>
            <div v-if="autoScanTriggerError" class="p-3 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-xs text-red-700 dark:text-red-400">{{ autoScanTriggerError }}</div>
            <div v-if="autoScanTriggerResult && autoScanTriggerResult.success" class="p-3 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl text-xs text-emerald-700 dark:text-emerald-400">
              {{ t('settings.autoScanTriggerSuccess') }}: {{ t('dataManage.date') }}={{ autoScanTriggerResult.date }}, {{ t('dataManage.playerCount') }}={{ autoScanTriggerResult.result?.player_count }}
            </div>
          </div>

          <div v-if="autoScanLastStatus && autoScanLastStatus.last_scan_time">
            <div class="flex items-center gap-2 mb-3">
              <component
                :is="autoScanLastStatus.last_scan_success ? CheckCircle2 : AlertCircle"
                class="w-4 h-4"
                :class="autoScanLastStatus.last_scan_success ? 'text-emerald-500' : 'text-red-500'"
              />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.autoScanLastStatus') }}</label>
            </div>
            <div class="p-3 rounded-xl text-xs space-y-1"
              :class="autoScanLastStatus.last_scan_success
                ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-400'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 text-red-700 dark:text-red-400'"
            >
              <div class="flex items-center gap-2">
                <Clock class="w-3.5 h-3.5" />
                <span>{{ t('settings.autoScanLastTime') }}: {{ formatScanTime(autoScanLastStatus.last_scan_time) }}</span>
              </div>
              <div v-if="autoScanLastStatus.last_scan_success && autoScanLastStatus.last_scan_date" class="flex items-center gap-2">
                <Calendar class="w-3.5 h-3.5" />
                <span>{{ t('settings.autoScanLastDate') }}: {{ autoScanLastStatus.last_scan_date }}</span>
              </div>
              <div v-if="autoScanLastStatus.last_scan_success && autoScanLastStatus.last_scan_result" class="flex items-center gap-2">
                <BarChart3 class="w-3.5 h-3.5" />
                <span>{{ t('dataManage.playerCount') }}: {{ autoScanLastStatus.last_scan_result.player_count }}</span>
              </div>
              <div v-if="!autoScanLastStatus.last_scan_success && autoScanLastStatus.last_scan_error" class="flex items-center gap-2">
                <AlertCircle class="w-3.5 h-3.5" />
                <span>{{ autoScanLastStatus.last_scan_error }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="100"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <User class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.about') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.aboutDesc') }}</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Code class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.author') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">RiNG</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Scale class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.license') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">MIT</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <ExternalLink class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.projectRepo') }}</p>
              <a
                href="https://github.com/RingOnTheWay/minetrack"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-brand dark:text-brand-light hover:underline"
              >GitHub</a>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Code class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.version') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">v0.1.0</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Calendar class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.buildDate') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ buildDate }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showFolderBrowser" class="global-loading-overlay" @click.self="showFolderBrowser = false">
        <div class="folder-browser-card dark:bg-slate-800 dark:border-slate-700">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
                <HardDrive class="w-5 h-5 text-brand dark:text-brand-light" />
              </div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.selectFolder') }}</h3>
            </div>
            <button class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" @click="showFolderBrowser = false">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <div class="mb-3 px-3 py-2 bg-slate-50 dark:bg-slate-800 rounded-lg text-xs text-slate-500 dark:text-slate-400 font-mono break-all">
            {{ folderBrowserPath || t('dataManage.selectDrive') }}
          </div>

          <div v-if="folderBrowserError" class="mb-3 px-3 py-2 bg-red-50 dark:bg-red-900/30 rounded-lg text-xs text-red-600 dark:text-red-400">{{ folderBrowserError }}</div>

          <div v-if="folderBrowserLoading" class="py-12 text-center">
            <Loader2 class="w-6 h-6 animate-spin text-brand mx-auto" />
          </div>
          <div v-else class="max-h-72 overflow-y-auto overflow-x-hidden hide-scrollbar space-y-0.5">
            <button
              v-if="folderBrowserParent !== '' || folderBrowserIsRoot"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all"
              @click="browseTo(folderBrowserIsRoot ? '' : folderBrowserParent)"
            >
              <ArrowLeft class="w-4 h-4" />
              <span>{{ folderBrowserIsRoot ? t('dataManage.selectDrive') : '..' }}</span>
            </button>
            <button
              v-for="dir in folderBrowserDirs"
              :key="dir.path"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all"
              :class="dir.accessible ? 'text-slate-700 dark:text-slate-300 hover:bg-brand/5 dark:hover:bg-brand/10 hover:text-brand dark:hover:text-brand-light' : 'text-slate-300 dark:text-slate-600 cursor-not-allowed'"
              @click="dir.accessible && browseTo(dir.path)"
            >
              <Lock v-if="!dir.accessible" class="w-4 h-4 text-slate-300 dark:text-slate-600" />
              <Folder v-else class="w-4 h-4 text-brand/60 dark:text-brand-light/60" />
              <span>{{ dir.name }}</span>
            </button>
          </div>

          <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-end gap-2">
            <button class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all" @click="showFolderBrowser = false">{{ t('dataManage.cancel') }}</button>
            <button
              class="btn-brand px-4 py-2 text-sm rounded-lg transition-all"
              :disabled="!folderBrowserPath || folderBrowserIsRoot"
              @click="selectFolderAndClose"
            >
              {{ t('dataManage.selectThisFolder') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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
