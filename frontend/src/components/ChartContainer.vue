<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import { useAppStore } from '@/stores/app'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

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
}>(), {
  chartType: 'line',
  height: '350px',
})

const app = useAppStore()

const option = computed(() => {
  const isArea = props.chartType === 'line'
  const dark = app.isDark
  const maxSeries = app.maxLegendPlayers

  const limitedSeries = props.series.slice(0, maxSeries)

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

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: { color: '#d1ddd1', type: 'dashed' },
      },
      backgroundColor: dark ? 'rgba(30,41,59,0.95)' : 'rgba(255,255,255,0.95)',
      borderColor: dark ? 'rgba(119,153,119,0.3)' : 'rgba(119,153,119,0.2)',
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
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 20,
      textStyle: { fontSize: 12, color: dark ? '#94a3b8' : '#64748b' },
    },
    grid: {
      left: 10,
      right: 20,
      top: 10,
      bottom: 40,
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
    yAxis: {
      type: 'value',
      name: props.yAxisLabel || '',
      nameTextStyle: { color: dark ? '#64748b' : '#94a3b8', fontSize: 12, padding: [0, 0, 0, -20] },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: dark ? '#64748b' : '#94a3b8', fontSize: 12 },
      splitLine: { lineStyle: { color: dark ? '#1e3a1e' : '#d1ddd1', type: 'dashed' } },
    },
    series: seriesList,
    animationDuration: 800,
    animationEasing: 'cubicOut' as const,
  }
})
</script>

<template>
  <VChart :option="option" :style="{ height, width: '100%' }" autoresize />
</template>
