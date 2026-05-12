import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAppStore } from './app'

export const useDataStore = defineStore('data', () => {
  const mapSizes = ref<Record<string, Record<string, number>>>({})
  const playerStats = ref<Record<string, Record<string, Record<string, number>>>>({})
  const battleStats = ref<{ killed: Record<string, Record<string, Record<string, number>>>; killed_by: Record<string, Record<string, Record<string, number>>> }>({
    killed: {}, killed_by: {},
  })
  const craftStats = ref<{ crafted: Record<string, Record<string, Record<string, number>>>; used: Record<string, Record<string, Record<string, number>>> }>({
    crafted: {}, used: {},
  })
  const itemStats = ref<{ picked_up: Record<string, Record<string, Record<string, number>>>; dropped: Record<string, Record<string, Record<string, number>>>; used: Record<string, Record<string, Record<string, number>>> }>({
    picked_up: {}, dropped: {}, used: {},
  })

  const allDates = ref<string[]>([])
  const allPlayers = ref<Set<string>>(new Set())
  const loading = ref(false)
  const loaded = ref(false)

  function collectPlayersFromStats(stats: Record<string, Record<string, number>>) {
    Object.values(stats).forEach(dateData => {
      Object.keys(dateData || {}).forEach(p => allPlayers.value.add(p))
    })
  }

  function collectPlayersFromDetail(stats: Record<string, Record<string, Record<string, number>>>) {
    Object.values(stats).forEach(dateData => {
      Object.keys(dateData || {}).forEach(p => allPlayers.value.add(p))
    })
  }

  async function loadFromAPI() {
    const statTypes = ['play_time', 'deaths', 'mob_kills', 'player_kills', 'jumps',
      'distance_walked', 'sprint_one_cm', 'walk_one_cm', 'fly_one_cm', 'climb_one_cm',
      'swim_one_cm', 'horse_one_cm', 'boat_one_cm', 'aviate_one_cm', 'fall_one_cm']

    const playerStatsPromises = statTypes.map(async t => {
      const r = await fetch(`/api/player_stats?type=${encodeURIComponent(t)}`)
      return { t, data: await r.json() }
    })

    const promises = [
      fetch('/api/map_sizes').then(r => r.json()),
      Promise.all(playerStatsPromises),
      fetch('/api/stats/battle?category=killed').then(r => r.json()),
      fetch('/api/stats/battle?category=killed_by').then(r => r.json()),
      fetch('/api/stats/craft?category=crafted').then(r => r.json()).catch(() => ({})),
      fetch('/api/stats/craft?category=used').then(r => r.json()).catch(() => ({})),
      fetch('/api/stats/item?category=picked_up').then(r => r.json()).catch(() => ({})),
      fetch('/api/stats/item?category=dropped').then(r => r.json()).catch(() => ({})),
      fetch('/api/stats/item?category=used').then(r => r.json()).catch(() => ({})),
    ]

    const [ms, psArr, bk, bkBy, cc, cu, ip, id, iu] = await Promise.all(promises)

    mapSizes.value = ms || {}
    const ps: Record<string, any> = {}
    psArr.forEach((item: any) => { ps[item.t] = item.data || {} })
    playerStats.value = ps
    battleStats.value = { killed: bk || {}, killed_by: bkBy || {} }
    craftStats.value = { crafted: cc || {}, used: cu || {} }
    itemStats.value = { picked_up: ip || {}, dropped: id || {}, used: iu || {} }
  }

  async function loadStaticData() {
    const r = await fetch('data.json')
    const data = await r.json()
    mapSizes.value = data.map_sizes || {}
    playerStats.value = data.player_stats || {}
    if (data.battle_stats) battleStats.value = data.battle_stats
    if (data.craft_stats) craftStats.value = data.craft_stats
    if (data.item_stats) itemStats.value = data.item_stats
    if (data.detail_stats) {
      const ds = data.detail_stats
      if (ds.battle) battleStats.value = ds.battle as any
      if (ds.craft) craftStats.value = ds.craft as any
      if (ds.item) itemStats.value = ds.item as any
    }
  }

  function extractMetadata() {
    allPlayers.value.clear()
    const dateSet = new Set<string>()
    Object.keys(mapSizes.value).forEach(d => dateSet.add(d))
    Object.values(playerStats.value).forEach((statData: any) => {
      Object.keys(statData).forEach(d => {
        dateSet.add(d)
        collectPlayersFromStats(statData[d] as any)
      })
    })
    Object.values(battleStats.value).forEach((catData: any) => collectPlayersFromDetail(catData))
    Object.values(craftStats.value).forEach((catData: any) => collectPlayersFromDetail(catData))
    Object.values(itemStats.value).forEach((catData: any) => collectPlayersFromDetail(catData))
    allDates.value = Array.from(dateSet).sort()
  }

  async function loadAll() {
    if (loaded.value) return
    loading.value = true
    try {
      const appStore = useAppStore()
      if (appStore.isStatic) {
        await loadStaticData()
      } else {
        await loadFromAPI()
      }
      extractMetadata()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  return {
    mapSizes, playerStats, battleStats, craftStats, itemStats,
    allDates, allPlayers, loading, loaded,
    loadAll,
  }
})