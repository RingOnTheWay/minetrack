<script setup lang="ts">
import { computed, provide, ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, LegendScrollComponent,
  DataZoomComponent
} from 'echarts/components'
import { useAppStore } from '@/stores/app'
import { useI18n } from 'vue-i18n'
import { BarChart3 } from 'lucide-vue-next'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, LegendScrollComponent, DataZoomComponent])

export interface ChartSeries {
  name: string
  data: number[]
  color: string
  type?: 'line' | 'bar'
  fill?: boolean
  strokeWidth?: number
}

const props = withDefaults(defineProps<{
  labels: string[]
  series: ChartSeries[]
  yAxisLabel?: string
  chartType?: 'line' | 'bar'
  height?: string
  maxLegendItems?: number
}>(), {
  chartType: 'line',
  height: '350px',
  maxLegendItems: 0,
})

const app = useAppStore()
const { t } = useI18n()

function hexToRgba(hex: string, alpha: number) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

const isEmpty = computed(() => {
  if (props.series.length === 0) return true
  return props.series.every(s => !s.data || s.data.length === 0)
})

const chartHeight = computed(() => {
  const base = parseInt(props.height) || 350
  const extra = Math.max(0, props.series.length - 5) * 10
  return `${base + extra}px`
})

const chartRef = ref<InstanceType<typeof VChart> | null>(null)

// Key forces VChart to fully recreate when series composition changes.
// This prevents stale legend items from ECharts' merge-mode setOption.
const chartKey = computed(() => {
  const names = props.series.map(s => s.name).join('|')
  return `${app.currentServer}:${names}`
})

const option = computed(() => {
  const isArea = props.chartType === 'line'
  const dark = app.isDark
  const maxSeries = app.maxLegendPlayers
  const brandColor = app.currentTheme.primary

  const limitedSeries = props.series.slice(0, maxSeries)
  const useScrollLegend = limitedSeries.length > 5

  const seriesList = limitedSeries.map((s) => {
    const base: any = {
      name: s.name,
      type: s.type || props.chartType,
      data: s.data,
      smooth: isArea ? 0.4 : false,
      symbolSize: 0,
      symbol: 'none',
      lineStyle: {
        width: s.strokeWidth || (isArea ? 3 : 2),
        color: s.color,
      },
      itemStyle: {
        color: s.color,
        borderRadius: props.chartType === 'bar' ? [6, 6, 0, 0] : 0,
      },
    }

    if (isArea && s.fill !== false) {
      base.areaStyle = {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: s.color + (dark ? 'a0' : '80') },
            { offset: 1, color: s.color + (dark ? '18' : '08') },
          ],
        },
      }
    }

    if (props.chartType === 'bar') {
      base.barMaxWidth = 40
      base.itemStyle.borderRadius = [6, 6, 0, 0]
    }

    return base
  })

  const allValues = limitedSeries.flatMap(s => s.data).filter((v): v is number => v != null && !isNaN(v))
  const yMax = allValues.length > 0 ? Math.max(...allValues) : 0

  if (seriesList.length > 0) {
    const mirrorData = new Array(props.labels.length).fill(0)
    mirrorData[0] = yMax
    seriesList.push({
      type: props.chartType,
      yAxisIndex: 1,
      data: mirrorData,
      showSymbol: false,
      lineStyle: { width: 0, opacity: 0 },
      itemStyle: { opacity: 0 },
      areaStyle: { opacity: 0 },
      silent: true,
      tooltip: { show: false },
    } as any)
  }

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: props.chartType === 'bar' ? 'shadow' : 'line',
        lineStyle: { color: '#d1ddd1', type: 'dashed' },
        shadowStyle: {
          color: hexToRgba(brandColor, dark ? 0.15 : 0.12),
        },
      },
      backgroundColor: dark ? 'rgba(30,41,59,0.95)' : 'rgba(255,255,255,0.95)',
      borderColor: hexToRgba(brandColor, dark ? 0.3 : 0.2),
      borderWidth: 1,
      padding: [12, 16],
      textStyle: { color: dark ? '#e2e8f0' : '#334155', fontSize: 12 },
      extraCssText: 'border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.08);backdrop-filter:blur(12px);max-height:400px;overflow-y:auto;' + (dark ? 'color:#e2e8f0;' : ''),
      appendToBody: true,
      formatter: (params: any) => {
        if (!Array.isArray(params) || params.length === 0) return ''
        const max = 10
        let html = `<div style="font-weight:600;margin-bottom:6px">${params[0].axisValue}</div>`
        const sorted = [...params].sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
        const show = sorted.slice(0, max)
        for (const item of show) {
          const dot = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${item.color};margin-right:6px;vertical-align:middle"></span>`
          html += `<div style="display:flex;justify-content:space-between;align-items:center;gap:16px;line-height:1.8">${dot}<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${item.seriesName}</span><span style="font-weight:600;margin-left:8px">${item.value ?? 0}</span></div>`
        }
        if (sorted.length > max) {
          html += `<div style="text-align:center;color:${dark ? '#64748b' : '#94a3b8'};padding-top:4px;font-size:11px">已隐藏后面 ${sorted.length - max} 条数据</div>`
        }
        return html
      },
    },
    legend: {
      type: useScrollLegend ? 'scroll' : 'plain',
      data: limitedSeries.map(s => s.name),
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 20,
      pageIconSize: 12,
      pageIconColor: dark ? '#94a3b8' : '#64748b',
      pageIconInactiveColor: dark ? '#334155' : '#cbd5e1',
      pageTextStyle: { fontSize: 12, color: dark ? '#94a3b8' : '#64748b' },
      textStyle: { fontSize: 12, color: dark ? '#94a3b8' : '#64748b' },
    },
    grid: {
      left: 10,
      right: 10,
      top: 10,
      bottom: useScrollLegend ? 50 : 35,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.labels,
      boundaryGap: props.chartType === 'bar',
      axisLine: { lineStyle: { color: dark ? '#334155' : '#e2e8f0' } },
      axisTick: { show: false },
      axisLabel: { color: dark ? '#64748b' : '#94a3b8', fontSize: 12 },
    },
    yAxis: [
      {
        type: 'value',
        name: props.yAxisLabel || '',
        nameTextStyle: { color: dark ? '#64748b' : '#94a3b8', fontSize: 12, padding: [0, 0, 0, -20] },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: dark ? '#64748b' : '#94a3b8',
          fontSize: 12,
          formatter: (v: number) => Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/\.?0+$/, ''),
        },
        splitLine: { lineStyle: { color: dark ? hexToRgba(brandColor, 0.15) : '#d1ddd1', type: 'dashed' } },
      },
      {
        type: 'value',
        position: 'right',
        alignTicks: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: dark ? '#64748b' : '#94a3b8',
          fontSize: 12,
          formatter: (v: number) => Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/\.?0+$/, ''),
        },
        splitLine: { show: false },
      },
    ],
    series: seriesList,
    animationDuration: 800,
    animationEasing: 'cubicOut' as const,
  }
})
</script>

<template>
  <div v-if="isEmpty" :style="{ height: chartHeight, width: '100%' }" class="flex flex-col items-center justify-center gap-3">
    <div class="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-700/50 flex items-center justify-center">
      <BarChart3 class="w-8 h-8 text-slate-300 dark:text-slate-600" />
    </div>
    <span class="text-sm text-slate-400 dark:text-slate-500">{{ t('common.noData') }}</span>
  </div>
  <VChart v-else ref="chartRef" :key="chartKey" :option="option" :style="{ height: chartHeight, width: '100%' }" autoresize />
</template>
