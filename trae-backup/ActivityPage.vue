<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import ChartContainer from '@/components/ChartContainer.vue'
import type { ChartSeries } from '@/components/ChartContainer.vue'
import { TrendingUp } from 'lucide-vue-next'
import PlayerFilter from '@/components/PlayerFilter.vue'

const { t, locale } = useI18n()

const ACTIVITY_KEYS = [
  'sprint_one_cm', 'walk_one_cm', 'fly_one_cm', 'climb_one_cm',
  'swim_one_cm', 'horse_one_cm', 'boat_one_cm', 'aviate_one_cm', 'fall_one_cm',
] as const

const ACTIVITY_LABELS: Record<string, string> = {
  sprint_one_cm: 'activity.sprint', walk_one_cm: 'activity.walk',
  fly_one_cm: 'activity.fly', climb_one_cm: 'activity.climb',
  swim_one_cm: 'activity.swim', horse_one_cm: 'activity.horse',
  boat_one_cm: 'activity.boat', aviate_one_cm: 'activity.aviate',
  fall_one_cm: 'activity.fall',
}

const data = useDataStore()
const filter = usePlayerFilter(data.allPlayers)
const currentKey = ref<string>('sprint_one_cm')

const currentLabel = computed(() => t(ACTIVITY_LABELS[currentKey.value] || currentKey.value))

onMounted(async () => { await data.loadAll(); filter.init() })

const activePlayers = computed<string[]>(() =>
  filter.selected.value.size === 0 ? Array.from(data.allPlayers).sort() : Array.from(filter.selected.value).sort()
)

function getColors(n: number) {
  const c: string[] = []
  for (let i = 0; i < n; i++) c.push(`hsl(${(i * 137.508) % 360}, 70%, 45%)`)
  return c
}

const chartLabels = computed(() => data.allDates)

const chartSeries = computed<ChartSeries[]>(() => {
  const statData = (data.playerStats as any)[currentKey.value] || {}
  const ds = data.allDates; const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return [
    ...players.map((p, i) => ({
      name: p,
      data: ds.map(date => Math.round(statData[date]?.[p] || 0)),
      color: colors[i] || '#888',
      type: 'bar' as const,
    })),
    { name: t('common.total'), data: ds.map(date => Math.round(players.reduce((sum, p) => sum + (statData[date]?.[p] || 0), 0))), color: '#FF6B6B', type: 'bar' as const },
  ]
})

const yAxisLabel = computed(() => t('activity.unit'))
</script>

<template>
  <div class="space-y-6">
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="key in ACTIVITY_KEYS"
        :key="key"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
        :class="currentKey === key
          ? 'subnav-active'
          : 'subnav-inactive'"
        @click="currentKey = key"
      >
        {{ t(ACTIVITY_LABELS[key]) }}
      </button>
    </div>

    <PlayerFilter :filter="filter" />

    <div class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <TrendingUp class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ currentLabel }}</h3>
        </div>

        <ChartContainer
          :labels="chartLabels"
          :series="chartSeries"
          :y-axis-label="yAxisLabel"
          chart-type="bar"
          height="400px"
        />
      </div>
    </div>
  </div>
</template>
