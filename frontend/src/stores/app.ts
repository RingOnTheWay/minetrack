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
}

export type NavKey = '/' | '/map' | '/players' | '/battle' | '/craft' | '/items' | '/activity' | '/data-manage'

const ALL_NAV_KEYS: NavKey[] = ['/', '/map', '/players', '/battle', '/craft', '/items', '/activity', '/data-manage']

const DEFAULT_NAV_VISIBILITY: Record<NavKey, boolean> = {
  '/': true,
  '/map': true,
  '/players': true,
  '/battle': true,
  '/craft': true,
  '/items': true,
  '/activity': true,
  '/data-manage': true,
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
    if (key === '/data-manage' && isStatic) return
    navVisibility.value[key] = !navVisibility.value[key]
  }

  function isNavVisible(key: NavKey): boolean {
    if (key === '/data-manage' && isStatic) return false
    return navVisibility.value[key]
  }

  function toggleChartTotal() {
    showChartTotal.value = !showChartTotal.value
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

  return {
    mode,
    loading,
    error,
    darkMode,
    themeColorPrimary,
    navVisibility,
    showChartTotal,
    currentTheme,
    isLocal,
    isStatic,
    isDark,
    initialize,
    setMode,
    setLoading,
    setError,
    toggleDarkMode,
    setThemeColor,
    toggleNavVisibility,
    isNavVisible,
    toggleChartTotal,
  }
})
