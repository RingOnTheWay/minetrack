<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const data = useDataStore()

onMounted(() => { data.loadAll() })

const mapKeys = ['world', 'world_nether', 'world_the_end'] as const
const mapLabels: Record<string, string> = { world: '主世界', world_nether: '下界', world_the_end: '末地' }
const mapColors = ['#00D9FF', '#FF8A65', '#B388FF']

const chartData = computed(() => {
  const dates = data.allDates
  return {
    labels: dates,
    datasets: mapKeys.map((key, i) => ({
      label: mapLabels[key],
      data: dates.map(d => data.mapSizes[d]?.[key] || 0),
      borderColor: mapColors[i],
      backgroundColor: mapColors[i] + '20',
      tension: 0.4, fill: true, pointRadius: 3, pointHoverRadius: 5,
    })),
  }
})

const chartOptions = {
  responsive: true, maintainAspectRatio: true,
  plugins: { legend: { position: 'bottom' as const, labels: { usePointStyle: true, pointStyle: 'circle', padding: 20, font: { size: 12 } } } },
  scales: { y: { beginAtZero: true, title: { display: true, text: '大小 (MB)' } } },
}
</script>

<template>
  <div>
    <div class="surface-card" style="padding:20px;border-radius:16px">
      <h3 style="margin-bottom:12px;font-weight:500">地图大小变化</h3>
      <Line :data="chartData" :options="chartOptions" style="max-height:400px" />
    </div>
  </div>
</template>

<style scoped>
.surface-card { background: var(--md-sys-color-surface-container-low); }
</style>
