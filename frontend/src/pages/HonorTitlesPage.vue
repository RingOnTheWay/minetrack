<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { useI18n } from 'vue-i18n'
import {
  Trophy, Skull, Swords, Clock, Pickaxe, Hammer, Fish,
  BedDouble, Shield, Zap, Heart, Footprints, Anchor,
  Gem, Flame, Crown, Star, Target, Compass
} from 'lucide-vue-next'

const { t } = useI18n()
const data = useDataStore()

onMounted(() => {
  data.loadAll()
})

interface HonorTitle {
  key: string
  icon: any
}

const cumulativeTitles: HonorTitle[] = [
  { key: 'mineGod', icon: Pickaxe },
  { key: 'deathMaster', icon: Skull },
  { key: 'slayerKing', icon: Swords },
  { key: 'ironMan', icon: Clock },
  { key: 'craftMaster', icon: Hammer },
  { key: 'fisherman', icon: Fish },
  { key: 'sleepyhead', icon: BedDouble },
  { key: 'survivor', icon: Shield },
  { key: 'enchanter', icon: Zap },
  { key: 'marathoner', icon: Footprints },
]

const latestTitles: HonorTitle[] = [
  { key: 'creeperBait', icon: Flame },
  { key: 'diamondHunter', icon: Gem },
  { key: 'pvpKing', icon: Crown },
  { key: 'bedBreaker', icon: Target },
  { key: 'villagerFriend', icon: Star },
  { key: 'acrobat', icon: Compass },
  { key: 'deepDiver', icon: Anchor },
  { key: 'tank', icon: Heart },
  { key: 'treasureHunter', icon: Trophy },
  { key: 'speedster', icon: Zap },
]

function getPlayerStatCumulative(statType: string): Record<string, number> {
  const statData = data.playerStats[statType]
  if (!statData) return {}
  const dates = data.allDates
  if (dates.length === 0) return {}
  return statData[dates[dates.length - 1]] || {}
}

function getPlayerStatDelta(statType: string): Record<string, number> {
  const statData = data.playerStats[statType]
  if (!statData) return {}
  const dates = data.allDates
  if (dates.length === 0) return {}
  const latestDate = dates[dates.length - 1]
  const latest = statData[latestDate] || {}
  if (dates.length === 1) return latest
  const prevDate = dates[dates.length - 2]
  const prev = statData[prevDate] || {}
  const delta: Record<string, number> = {}
  for (const player of Object.keys(latest)) {
    const d = (latest[player] || 0) - (prev[player] || 0)
    if (d > 0) delta[player] = d
  }
  return delta
}

function getTopPlayer(stats: Record<string, number>): { name: string; value: number } | null {
  const entries = Object.entries(stats)
  if (entries.length === 0) return null
  entries.sort((a, b) => b[1] - a[1])
  return { name: entries[0][0], value: entries[0][1] }
}

function getDetailStatCumulative(domain: string, category: string, keyPrefix?: string): Record<string, number> {
  const statsMap: Record<string, any> = {
    battle: data.battleStats,
    craft: data.craftStats,
    item: data.itemStats,
    block: data.blockStats,
  }
  const domainData = statsMap[domain]
  if (!domainData) return {}
  const catData = domainData[category]
  if (!catData) return {}
  const dates = data.allDates
  if (dates.length === 0) return {}
  const dateData = catData[dates[dates.length - 1]]
  if (!dateData) return {}
  const totals: Record<string, number> = {}
  for (const [player, keys] of Object.entries(dateData || {})) {
    for (const [key, value] of Object.entries(keys || {})) {
      if (!keyPrefix || key.startsWith(keyPrefix)) {
        totals[player] = (totals[player] || 0) + (value || 0)
      }
    }
  }
  return totals
}

function getDetailStatDelta(domain: string, category: string, keyPrefix?: string): Record<string, number> {
  const statsMap: Record<string, any> = {
    battle: data.battleStats,
    craft: data.craftStats,
    item: data.itemStats,
    block: data.blockStats,
  }
  const domainData = statsMap[domain]
  if (!domainData) return {}
  const catData = domainData[category]
  if (!catData) return {}
  const dates = data.allDates
  if (dates.length === 0) return {}
  const latestDate = dates[dates.length - 1]
  const latestData = catData[latestDate]
  if (!latestData) return {}
  if (dates.length === 1) {
    const totals: Record<string, number> = {}
    for (const [player, keys] of Object.entries(latestData || {})) {
      for (const [key, value] of Object.entries(keys || {})) {
        if (!keyPrefix || key.startsWith(keyPrefix)) {
          totals[player] = (totals[player] || 0) + (value || 0)
        }
      }
    }
    return totals
  }
  const prevDate = dates[dates.length - 2]
  const prevData = catData[prevDate] || {}
  const delta: Record<string, number> = {}
  for (const [player, keys] of Object.entries(latestData || {})) {
    for (const [key, value] of Object.entries(keys || {})) {
      if (!keyPrefix || key.startsWith(keyPrefix)) {
        const prevVal = (prevData[player] || {})[key] || 0
        const d = value - prevVal
        if (d > 0) {
          delta[player] = (delta[player] || 0) + d
        }
      }
    }
  }
  return delta
}

function computeCumulativeResult(key: string): { name: string; value: number; formattedValue: string } | null {
  let result: { name: string; value: number } | null = null

  switch (key) {
    case 'mineGod': {
      const mined = getDetailStatCumulative('block', 'mined')
      result = getTopPlayer(mined)
      break
    }
    case 'deathMaster': {
      const deaths = getPlayerStatCumulative('deaths')
      result = getTopPlayer(deaths)
      break
    }
    case 'slayerKing': {
      const kills = getPlayerStatCumulative('mob_kills')
      result = getTopPlayer(kills)
      break
    }
    case 'ironMan': {
      const playTime = getPlayerStatCumulative('play_time')
      result = getTopPlayer(playTime)
      break
    }
    case 'craftMaster': {
      const crafted = getDetailStatCumulative('craft', 'crafted')
      result = getTopPlayer(crafted)
      break
    }
    case 'fisherman': {
      const fish = getPlayerStatCumulative('fish_caught')
      result = getTopPlayer(fish)
      break
    }
    case 'sleepyhead': {
      const sleep = getPlayerStatCumulative('sleep_in_bed')
      result = getTopPlayer(sleep)
      break
    }
    case 'survivor': {
      const deaths = getPlayerStatCumulative('deaths')
      const playTime = getPlayerStatCumulative('play_time')
      const ratios: Record<string, number> = {}
      for (const player of Object.keys(playTime)) {
        const d = deaths[player] || 0
        const pt = playTime[player] || 0
        if (pt > 0) {
          ratios[player] = pt / (d + 1)
        }
      }
      result = getTopPlayer(ratios)
      break
    }
    case 'enchanter': {
      const enchant = getPlayerStatCumulative('enchant_item')
      result = getTopPlayer(enchant)
      break
    }
    case 'marathoner': {
      const walkCm = getPlayerStatCumulative('walk_one_cm')
      const sprintCm = getPlayerStatCumulative('sprint_one_cm')
      const total: Record<string, number> = {}
      for (const player of Object.keys(walkCm)) {
        total[player] = (walkCm[player] || 0) + (sprintCm[player] || 0)
      }
      result = getTopPlayer(total)
      break
    }
  }

  if (!result) return null
  return { ...result, formattedValue: formatValue(key, result.value) }
}

function computeLatestResult(key: string): { name: string; value: number; formattedValue: string } | null {
  let result: { name: string; value: number } | null = null

  switch (key) {
    case 'creeperBait': {
      const killedByCreeper = getDetailStatDelta('battle', 'killed_by', 'creeper')
      result = getTopPlayer(killedByCreeper)
      break
    }
    case 'diamondHunter': {
      const diamondMined = getDetailStatDelta('block', 'mined', 'diamond_ore')
      const diamondDeepslate = getDetailStatDelta('block', 'mined', 'deepslate_diamond_ore')
      const diamondPicked = getDetailStatDelta('item', 'picked_up', 'diamond')
      const total: Record<string, number> = {}
      for (const player of Object.keys(diamondMined)) {
        total[player] = (total[player] || 0) + (diamondMined[player] || 0)
      }
      for (const player of Object.keys(diamondDeepslate)) {
        total[player] = (total[player] || 0) + (diamondDeepslate[player] || 0)
      }
      for (const player of Object.keys(diamondPicked)) {
        total[player] = (total[player] || 0) + (diamondPicked[player] || 0)
      }
      result = getTopPlayer(total)
      break
    }
    case 'pvpKing': {
      const pvp = getPlayerStatDelta('player_kills')
      result = getTopPlayer(pvp)
      break
    }
    case 'bedBreaker': {
      const bedsUsed = getPlayerStatDelta('sleep_in_bed')
      result = getTopPlayer(bedsUsed)
      break
    }
    case 'villagerFriend': {
      const traded = getPlayerStatDelta('traded_with_villager')
      const talked = getPlayerStatDelta('talked_to_villager')
      const total: Record<string, number> = {}
      for (const player of Object.keys(traded)) {
        total[player] = (total[player] || 0) + (traded[player] || 0)
      }
      for (const player of Object.keys(talked)) {
        total[player] = (total[player] || 0) + (talked[player] || 0)
      }
      result = getTopPlayer(total)
      break
    }
    case 'acrobat': {
      const jumps = getPlayerStatDelta('jumps')
      result = getTopPlayer(jumps)
      break
    }
    case 'deepDiver': {
      const swimCm = getPlayerStatDelta('swim_one_cm')
      result = getTopPlayer(swimCm)
      break
    }
    case 'tank': {
      const dmgTaken = getPlayerStatDelta('damage_taken')
      result = getTopPlayer(dmgTaken)
      break
    }
    case 'treasureHunter': {
      const picked = getDetailStatDelta('item', 'picked_up')
      result = getTopPlayer(picked)
      break
    }
    case 'speedster': {
      const sprintCm = getPlayerStatDelta('sprint_one_cm')
      result = getTopPlayer(sprintCm)
      break
    }
  }

  if (!result) return null
  return { ...result, formattedValue: formatValue(key, result.value) }
}

function formatValue(key: string, value: number): string {
  if (value === 0) return '0'
  switch (key) {
    case 'ironMan': {
      const hours = value / 3600
      return hours >= 1 ? `${hours.toFixed(1)}h` : `${(value / 60).toFixed(0)}m`
    }
    case 'marathoner':
    case 'speedster': {
      const km = value / 100000
      return `${km.toFixed(1)}km`
    }
    case 'deepDiver': {
      const km = value / 100000
      return km >= 1 ? `${km.toFixed(1)}km` : `${(value / 100).toFixed(0)}m`
    }
    case 'survivor':
      return `${value.toFixed(1)}`
    default:
      return value.toLocaleString()
  }
}

const cumulativeHonors = computed(() =>
  cumulativeTitles.map(title => ({
    ...title,
    result: computeCumulativeResult(title.key),
  }))
)

const latestHonors = computed(() =>
  latestTitles.map(title => ({
    ...title,
    result: computeLatestResult(title.key),
  }))
)

const goldStyle = {
  border: 'border-amber-400/60 dark:border-amber-500/50',
  bg: 'bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 dark:from-amber-950/30 dark:via-yellow-950/20 dark:to-orange-950/30',
  iconBg: 'bg-gradient-to-br from-amber-400 to-yellow-500',
}

function getPlayerColor(index: number): string {
  return `hsl(${(index * 137.508) % 360}, 70%, 50%)`
}
</script>

<template>
  <div class="space-y-6">
    <div
      v-motion-slide-bottom :delay="100"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-amber-500/5 to-transparent rounded-full blur-3xl opacity-50" />

      <div class="relative">
        <div class="flex items-center gap-3 mb-6">
          <Crown class="w-5 h-5 text-amber-500" />
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('honor.cumulative') }}</h3>
          <span class="text-xs text-slate-400 dark:text-slate-500 px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-full">{{ t('honor.cumulativeDesc') }} · {{ data.allDates.length }} {{ t('honor.days') }}</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="(honor, index) in cumulativeHonors"
            :key="honor.key"
            v-motion-slide-bottom :delay="150 + index * 50"
            class="relative group"
          >
            <div
              :class="[goldStyle.border, goldStyle.bg]"
              class="relative rounded-xl p-4 border shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden h-full"
            >
              <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-white/40 to-transparent dark:from-white/5 dark:to-transparent rounded-full blur-xl" />

              <div class="relative flex flex-col h-full">
                <div class="flex items-center justify-between mb-3">
                  <div :class="goldStyle.iconBg" class="w-10 h-10 rounded-lg flex items-center justify-center shadow-md">
                    <component :is="honor.icon" class="w-5 h-5 text-white" />
                  </div>
                  <span class="text-lg">👑</span>
                </div>

                <h4 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-1">{{ t(`honor.titles.${honor.key}`) }}</h4>
                <p class="text-xs text-slate-400 dark:text-slate-500 mb-3 line-clamp-2 flex-1">{{ t(`honor.descs.${honor.key}`) }}</p>

                <div v-if="honor.result" class="flex items-center gap-2 pt-2 border-t border-slate-200/50 dark:border-slate-700/50">
                  <div
                    class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                    :style="{ backgroundColor: getPlayerColor(index) }"
                  >
                    {{ honor.result.name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="min-w-0">
                    <div class="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{{ honor.result.name }}</div>
                    <div class="text-xs text-brand dark:text-brand-light font-medium">{{ honor.result.formattedValue }}</div>
                  </div>
                </div>
                <div v-else class="text-xs text-slate-400 dark:text-slate-500 italic pt-2 border-t border-slate-200/50 dark:border-slate-700/50">
                  {{ t('common.noData') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="200"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-sky-500/5 to-transparent rounded-full blur-3xl opacity-50" />

      <div class="relative">
        <div class="flex items-center gap-3 mb-6">
          <Star class="w-5 h-5 text-sky-500" />
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('honor.latest') }}</h3>
          <span class="text-xs text-slate-400 dark:text-slate-500 px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-full">{{ data.allDates.length ? data.allDates[data.allDates.length - 1] : t('honor.latestDesc') }}</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="(honor, index) in latestHonors"
            :key="honor.key"
            v-motion-slide-bottom :delay="250 + index * 50"
            class="relative group"
          >
            <div
              :class="[goldStyle.border, goldStyle.bg]"
              class="relative rounded-xl p-4 border shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden h-full"
            >
              <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-white/40 to-transparent dark:from-white/5 dark:to-transparent rounded-full blur-xl" />

              <div class="relative flex flex-col h-full">
                <div class="flex items-center justify-between mb-3">
                  <div :class="goldStyle.iconBg" class="w-10 h-10 rounded-lg flex items-center justify-center shadow-md">
                    <component :is="honor.icon" class="w-5 h-5 text-white" />
                  </div>
                  <span class="text-lg">👑</span>
                </div>

                <h4 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-1">{{ t(`honor.titles.${honor.key}`) }}</h4>
                <p class="text-xs text-slate-400 dark:text-slate-500 mb-3 line-clamp-2 flex-1">{{ t(`honor.descs.${honor.key}`) }}</p>

                <div v-if="honor.result" class="flex items-center gap-2 pt-2 border-t border-slate-200/50 dark:border-slate-700/50">
                  <div
                    class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                    :style="{ backgroundColor: getPlayerColor(index) }"
                  >
                    {{ honor.result.name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="min-w-0">
                    <div class="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{{ honor.result.name }}</div>
                    <div class="text-xs text-brand dark:text-brand-light font-medium">{{ honor.result.formattedValue }}</div>
                  </div>
                </div>
                <div v-else class="text-xs text-slate-400 dark:text-slate-500 italic pt-2 border-t border-slate-200/50 dark:border-slate-700/50">
                  {{ t('common.noData') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
