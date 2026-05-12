<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from 'chart.js'
import PlayerFilter from '@/components/PlayerFilter.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

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

const chartData = computed(() => {
  const statData = (data.playerStats as any)[currentKey.value] || {}
  const ds = data.allDates; const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return {
    labels: ds,
    datasets: [
      ...players.map((p, i) => ({
        label: p,
        data: ds.map(date => Math.round(statData[date]?.[p] || 0)),
        backgroundColor: colors[i] || '#888',
      })),
      { label: locale.value === 'zh-CN' ? '总计' : 'Total', data: ds.map(date => Math.round(players.reduce((sum, p) => sum + (statData[date]?.[p] || 0), 0))), backgroundColor: 'rgba(255,107,107,0.5)', borderColor: '#FF6B6B', borderWidth: 2, hidden: true },
    ],
  }
})

const yAxisLabel = computed(() => locale.value === 'zh-CN' ? '距离 (cm)' : 'Distance (cm)')
</script>

<template>
  <div>
    <div class="stat-tabs">
      <button v-for="key in ACTIVITY_KEYS" :key="key" :class="{ active: currentKey === key }"
              @click="currentKey = key">{{ t(ACTIVITY_LABELS[key]) }}</button>
    </div>
    <PlayerFilter :filter="filter" />
    <div class="surface-card" style="padding:20px;border-radius:16px">
      <h3 style="margin-bottom:12px;font-weight:500">{{ currentLabel }}</h3>
      <Bar :data="chartData" :options="{ responsive:true, plugins:{legend:{position:'bottom' as const,labels:{usePointStyle:true,pointStyle:'circle',padding:20,font:{size:12}}}}, scales:{y:{beginAtZero:true,title:{display:true,text:yAxisLabel}}} }" style="max-height:400px" />
    </div>
  </div>
</template>

<style scoped>
.stat-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.stat-tabs button { padding: 8px 16px; border-radius: 20px; border: 1px solid var(--md-sys-color-outline); background: none; color: var(--md-sys-color-on-surface); font-size: 13px; cursor: pointer; }
.stat-tabs button.active { background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); border-color: var(--md-sys-color-primary); }
.surface-card { background: var(--md-sys-color-surface-container-low); }
</style>
