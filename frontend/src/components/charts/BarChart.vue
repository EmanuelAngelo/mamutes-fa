<template>
  <div class="chart-container">
    <Bar v-if="data" :data="data" :options="options" />
  </div>
</template>

<script lang="ts">
export default {
  name: 'BarChart',
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

type Item = { label: string; value: number }
type Series = {
  label: string
  data: number[]
  colorKey?: 'primary' | 'info' | 'success' | 'warning' | 'error' | 'secondary'
}

const props = defineProps<{
  title?: string
  items?: Item[]
  labels?: string[]
  series?: Series[]
  yMin?: number
  yMax?: number
  stacked?: boolean
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
  const info = readThemeRgb('info')
  const success = readThemeRgb('success')
  const warning = readThemeRgb('warning')
  const error = readThemeRgb('error')
  const secondary = readThemeRgb('secondary')
  const onSurface = readThemeRgb('on-surface')
  const surface = readThemeRgb('surface')
  return {
    primary,
    info,
    success,
    warning,
    error,
    secondary,
    onSurface,
    axis: withAlpha(onSurface, 0.8),
    grid: withAlpha(onSurface, 0.14),
    barFill: withAlpha(info, 0.55),
    tooltipBg: withAlpha(surface, 0.96),
  }
})

const palette = computed(() => {
  const t = theme.value
  return {
    primary: t.primary,
    info: t.info,
    success: t.success,
    warning: t.warning,
    error: t.error,
    secondary: t.secondary,
  }
})

const data = computed(() => {
  const t = theme.value
  const pal = palette.value

  if (props.series?.length && props.labels?.length) {
    return {
      labels: props.labels,
      datasets: props.series.map((s) => {
        const key = s.colorKey ?? 'info'
        const rgb = pal[key]
        return {
          label: s.label,
          data: s.data,
          backgroundColor: withAlpha(rgb, 0.55),
          borderColor: rgb,
          borderWidth: 1,
          borderRadius: 8,
        }
      }),
    }
  }

  return {
    labels: (props.items ?? []).map(i => i.label),
    datasets: [
      {
        label: props.title ?? 'Ranking',
        data: (props.items ?? []).map(i => i.value),
        backgroundColor: t.barFill,
        borderColor: t.info,
        borderWidth: 1,
        borderRadius: 8,
      },
    ],
  }
})

const options = computed(() => {
  const t = theme.value
  const stacked = Boolean(props.stacked)
  const yMin = typeof props.yMin === 'number' ? props.yMin : 0
  const yMax = typeof props.yMax === 'number' ? props.yMax : 10
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: t.axis },
      },
      tooltip: {
        backgroundColor: t.tooltipBg,
        borderColor: t.grid,
        borderWidth: 1,
        titleColor: t.onSurface,
        bodyColor: t.onSurface,
        displayColors: stacked,
      },
    },
    scales: {
      x: {
        stacked,
        ticks: { color: t.axis },
        grid: { color: t.grid },
      },
      y: {
        stacked,
        min: yMin,
        max: yMax,
        ticks: { color: t.axis },
        grid: { color: t.grid },
      },
    },
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 260px;
}
</style>