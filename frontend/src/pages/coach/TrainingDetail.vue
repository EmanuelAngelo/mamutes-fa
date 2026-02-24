<template>
  <div class="space-y-4" v-if="dash">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">Treino {{ dash.training.date }}</h1>
        <div class="text-sm text-gray-600">{{ dash.training.location || '-' }}</div>
      </div>
      <div class="flex gap-2">
        <v-btn variant="tonal" :loading="downloading" @click="downloadPdf">Exportar PDF</v-btn>
      </div>
    </div>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Resumo</v-card-title>
          <v-card-text class="space-y-2">
            <div>Atletas: <b>{{ dash.summary.athletes_total }}</b></div>
            <div>Drills: <b>{{ dash.summary.drills_total }}</b></div>
            <div>Média ponderada: <b>{{ dash.summary.training_weighted_average ?? '-' }}</b></div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Top 10 (Ranking)</v-card-title>
          <v-card-text style="height: 300px">
            <BarChart
              title="Média ponderada"
              :items="barItems"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>Ranking</v-card-title>
      <v-card-text>
        <v-table density="compact">
          <thead>
            <tr>
              <th>#</th>
              <th>Atleta</th>
              <th>Pos</th>
              <th>Média</th>
              <th>Drills</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in dash.ranking" :key="r.athlete_id">
              <td>{{ r.rank }}</td>
              <td>{{ r.athlete_name }}</td>
              <td>{{ r.position || '-' }}</td>
              <td>{{ r.weighted_average ?? '-' }}</td>
              <td>{{ r.scored_drills_count }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <ScoreMatrixTable
      :attendance="dash.attendance"
      :drills="dash.drills"
      :scoreMap="dash.score_map"
    />

    <v-card>
      <v-card-title>Ranking por posição</v-card-title>
      <v-card-text>
        <v-expansion-panels>
          <v-expansion-panel v-for="(items, pos) in dash.ranking_by_position" :key="pos">
            <v-expansion-panel-title>
              {{ pos }} ({{ items.length }})
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <v-table density="compact">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Atleta</th>
                    <th>Média</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="it in items" :key="it.athlete_id">
                    <td>{{ it.rank }}</td>
                    <td>{{ it.athlete_name }}</td>
                    <td>{{ it.weighted_average ?? '-' }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </div>

  <v-skeleton-loader v-else type="article, table" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '@/api/http'
import BarChart from '@/components/charts/BarChart.vue'
import ScoreMatrixTable from '@/components/coach/ScoreMatrixTable.vue'

const route = useRoute()
const dash = ref<any | null>(null)
const downloading = ref(false)

const trainingId = computed(() => Number(route.params.id))

const barItems = computed(() => {
  const top = (dash.value?.ranking ?? []).slice(0, 10)
  return top.map((x: any) => ({ label: x.athlete_name, value: x.weighted_average ?? 0 }))
})

async function fetchCoachDashboard() {
  const { data } = await http.get(`/api/trainings/${trainingId.value}/coach_dashboard/`)
  dash.value = data
}

async function downloadPdf() {
  downloading.value = true
  try {
    const url = `${import.meta.env.VITE_API_BASE_URL}/api/trainings/${trainingId.value}/export/pdf/`
    // abre em nova aba (mantém auth via header não vai; aqui depende do token)
    // Melhor: baixar via axios blob com Authorization
    const res = await http.get(`/api/trainings/${trainingId.value}/export/pdf/`, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const blobUrl = URL.createObjectURL(blob)
    window.open(blobUrl, '_blank')
  } finally {
    downloading.value = false
  }
}

onMounted(fetchCoachDashboard)
</script>