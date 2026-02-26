<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-calendar-check</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Coach</div>
            <div class="text-h6 font-weight-bold">
              Treino {{ dashboard?.training?.date ? formatDateBR(dashboard.training.date) : '' }}
            </div>
          </div>
        </div>

        <v-btn
          color="primary"
          variant="flat"
          rounded="xl"
          :disabled="!dashboard"
          :loading="downloading"
          @click="downloadPdf"
        >
          <v-icon start>mdi-file-pdf-box</v-icon>
          Exportar PDF
        </v-btn>
      </div>
    </v-sheet>

    <v-card v-if="error" variant="tonal" rounded="xl" class="mt-4">
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

    <div v-else-if="loading" class="d-flex justify-center py-10">
      <v-progress-circular indeterminate />
    </div>

    <div v-else-if="dashboard">
      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title>Resumo</v-card-title>
        <v-card-text>
          <div><strong>Local:</strong> {{ dashboard.training.location || '-' }}</div>
          <div>
            <strong>Média do treino:</strong>
            {{ dashboard.summary.training_weighted_average ?? '-' }}
          </div>
        </v-card-text>
      </v-card>

      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title class="d-flex flex-wrap align-center justify-space-between">
          Lista de presença
          <v-btn class="mt-2 mt-sm-0" variant="tonal" :loading="savingAttendance" @click="saveAttendance">
            Salvar presença
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="attendanceError" type="error" variant="tonal" class="mb-3">
            {{ attendanceError }}
          </v-alert>

          <v-progress-circular v-if="loadingAttendance" indeterminate />

          <div v-else class="table-scroll">
            <v-table>
            <thead>
              <tr>
                <th>Atleta</th>
                <th>Camisa</th>
                <th>Posição</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in attendanceRows" :key="row.athlete_id">
                <td>{{ row.athlete_name }}</td>
                <td>{{ row.jersey_number || '-' }}</td>
                <td>{{ row.position || '-' }}</td>
                <td>
                  <v-select
                    v-model="row.status"
                    :items="attendanceStatusItems"
                    item-title="label"
                    item-value="value"
                    density="compact"
                    variant="outlined"
                    hide-details
                  />
                </td>
              </tr>
            </tbody>
            </v-table>
          </div>
        </v-card-text>
      </v-card>

      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title class="d-flex flex-wrap align-center justify-space-between">
          Drills do treino
          <v-btn class="mt-2 mt-sm-0" variant="tonal" :loading="savingDrill" @click="addDrill">
            Adicionar drill
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="drillError" type="error" variant="tonal" class="mb-3">
            {{ drillError }}
          </v-alert>

          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="newDrill.drill"
                :items="catalog"
                item-title="name"
                item-value="id"
                label="Catálogo (opcional)"
                clearable
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field v-model="newDrill.name_override" label="Nome (override)" />
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field v-model.number="newDrill.order" type="number" label="Ordem" />
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field v-model.number="newDrill.max_score" type="number" label="Max" />
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field v-model.number="newDrill.weight" type="number" label="Peso" />
            </v-col>
            <v-col cols="12" md="10">
              <v-textarea v-model="newDrill.description" label="Descrição" />
            </v-col>
          </v-row>

          <v-divider class="my-3" />

          <div class="table-scroll">
            <v-table>
            <thead>
              <tr>
                <th>Ordem</th>
                <th>Drill</th>
                <th>Peso</th>
                <th>Max</th>
                <th>Média</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in dashboard.drills" :key="d.training_drill_id">
                <td>{{ d.order }}</td>
                <td>{{ d.name }}</td>
                <td>{{ d.weight }}</td>
                <td>{{ d.max_score }}</td>
                <td>{{ d.average_score ?? '-' }}</td>
                <td>
                  <v-btn
                    size="small"
                    color="error"
                    variant="text"
                    :loading="deletingDrillId === d.training_drill_id"
                    @click="deleteDrill(d.training_drill_id)"
                  >
                    Remover
                  </v-btn>
                </td>
              </tr>
            </tbody>
            </v-table>
          </div>
        </v-card-text>
      </v-card>

      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title class="d-flex flex-wrap align-center justify-space-between">
          Avaliação individual
          <v-btn
            class="mt-2 mt-sm-0"
            color="primary"
            variant="tonal"
            :loading="savingScore"
            @click="saveScore"
          >
            Salvar avaliação
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="scoreError" type="error" variant="tonal" class="mb-3">
            {{ scoreError }}
          </v-alert>

          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="scoreForm.athlete_id"
                :items="scoreAthleteItems"
                item-title="label"
                item-value="value"
                label="Atleta"
                clearable
              />
            </v-col>

            <v-col cols="12" md="5">
              <v-select
                v-model="scoreForm.training_drill_id"
                :items="scoreDrillItems"
                item-title="label"
                item-value="value"
                label="Drill"
                clearable
              />
            </v-col>

            <v-col cols="12" md="3">
              <v-text-field
                v-model.number="scoreForm.score"
                type="number"
                label="Nota"
                :hint="selectedScoreDrill ? `Max: ${selectedScoreDrill.max_score}` : undefined"
                persistent-hint
              />
            </v-col>

            <v-col cols="12">
              <v-textarea v-model="scoreForm.comment" label="Comentário (opcional)" />
            </v-col>
          </v-row>

          <div class="text-body-2 text-medium-emphasis" v-if="existingScore">
            Já existe avaliação para esta combinação. Ao salvar, ela será atualizada.
          </div>
        </v-card-text>
      </v-card>

      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title>Ranking</v-card-title>
        <v-card-text>
          <div class="table-scroll">
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
          </div>
        </v-card-text>
      </v-card>

      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title>Presença</v-card-title>
        <v-card-text>
          <div class="table-scroll">
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
          </div>
        </v-card-text>
      </v-card>
    </div>

    <v-alert v-else type="info" variant="tonal">
      Nenhum dado retornado.
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '../../api/http'
function formatDateBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const m = /^\d{4}-\d{2}-\d{2}$/.exec(iso)
  if (!m) return iso
  const [y, mm, dd] = iso.split('-')
  return `${dd}/${mm}/${y}`
}

const route = useRoute()

const dashboard = ref<any | null>(null)
const loading = ref(false)
const downloading = ref(false)
const error = ref<string | null>(null)
const lastUrl = ref<string>('')

const catalog = ref<any[]>([])

const loadingAttendance = ref(false)
const savingAttendance = ref(false)
const attendanceError = ref<string | null>(null)
const attendanceRows = ref<any[]>([])

const savingDrill = ref(false)
const drillError = ref<string | null>(null)
const deletingDrillId = ref<number | null>(null)

const savingScore = ref(false)
const scoreError = ref<string | null>(null)

const scoreForm = ref({
  athlete_id: null as number | null,
  training_drill_id: null as number | null,
  score: null as number | null,
  comment: '',
})

const attendanceStatusItems = [
  { label: 'Presente', value: 'PRESENT' },
  { label: 'Ausente', value: 'ABSENT' },
  { label: 'Justificado', value: 'JUSTIFIED' },
  { label: 'Atraso', value: 'LATE' },
]

const newDrill = ref({
  drill: null as number | null,
  name_override: '',
  order: 1,
  description: '',
  max_score: 10,
  weight: 1,
})

const scoreAthleteItems = computed(() => {
  const att = dashboard.value?.attendance ?? []
  return att.map((a: any) => ({
    label: `${a.athlete_name}${a.jersey_number ? ` #${a.jersey_number}` : ''}`,
    value: a.athlete_id,
  }))
})

const scoreDrillItems = computed(() => {
  const drills = dashboard.value?.drills ?? []
  return drills.map((d: any) => ({
    label: `${d.order}. ${d.name}`,
    value: d.training_drill_id,
  }))
})

const selectedScoreDrill = computed(() => {
  const id = scoreForm.value.training_drill_id
  if (!id) return null
  return (dashboard.value?.drills ?? []).find((d: any) => d.training_drill_id === id) ?? null
})

const existingScore = computed(() => {
  const athleteId = scoreForm.value.athlete_id
  const drillId = scoreForm.value.training_drill_id
  if (!athleteId || !drillId) return null
  const map = dashboard.value?.score_map ?? {}
  return map[String(athleteId)]?.[String(drillId)] ?? null
})

function syncScoreFormFromExisting() {
  const ex = existingScore.value
  if (ex) {
    scoreForm.value.score = typeof ex.score === 'number' ? ex.score : Number(ex.score)
    scoreForm.value.comment = ex.comment ?? ''
    return
  }
  scoreForm.value.score = null
  scoreForm.value.comment = ''
}

async function fetchDashboard() {
  loading.value = true
  error.value = null
  dashboard.value = null

  const id = route.params.id
  const url = `/trainings/${id}/coach_dashboard/`
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

async function fetchCatalog() {
  try {
    const { data } = await http.get('/trainings/catalog/?ordering=name')
    catalog.value = data
  } catch (e) {
    console.error(e)
  }
}

function buildAttendanceRowsFrom(athletes: any[], existingAttendance: any[]) {
  const existingByAthleteId = new Map<number, any>()
  for (const a of existingAttendance ?? []) {
    existingByAthleteId.set(a.athlete_id, a)
  }

  attendanceRows.value = athletes.map((ath) => {
    const ex = existingByAthleteId.get(ath.id)
    return {
      athlete_id: ath.id,
      athlete_name: ath.name,
      jersey_number: ath.jersey_number,
      position: ath.current_position,
      status: ex?.status ?? 'PRESENT',
    }
  })
}

async function fetchAttendanceEditorData() {
  loadingAttendance.value = true
  attendanceError.value = null
  try {
    const [{ data: athletes }] = await Promise.all([
      http.get('/athletes/?is_active=true&ordering=name'),
    ])
    buildAttendanceRowsFrom(athletes, dashboard.value?.attendance)
  } catch (e: any) {
    const status = e?.response?.status
    attendanceError.value = status ? `Falha ao carregar atletas (HTTP ${status}).` : 'Falha ao carregar atletas.'
    console.error(e)
  } finally {
    loadingAttendance.value = false
  }
}

async function saveAttendance() {
  savingAttendance.value = true
  attendanceError.value = null
  const id = route.params.id
  const url = `/trainings/${id}/attendance_bulk/`
  lastUrl.value = url
  try {
    const payload = attendanceRows.value.map((r) => ({
      athlete: r.athlete_id,
      status: r.status,
      checkin_time: null,
    }))
    await http.post(url, payload)
    await fetchDashboard()
  } catch (e: any) {
    const status = e?.response?.status
    attendanceError.value = status ? `Falha ao salvar presença (HTTP ${status}).` : 'Falha ao salvar presença.'
    console.error(e)
  } finally {
    savingAttendance.value = false
  }
}

async function addDrill() {
  savingDrill.value = true
  drillError.value = null

  const id = route.params.id
  const url = `/trainings/${id}/drills_bulk/`
  lastUrl.value = url

  try {
    const payload = [{
      drill: newDrill.value.drill,
      name_override: newDrill.value.name_override || null,
      order: Number(newDrill.value.order || 1),
      description: newDrill.value.description || null,
      max_score: Number(newDrill.value.max_score || 10),
      weight: Number(newDrill.value.weight || 1),
    }]
    await http.post(url, payload)

    newDrill.value = {
      drill: null,
      name_override: '',
      order: 1,
      description: '',
      max_score: 10,
      weight: 1,
    }

    await fetchDashboard()
  } catch (e: any) {
    const status = e?.response?.status
    drillError.value = status ? `Falha ao adicionar drill (HTTP ${status}).` : 'Falha ao adicionar drill.'
    console.error(e)
  } finally {
    savingDrill.value = false
  }
}

async function deleteDrill(trainingDrillId: number) {
  deletingDrillId.value = trainingDrillId
  drillError.value = null
  try {
    await http.delete(`/trainings/drills/${trainingDrillId}/`)
    await fetchDashboard()
  } catch (e: any) {
    const status = e?.response?.status
    drillError.value = status ? `Falha ao remover drill (HTTP ${status}).` : 'Falha ao remover drill.'
    console.error(e)
  } finally {
    deletingDrillId.value = null
  }
}

async function downloadPdf() {
  downloading.value = true
  const id = route.params.id
  const url = `/trainings/${id}/export/pdf/`
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

async function saveScore() {
  scoreError.value = null
  const athleteId = scoreForm.value.athlete_id
  const trainingDrillId = scoreForm.value.training_drill_id
  const score = scoreForm.value.score

  if (!athleteId || !trainingDrillId) {
    scoreError.value = 'Selecione atleta e drill.'
    return
  }

  if (score === null || Number.isNaN(Number(score))) {
    scoreError.value = 'Informe uma nota.'
    return
  }

  const maxScore = selectedScoreDrill.value?.max_score
  if (typeof maxScore === 'number' && Number(score) > maxScore) {
    scoreError.value = `Nota maior que o máximo (${maxScore}).`
    return
  }

  savingScore.value = true
  const id = route.params.id
  const url = `/trainings/${id}/scores_bulk/`
  lastUrl.value = url
  try {
    await http.post(url, [{
      training_drill: trainingDrillId,
      athlete: athleteId,
      score: Number(score),
      comment: scoreForm.value.comment?.trim() ? scoreForm.value.comment.trim() : null,
    }])

    await fetchDashboard()
    syncScoreFormFromExisting()
  } catch (e: any) {
    const status = e?.response?.status
    scoreError.value = status ? `Falha ao salvar avaliação (HTTP ${status}).` : 'Falha ao salvar avaliação.'
    console.error(e)
  } finally {
    savingScore.value = false
  }
}

onMounted(fetchDashboard)

watch(
  () => dashboard.value,
  (val) => {
    if (val) fetchAttendanceEditorData()
  },
  { immediate: false }
)

onMounted(fetchCatalog)

watch(
  () => [scoreForm.value.athlete_id, scoreForm.value.training_drill_id],
  () => syncScoreFormFromExisting()
)
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