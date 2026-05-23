import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

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

  const filterEnabled = ref<boolean>((() => {
    try {
      const stored = localStorage.getItem('filterEnabled')
      if (stored !== null) return stored === 'true'
    } catch {}
    return false
  })())

  const minPlaytimeHours = ref<number>((() => {
    try {
      const stored = localStorage.getItem('minPlaytimeHours')
      if (stored !== null) return parseFloat(stored) || 1
    } catch {}
    return 1
  })())

  const whitelist = ref<string[]>((() => {
    try {
      const stored = localStorage.getItem('whitelist')
      if (stored !== null) return JSON.parse(stored)
    } catch {}
    return []
  })())

  const blacklist = ref<string[]>((() => {
    try {
      const stored = localStorage.getItem('blacklist')
      if (stored !== null) return JSON.parse(stored)
    } catch {}
    return []
  })())

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
    filterEnabled.value = val
  }

  function setMinPlaytimeHours(val: number) {
    minPlaytimeHours.value = val
  }

  function setWhitelist(val: string[]) {
    whitelist.value = val
  }

  function setBlacklist(val: string[]) {
    blacklist.value = val
  }

  function setAutoScanEnabled(val: boolean) {
    autoScanEnabled.value = val
  }

  function setAutoScanFolder(val: string) {
    autoScanFolder.value = val
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

  watch(filterEnabled, (val) => {
    try {
      localStorage.setItem('filterEnabled', String(val))
    } catch {}
  })

  watch(minPlaytimeHours, (val) => {
    try {
      localStorage.setItem('minPlaytimeHours', String(val))
    } catch {}
  })

  watch(whitelist, (val) => {
    try {
      localStorage.setItem('whitelist', JSON.stringify(val))
    } catch {}
  }, { deep: true })

  watch(blacklist, (val) => {
    try {
      localStorage.setItem('blacklist', JSON.stringify(val))
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
    autoScanEnabled,
    autoScanFolder,
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
    setAutoScanEnabled,
    setAutoScanFolder,
  }
})
