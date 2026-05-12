<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import { getItemName } from '@/i18n/items'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from 'chart.js'
import PlayerFilter from '@/components/PlayerFilter.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const { t, locale } = useI18n()
const data = useDataStore()
const filter = usePlayerFilter(data.allPlayers)
const category = ref<'picked_up' | 'dropped' | 'used'>('picked_up')

onMounted(async () => { await data.loadAll(); filter.init() })

const activePlayers = computed<string[]>(() =>
  filter.selected.value.size === 0 ? Array.from(data.allPlayers).sort() : Array.from(filter.selected.value).sort()
)
const statData = computed(() => (data.itemStats as any)[category.value] || {})
const dates = computed(() => data.allDates)

function getColors(n: number) {
  const c: string[] = []
  for (let i = 0; i < n; i++) c.push(`hsl(${(i * 137.508) % 360}, 70%, 45%)`)
  return c
}

const categoryLabel: Record<string, string> = {
  picked_up: t('item.picked_up'), dropped: t('item.dropped'), used: t('item.used'),
}

const chartData = computed(() => {
  const sd = statData.value; const ds = dates.value; const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return {
    labels: ds,
    datasets: [
      ...players.map((p, i) => ({
        label: p,
        data: ds.map(date => {
          const pd = sd[date]?.[p] || {}
          return Object.values(pd as Record<string, number>).reduce((s, v) => s + v, 0)
        }),
        backgroundColor: colors[i] || '#888',
      })),
      { label: locale.value === 'zh-CN' ? '总计' : 'Total', data: ds.map(date => players.reduce((sum, p) => { const pd = sd[date]?.[p] || {}; return sum + Object.values(pd as Record<string, number>).reduce((s, v) => s + v, 0) }, 0)), backgroundColor: 'rgba(255,107,107,0.5)', borderColor: '#FF6B6B', borderWidth: 2, hidden: true },
    ],
  }
})

const topItems = computed(() => {
  const _l = locale.value
  const sd = statData.value; const ds = dates.value; const totals: Record<string, number> = {}
  activePlayers.value.forEach(p => {
    ds.forEach(date => {
      const pd = sd[date]?.[p] || {}
      Object.entries(pd as Record<string, number>).forEach(([item, count]) => {
        totals[item] = (totals[item] || 0) + count
      })
    })
  })
  return Object.entries(totals).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([key, count]) => ({ key, name: getItemName(key, _l), count }))
})
</script>

<template>
  <div>
    <div class="stat-tabs">
      <button :class="{ active: category === 'picked_up' }" @click="category = 'picked_up'">{{ t('item.picked_up') }}</button>
      <button :class="{ active: category === 'dropped' }" @click="category = 'dropped'">{{ t('item.dropped') }}</button>
      <button :class="{ active: category === 'used' }" @click="category = 'used'">{{ t('item.used') }}</button>
    </div>
    <PlayerFilter :filter="filter" />
    <div class="surface-card" style="padding:20px;border-radius:16px;margin-bottom:16px">
      <h3 style="margin-bottom:12px;font-weight:500">{{ categoryLabel[category] }}</h3>
      <Bar :data="chartData" :options="{ responsive:true, plugins:{legend:{position:'bottom' as const,labels:{usePointStyle:true,pointStyle:'circle',padding:20,font:{size:12}}}} }" style="max-height:400px" />
    </div>
    <div class="surface-card" style="padding:20px;border-radius:16px">
      <h3 style="margin-bottom:12px;font-weight:500">{{ t('common.topN', { n: 10 }) }}</h3>
      <table style="width:100%;border-collapse:collapse">
        <thead><tr style="text-align:left;border-bottom:1px solid var(--md-sys-color-outline-variant)">
          <th style="padding:8px">#</th><th style="padding:8px">{{ locale === 'zh-CN' ? '物品' : 'Item' }}</th><th style="padding:8px;text-align:right">{{ locale === 'zh-CN' ? '数量' : 'Count' }}</th>
        </tr></thead>
        <tbody>
          <tr v-for="(item, i) in topItems" :key="item.key" style="border-bottom:1px solid var(--md-sys-color-outline-variant)">
            <td style="padding:8px"><span :style="{display:'inline-block',width:'28px',height:'28px',lineHeight:'28px',textAlign:'center',borderRadius:'50%',background:i===0?'#FFD700':i===1?'#C0C0C0':i===2?'#CD7F32':'var(--md-sys-color-surface-container-highest)',color:i<3?'#000':'inherit',fontWeight:'bold',fontSize:12}">{{ i + 1 }}</span></td>
            <td style="padding:8px">{{ item.name }}</td>
            <td style="padding:8px;text-align:right;fontWeight:500">{{ item.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.stat-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.stat-tabs button { padding: 8px 20px; border-radius: 20px; border: 1px solid var(--md-sys-color-outline); background: none; color: var(--md-sys-color-on-surface); font-size: 13px; cursor: pointer; }
.stat-tabs button.active { background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); border-color: var(--md-sys-color-primary); }
.surface-card { background: var(--md-sys-color-surface-container-low); }
</style>
