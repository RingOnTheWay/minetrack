<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { useI18n } from 'vue-i18n'
import ChartContainer from '@/components/ChartContainer.vue'
import type { ChartSeries } from '@/components/ChartContainer.vue'
import { Map, TrendingUp, Activity } from 'lucide-vue-next'
import DateRangeFilter from '@/components/DateRangeFilter.vue'
import { useDateRange } from '@/services/useDateRange'

const { t } = useI18n()
const data = useDataStore()
const dateRange = useDateRange(() => data.allDates)

onMounted(() => { data.loadAll() })

const mapKeys = ['world', 'world_nether', 'world_the_end'] as const
const mapLabels = computed<Record<string, string>>(() => ({
  world: t('map.world'), world_nether: t('map.nether'), world_the_end: t('map.end'),
}))
const mapColors = ['#60d5f2', '#f26060', '#d4af37']

const chartLabels = computed(() => dateRange.filteredDates.value)

const chartSeries = computed<ChartSeries[]>(() =>
  mapKeys.map((key, i) => ({
    name: mapLabels.value[key],
    data: dateRange.filteredDates.value.map(d => data.mapSizes[d]?.[key] || 0),
    color: mapColors[i],
    type: 'line' as const,
    fill: true,
    strokeWidth: 3,
  }))
)

const latestMapData = computed(() => {
  const dates = data.allDates
  if (dates.length === 0) return { world: 0, world_nether: 0, world_the_end: 0 }
  const last = dates[dates.length - 1]
  return {
    world: data.mapSizes[last]?.world || 0,
    world_nether: data.mapSizes[last]?.world_nether || 0,
    world_the_end: data.mapSizes[last]?.world_the_end || 0,
  }
})

const mapGrowth = computed(() => {
  const dates = data.allDates
  if (dates.length < 2) return '0'
  const last = dates[dates.length - 1]
  const prev = dates[dates.length - 2]
  const lastVal = data.mapSizes[last]?.world || 0
  const prevVal = data.mapSizes[prev]?.world || 0
  if (prevVal === 0) return '0'
  return ((lastVal - prevVal) / prevVal * 100).toFixed(1)
})
</script>

<template>
  <div class="space-y-6">
    <DateRangeFilter
      :start-date="dateRange.startDate.value"
      :end-date="dateRange.endDate.value"
      :has-filter="dateRange.hasFilter.value"
      :available-dates="data.allDates"
      @update:start="dateRange.startDate.value = $event"
      @update:end="dateRange.endDate.value = $event"
      @clear="dateRange.clearDateRange()"
    />

    <div class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
              <Activity class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('map.title') }}</h3>
              <div class="flex items-center gap-2 mt-1">
                <TrendingUp class="w-4 h-4 text-emerald-500" />
                <span class="text-sm text-emerald-600 dark:text-emerald-400 font-medium">+{{ mapGrowth }}% {{ t('common.growth') || '增长' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4 mb-6">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
            <div class="w-2.5 h-2.5 bg-[#60d5f2] rounded-full animate-pulse" />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('map.world') }}: {{ latestMapData.world }}</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-red-50 dark:bg-red-900/30 rounded-lg">
            <div class="w-2.5 h-2.5 bg-[#f26060] rounded-full animate-pulse" />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('map.nether') }}: {{ latestMapData.world_nether }}</span>
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-amber-50 dark:bg-amber-900/30 rounded-lg">
            <div class="w-2.5 h-2.5 bg-[#d4af37] rounded-full animate-pulse" />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('map.end') }}: {{ latestMapData.world_the_end }}</span>
          </div>
        </div>

        <ChartContainer
          :labels="chartLabels"
          :series="chartSeries"
          :y-axis-label="t('map.unit')"
          chart-type="line"
          height="400px"
        />
      </div>
    </div>
  </div>
</template>
