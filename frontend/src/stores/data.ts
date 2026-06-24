import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAppStore } from './app'

const LOADING_MESSAGES = [
  '少女丈量世界版图中...',
  '少女翻阅时光日记中...',
  '少女记录死亡笔记中...',
  '少女清点怪物战利品中...',
  '少女围观玩家互殴中...',
  '少女数着跳跃次数中...',
  '少女追踪足迹中...',
  '少女测量疾跑距离中...',
  '少女仰望飞行轨迹中...',
  '少女潜水探测中...',
  '少女策马奔腾中...',
  '少女泛舟湖上中...',
  '少女翱翔天际中...',
  '少女计算坠落距离中...',
  '少女包扎伤口中...',
  '少女整理床铺中...',
  '少女垂钓统计中...',
  '少女喂养动物中...',
  '少女与村民讨价还价中...',
  '少女施展附魔中...',
  '少女敲打工作台中...',
  '少女烧炼矿石中...',
  '少女锻造铁砧中...',
  '少女翻箱倒柜中...',
  '少女敲响钟声中...',
  '少女品尝蛋糕中...',
  '少女潜行观察中...',
  '少女记录击杀战报中...',
  '少女撰写阵亡通知中...',
  '少女打造装备中...',
  '少女试用道具中...',
  '少女拾取战利品中...',
  '少女丢弃杂物中...',
  '少女挖掘方块中...',
  '少女整理情报中...',
]

const DEFAULT_LOADING_MESSAGE = '少女祈祷中...'

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
  const blockStats = ref<{ mined: Record<string, Record<string, Record<string, number>>>; broken: Record<string, Record<string, Record<string, number>>> }>({
    mined: {}, broken: {},
  })

  const allDates = ref<string[]>([])
  const allPlayers = ref<Set<string>>(new Set())
  const loading = ref(false)
  const loaded = ref(false)
  const loadingMessage = ref(DEFAULT_LOADING_MESSAGE)

  let messageTimer: ReturnType<typeof setInterval> | null = null
  let messageIndex = 0

  function startMessageRotation() {
    messageIndex = 0
    loadingMessage.value = LOADING_MESSAGES[0]
    messageTimer = setInterval(() => {
      messageIndex = (messageIndex + 1) % LOADING_MESSAGES.length
      loadingMessage.value = LOADING_MESSAGES[messageIndex]
    }, 800)
  }

  function stopMessageRotation() {
    if (messageTimer) {
      clearInterval(messageTimer)
      messageTimer = null
    }
    loadingMessage.value = DEFAULT_LOADING_MESSAGE
  }

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
    const appStore = useAppStore()
    const serverName = appStore.currentServer
    if (!serverName) return

    const sn = encodeURIComponent(serverName)
    const statTypes = ['play_time', 'deaths', 'mob_kills', 'player_kills', 'jumps',
      'distance_walked', 'sprint_one_cm', 'walk_one_cm', 'fly_one_cm', 'climb_one_cm',
      'swim_one_cm', 'horse_one_cm', 'boat_one_cm', 'aviate_one_cm', 'fall_one_cm',
      'damage_taken', 'sleep_in_bed', 'fish_caught', 'animals_bred',
      'traded_with_villager', 'talked_to_villager', 'enchant_item',
      'interact_with_crafting_table', 'interact_with_furnace',
      'interact_with_anvil', 'open_chest', 'bell_ring', 'drop_count',
      'eat_cake_slice', 'sneak_time', 'leave_game']

    const playerStatsPromises = statTypes.map(async t => {
      const r = await fetch(`/api/player_stats?type=${encodeURIComponent(t)}&server_name=${sn}`)
      return { t, data: await r.json() }
    })

    const promises = [
      fetch(`/api/map_sizes?server_name=${sn}`).then(r => r.json()),
      Promise.all(playerStatsPromises),
      fetch(`/api/stats/battle?category=killed&server_name=${sn}`).then(r => r.json()),
      fetch(`/api/stats/battle?category=killed_by&server_name=${sn}`).then(r => r.json()),
      fetch(`/api/stats/craft?category=crafted&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/craft?category=used&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/item?category=picked_up&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/item?category=dropped&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/item?category=used&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/block?category=mined&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/stats/block?category=broken&server_name=${sn}`).then(r => r.json()).catch(() => ({})),
    ]

    const [ms, psArr, bk, bkBy, cc, cu, ip, id, iu, bm, bb] = await Promise.all(promises)

    mapSizes.value = ms || {}
    const ps: Record<string, any> = {}
    psArr.forEach((item: any) => { ps[item.t] = item.data || {} })
    playerStats.value = ps
    battleStats.value = { killed: bk || {}, killed_by: bkBy || {} }
    craftStats.value = { crafted: cc || {}, used: cu || {} }
    itemStats.value = { picked_up: ip || {}, dropped: id || {}, used: iu || {} }
    blockStats.value = { mined: bm || {}, broken: bb || {} }
  }

  let staticDataCache: any = null

  async function loadStaticData() {
    const r = await fetch('data.json')
    const data = await r.json()
    staticDataCache = data

    applyStaticData(data)
  }

  function applyStaticData(data: any) {
    // New format: { servers: { [name]: { map_sizes, player_stats, detail_stats } } }
    if (data.servers) {
      const appStore = useAppStore()
      const serverNames = Object.keys(data.servers)
      appStore.setServers(serverNames)
      appStore.serversLoaded = true

      // Pick current server: saved preference, or first available
      let target = appStore.currentServer
      if (!target || !serverNames.includes(target)) {
        target = serverNames[0] || ''
        appStore.setCurrentServer(target)
      }

      const sd = data.servers[target] || {}
      mapSizes.value = sd.map_sizes || {}
      playerStats.value = sd.player_stats || {}
      if (sd.detail_stats) {
        const ds = sd.detail_stats
        if (ds.battle) battleStats.value = ds.battle as any
        if (ds.craft) craftStats.value = ds.craft as any
        if (ds.item) itemStats.value = ds.item as any
        if (ds.block) blockStats.value = ds.block as any
      }
      return
    }

    // Legacy format: flat structure (no server grouping)
    mapSizes.value = data.map_sizes || {}
    playerStats.value = data.player_stats || {}
    if (data.battle_stats) battleStats.value = data.battle_stats
    if (data.craft_stats) craftStats.value = data.craft_stats
    if (data.item_stats) itemStats.value = data.item_stats
    if (data.block_stats) blockStats.value = data.block_stats
    if (data.detail_stats) {
      const ds = data.detail_stats
      if (ds.battle) battleStats.value = ds.battle as any
      if (ds.craft) craftStats.value = ds.craft as any
      if (ds.item) itemStats.value = ds.item as any
      if (ds.block) blockStats.value = ds.block as any
    }
  }

  function switchStaticServer() {
    if (staticDataCache) {
      applyStaticData(staticDataCache)
      extractMetadata()
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
    Object.values(blockStats.value).forEach((catData: any) => collectPlayersFromDetail(catData))
    allDates.value = Array.from(dateSet).sort()
  }

  async function loadAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    startMessageRotation()
    try {
      const appStore = useAppStore()
      if (appStore.isStatic) {
        loadingMessage.value = '少女翻阅古籍中...'
        await loadStaticData()
      } else {
        if (!appStore.serversLoaded) {
          await appStore.loadServers()
        }
        if (!appStore.currentServer) {
          loaded.value = true
          return
        }
        try {
          await loadFromAPI()
        } catch {
          appStore.setMode('static')
          loadingMessage.value = '少女翻阅古籍中...'
          await loadStaticData()
        }
      }
      extractMetadata()
      loaded.value = true
    } finally {
      stopMessageRotation()
      loading.value = false
    }
  }

  async function reload() {
    loaded.value = false
    await loadAll(true)
  }

  return {
    mapSizes, playerStats, battleStats, craftStats, itemStats, blockStats,
    allDates, allPlayers, loading, loaded, loadingMessage,
    loadAll, reload, switchStaticServer,
  }
})