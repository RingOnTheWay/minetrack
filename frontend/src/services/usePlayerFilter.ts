import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'

export function usePlayerFilter(allPlayers: () => Set<string>) {
  const selected = ref<Set<string>>(new Set<string>())

  const sortedPlayers = computed(() =>
    Array.from(allPlayers()).sort()
  )

  function init() {
    const app = useAppStore()
    const defaults = app.defaultSelectedPlayers
    const players = allPlayers()
    if (defaults.length > 0) {
      selected.value = new Set<string>()
      for (const p of defaults) {
        if (players.has(p)) {
          selected.value.add(p)
        }
      }
      if (selected.value.size === 0) {
        players.forEach(p => selected.value.add(p))
      }
    } else {
      selected.value = new Set<string>()
      players.forEach(p => selected.value.add(p))
    }
  }

  // Auto re-init when player set changes (e.g. server switch)
  watch(() => allPlayers().size, () => {
    init()
  })

  function toggle(player: string) {
    if (selected.value.has(player)) {
      selected.value.delete(player)
    } else {
      selected.value.add(player)
    }
  }

  function remove(player: string) {
    selected.value.delete(player)
  }

  function selectAll() {
    allPlayers().forEach(p => selected.value.add(p))
  }

  function deselectAll() {
    selected.value.clear()
  }

  return { selected, sortedPlayers, init, toggle, remove, selectAll, deselectAll }
}

export function generateColors(count: number): string[] {
  const colors: string[] = []
  for (let i = 0; i < count; i++) {
    const hue = (i * 137.508) % 360
    colors.push(`hsl(${hue}, 70%, 50%)`)
  }
  return colors
}

export function generateColorPairs(count: number): { border: string; bg: string }[] {
  const pairs: { border: string; bg: string }[] = []
  for (let i = 0; i < count; i++) {
    const hue = (i * 137.508) % 360
    pairs.push({
      border: `hsl(${hue}, 70%, 45%)`,
      bg: `hsla(${hue}, 70%, 60%, 0.18)`,
    })
  }
  return pairs
}
