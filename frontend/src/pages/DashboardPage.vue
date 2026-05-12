<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const { t, locale } = useI18n()
const data = useDataStore()
const router = useRouter()

onMounted(() => { data.loadAll() })

const totalDays = computed(() => data.allDates.length)
const playerCount = computed(() => data.allPlayers.size)
const dateRange = computed(() => {
  const d = data.allDates
  if (d.length === 0) return '-'
  return d.length === 1 ? d[0] : `${d[0]} ~ ${d[d.length - 1]}`
})

const mapKeys = ['world', 'world_nether', 'world_the_end'] as const
const mapLabels = computed<Record<string, string>>(() => ({
  world: t('map.world'), world_nether: t('map.nether'), world_the_end: t('map.end'),
}))
const mapColors = ['#00D9FF', '#FF8A65', '#B388FF']

const mapChartData = computed(() => {
  const dates = data.allDates
  if (dates.length === 0) return null
  return {
    labels: dates,
    datasets: mapKeys.map((key, i) => ({
      label: mapLabels.value[key],
      data: dates.map(d => data.mapSizes[d]?.[key] || 0),
      borderColor: mapColors[i],
      backgroundColor: mapColors[i] + '20',
      tension: 0.4, fill: true, pointRadius: 2, pointHoverRadius: 4,
    })),
  }
})

const mapChartOptions = computed(() => ({
  responsive: true, maintainAspectRatio: true,
  plugins: { legend: { position: 'bottom' as const, labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11 } } } },
  scales: { y: { beginAtZero: true, title: { display: true, text: t('map.unit') } } },
}))

const quickLinks = computed(() => [
  { path: '/map', icon: 'map', label: t('nav.mapStats') },
  { path: '/players', icon: 'people', label: t('nav.playerStats') },
  { path: '/battle', icon: 'swords', label: t('nav.battleStats') },
  { path: '/craft', icon: 'build', label: t('nav.craftStats') },
  { path: '/items', icon: 'inventory_2', label: t('nav.itemStats') },
])

function goPage(path: string) { router.push(path) }
</script>

<template>
  <div class="dashboard">
    <div class="stats-row">
      <div class="stat-card surface-card"><span class="stat-value">{{ totalDays }}</span><span class="stat-label">{{ t('dashboard.totalDays') }}</span></div>
      <div class="stat-card surface-card"><span class="stat-value">{{ playerCount }}</span><span class="stat-label">{{ t('dashboard.playerCount') }}</span></div>
      <div class="stat-card surface-card"><span class="stat-value">{{ dateRange }}</span><span class="stat-label">{{ t('dashboard.dateRange') }}</span></div>
    </div>
    <div class="quick-links">
      <button v-for="item in quickLinks" :key="item.path" class="quick-card surface-card" @click="goPage(item.path)">
        <span class="material-symbols-outlined">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>
    <div v-if="mapChartData" class="surface-card" style="padding:20px;margin-top:16px;border-radius:16px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
        <h3 style="font-weight:500;margin:0">{{ t('dashboard.mapTrend') }}</h3>
        <button class="detail-btn" @click="goPage('/map')">{{ t('common.viewDetail') }}</button>
      </div>
      <Line :data="mapChartData" :options="mapChartOptions" style="max-height:320px" />
    </div>
  </div>
</template>

<style scoped>
.dashboard { width: 100%; }
.stats-row { display: flex; gap: 16px; }
.stat-card { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 24px 16px; border-radius: 16px; }
.stat-value { font-size: 32px; font-weight: 700; color: var(--md-sys-color-primary); }
.stat-label { font-size: 13px; color: var(--md-sys-color-on-surface-variant); margin-top: 4px; }
.quick-links { display: flex; gap: 12px; margin-top: 20px; }
.quick-card { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px 16px; border-radius: 16px; cursor: pointer; transition: background 0.2s; }
.quick-card:hover { background: var(--md-sys-color-surface-container-highest); }
.quick-card .material-symbols-outlined { font-size: 28px; color: var(--md-sys-color-primary); }
.surface-card { background: var(--md-sys-color-surface-container-low); }
.detail-btn { background: none; border: none; color: var(--md-sys-color-primary); font-size: 13px; cursor: pointer; padding: 4px 8px; border-radius: 8px; transition: background 0.2s; }
.detail-btn:hover { background: var(--md-sys-color-surface-container-highest); }
</style>
