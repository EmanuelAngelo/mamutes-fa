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

const props = defineProps<{
  title?: string
  items: Item[]
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
  const info = readThemeRgb('info')
  const onSurface = readThemeRgb('on-surface')
  const surface = readThemeRgb('surface')
  return {
    info,
    onSurface,
    axis: withAlpha(onSurface, 0.8),
    grid: withAlpha(onSurface, 0.14),
    barFill: withAlpha(info, 0.55),
    tooltipBg: withAlpha(surface, 0.96),
  }
})

const data = computed(() => {
  const t = theme.value
  return {
    labels: props.items.map(i => i.label),
    datasets: [
      {
        label: props.title ?? 'Ranking',
        data: props.items.map(i => i.value),
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
        displayColors: false,
      },
    },
    scales: {
      x: {
        ticks: { color: t.axis },
        grid: { color: t.grid },
      },
      y: {
        min: 0,
        max: 10,
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