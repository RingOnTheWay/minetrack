<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiPost, apiDelete, apiGet, consumeSSE } from '@/services/api'
import { useDataStore } from '@/stores/data'
import { useAppStore } from '@/stores/app'
import { Upload, Trash2, Database, Loader2, FolderOpen, Calendar, Play, HardDrive, ArrowLeft, Folder, Lock, FileArchive } from 'lucide-vue-next'
import DatePickerPopup from '@/components/DatePickerPopup.vue'

const { t } = useI18n()
const dataStore = useDataStore()
const app = useAppStore()

const activeTab = ref<'import' | 'delete'>('import')

const scanFolder = ref('')
const scanArchive = ref('')
const scanMode = ref<'folder' | 'archive'>('folder')
const scanDate = ref('')
const scanLoading = ref(false)
const scanResult = ref<any>(null)
const scanError = ref('')

const showScanDatePicker = ref(false)
const scanDateInputRef = ref<HTMLElement | null>(null)

const batchFolder = ref('')
const batchScanMode = ref<'folder' | 'archive'>('folder')
const batchLoading = ref(false)
const batchResult = ref<any>(null)
const batchError = ref('')

const dates = ref<string[]>([])
const datesLoading = ref(false)
const deleteLoading = ref(false)
const deleteResult = ref<any>(null)
const deleteError = ref('')

const deleteAllLoading = ref(false)
const deleteAllResult = ref<any>(null)
const deleteAllError = ref('')
const showDeleteAllConfirm = ref(false)

const deleteDate = ref('')
const deleteSingleLoading = ref(false)
const deleteSingleResult = ref<any>(null)
const deleteSingleError = ref('')

const showSingleDatePicker = ref(false)

const showRangePicker = ref(false)
const rangeStart = ref('')
const rangeEnd = ref('')
const rangeMatchedDates = ref<string[]>([])

const popupStyle = ref({ top: '0px', left: '0px' })
const singleInputRef = ref<HTMLElement | null>(null)
const rangeInputRef = ref<HTMLElement | null>(null)

const globalLoading = ref(false)
const globalLoadingText = ref('')
const globalLoadingSubText = ref('')
const progressCurrent = ref(0)
const progressTotal = ref(0)
const abortController = ref<AbortController | null>(null)

onMounted(() => { loadDates(); document.addEventListener('click', handleClickOutside); document.addEventListener('scroll', handleScroll, true) })
onBeforeUnmount(() => { document.removeEventListener('click', handleClickOutside); document.removeEventListener('scroll', handleScroll, true) })

function getFilterConfig() {
  return {
    filter_enabled: app.filterEnabled,
    min_playtime_hours: app.minPlaytimeHours,
    whitelist: app.whitelist,
    blacklist: app.blacklist,
  }
}

function handleScroll() {
  if (showScanDatePicker.value) updatePopupPosition(scanDateInputRef.value)
  else if (showSingleDatePicker.value) updatePopupPosition(singleInputRef.value)
  else if (showRangePicker.value) updatePopupPosition(rangeInputRef.value)
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.date-picker-trigger') && !target.closest('.date-picker-popup')) {
    showScanDatePicker.value = false
    showSingleDatePicker.value = false
    showRangePicker.value = false
  }
}

function updatePopupPosition(el: HTMLElement | null) {
  if (!el) return
  const rect = el.getBoundingClientRect()
  popupStyle.value = {
    top: `${rect.bottom + 8}px`,
    left: `${rect.left}px`,
  }
}

function openSinglePicker() {
  showSingleDatePicker.value = true
  showScanDatePicker.value = false
  showRangePicker.value = false
  nextTick(() => updatePopupPosition(singleInputRef.value))
}

function openScanDatePicker() {
  showScanDatePicker.value = true
  showSingleDatePicker.value = false
  showRangePicker.value = false
  nextTick(() => updatePopupPosition(scanDateInputRef.value))
}

function openRangePicker() {
  showRangePicker.value = !showRangePicker.value
  showScanDatePicker.value = false
  showSingleDatePicker.value = false
  if (showRangePicker.value) {
    nextTick(() => updatePopupPosition(rangeInputRef.value))
  }
}

async function loadDates() {
  datesLoading.value = true
  try {
    const params: Record<string, string> = {}
    if (app.currentServer) params.server_name = app.currentServer
    dates.value = await apiGet<string[]>('/api/dates', params)
  }
  catch { dates.value = [] }
  finally { datesLoading.value = false }
}

async function refreshAllData() {
  await Promise.all([loadDates(), dataStore.reload()])
}

async function handleScan() {
  if (scanMode.value === 'folder' && !scanFolder.value.trim()) return
  if (scanMode.value === 'archive' && !scanArchive.value.trim()) return
  scanLoading.value = true; scanResult.value = null; scanError.value = ''
  globalLoading.value = true; globalLoadingText.value = t('dataManage.singleScan'); progressTotal.value = 0
  try {
    const filterConfig = getFilterConfig()
    const date = scanDate.value || undefined
    const serverName = app.currentServer || 'default'
    if (scanMode.value === 'folder') {
      const body: Record<string, any> = { folder: scanFolder.value.trim(), filter_config: filterConfig, server_name: serverName }
      if (date) body.date = date
      scanResult.value = await apiPost('/api/scan', body)
    } else {
      const body: Record<string, any> = { archive: scanArchive.value.trim(), filter_config: filterConfig, server_name: serverName }
      if (date) body.date = date
      scanResult.value = await apiPost('/api/scan_archive', body)
    }
    globalLoading.value = false
    await refreshAllData()
  } catch (e: any) { scanError.value = e.message || t('dataManage.operationFailed') }
  finally { scanLoading.value = false; globalLoading.value = false }
}

async function handleBatchScan() {
  if (!batchFolder.value.trim()) return
  batchLoading.value = true; batchResult.value = null; batchError.value = ''
  globalLoadingSubText.value = ''
  progressTotal.value = 0; progressCurrent.value = 0
  abortController.value = new AbortController()

  try {
    await consumeSSE('/api/batch_scan_stream', { parent_folder: batchFolder.value.trim(), filter_config: getFilterConfig(), scan_mode: batchScanMode.value, server_name: app.currentServer || 'default' }, {
      signal: abortController.value.signal,
      onStart: (data) => {
        progressTotal.value = data.total
        if (data.total > 0) {
          progressCurrent.value = 0
          globalLoading.value = true
          globalLoadingText.value = `${t('dataManage.batchScan')} (0/${data.total})`
        }
      },
      onProgress: (data) => {
        progressTotal.value = data.total
        progressCurrent.value = data.current
        globalLoadingText.value = `${t('dataManage.batchScan')} (${data.current}/${data.total})`
        const typeLabel = data.item_type === 'archive' ? t('dataManage.archiveMode') : t('dataManage.folderMode')
        globalLoadingSubText.value = `${typeLabel}: ${data.name}`
      },
      onExtracting: (data) => {
        progressTotal.value = data.total
        progressCurrent.value = data.current
        globalLoading.value = true
        globalLoadingText.value = `${t('dataManage.batchScan')} (${data.current}/${data.total})`
        globalLoadingSubText.value = `${t('dataManage.extracting')} ${data.name}`
      },
      onComplete: (data) => {
        batchResult.value = { imported: data.imported, total: data.total, filtered_count: data.filtered_count, errors: data.errors || [] }
        globalLoadingSubText.value = ''
        globalLoading.value = false
      },
    })
    await refreshAllData()
  } catch (e: any) {
    if (e.name === 'AbortError') {
      batchError.value = t('dataManage.scanAborted')
    } else {
      batchError.value = e.message || t('dataManage.operationFailed')
    }
  } finally {
    batchLoading.value = false; globalLoading.value = false; globalLoadingSubText.value = ''; abortController.value = null
  }
}

function cancelBatchScan() {
  if (abortController.value) {
    abortController.value.abort()
  }
}

async function handleDeleteSingle() {
  if (!deleteDate.value) return
  deleteSingleLoading.value = true; deleteSingleResult.value = null; deleteSingleError.value = ''
  globalLoading.value = true; globalLoadingText.value = t('dataManage.deleteByDate'); progressTotal.value = 0
  try {
    deleteSingleResult.value = await apiDelete('/api/delete_date', { date: deleteDate.value, server_name: app.currentServer })
    globalLoading.value = false
    await refreshAllData()
  } catch (e: any) { deleteSingleError.value = e.message || t('dataManage.operationFailed') }
  finally { deleteSingleLoading.value = false; globalLoading.value = false }
}

async function handleBatchDelete() {
  if (rangeMatchedDates.value.length === 0) return
  deleteLoading.value = true; deleteResult.value = null; deleteError.value = ''
  const datesToDelete = [...rangeMatchedDates.value]
  progressTotal.value = datesToDelete.length
  progressCurrent.value = 0
  globalLoading.value = true; globalLoadingText.value = t('dataManage.batchDelete')

  try {
    await consumeSSE('/api/batch_delete_stream', { dates: datesToDelete, server_name: app.currentServer }, {
      onStart: (data) => { progressTotal.value = data.total },
      onProgress: (data) => {
        progressCurrent.value = data.current
        progressTotal.value = data.total
        globalLoadingText.value = `${t('dataManage.batchDelete')} (${data.current}/${data.total})`
      },
      onComplete: (data) => {
        deleteResult.value = {
          total_dates: data.total_dates,
          total_map_deleted: data.total_map_deleted,
          total_player_deleted: data.total_player_deleted,
          total_detail_deleted: data.total_detail_deleted,
        }
        globalLoading.value = false
      },
    })
    rangeStart.value = ''; rangeEnd.value = ''; rangeMatchedDates.value = []
    await refreshAllData()
  } catch (e: any) {
    deleteError.value = e.message || t('dataManage.operationFailed')
  } finally {
    deleteLoading.value = false; globalLoading.value = false
  }
}

async function handleDeleteAll() {
  showDeleteAllConfirm.value = false
  deleteAllLoading.value = true; deleteAllResult.value = null; deleteAllError.value = ''
  globalLoading.value = true; globalLoadingText.value = t('dataManage.deleteAll'); progressTotal.value = 0

  try {
    deleteAllResult.value = await apiDelete('/api/delete_all', { server_name: app.currentServer })
    globalLoading.value = false
    await refreshAllData()
  } catch (e: any) {
    deleteAllError.value = e.message || t('dataManage.operationFailed')
  } finally {
    deleteAllLoading.value = false; globalLoading.value = false
  }
}

function computeRangeDates() {
  if (!rangeStart.value || !rangeEnd.value) { rangeMatchedDates.value = []; return }
  rangeMatchedDates.value = dates.value.filter(d => d >= rangeStart.value && d <= rangeEnd.value)
}

function handleSelectSingleDate(date: string) {
  deleteDate.value = date
  showSingleDatePicker.value = false
}

function handleSelectScanDate(date: string) {
  scanDate.value = date
  showScanDatePicker.value = false
}

function handleScanDateClear() {
  scanDate.value = ''
  showScanDatePicker.value = false
}

function handleSelectRange(start: string, end: string) {
  rangeStart.value = start
  rangeEnd.value = end
  if (start && end) {
    computeRangeDates()
    showRangePicker.value = false
  } else {
    rangeMatchedDates.value = []
  }
}

function handleSingleClear() {
  deleteDate.value = ''
  showSingleDatePicker.value = false
}

function handleRangeClear() {
  rangeStart.value = ''
  rangeEnd.value = ''
  rangeMatchedDates.value = []
  showRangePicker.value = false
}

const showFolderBrowser = ref(false)
const folderBrowserTarget = ref<'scan' | 'batch'>('scan')
const folderBrowserMode = ref<'folder' | 'archive' | 'batch'>('folder')
const folderBrowserPath = ref('')
const folderBrowserParent = ref('')
const folderBrowserDirs = ref<{name: string; path: string; accessible: boolean}[]>([])
const folderBrowserArchives = ref<{name: string; path: string}[]>([])
const folderBrowserIsRoot = ref(false)
const folderBrowserLoading = ref(false)
const folderBrowserError = ref('')

async function openFolderBrowser(target: 'scan' | 'batch') {
  folderBrowserTarget.value = target
  if (target === 'scan') {
    folderBrowserMode.value = scanMode.value === 'archive' ? 'archive' : 'folder'
  } else {
    folderBrowserMode.value = batchScanMode.value === 'archive' ? 'batch' : 'batch'
  }
  folderBrowserError.value = ''
  folderBrowserArchives.value = []
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
    folderBrowserArchives.value = data.archives || []
  } catch (e: any) {
    folderBrowserError.value = e.message || t('dataManage.operationFailed')
  } finally {
    folderBrowserLoading.value = false
  }
}

function selectFolderAndClose() {
  if (folderBrowserTarget.value === 'scan') {
    if (folderBrowserMode.value === 'archive') {
      scanArchive.value = ''
    } else {
      scanFolder.value = folderBrowserPath.value
    }
  } else {
    batchFolder.value = folderBrowserPath.value
  }
  showFolderBrowser.value = false
}

function selectArchiveAndClose(archivePath: string) {
  if (folderBrowserTarget.value === 'scan') {
    scanArchive.value = archivePath
  }
  showFolderBrowser.value = false
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tab in (['import', 'delete'] as const)"
        :key="tab"
        class="px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200"
        :class="activeTab === tab
          ? (tab === 'delete' ? 'delete-tab-active' : 'subnav-active')
          : 'subnav-inactive'"
        @click="activeTab = tab"
      >
        {{ t(`dataManage.${tab}Tab`) }}
      </button>
    </div>

    <div v-if="activeTab === 'import'" class="space-y-6">
      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <Upload class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.singleScan') }}</h3>
        </div>

        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <button
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
              :class="scanMode === 'folder' ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'"
              @click="scanMode = 'folder'"
            >
              <Folder class="w-4 h-4" />
              {{ t('dataManage.folderMode') }}
            </button>
            <button
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
              :class="scanMode === 'archive' ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'"
              @click="scanMode = 'archive'"
            >
              <FileArchive class="w-4 h-4" />
              {{ t('dataManage.archiveMode') }}
            </button>
          </div>

          <div v-if="scanMode === 'folder'">
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.serverFolder') }}</label>
            <div class="flex gap-2">
              <input v-model="scanFolder" type="text" :placeholder="t('dataManage.folderPlaceholder')" class="flex-1 px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all" />
              <button class="px-4 py-3 bg-brand/10 dark:bg-brand/20 hover:bg-brand/20 text-brand dark:text-brand-light rounded-xl transition-all flex items-center gap-2" @click="openFolderBrowser('scan')">
                <FolderOpen class="w-4 h-4" />
              </button>
            </div>
          </div>
          <div v-else>
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.archivePath') }}</label>
            <div class="flex gap-2">
              <input v-model="scanArchive" type="text" :placeholder="t('dataManage.archivePlaceholder')" class="flex-1 px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all" />
              <button class="px-4 py-3 bg-brand/10 dark:bg-brand/20 hover:bg-brand/20 text-brand dark:text-brand-light rounded-xl transition-all flex items-center gap-2" @click="openFolderBrowser('scan')">
                <FolderOpen class="w-4 h-4" />
              </button>
            </div>
            <p class="mt-1 text-xs text-amber-600 dark:text-amber-400">{{ t('dataManage.archiveHint') }}</p>
          </div>
          <div>
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.scanDate') }}</label>
            <div class="relative">
              <input
                ref="scanDateInputRef"
                :value="scanDate"
                readonly
                class="date-picker-trigger w-full px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40"
                :placeholder="t('dataManage.scanDatePlaceholder')"
                @click.stop="openScanDatePicker"
              />
              <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ t('dataManage.scanDateHint') }}</p>
          </div>
          <button
            class="btn-brand inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all"
            :disabled="scanLoading || (scanMode === 'folder' ? !scanFolder.trim() : !scanArchive.trim())"
            @click="handleScan"
          >
            <Loader2 v-if="scanLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            {{ scanLoading ? t('common.loading') : t('dataManage.execute') }}
          </button>
        </div>

        <div v-if="scanError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{{ scanError }}</div>
        <div v-if="scanResult" class="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl">
          <div class="font-semibold text-emerald-800 dark:text-emerald-300 text-sm mb-2">{{ t('dataManage.scanSuccess') }}</div>
          <div class="flex flex-wrap gap-3 text-xs text-emerald-700 dark:text-emerald-400">
            <span>{{ t('dataManage.date') }}: {{ scanResult.date }}</span>
            <span>{{ t('dataManage.playerCount') }}: {{ scanResult.player_count }}<template v-if="scanResult.filtered_count"> ({{ t('dataManage.filteredOut', { n: scanResult.filtered_count }) }})</template></span>
            <span>{{ t('dataManage.battleCount') }}: {{ scanResult.battle_stats_count }}</span>
            <span>{{ t('dataManage.craftCount') }}: {{ scanResult.craft_stats_count }}</span>
            <span>{{ t('dataManage.itemCount') }}: {{ scanResult.item_stats_count }}</span>
            <span>{{ t('dataManage.blockCount') }}: {{ scanResult.block_stats_count || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <Database class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.batchScan') }}</h3>
        </div>

        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <button
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
              :class="batchScanMode === 'folder' ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'"
              @click="batchScanMode = 'folder'"
            >
              <Folder class="w-4 h-4" />
              {{ t('dataManage.folderMode') }}
            </button>
            <button
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
              :class="batchScanMode === 'archive' ? 'bg-brand/10 dark:bg-brand/20 text-brand dark:text-brand-light' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'"
              @click="batchScanMode = 'archive'"
            >
              <FileArchive class="w-4 h-4" />
              {{ t('dataManage.archiveMode') }}
            </button>
          </div>

          <div>
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.parentFolder') }}</label>
            <div class="flex gap-2">
              <input v-model="batchFolder" type="text" :placeholder="t('dataManage.parentFolderPlaceholder')" class="flex-1 px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all" />
              <button class="px-4 py-3 bg-brand/10 dark:bg-brand/20 hover:bg-brand/20 text-brand dark:text-brand-light rounded-xl transition-all flex items-center gap-2" @click="openFolderBrowser('batch')">
                <FolderOpen class="w-4 h-4" />
              </button>
            </div>
          </div>
          <p v-if="batchScanMode === 'folder'" class="text-xs text-slate-500 dark:text-slate-400">{{ t('dataManage.batchHintV2') }}</p>
          <p v-else class="text-xs text-amber-600 dark:text-amber-400">{{ t('dataManage.batchArchiveHint') }}</p>
          <button
            class="btn-brand inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all"
            :disabled="batchLoading || !batchFolder.trim()"
            @click="handleBatchScan"
          >
            <Loader2 v-if="batchLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            {{ batchLoading ? t('common.loading') : t('dataManage.execute') }}
          </button>
        </div>

        <div v-if="batchError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{{ batchError }}</div>
        <div v-if="batchResult" class="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl">
          <div class="font-semibold text-emerald-800 dark:text-emerald-300 text-sm mb-2">{{ t('dataManage.batchScanSuccess') }}</div>
          <div class="text-xs text-emerald-700 dark:text-emerald-400">
            {{ t('dataManage.importedDays', { n: batchResult.imported }) }}<template v-if="batchResult.filtered_count"> · {{ t('dataManage.filteredOut', { n: batchResult.filtered_count }) }}</template>
          </div>
          <div v-if="batchResult.errors && batchResult.errors.length" class="mt-3 pt-3 border-t border-emerald-200 dark:border-emerald-700/50">
            <div class="text-xs font-medium text-red-600 dark:text-red-400 mb-1">{{ t('dataManage.scanErrors') }}</div>
            <div v-for="(err, idx) in batchResult.errors" :key="idx" class="text-xs text-red-500 dark:text-red-400">{{ err.folder }}: {{ err.error }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'delete'" class="space-y-6">
      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
          <div class="w-12 h-12 accent-icon-bg rounded-xl flex items-center justify-center">
            <Trash2 class="w-6 h-6 accent-icon-color" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.deleteByDate') }}</h3>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.selectDate') }}</label>
            <div class="relative">
              <input
                ref="singleInputRef"
                :value="deleteDate"
                readonly
                class="date-picker-trigger w-full px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 transition-all cursor-pointer accent-focus-ring"
                :placeholder="t('dataManage.selectDate')"
                @click.stop="openSinglePicker"
              />
              <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
          <button
            class="btn-accent inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all"
            :disabled="deleteSingleLoading || !deleteDate"
            @click="handleDeleteSingle"
          >
            <Loader2 v-if="deleteSingleLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            {{ deleteSingleLoading ? t('common.loading') : t('dataManage.execute') }}
          </button>
        </div>

        <div v-if="deleteSingleError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{{ deleteSingleError }}</div>
        <div v-if="deleteSingleResult" class="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl">
          <div class="font-semibold text-emerald-800 dark:text-emerald-300 text-sm mb-2">{{ t('dataManage.deleteSuccess', { date: deleteSingleResult.date }) }}</div>
          <div class="flex flex-wrap gap-3 text-xs text-emerald-700 dark:text-emerald-400">
            <span>{{ t('dataManage.mapDeleted') }}: {{ deleteSingleResult.map_records_deleted }}</span>
            <span>{{ t('dataManage.playerDeleted') }}: {{ deleteSingleResult.player_records_deleted }}</span>
            <span>{{ t('dataManage.detailDeleted') }}: {{ deleteSingleResult.detail_records_deleted }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
          <div class="w-12 h-12 accent-icon-bg rounded-xl flex items-center justify-center">
            <Trash2 class="w-6 h-6 accent-icon-color" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.batchDelete') }}</h3>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block mb-2 text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('dataManage.selectDateRange') }}</label>
            <div class="relative">
              <input
                ref="rangeInputRef"
                :value="rangeStart && rangeEnd ? `${rangeStart} ~ ${rangeEnd}` : rangeStart ? `${rangeStart} ~ ...` : ''"
                readonly
                class="date-picker-trigger w-full px-4 py-3 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 transition-all cursor-pointer accent-focus-ring"
                :placeholder="t('dataManage.selectDateRangePlaceholder')"
                @click.stop="openRangePicker"
              />
              <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>

          <div v-if="rangeMatchedDates.length > 0" class="p-3 accent-matched-bg rounded-xl">
            <div class="text-xs accent-matched-text font-medium mb-2">{{ t('dataManage.matchedDates', { n: rangeMatchedDates.length }) }}</div>
            <div class="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
              <span v-for="d in rangeMatchedDates" :key="d" class="inline-block px-2 py-1 bg-white/80 dark:bg-slate-700/80 text-xs text-slate-600 dark:text-slate-400 rounded-lg border border-slate-100 dark:border-slate-600">{{ d }}</span>
            </div>
          </div>

          <button
            class="btn-accent w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all"
            :disabled="deleteLoading || rangeMatchedDates.length === 0"
            @click="handleBatchDelete"
          >
            <Loader2 v-if="deleteLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            {{ deleteLoading ? t('common.loading') : t('dataManage.confirmBatchDelete', { n: rangeMatchedDates.length }) }}
          </button>
        </div>

        <div v-if="deleteError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{{ deleteError }}</div>
        <div v-if="deleteResult" class="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl">
          <div class="font-semibold text-emerald-800 dark:text-emerald-300 text-sm mb-2">{{ t('dataManage.batchDeleteSuccess') }}</div>
          <div class="flex flex-wrap gap-3 text-xs text-emerald-700 dark:text-emerald-400">
            <span>{{ t('dataManage.totalDates') }}: {{ deleteResult.total_dates }}</span>
            <span>{{ t('dataManage.mapDeleted') }}: {{ deleteResult.total_map_deleted }}</span>
            <span>{{ t('dataManage.playerDeleted') }}: {{ deleteResult.total_player_deleted }}</span>
            <span>{{ t('dataManage.detailDeleted') }}: {{ deleteResult.total_detail_deleted }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 group">
        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
          <div class="w-12 h-12 accent-icon-bg rounded-xl flex items-center justify-center">
            <Trash2 class="w-6 h-6 accent-icon-color" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.deleteAll') }}</h3>
        </div>

        <div class="space-y-4">
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('dataManage.deleteAllHint') }}</p>
          <button
            class="btn-danger inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all"
            :disabled="deleteAllLoading"
            @click="showDeleteAllConfirm = true"
          >
            <Loader2 v-if="deleteAllLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            {{ deleteAllLoading ? t('common.loading') : t('dataManage.deleteAllConfirm') }}
          </button>
        </div>

        <div v-if="deleteAllError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800/50 rounded-xl text-sm text-red-700 dark:text-red-400">{{ deleteAllError }}</div>
        <div v-if="deleteAllResult" class="mt-4 p-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/50 rounded-xl">
          <div class="font-semibold text-emerald-800 dark:text-emerald-300 text-sm mb-2">{{ t('dataManage.deleteAllSuccess') }}</div>
          <div class="flex flex-wrap gap-3 text-xs text-emerald-700 dark:text-emerald-400">
            <span>{{ t('dataManage.mapDeleted') }}: {{ deleteAllResult.total_map_deleted }}</span>
            <span>{{ t('dataManage.playerDeleted') }}: {{ deleteAllResult.total_player_deleted }}</span>
            <span>{{ t('dataManage.detailDeleted') }}: {{ deleteAllResult.total_detail_deleted }}</span>
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
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">
                {{ folderBrowserMode === 'archive' ? t('dataManage.selectArchive') : t('dataManage.selectFolder') }}
              </h3>
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
              @click="browseTo(folderBrowserParent === '__root__' ? '' : folderBrowserParent)"
            >
              <ArrowLeft class="w-4 h-4" />
              <span>{{ (folderBrowserIsRoot || folderBrowserParent === '__root__') ? t('dataManage.selectDrive') : '..' }}</span>
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
            <button
              v-if="folderBrowserMode === 'archive' || folderBrowserMode === 'batch'"
              v-for="archive in folderBrowserArchives"
              :key="archive.path"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all"
              :class="folderBrowserMode === 'archive' ? 'text-slate-700 dark:text-slate-300 hover:bg-brand/5 dark:hover:bg-brand/10 hover:text-brand dark:hover:text-brand-light' : 'text-slate-400 dark:text-slate-500'"
              @click="folderBrowserMode === 'archive' && selectArchiveAndClose(archive.path)"
            >
              <FileArchive class="w-4 h-4 text-amber-500 dark:text-amber-400" />
              <span>{{ archive.name }}</span>
            </button>
          </div>

          <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <div v-if="(folderBrowserMode === 'archive' || folderBrowserMode === 'batch') && folderBrowserArchives.length > 0" class="text-xs text-slate-400 dark:text-slate-500">
              {{ t('dataManage.archiveCount', { n: folderBrowserArchives.length }) }}
            </div>
            <div v-else></div>
            <div class="flex gap-2">
              <button class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all" @click="showFolderBrowser = false">{{ t('dataManage.cancel') }}</button>
              <button
                v-if="folderBrowserMode !== 'archive'"
                class="btn-brand px-4 py-2 text-sm rounded-lg transition-all"
                :disabled="!folderBrowserPath || folderBrowserIsRoot"
                @click="selectFolderAndClose"
              >
                {{ t('dataManage.selectThisFolder') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <DatePickerPopup
        :visible="showScanDatePicker"
        :available-dates="dates"
        mode="single"
        color-scheme="brand"
        :selected-date="scanDate"
        :popup-style="popupStyle"
        :free-select="true"
        @select="handleSelectScanDate"
        @clear="handleScanDateClear"
      />
    </Teleport>

    <Teleport to="body">
      <DatePickerPopup
        :visible="showSingleDatePicker"
        :available-dates="dates"
        mode="single"
        color-scheme="accent"
        :selected-date="deleteDate"
        :popup-style="popupStyle"
        @select="handleSelectSingleDate"
        @clear="handleSingleClear"
      />
    </Teleport>

    <Teleport to="body">
      <DatePickerPopup
        :visible="showRangePicker"
        :available-dates="dates"
        mode="range"
        color-scheme="accent"
        :range-start="rangeStart"
        :range-end="rangeEnd"
        :popup-style="popupStyle"
        @select-range="handleSelectRange"
        @clear="handleRangeClear"
      />
    </Teleport>

    <Teleport to="body">
      <div v-if="globalLoading" class="global-loading-overlay">
        <div class="global-loading-card dark:bg-slate-800">
          <div class="h-12 flex items-center justify-center">
            <Loader2 class="w-12 h-12 animate-spin text-brand" />
          </div>
          <div class="mt-6 text-base font-semibold text-slate-700 dark:text-slate-200">{{ globalLoadingText }}</div>
          <div v-if="globalLoadingSubText" class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ globalLoadingSubText }}</div>
          <div v-if="progressTotal > 0" class="mt-4 w-64">
            <div class="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
              <div class="h-full bg-brand rounded-full transition-all duration-300 ease-out" :style="{ width: `${progressTotal > 0 ? (progressCurrent / progressTotal) * 100 : 0}%` }" />
            </div>
            <div class="mt-2 text-xs text-slate-400 dark:text-slate-500 text-center">{{ progressCurrent }} / {{ progressTotal }}</div>
          </div>
          <div v-else class="mt-2 text-sm text-slate-400 dark:text-slate-500">{{ t('common.loading') }}</div>
          <button
            v-if="abortController"
            class="mt-4 px-4 py-2 text-sm text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 border border-red-200 dark:border-red-800/50 rounded-lg transition-all"
            @click="cancelBatchScan"
          >
            {{ t('dataManage.cancelScan') }}
          </button>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDeleteAllConfirm" class="global-loading-overlay" @click.self="showDeleteAllConfirm = false">
        <div class="folder-browser-card dark:bg-slate-800 dark:border-slate-700">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-gradient-to-br from-red-500/20 to-red-500/10 rounded-xl flex items-center justify-center">
              <Trash2 class="w-5 h-5 text-red-500" />
            </div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dataManage.deleteAll') }}</h3>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-6">{{ t('dataManage.deleteAllHint') }}</p>
          <div class="flex items-center justify-end gap-2">
            <button class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all" @click="showDeleteAllConfirm = false">{{ t('dataManage.cancel') }}</button>
            <button
              class="btn-danger px-4 py-2 text-sm rounded-lg transition-all inline-flex items-center gap-2"
              @click="handleDeleteAll"
            >
              <Trash2 class="w-4 h-4" />
              {{ t('dataManage.deleteAllConfirm') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
