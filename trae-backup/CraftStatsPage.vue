<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import { usePlayerFilter } from '@/services/usePlayerFilter'
import { useI18n } from 'vue-i18n'
import { getItemName } from '@/i18n/items'
import ChartContainer from '@/components/ChartContainer.vue'
import type { ChartSeries } from '@/components/ChartContainer.vue'
import { Hammer, Trophy } from 'lucide-vue-next'
import PlayerFilter from '@/components/PlayerFilter.vue'

const { t, locale } = useI18n()
const data = useDataStore()
const filter = usePlayerFilter(data.allPlayers)
const category = ref<'crafted' | 'used'>('crafted')

onMounted(async () => { await data.loadAll(); filter.init() })

const activePlayers = computed<string[]>(() =>
  filter.selected.value.size === 0 ? Array.from(data.allPlayers).sort() : Array.from(filter.selected.value).sort()
)

const statData = computed(() => (data.craftStats as any)[category.value] || {})
const dates = computed(() => data.allDates)

function getColors(n: number) {
  const c: string[] = []
  for (let i = 0; i < n; i++) c.push(`hsl(${(i * 137.508) % 360}, 70%, 45%)`)
  return c
}

const chartLabels = computed(() => dates.value)

const chartSeries = computed<ChartSeries[]>(() => {
  const sd = statData.value; const ds = dates.value; const players = activePlayers.value
  const colors = getColors(players.length + 1)
  return [
    ...players.map((p, i) => ({
      name: p,
      data: ds.map(date => {
        const pd = sd[date]?.[p] || {}
        return Object.values(pd as Record<string, number>).reduce((s, v) => s + v, 0)
      }),
      color: colors[i] || '#888',
      type: 'bar' as const,
    })),
    {
      name: t('common.total'),
      data: ds.map(date => {
        return players.reduce((sum, p) => {
          const pd = sd[date]?.[p] || {}
          return sum + Object.values(pd as Record<string, number>).reduce((s, v) => s + v, 0)
        }, 0)
      }),
      color: '#FF6B6B',
      type: 'bar' as const,
    },
  ]
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

const rankColors = ['#FFD700', '#C0C0C0', '#CD7F32']
</script>

<template>
  <div class="space-y-6">
    <div class="flex gap-2">
      <button
        class="px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200"
        :class="category === 'crafted'
          ? 'subnav-active'
          : 'subnav-inactive'"
        @click="category = 'crafted'"
      >
        {{ t('craft.crafted') }}
      </button>
      <button
        class="px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200"
        :class="category === 'used'
          ? 'subnav-active'
          : 'subnav-inactive'"
        @click="category = 'used'"
      >
        {{ t('craft.used') }}
      </button>
    </div>

    <PlayerFilter :filter="filter" />

    <div class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <Hammer class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ category === 'crafted' ? t('craft.crafted') : t('craft.used') }}</h3>
        </div>

        <ChartContainer
          :labels="chartLabels"
          :series="chartSeries"
          chart-type="bar"
          height="400px"
        />
      </div>
    </div>

    <div class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 dark:from-brand/20 to-brand/10 dark:to-brand/15 rounded-xl flex items-center justify-center">
            <Trophy class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('common.topN', { n: 10 }) }}</h3>
        </div>

        <div class="overflow-hidden rounded-xl border border-slate-100 dark:border-slate-700">
          <table class="w-full">
            <thead>
              <tr class="bg-slate-50/80 dark:bg-slate-800/80">
                <th class="px-4 py-3 text-left text-sm font-medium text-slate-600 dark:text-slate-400">#</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('common.item') }}</th>
                <th class="px-4 py-3 text-right text-sm font-medium text-slate-600 dark:text-slate-400">{{ t('common.count') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in topItems" :key="item.key" class="border-t border-slate-100 dark:border-slate-700 hover:bg-slate-50/50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-4 py-3">
                  <span
                    class="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold"
                    :class="i >= 3 ? 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400 dark:ring-1 dark:ring-slate-600' : ''"
                    :style="i < 3 ? { background: rankColors[i], color: '#000' } : undefined"
                  >
                    {{ i + 1 }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-slate-700 dark:text-slate-300">{{ item.name }}</td>
                <td class="px-4 py-3 text-sm font-medium text-slate-900 dark:text-slate-50 text-right">{{ item.count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
