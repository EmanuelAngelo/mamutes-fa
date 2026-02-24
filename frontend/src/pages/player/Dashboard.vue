<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">Meu Dashboard</h1>
      <v-chip v-if="latest?.training" color="primary" variant="tonal">
        Último treino: {{ latest.training.date }}
      </v-chip>
    </div>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Média do treino</v-card-title>
          <v-card-text class="text-3xl font-semibold">
            {{ latest?.day_weighted_average ?? '-' }}
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Pontos de melhoria (últimos treinos)</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item v-for="it in improvements" :key="it.drill_name">
                <v-list-item-title>
                  {{ it.drill_name }} — média: {{ it.average_score ?? '-' }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ it.last_comment || 'Sem comentário' }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card v-if="latest?.drills?.length">
      <v-card-title>Notas do último treino</v-card-title>
      <v-card-text>
        <v-table density="compact">
          <thead>
            <tr>
              <th>Drill</th>
              <th>Nota</th>
              <th>Comentário</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in latest.drills" :key="d.training_drill_id">
              <td>{{ d.drill_name }}</td>
              <td>{{ d.score ?? '-' }}</td>
              <td>{{ d.comment ?? '-' }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title class="flex items-center justify-between">
        Tendência por drill
        <div class="w-[320px]">
          <v-select
            v-model="selectedDrillName"
            :items="drillNames"
            label="Selecione o drill"
            density="compact"
            hide-details
          />
        </div>
      </v-card-title>
      <v-card-text style="height: 300px">
        <LineChart :title="selectedDrillName || 'Tendência'" :items="trendChartItems" />
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { http } from '@/api/http'
import LineChart from '@/components/charts/LineChart.vue'

type LatestResp = {
  training: { id: number; date: string; start_time?: string; location?: string; notes?: string }
  attendance_status: string
  day_weighted_average: number | null
  drills: Array<{ training_drill_id: number; drill_name: string; score: number | null; comment: string | null; weight: number }>
}

type Improvement = { drill_name: string; average_score: number | null; last_comment: string | null }

const latest = ref<LatestResp | null>(null)
const improvements = ref<Improvement[]>([])
const selectedDrillName = ref<string>('')

const trendItems = ref<Array<{ date: string; score: number; drill_name: string }>>([])

const drillNames = computed(() => {
  const names = latest.value?.drills?.map(d => d.drill_name) ?? []
  return Array.from(new Set(names))
})

const trendChartItems = computed(() => {
  return trendItems.value.map(it => ({ label: it.date, value: it.score }))
})

async function fetchLatest() {
  const { data } = await http.get('/api/dashboard/my/latest-training/')
  latest.value = data
  if (!selectedDrillName.value && data?.drills?.length) {
    selectedDrillName.value = data.drills[0].drill_name
  }
}

async function fetchImprovements() {
  const { data } = await http.get('/api/dashboard/my/improvements/?last_trainings=8&top=3')
  // backend: { items: [...] }
  improvements.value = (data.items || []).map((x: any) => ({
    drill_name: x.drill_name,
    average_score: x.average_score ?? x.average_score, // compat
    last_comment: x.last_comment ?? null,
  }))
}

async function fetchTrendByName(name: string) {
  if (!name) return
  const { data } = await http.get(`/api/dashboard/my/drill-trends/?name=${encodeURIComponent(name)}&limit=20`)
  trendItems.value = (data.items || []).map((x: any) => ({
    date: x.date,
    score: x.score,
    drill_name: x.drill_name,
  }))
}

onMounted(async () => {
  await Promise.all([fetchLatest(), fetchImprovements()])
})

watch(selectedDrillName, async (v) => {
  await fetchTrendByName(v)
})
</script>