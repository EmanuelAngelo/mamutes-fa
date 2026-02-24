<template>
  <Bar v-if="data" :data="data" :options="options" />
</template>

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

const data = computed(() => ({
  labels: props.items.map(i => i.label),
  datasets: [{ label: props.title ?? 'Ranking', data: props.items.map(i => i.value) }],
}))

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: { y: { min: 0, max: 10 } },
}))
</script>

<style scoped>
:deep(canvas){ height: 260px !important; }
</style>