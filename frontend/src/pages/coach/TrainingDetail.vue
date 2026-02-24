<template>
  <v-container>
    <v-card v-if="error" class="mb-4">
      <v-card-title>Erro ao carregar treino</v-card-title>
      <v-card-text>
        <v-alert type="error" variant="tonal" class="mb-3">
          {{ error }}
        </v-alert>

        <div class="text-body-2">
          Tentamos carregar: <b>{{ lastUrl }}</b>
        </div>

        <v-btn class="mt-3" variant="tonal" @click="fetchDashboard">
          Tentar novamente
        </v-btn>
      </v-card-text>
    </v-card>

    <v-progress-circular v-else-if="loading" indeterminate />

    <div v-else-if="dashboard">
      <v-card class="mb-4">
        <v-card-title>Treino {{ dashboard.training.date }}</v-card-title>
        <v-card-text>
          <div><strong>Local:</strong> {{ dashboard.training.location || '-' }}</div>
          <div>
            <strong>Média do treino:</strong>
            {{ dashboard.summary.training_weighted_average ?? '-' }}
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" variant="tonal" :loading="downloading" @click="downloadPdf">
            Exportar PDF
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card class="mb-4">
        <v-card-title>Ranking</v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>#</th>
                <th>Atleta</th>
                <th>Posição</th>
                <th>Média</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in dashboard.ranking" :key="r.athlete_id">
                <td>{{ r.rank }}</td>
                <td>{{ r.athlete_name }}</td>
                <td>{{ r.position || '-' }}</td>
                <td>{{ r.weighted_average ?? '-' }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>

      <v-card>
        <v-card-title>Presença</v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>Atleta</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in dashboard.attendance" :key="a.athlete_id">
                <td>{{ a.athlete_name }}</td>
                <td>{{ a.status }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </div>

    <v-alert v-else type="info" variant="tonal">
      Nenhum dado retornado.
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '@/api/http'

const route = useRoute()

const dashboard = ref<any | null>(null)
const loading = ref(false)
const downloading = ref(false)
const error = ref<string | null>(null)
const lastUrl = ref<string>('')

async function fetchDashboard() {
  loading.value = true
  error.value = null
  dashboard.value = null

  const id = route.params.id
  const url = `/api/trainings/${id}/coach_dashboard/`
  lastUrl.value = url

  try {
    const { data } = await http.get(url)
    dashboard.value = data
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 404) {
      error.value = `Endpoint não encontrado (404). Confirme se existe no backend: ${url}`
    } else if (status) {
      error.value = `Falha ao carregar (HTTP ${status}).`
    } else {
      error.value = 'Falha ao carregar (erro de rede ou CORS).'
    }
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function downloadPdf() {
  downloading.value = true
  const id = route.params.id
  const url = `/api/trainings/${id}/export/pdf/`
  lastUrl.value = url

  try {
    const res = await http.get(url, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const blobUrl = URL.createObjectURL(blob)
    window.open(blobUrl, '_blank')
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 404) {
      error.value = `Export PDF não encontrado (404). Confirme se existe no backend: ${url}`
    } else if (status) {
      error.value = `Falha ao exportar PDF (HTTP ${status}).`
    } else {
      error.value = 'Falha ao exportar PDF (erro de rede ou CORS).'
    }
    console.error(e)
  } finally {
    downloading.value = false
  }
}

onMounted(fetchDashboard)
</script>