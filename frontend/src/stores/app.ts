import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { apiGet } from '@/services/api'

export interface ThemeColor {
  name: string
  primary: string
  light: string
  dark: string
}

export const themePresets: ThemeColor[] = [
  { name: 'Emerald', primary: '#779977', light: '#99bb99', dark: '#556655' },
  { name: 'Amber', primary: '#BB9955', light: '#D4B877', dark: '#8A6D33' },
  { name: 'Teal', primary: '#335566', light: '#557788', dark: '#223344' },
  { name: 'Rose', primary: '#AA4477', light: '#CC6699', dark: '#883355' },
  { name: 'Sky', primary: '#7799CC', light: '#99BBDD', dark: '#5577AA' },
  { name: 'HotPink', primary: '#FF2291', light: '#FF55AA', dark: '#CC1177' },
  { name: 'Gold', primary: '#FFD700', light: '#FFE44D', dark: '#CCB000' },
  { name: 'Navy', primary: '#38538A', light: '#5A75AA', dark: '#263A60' },
  { name: 'Crimson', primary: '#FF4637', light: '#FF7066', dark: '#CC3328' },
]

export const THEME_GROUPS: { label: string; presets: ThemeColor[] }[] = [
  {
    label: 'AM',
    presets: [
      themePresets.find(p => p.name === 'Rose')!,
      themePresets.find(p => p.name === 'Emerald')!,
      themePresets.find(p => p.name === 'Sky')!,
      themePresets.find(p => p.name === 'Amber')!,
      themePresets.find(p => p.name === 'Teal')!,
    ],
  },
  {
    label: 'KB',
    presets: [
      themePresets.find(p => p.name === 'Gold')!,
      themePresets.find(p => p.name === 'Navy')!,
      themePresets.find(p => p.name === 'Crimson')!,
      themePresets.find(p => p.name === 'HotPink')!,
    ],
  },
]

function findGroup(primary: string): { label: string; presets: ThemeColor[] } {
  return THEME_GROUPS.find(g => g.presets.some(p => p.primary === primary)) || THEME_GROUPS[0]
}

function findPreset(primary: string): ThemeColor {
  return themePresets.find(p => p.primary === primary) || themePresets[0]
}

function applyThemeColor(theme: ThemeColor) {
  const root = document.documentElement
  root.style.setProperty('--color-brand', theme.primary)
  root.style.setProperty('--color-brand-light', theme.light)
  root.style.setProperty('--color-brand-dark', theme.dark)
  root.style.setProperty('--brand', theme.primary)
  root.style.setProperty('--brand-light', theme.light)
  root.style.setProperty('--brand-dark', theme.dark)

  const group = findGroup(theme.primary)
  group.presets.forEach((preset, i) => {
    root.style.setProperty(`--honor-glow-${i + 1}`, preset.primary)
    root.style.setProperty(`--honor-glow-${i + 1}-light`, preset.light)
    root.style.setProperty(`--honor-glow-${i + 1}-dark`, preset.dark)
  })
  root.style.setProperty('--honor-glow-count', String(group.presets.length))
}

export type NavKey = '/' | '/map' | '/players' | '/battle' | '/craft' | '/items' | '/blocks' | '/activity' | '/data-manage' | '/honor'

const ALL_NAV_KEYS: NavKey[] = ['/', '/map', '/players', '/battle', '/craft', '/items', '/blocks', '/activity', '/data-manage', '/honor']

const ROUTE_LOADING_MESSAGES: Record<string, string> = {
  '/': '少女布置仪表盘中...',
  '/map': '少女丈量世界版图中...',
  '/players': '少女翻阅玩家名册中...',
  '/battle': '少女磨砺兵刃中...',
  '/craft': '少女点燃熔炉中...',
  '/items': '少女清点背包中...',
  '/blocks': '少女挥舞镐头中...',
  '/activity': '少女追踪足迹中...',
  '/data-manage': '少女整理档案中...',
  '/honor': '少女颁发荣誉中...',
  '/settings': '少女调整旋钮中...',
}

const DEFAULT_ROUTE_LOADING_MESSAGE = '少女祈祷中...'

const DEFAULT_NAV_VISIBILITY: Record<NavKey, boolean> = {
  '/': true,
  '/map': true,
  '/players': true,
  '/battle': true,
  '/craft': true,
  '/items': true,
  '/blocks': true,
  '/activity': true,
  '/data-manage': true,
  '/honor': true,
}

function loadNavVisibility(): Record<NavKey, boolean> {
  try {
    const stored = localStorage.getItem('navVisibility')
    if (stored) {
      const parsed = JSON.parse(stored)
      const result = { ...DEFAULT_NAV_VISIBILITY }
      for (const key of ALL_NAV_KEYS) {
        if (typeof parsed[key] === 'boolean') {
          result[key] = parsed[key]
        }
      }
      return result
    }
  } catch {}
  return { ...DEFAULT_NAV_VISIBILITY }
}

export interface FilterConfig {
  filterEnabled: boolean
  minPlaytimeHours: number
  whitelist: string[]
  blacklist: string[]
}

const DEFAULT_FILTER: FilterConfig = {
  filterEnabled: false,
  minPlaytimeHours: 1,
  whitelist: [],
  blacklist: [],
}

function loadGlobalFilter(): FilterConfig {
  try {
    const enabled = localStorage.getItem('filterEnabled')
    const hours = localStorage.getItem('minPlaytimeHours')
    const wl = localStorage.getItem('whitelist')
    const bl = localStorage.getItem('blacklist')
    return {
      filterEnabled: enabled !== null ? enabled === 'true' : DEFAULT_FILTER.filterEnabled,
      minPlaytimeHours: hours !== null ? parseFloat(hours) || DEFAULT_FILTER.minPlaytimeHours : DEFAULT_FILTER.minPlaytimeHours,
      whitelist: wl !== null ? JSON.parse(wl) : DEFAULT_FILTER.whitelist,
      blacklist: bl !== null ? JSON.parse(bl) : DEFAULT_FILTER.blacklist,
    }
  } catch {
    return { ...DEFAULT_FILTER }
  }
}

function loadServerFilter(serverName: string): FilterConfig {
  if (!serverName) return loadGlobalFilter()
  try {
    const stored = localStorage.getItem(`filter_config_${serverName}`)
    if (stored !== null) return JSON.parse(stored)
  } catch {}
  // 新服务器从全局模板复制
  return { ...loadGlobalFilter() }
}

function saveServerFilter(serverName: string, config: FilterConfig) {
  if (!serverName) return
  try {
    localStorage.setItem(`filter_config_${serverName}`, JSON.stringify(config))
  } catch {}
}

export const useAppStore = defineStore('app', () => {
  const mode = ref<'local' | 'static'>('local')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const routeLoading = ref(false)
  const routeLoadingMessage = ref(DEFAULT_ROUTE_LOADING_MESSAGE)

  const darkMode = ref<boolean>((() => {
    try {
      const stored = localStorage.getItem('darkMode')
      if (stored !== null) return stored === 'true'
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    } catch {
      return false
    }
  })())

  const themeColorPrimary = ref<string>((() => {
    try {
      const stored = localStorage.getItem('themeColor')
      if (stored !== null) return stored
    } catch {}
    return '#779977'
  })())

  const navVisibility = ref<Record<NavKey, boolean>>(loadNavVisibility())

  const showChartTotal = ref<boolean>((() => {
    try {
      const stored = localStorage.getItem('showChartTotal')
      if (stored !== null) return stored === 'true'
    } catch {}
    return false
  })())

  const maxLegendPlayers = ref<number>((() => {
    try {
      const stored = localStorage.getItem('maxLegendPlayers')
      if (stored !== null) return parseInt(stored, 10) || 10
    } catch {}
    return 10
  })())

  const defaultSelectedPlayers = ref<string[]>((() => {
    try {
      const stored = localStorage.getItem('defaultSelectedPlayers')
      if (stored !== null) return JSON.parse(stored)
    } catch {}
    return []
  })())

  // 全局默认 filter（设置页模板）
  const globalFilter = ref<FilterConfig>(loadGlobalFilter())

  // 兼容旧代码的 computed 属性（serverFilter 在 currentServer 之后初始化）
  const serverFilter = ref<FilterConfig>({ ...DEFAULT_FILTER })

  const filterEnabled = computed(() => serverFilter.value.filterEnabled)
  const minPlaytimeHours = computed(() => serverFilter.value.minPlaytimeHours)
  const whitelist = computed(() => serverFilter.value.whitelist)
  const blacklist = computed(() => serverFilter.value.blacklist)

  const autoScanEnabled = ref<boolean>((() => {
    try {
      const stored = localStorage.getItem('autoScanEnabled')
      if (stored !== null) return stored === 'true'
    } catch {}
    return false
  })())

  const autoScanFolder = ref<string>((() => {
    try {
      const stored = localStorage.getItem('autoScanFolder')
      if (stored !== null) return stored
    } catch {}
    return ''
  })())

  const servers = ref<string[]>([])
  const currentServer = ref<string>((() => {
    try {
      const stored = localStorage.getItem('currentServer')
      if (stored !== null) return stored
    } catch {}
    return ''
  })())
  const serversLoaded = ref<boolean>(false)
  // currentServer 已定义，现在初始化 serverFilter
  serverFilter.value = loadServerFilter(currentServer.value || '')
  const autoScanServerName = ref<string>((() => {
    try {
      const stored = localStorage.getItem('autoScanServerName')
      if (stored !== null) return stored
    } catch {}
    return ''
  })())

  const currentTheme = computed<ThemeColor>(() => findPreset(themeColorPrimary.value))
  const isLocal = computed(() => mode.value === 'local')
  const isStatic = computed(() => mode.value === 'static')
  const isDark = computed(() => darkMode.value)

  function applyDarkMode(dark: boolean) {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleDarkMode() {
    darkMode.value = !darkMode.value
  }

  function setThemeColor(primary: string) {
    themeColorPrimary.value = primary
  }

  function toggleNavVisibility(key: NavKey) {
    if (key === '/data-manage' && isStatic.value) return
    navVisibility.value[key] = !navVisibility.value[key]
  }

  function isNavVisible(key: NavKey): boolean {
    if (key === '/data-manage' && isStatic.value) return false
    return navVisibility.value[key]
  }

  function toggleChartTotal() {
    showChartTotal.value = !showChartTotal.value
  }

  function setMaxLegendPlayers(val: number) {
    maxLegendPlayers.value = val
  }

  function setDefaultSelectedPlayers(val: string[]) {
    defaultSelectedPlayers.value = val
  }

  function setFilterEnabled(val: boolean) {
    serverFilter.value = { ...serverFilter.value, filterEnabled: val }
    saveServerFilter(currentServer.value, serverFilter.value)
  }

  function setMinPlaytimeHours(val: number) {
    serverFilter.value = { ...serverFilter.value, minPlaytimeHours: val }
    saveServerFilter(currentServer.value, serverFilter.value)
  }

  function setWhitelist(val: string[]) {
    serverFilter.value = { ...serverFilter.value, whitelist: val }
    saveServerFilter(currentServer.value, serverFilter.value)
  }

  function setBlacklist(val: string[]) {
    serverFilter.value = { ...serverFilter.value, blacklist: val }
    saveServerFilter(currentServer.value, serverFilter.value)
  }

  // 全局 filter setter（设置页模板）
  function setGlobalFilterEnabled(val: boolean) {
    globalFilter.value = { ...globalFilter.value, filterEnabled: val }
    persistGlobalFilter()
  }

  function setGlobalMinPlaytimeHours(val: number) {
    globalFilter.value = { ...globalFilter.value, minPlaytimeHours: val }
    persistGlobalFilter()
  }

  function setGlobalWhitelist(val: string[]) {
    globalFilter.value = { ...globalFilter.value, whitelist: val }
    persistGlobalFilter()
  }

  function setGlobalBlacklist(val: string[]) {
    globalFilter.value = { ...globalFilter.value, blacklist: val }
    persistGlobalFilter()
  }

  function persistGlobalFilter() {
    try {
      localStorage.setItem('filterEnabled', String(globalFilter.value.filterEnabled))
      localStorage.setItem('minPlaytimeHours', String(globalFilter.value.minPlaytimeHours))
      localStorage.setItem('whitelist', JSON.stringify(globalFilter.value.whitelist))
      localStorage.setItem('blacklist', JSON.stringify(globalFilter.value.blacklist))
    } catch {}
  }

  // 将全局模板应用到当前服务器
  function applyGlobalFilterToServer() {
    serverFilter.value = { ...globalFilter.value }
    saveServerFilter(currentServer.value, serverFilter.value)
  }

  // 将当前服务器配置应用到全局模板
  function applyServerFilterToGlobal() {
    globalFilter.value = { ...serverFilter.value }
    persistGlobalFilter()
  }

  function setAutoScanEnabled(val: boolean) {
    autoScanEnabled.value = val
  }

  function setAutoScanFolder(val: string) {
    autoScanFolder.value = val
  }

  function setServers(list: string[]) {
    servers.value = list
  }

  function setCurrentServer(name: string) {
    currentServer.value = name
  }

  async function loadServers() {
    try {
      const list = await apiGet<string[]>('/api/servers')
      servers.value = list
      serversLoaded.value = true
      if (list.length > 0 && !list.includes(currentServer.value)) {
        currentServer.value = list[0]
      } else if (list.length === 0) {
        currentServer.value = ''
      }
    } catch {
      serversLoaded.value = true
    }
  }

  function setAutoScanServerName(val: string) {
    autoScanServerName.value = val
  }

  watch(darkMode, (val) => {
    applyDarkMode(val)
    try {
      localStorage.setItem('darkMode', String(val))
    } catch {}
  }, { immediate: true })

  watch(themeColorPrimary, (val) => {
    const theme = findPreset(val)
    applyThemeColor(theme)
    try {
      localStorage.setItem('themeColor', val)
    } catch {}
  }, { immediate: true })

  watch(navVisibility, (val) => {
    try {
      localStorage.setItem('navVisibility', JSON.stringify(val))
    } catch {}
  }, { deep: true })

  watch(showChartTotal, (val) => {
    try {
      localStorage.setItem('showChartTotal', String(val))
    } catch {}
  })

  watch(maxLegendPlayers, (val) => {
    try {
      localStorage.setItem('maxLegendPlayers', String(val))
    } catch {}
  })

  watch(defaultSelectedPlayers, (val) => {
    try {
      localStorage.setItem('defaultSelectedPlayers', JSON.stringify(val))
    } catch {}
  }, { deep: true })

  watch(autoScanEnabled, (val) => {
    try {
      localStorage.setItem('autoScanEnabled', String(val))
    } catch {}
  })

  watch(autoScanFolder, (val) => {
    try {
      localStorage.setItem('autoScanFolder', val)
    } catch {}
  })

  watch(currentServer, (val) => {
    try {
      localStorage.setItem('currentServer', val)
    } catch {}
    // 切换服务器时加载对应 filter 配置
    serverFilter.value = loadServerFilter(val || '')
  })

  watch(autoScanServerName, (val) => {
    try {
      localStorage.setItem('autoScanServerName', val)
    } catch {}
  })

  function initialize() {
    const searchParams = new URLSearchParams(window.location.search)
    if (searchParams.get('mode') === 'static' || window.location.protocol === 'file:') {
      mode.value = 'static'
    }
    applyDarkMode(darkMode.value)
    applyThemeColor(currentTheme.value)
  }

  function setMode(newMode: 'local' | 'static') {
    mode.value = newMode
  }

  function setLoading(val: boolean) {
    loading.value = val
  }

  function setError(err: string | null) {
    error.value = err
  }

  function setRouteLoading(val: boolean, path?: string) {
    routeLoading.value = val
    if (val && path) {
      routeLoadingMessage.value = ROUTE_LOADING_MESSAGES[path] || DEFAULT_ROUTE_LOADING_MESSAGE
    }
  }

  return {
    mode,
    loading,
    error,
    routeLoading,
    routeLoadingMessage,
    darkMode,
    themeColorPrimary,
    navVisibility,
    showChartTotal,
    maxLegendPlayers,
    defaultSelectedPlayers,
    filterEnabled,
    minPlaytimeHours,
    whitelist,
    blacklist,
    globalFilter,
    serverFilter,
    autoScanEnabled,
    autoScanFolder,
    servers,
    currentServer,
    serversLoaded,
    autoScanServerName,
    currentTheme,
    isLocal,
    isStatic,
    isDark,
    initialize,
    setMode,
    setLoading,
    setError,
    setRouteLoading,
    toggleDarkMode,
    setThemeColor,
    toggleNavVisibility,
    isNavVisible,
    toggleChartTotal,
    setMaxLegendPlayers,
    setDefaultSelectedPlayers,
    setFilterEnabled,
    setMinPlaytimeHours,
    setWhitelist,
    setBlacklist,
    setGlobalFilterEnabled,
    setGlobalMinPlaytimeHours,
    setGlobalWhitelist,
    setGlobalBlacklist,
    applyGlobalFilterToServer,
    applyServerFilterToGlobal,
    setAutoScanEnabled,
    setAutoScanFolder,
    setServers,
    setCurrentServer,
    loadServers,
    setAutoScanServerName,
  }
})
