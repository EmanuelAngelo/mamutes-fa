<template>
  <div class="chart-container">
    <Doughnut v-if="data" :data="data" :options="options" />
  </div>
</template>

<script lang="ts">
export default {
  name: 'PieChart',
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

type Item = {
  label: string
  value: number
}

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
  const onSurface = readThemeRgb('on-surface')
  const surface = readThemeRgb('surface')

  const colors = [
    readThemeRgb('error'),
    readThemeRgb('warning'),
    readThemeRgb('info'),
    readThemeRgb('success'),
  ].filter((c): c is string => typeof c === 'string' && c.length > 0)

  const safeColors = colors.length ? colors : [onSurface]

  return {
    onSurface,
    axis: withAlpha(onSurface, 0.8),
    border: withAlpha(onSurface, 0.14),
    tooltipBg: withAlpha(surface, 0.96),
    colors: safeColors,
  }
})

const data = computed(() => {
  const t = theme.value
  const pick = (idx: number) => t.colors[idx % t.colors.length] ?? t.onSurface
  return {
    labels: props.items.map(i => i.label),
    datasets: [
      {
        label: String(props.title ?? 'Distribuição'),
        data: props.items.map(i => i.value),
        backgroundColor: props.items.map((_, idx) => withAlpha(pick(idx), 0.6)),
        borderColor: props.items.map((_, idx) => pick(idx)),
        borderWidth: 1,
      },
    ],
  }
})

const options = computed(() => {
  const t = theme.value
  return {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '62%',
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: t.axis,
          usePointStyle: true,
          boxWidth: 10,
        },
      },
      tooltip: {
        backgroundColor: t.tooltipBg,
        borderColor: t.border,
        borderWidth: 1,
        titleColor: t.onSurface,
        bodyColor: t.onSurface,
        callbacks: {
          label: (ctx: any) => {
            const label = String(ctx.label ?? '')
            const value = Number(ctx.parsed ?? 0)
            const total = Array.isArray(ctx.dataset?.data)
              ? (ctx.dataset.data as Array<number>).reduce((a: number, b: number) => a + Number(b || 0), 0)
              : 0
            const pct = total ? ((value / total) * 100).toFixed(1) : '0.0'
            return `${label}: ${value} (${pct}%)`
          },
        },
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
