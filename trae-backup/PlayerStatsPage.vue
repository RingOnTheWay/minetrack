<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import ChartContainer from '@/components/ChartContainer.vue'
import type { ChartSeries } from '@/components/ChartContainer.vue'
import { Users } from 'lucide-vue-next'
import PlayerFilter from '@/components/PlayerFilter.vue'

const { t, locale } = useI18n()

const STAT_KEYS = ['play_time', 'deaths', 'mob_kills', 'player_kills', 'jumps', 'distance_walked'] as const

const STAT_I18N: Record<string, string> = {
  play_time: 'playerStats.playTime', deaths: 'playerStats.deaths',
  mob_kills: 'playerStats.mobKills', player_kills: 'playerStats.playerKills',
  jumps: 'playerStats.jumps', distance_walked: 'playerStats.distanceWalked',
}

const STAT_TRANSFORM: Record<string, ((v: number) => number) | null> = {
  play_time: (v: number) => Number((v / 3600).toFixed(1)),
  distance_walked: (v: number) => Number((v / 100000).toFixed(1)),
}

const data = useDataStore()
const filter = usePlayerFilter(data.allPlayers)
const currentKey = ref<string>('play_time')

const currentLabel = computed(() => t(STAT_I18N[currentKey.value] || currentKey.value))

onMounted(async () => { await data.loadAll(); filter.init() })

const activePlayers = computed<string[]>(() =>
  filter.selected.value.size === 0 ? Array.from(data.allPlayers).sort() : Array.from(filter.selected.value).sort()
)

function getColors(n: number) {
  const colors: string[] = []
  for (let i = 0; i < n; i++) colors.push(`hsl(${(i * 137.508) % 360}, 70%, 50%)`)
  return colors
}

function transformValue(key: string, v: number): number {
  const fn = STAT_TRANSFORM[key]
  return fn ? fn(v) : v
}

const chartLabels = computed(() => data.allDates)

const chartSeries = computed<ChartSeries[]>(() => {
  const statData = (data.playerStats as any)[currentKey.value] || {}
  const dates = data.allDates
  const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return [
    ...players.map((p, i) => ({
      name: p,
      data: dates.map(date => transformValue(currentKey.value, statData[date]?.[p] || 0)),
      color: colors[i],
      type: 'line' as const,
      fill: false,
      strokeWidth: 2,
    })),
    {
      name: locale.value === 'zh-CN' ? '总计' : 'Total',
      data: dates.map(date => transformValue(currentKey.value, players.reduce((sum, p) => sum + (statData[date]?.[p] || 0), 0))),
      color: '#FF6B6B',
      type: 'line' as const,
      fill: false,
      strokeWidth: 3,
    },
  ]
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="key in STAT_KEYS"
        :key="key"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
        :class="currentKey === key
          ? 'subnav-active'
          : 'subnav-inactive'"
        @click="currentKey = key"
      >
        {{ t(STAT_I18N[key]) }}
      </button>
    </div>

    <PlayerFilter :filter="filter" />

    <div class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <Users class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ currentLabel }}</h3>
        </div>

        <ChartContainer
          :labels="chartLabels"
          :series="chartSeries"
          :y-axis-label="currentLabel"
          chart-type="line"
          height="400px"
        />
      </div>
    </div>
  </div>
</template>
