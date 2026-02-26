<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-chart-line</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Coach</div>
            <div class="text-h6 font-weight-bold">Dashboard</div>
          </div>
        </div>

        <v-btn color="primary" variant="flat" rounded="xl" :to="{ name: 'coach-trainings' }">
          <v-icon start>mdi-whistle</v-icon>
          Ir para Treinos
        </v-btn>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
        <v-alert type="info" variant="tonal" class="mb-4">
          Aqui você vê um resumo: tendência da média do time e médias por drill do último treino.
          Para ranking, presença e matriz de notas, acesse um treino em “Treinos”.
        </v-alert>
      </v-card-text>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
      {{ error }}
    </v-alert>

    <div v-if="loading" class="d-flex justify-center py-10">
      <v-progress-circular indeterminate />
    </div>

    <v-row v-else class="mt-1">
      <v-col cols="12" md="6">
        <v-card variant="tonal" rounded="xl">
          <v-card-title class="d-flex flex-wrap align-center justify-space-between">
            Tendência (últimos treinos)
            <div v-if="latestTraining" class="text-body-2 text-medium-emphasis">
              Último: {{ formatDateBR(latestTraining.date) }} • {{ latestTraining.training_weighted_average ?? '-' }}
            </div>
          </v-card-title>
          <v-card-text>
            <div v-if="trendItems.length === 0" class="text-body-2 text-medium-emphasis">
              Sem dados suficientes.
            </div>
            <LineChart v-else title="Média ponderada" :items="trendItems" />

            <div v-if="comparison" class="text-body-2 text-medium-emphasis mt-3">
              <div v-if="comparison.biggest_improvement">
                Maior evolução: {{ comparison.biggest_improvement.athlete_name }} ({{ comparison.biggest_improvement.delta }})
              </div>
              <div v-if="comparison.biggest_regression">
                Regressão técnica: {{ comparison.biggest_regression.athlete_name }} ({{ comparison.biggest_regression.delta }})
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card variant="tonal" rounded="xl">
          <v-card-title>Média por drill (último treino)</v-card-title>
          <v-card-text>
            <div v-if="drillItems.length === 0" class="text-body-2 text-medium-emphasis">
              Sem drills/avaliações no último treino.
            </div>
            <BarChart v-else title="Média do drill" :items="drillItems" />

            <div v-if="hardestDrill || mostConsistentAthlete" class="text-body-2 text-medium-emphasis mt-3">
              <div v-if="hardestDrill">
                Drill mais difícil: {{ hardestDrill.name }} ({{ hardestDrill.avg_score ?? '-' }})
              </div>
              <div v-if="mostConsistentAthlete">
                Atleta mais consistente: {{ mostConsistentAthlete.athlete_name }} (var {{ mostConsistentAthlete.variance }})
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LineChart from '../../components/charts/LineChart.vue'
import BarChart from '../../components/charts/BarChart.vue'
import { http } from '../../api/http'
function formatDateBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const m = /^\d{4}-\d{2}-\d{2}$/.exec(iso)
  if (!m) return iso
  const [y, mm, dd] = iso.split('-')
  return `${dd}/${mm}/${y}`
}

type Item = { label: string; value: number }

const loading = ref(false)
const error = ref<string | null>(null)
const trendItems = ref<Item[]>([])
const drillItems = ref<Item[]>([])
const latestTraining = ref<any | null>(null)
const comparison = ref<any | null>(null)
const hardestDrill = ref<any | null>(null)
const mostConsistentAthlete = ref<any | null>(null)

async function fetchOverview() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/trainings/evolution/?limit=8')
    const teamTrend = (data?.team_trend ?? []) as Array<{ label: string; value: number; training_id: number }>
    trendItems.value = teamTrend.map(x => ({ label: x.label, value: x.value }))
    comparison.value = data?.comparison ?? null

    const last = teamTrend.length ? teamTrend[teamTrend.length - 1] : undefined
    const lastTraining = comparison.value?.to_training
    latestTraining.value = lastTraining
      ? {
          id: lastTraining.id,
          date: String(lastTraining.date),
          training_weighted_average: last?.value ?? null,
        }
      : null

    drillItems.value = []
    hardestDrill.value = null
    mostConsistentAthlete.value = null

    const trainingId = latestTraining.value?.id
    if (trainingId) {
      const { data: analytics } = await http.get(`/trainings/${trainingId}/analytics/`)
      const byDrill = (analytics?.by_drill ?? []) as Array<{ name: string; avg_score: number | null }>
      drillItems.value = byDrill.map(d => ({ label: d.name, value: d.avg_score ?? 0 }))
      hardestDrill.value = analytics?.hardest_drill ?? null
      mostConsistentAthlete.value = analytics?.most_consistent_athlete ?? null
    }
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

<style scoped>
.page-header {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 16px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.70);
  backdrop-filter: blur(12px);
}

.page-header__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(var(--v-theme-on-primary), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 1),
    rgba(var(--v-theme-primary), 0.75)
  );
}
</style>