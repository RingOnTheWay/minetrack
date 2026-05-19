<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import { useDataStore } from '@/stores/data'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ChartContainer from '@/components/ChartContainer.vue'
import type { ChartSeries } from '@/components/ChartContainer.vue'
import {
  Calendar, Users, TrendingUp, Map, Swords, Hammer, Package,
  ArrowRight, Activity
} from 'lucide-vue-next'

const { t } = useI18n()
const data = useDataStore()
const router = useRouter()

const totalDays = computed(() => data.allDates.length)
const playerCount = computed(() => data.allPlayers.size)
const dateRange = computed(() => {
  const d = data.allDates
  if (d.length === 0) return '-'
  return d.length === 1 ? d[0] : `${d[0]} ~ ${d[d.length - 1]}`
})

const animatedTotalDays = ref(0)
const animatedPlayerCount = ref(0)

function animateValue(target: number, setter: (v: number) => void) {
  const duration = 1500
  const steps = 60
  const increment = target / steps
  let current = 0
  const timer = setInterval(() => {
    current += increment
    if (current >= target) {
      setter(target)
      clearInterval(timer)
    } else {
      setter(Math.floor(current))
    }
  }, duration / steps)
}

watch(totalDays, (val) => { if (val > 0) animateValue(val, (v) => animatedTotalDays.value = v) }, { immediate: true })
watch(playerCount, (val) => { if (val > 0) animateValue(val, (v) => animatedPlayerCount.value = v) }, { immediate: true })

onMounted(() => {
  data.loadAll()
})

const statCards = computed(() => [
  { icon: TrendingUp, value: totalDays.value, displayValue: animatedTotalDays.value, label: t('dashboard.totalDays'), gradient: 'from-blue-500 to-cyan-500' },
  { icon: Users, value: playerCount.value, displayValue: animatedPlayerCount.value, label: t('dashboard.playerCount'), gradient: 'from-purple-500 to-pink-500' },
  { icon: Calendar, value: dateRange.value, displayValue: dateRange.value, label: t('dashboard.dateRange'), gradient: 'from-emerald-500 to-teal-500' },
])

const navItems = computed(() => [
  { icon: Map, label: t('nav.mapStats'), path: '/map', color: 'from-blue-500 to-cyan-500', hoverShadow: 'hover:shadow-blue-200 dark:hover:shadow-blue-900/40' },
  { icon: Users, label: t('nav.playerStats'), path: '/players', color: 'from-purple-500 to-pink-500', hoverShadow: 'hover:shadow-purple-200 dark:hover:shadow-purple-900/40' },
  { icon: Swords, label: t('nav.battleStats'), path: '/battle', color: 'from-red-500 to-orange-500', hoverShadow: 'hover:shadow-red-200 dark:hover:shadow-red-900/40' },
  { icon: Hammer, label: t('nav.craftStats'), path: '/craft', color: 'from-amber-500 to-yellow-500', hoverShadow: 'hover:shadow-amber-200 dark:hover:shadow-amber-900/40' },
  { icon: Package, label: t('nav.itemStats'), path: '/items', color: 'from-emerald-500 to-teal-500', hoverShadow: 'hover:shadow-emerald-200 dark:hover:shadow-emerald-900/40' },
])

function goPage(path: string) { router.push(path) }

const mapKeys = ['world', 'world_nether', 'world_the_end'] as const
const mapLabels = computed<Record<string, string>>(() => ({
  world: t('map.world'), world_nether: t('map.nether'), world_the_end: t('map.end'),
}))
const mapColors = ['#60d5f2', '#f26060', '#d4af37']

const mapChartLabels = computed(() => data.allDates)

const mapChartSeries = computed<ChartSeries[]>(() =>
  mapKeys.map((key, i) => ({
    name: mapLabels.value[key],
    data: data.allDates.map(d => data.mapSizes[d]?.[key] || 0),
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
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
      <div
        v-for="(card, index) in statCards"
        :key="index"
        v-motion-slide-bottom :delay="index * 100"
        class="group relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-xl hover:-translate-y-1 hover:scale-[1.02] transition-all duration-300 overflow-hidden"
      >
        <div :class="`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`" />

        <div :class="`absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity`">
          <component :is="card.icon" class="w-16 h-16 text-brand dark:text-brand-light" />
        </div>

        <div class="relative space-y-3">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            <component :is="card.icon" class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>

          <div class="text-3xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-brand to-brand-light">
            {{ typeof card.value === 'number' ? card.displayValue : card.value }}
          </div>

          <div class="text-sm text-slate-600 dark:text-slate-400 font-medium">{{ card.label }}</div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 md:gap-6">
      <button
        v-for="(item, index) in navItems"
        :key="item.path"
        v-motion-slide-bottom :delay="300 + index * 100"
        :class="[item.hoverShadow]"
        class="relative bg-white dark:bg-slate-800 rounded-2xl p-4 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-md hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 group overflow-hidden"
        @click="goPage(item.path)"
      >
        <div :class="`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`" />

        <div class="absolute -top-8 -right-8 w-24 h-24 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full group-hover:scale-150 transition-transform duration-500" />

        <div class="relative flex flex-col items-center gap-4">
          <div :class="`w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br ${item.color} opacity-60 rounded-xl flex items-center justify-center group-hover:opacity-100 group-hover:rotate-3 transition-all duration-300`">
            <component :is="item.icon" class="w-6 h-6 md:w-8 md:h-8 text-white" />
          </div>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-brand dark:group-hover:text-brand-light transition-colors">
            {{ item.label }}
          </span>
        </div>
      </button>
    </div>

    <div
      v-motion-slide-bottom :delay="600"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-5 md:p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group"
    >
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
              <Activity class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('dashboard.mapTrend') }}</h3>
              <div class="flex items-center gap-2 mt-1">
                <TrendingUp class="w-4 h-4 text-emerald-500" />
                <span class="text-sm text-emerald-600 dark:text-emerald-400 font-medium">+{{ mapGrowth }}% {{ t('common.growth') || '增长' }}</span>
              </div>
            </div>
          </div>

          <button class="flex items-center gap-2 px-4 py-2 bg-brand/10 dark:bg-brand/20 hover:bg-brand/20 text-brand dark:text-brand-light rounded-lg transition-all group/btn" @click="goPage('/map')">
            <span class="text-sm font-medium">{{ t('common.viewDetail') }}</span>
            <ArrowRight class="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-2 md:gap-4 mb-6">
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

        <div class="relative">
          <ChartContainer
            :labels="mapChartLabels"
            :series="mapChartSeries"
            :y-axis-label="t('map.unit')"
            chart-type="line"
            height="350px"
          />
        </div>
      </div>
    </div>
  </div>
</template>
