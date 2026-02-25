<template>
  <Line v-if="data" :data="data" :options="options" />
</template>

<script lang="ts">
export default {
  name: 'LineChart',
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

type Item = { label: string; value: number }

const props = defineProps<{
  title?: string
  items: Item[]
}>()

const data = computed(() => {
  return {
    labels: props.items.map(i => i.label),
    datasets: [
      {
        label: props.title ?? 'Tendência',
        data: props.items.map(i => i.value),
        tension: 0.3,
      },
    ],
  }
})

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: { y: { min: 0, max: 10 } },
}))
</script>

<style scoped>
:deep(canvas){ height: 260px !important; }
</style>