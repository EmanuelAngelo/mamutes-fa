<template>
  <div class="chart-container">
    <Chart v-if="data" :type="chartType" :data="data" :options="options" />
  </div>
</template>

<script lang="ts">
export default {
  name: 'BoxPlotChart',
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { Chart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
} from 'chart.js'
import {
  BoxPlotController,
  BoxAndWiskers,
} from '@sgratzl/chartjs-chart-boxplot'

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BoxPlotController, BoxAndWiskers)

const chartType = 'boxplot' as any

type BoxplotStats = {
  min: number
  q1: number
  median: number
  q3: number
  max: number
  outliers?: number[]
  n?: number
}

type Item = {
  label: string
  stats: BoxplotStats
}

const props = defineProps<{
  title?: string
  items: Item[]
  yMin?: number
  yMax?: number
}>()

const readThemeRgb = (key: string) => {
  if (typeof window === 'undefined') return 'rgb(0, 0, 0)'

  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue(`--v-theme-${key}`)
    .trim()

  if (raw) return `rgb(${raw})`

  return getComputedStyle(document.body).color || 'rgb(0, 0, 0)'
}

const withAlpha = (rgb: string, alpha: number) => {
  const match = rgb.match(/rgb\(([^)]+)\)/)
  if (!match) return rgb
  return `rgba(${match[1]}, ${alpha})`
}

const theme = computed(() => {
  const primary = readThemeRgb('primary')
  const onSurface = readThemeRgb('on-surface')
  const surface = readThemeRgb('surface')

  return {
    primary,
    onSurface,
    axis: withAlpha(onSurface, 0.8),
    grid: withAlpha(onSurface, 0.14),
    fill: withAlpha(primary, 0.22),
    border: withAlpha(primary, 0.85),
    tooltipBg: withAlpha(surface, 0.96),
  }
})

const data = computed(() => {
  const t = theme.value
  const labels = props.items.map(i => i.label)
  const values = props.items.map(i => ({
    min: i.stats.min,
    q1: i.stats.q1,
    median: i.stats.median,
    q3: i.stats.q3,
    max: i.stats.max,
    outliers: Array.isArray(i.stats.outliers) ? i.stats.outliers : [],
  }))

  return {
    labels,
    datasets: [
      {
        label: String(props.title ?? 'Boxplot'),
        data: values,
        backgroundColor: t.fill,
        borderColor: t.border,
        borderWidth: 1,
        outlierColor: t.border,
        outlierRadius: 2.5,
        itemRadius: 0,
      } as any,
    ],
  } as any
})

const options = computed(() => {
  const t = theme.value
  const yMin = typeof props.yMin === 'number' ? props.yMin : 0
  const yMax = typeof props.yMax === 'number' ? props.yMax : 10

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
        labels: { color: t.axis },
      },
      tooltip: {
        backgroundColor: t.tooltipBg,
        borderColor: t.grid,
        borderWidth: 1,
        titleColor: t.onSurface,
        bodyColor: t.onSurface,
        callbacks: {
          label: (ctx: any) => {
            const raw = ctx?.raw || {}
            const q1 = Number(raw.q1)
            const med = Number(raw.median)
            const q3 = Number(raw.q3)
            const min = Number(raw.min)
            const max = Number(raw.max)
            return `min ${min} • q1 ${q1} • med ${med} • q3 ${q3} • max ${max}`
          },
        },
      },
    },
    scales: {
      x: {
        ticks: { color: t.axis },
        grid: { color: t.grid },
      },
      y: {
        min: yMin,
        max: yMax,
        ticks: { color: t.axis },
        grid: { color: t.grid },
      },
    },
  } as any
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 260px;
}
</style>
