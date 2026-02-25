<template>
  <div>
    <v-card class="mb-4">
      <v-card-title>Coach Dashboard</v-card-title>
      <v-card-text>
        <v-alert type="info" variant="tonal" class="mb-4">
          Selecione um treino para visualizar ranking, presença e matriz de notas.
        </v-alert>

        <v-btn variant="flat" color="primary" :to="{ name: 'coach-trainings' }">
          Ir para Treinos
        </v-btn>
      </v-card-text>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>

    <v-progress-circular v-if="loading" indeterminate />

    <v-row v-else>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex flex-wrap align-center justify-space-between">
            Tendência (últimos treinos)
            <div v-if="latestTraining" class="text-body-2 text-medium-emphasis">
              Último: {{ latestTraining.date }} • {{ latestTraining.training_weighted_average ?? '-' }}
            </div>
          </v-card-title>
          <v-card-text>
            <div v-if="trendItems.length === 0" class="text-body-2 text-medium-emphasis">
              Sem dados suficientes.
            </div>
            <LineChart v-else title="Média ponderada" :items="trendItems" />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Média por drill (último treino)</v-card-title>
          <v-card-text>
            <div v-if="drillItems.length === 0" class="text-body-2 text-medium-emphasis">
              Sem drills/avaliações no último treino.
            </div>
            <BarChart v-else title="Média do drill" :items="drillItems" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LineChart from '../../components/charts/LineChart.vue'
import BarChart from '../../components/charts/BarChart.vue'
import { http } from '../../api/http'

type Item = { label: string; value: number }

const loading = ref(false)
const error = ref<string | null>(null)
const trendItems = ref<Item[]>([])
const drillItems = ref<Item[]>([])
const latestTraining = ref<any | null>(null)

async function fetchOverview() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/trainings/coach_overview/?limit=8')
    trendItems.value = (data?.trend ?? []) as Item[]
    drillItems.value = (data?.latest_drills ?? []) as Item[]
    latestTraining.value = data?.latest_training ?? null
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao carregar gráficos (HTTP ${status}).` : 'Falha ao carregar gráficos.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchOverview)
</script>