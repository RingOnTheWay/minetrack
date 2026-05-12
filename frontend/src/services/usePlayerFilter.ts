import { ref, computed } from 'vue'

const DEFAULT_PLAYERS = ['MuxiAcio', 'RingOfficial', 'Roxy', 'hwj', 'roxy']

export function usePlayerFilter(allPlayers: Set<string>) {
  const selected = ref<Set<string>>(new Set<string>())

  const sortedPlayers = computed(() =>
    Array.from(allPlayers).sort()
  )

  function init() {
    selected.value.clear()
    const filtered = DEFAULT_PLAYERS.filter(p => allPlayers.has(p))
    if (filtered.length > 0) {
      filtered.forEach(p => selected.value.add(p))
    } else {
      allPlayers.forEach(p => selected.value.add(p))
    }
  }

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
    allPlayers.forEach(p => selected.value.add(p))
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
