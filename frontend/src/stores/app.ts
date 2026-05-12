import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const mode = ref<'local' | 'static'>('local')
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isLocal = computed(() => mode.value === 'local')
  const isStatic = computed(() => mode.value === 'static')

  function initialize() {
    const searchParams = new URLSearchParams(window.location.search)
    if (searchParams.get('mode') === 'static' || window.location.protocol === 'file:') {
      mode.value = 'static'
    }
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
    isLocal,
    isStatic,
    initialize,
    setMode,
    setLoading,
    setError,
  }
})