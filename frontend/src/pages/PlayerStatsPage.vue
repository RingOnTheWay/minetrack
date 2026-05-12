<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend
} from 'chart.js'
import PlayerFilter from '@/components/PlayerFilter.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

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

const chartData = computed(() => {
  const statData = (data.playerStats as any)[currentKey.value] || {}
  const dates = data.allDates
  const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return {
    labels: dates,
    datasets: [
      ...players.map((p, i) => ({
        label: p,
        data: dates.map(date => transformValue(currentKey.value, statData[date]?.[p] || 0)),
        borderColor: colors[i], backgroundColor: colors[i] + '30', tension: 0.4,
      })),
      {
        label: locale.value === 'zh-CN' ? '总计' : 'Total',
        data: dates.map(date => transformValue(currentKey.value, players.reduce((sum, p) => sum + (statData[date]?.[p] || 0), 0))),
        borderColor: '#FF6B6B', backgroundColor: 'rgba(255,107,107,0.1)',
        borderWidth: 3, tension: 0.4, pointRadius: 4, pointHoverRadius: 6, hidden: true,
      },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true, maintainAspectRatio: true,
  interaction: { mode: 'index' as const, intersect: false },
  plugins: { legend: { position: 'bottom' as const, labels: { usePointStyle: true, pointStyle: 'circle', padding: 20, font: { size: 12 } } } },
  scales: { y: { beginAtZero: true, title: { display: true, text: currentLabel.value } } },
}))
</script>

<template>
  <div>
    <div class="stat-tabs">
      <button v-for="key in STAT_KEYS" :key="key" :class="{ active: currentKey === key }"
              @click="currentKey = key">{{ t(STAT_I18N[key]) }}</button>
    </div>
    <PlayerFilter :filter="filter" />
    <div class="surface-card" style="padding:20px;border-radius:16px">
      <Line :data="chartData" :options="chartOptions" style="max-height:400px" />
    </div>
  </div>
</template>

<style scoped>
.stat-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.stat-tabs button { padding: 8px 16px; border-radius: 20px; border: 1px solid var(--md-sys-color-outline); background: none; color: var(--md-sys-color-on-surface); font-size: 13px; cursor: pointer; transition: all 0.2s; }
.stat-tabs button.active { background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); border-color: var(--md-sys-color-primary); }
.surface-card { background: var(--md-sys-color-surface-container-low); }
</style>
