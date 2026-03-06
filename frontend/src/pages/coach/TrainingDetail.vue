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

        <v-btn
          class="ml-2"
          variant="tonal"
          rounded="xl"
          :to="{ name: 'coach-trainings' }"
        >
          <v-icon start>mdi-arrow-left</v-icon>
          Voltar
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
      <v-progress-circular
        :model-value="progressValue"
        :rotate="360"
        :size="100"
        :width="15"
        color="primary"
      >
        <template #default>{{ progressValue }} %</template>
      </v-progress-circular>
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

      <div ref="attendanceAnchor">
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

          <v-progress-circular
            v-if="loadingAttendance"
            :model-value="progressValue"
            :rotate="360"
            :size="64"
            :width="10"
            color="primary"
          >
            <template #default>{{ progressValue }} %</template>
          </v-progress-circular>

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
      </div>

      <div ref="drillsAnchor">
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
      </div>

      <div ref="scoresAnchor">
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
            <v-col cols="12" md="4" class="d-flex align-center">
              <v-btn
                v-if="scoreForm.athlete_id && canEditScoresForSelectedAthlete && scoreMode === 'pending'"
                color="primary"
                variant="tonal"
                @click="startEditScores"
              >
                Editar avaliação
              </v-btn>
            </v-col>
          </v-row>

          <v-alert
            v-if="scoreForm.athlete_id && pendingScoreRows.length === 0"
            type="info"
            variant="tonal"
            class="mt-2"
          >
            Nenhum drill pendente para este atleta.
            <template #append>
              <v-btn
                v-if="canEditScoresForSelectedAthlete"
                size="small"
                color="primary"
                variant="tonal"
                @click="startEditScores"
              >
                Refazer avaliação
              </v-btn>
            </template>
          </v-alert>

          <div v-if="scoreForm.athlete_id && pendingScoreRows.length" class="table-scroll mt-3">
            <v-table>
              <thead>
                <tr>
                  <th style="width: 45%">Drill</th>
                  <th style="width: 18%">Max</th>
                  <th style="width: 18%">Nota</th>
                  <th>Comentário</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in pendingScoreRows" :key="row.training_drill_id">
                  <td>{{ row.label }}</td>
                  <td>{{ row.max_score }}</td>
                  <td>
                    <v-text-field
                      v-model.number="row.score"
                      type="number"
                      density="compact"
                      variant="outlined"
                      hide-details
                      :min="0"
                      :max="row.max_score"
                      step="0.1"
                    />
                  </td>
                  <td>
                    <v-text-field
                      v-model="row.comment"
                      density="compact"
                      variant="outlined"
                      hide-details
                      placeholder="(opcional)"
                    />
                  </td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-card-text>
      </v-card>
      </div>

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
                <td>{{ a.status_label ?? a.status }}</td>
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
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '../../api/http'
import { useProgressCircular } from '../../composables/useProgressCircular'
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
const attendanceEditorLoaded = ref(false)

const attendanceAnchor = ref<HTMLElement | null>(null)
const drillsAnchor = ref<HTMLElement | null>(null)
const scoresAnchor = ref<HTMLElement | null>(null)

type AnchorKey = 'attendance' | 'drills' | 'scores'
const anchors: Record<AnchorKey, typeof attendanceAnchor> = {
  attendance: attendanceAnchor,
  drills: drillsAnchor,
  scores: scoresAnchor,
}

const savingDrill = ref(false)
const drillError = ref<string | null>(null)
const deletingDrillId = ref<number | null>(null)

const savingScore = ref(false)
const scoreError = ref<string | null>(null)

const anyLoading = computed(() => loading.value || loadingAttendance.value)
const { progressValue } = useProgressCircular(anyLoading)

const scoreForm = ref({
  athlete_id: null as number | null,
})

const scoreMode = ref<'pending' | 'edit'>('pending')

type PendingScoreRow = {
  training_drill_id: number
  label: string
  max_score: number
  score: number | null
  comment: string
}

const pendingScoreRows = ref<PendingScoreRow[]>([])

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
  const presentStatus = new Set(['PRESENT', 'LATE'])
  return att
    .filter((a: any) => presentStatus.has(String(a?.status ?? 'PRESENT')))
    .map((a: any) => ({
      label: `${a.athlete_name}${a.jersey_number ? ` #${a.jersey_number}` : ''}`,
      value: a.athlete_id,
    }))
})

const canEditScoresForSelectedAthlete = computed(() => {
  const athleteId = scoreForm.value.athlete_id
  if (!athleteId) return false
  const drills = dashboard.value?.drills ?? []
  if (!Array.isArray(drills) || drills.length === 0) return false
  return drills.some((d: any) => Boolean(getScoreEntry(athleteId, d.training_drill_id)))
})

watch(
  scoreAthleteItems,
  (items) => {
    const current = scoreForm.value.athlete_id
    if (!current) return
    if (!items.some((i: any) => i.value === current)) {
      scoreForm.value.athlete_id = null
      pendingScoreRows.value = []
    }
  },
  { immediate: true }
)

function getScoreEntry(athleteId: number, trainingDrillId: number) {
  const map = dashboard.value?.score_map ?? {}
  const aKey = String(athleteId)
  const dKey = String(trainingDrillId)
  return (
    map?.[aKey]?.[dKey] ??
    map?.[athleteId]?.[trainingDrillId] ??
    null
  )
}

function getPendingDrillsForAthlete(athleteId: number): any[] {
  const drills = dashboard.value?.drills ?? []
  return drills.filter((d: any) => !getScoreEntry(athleteId, d.training_drill_id))
}

function buildEditRowsForAthlete(athleteId: number) {
  const drills = dashboard.value?.drills ?? []
  pendingScoreRows.value = drills.map((d: any) => {
    const entry = getScoreEntry(athleteId, d.training_drill_id)
    return {
      training_drill_id: d.training_drill_id,
      label: `${d.order}. ${d.name}`,
      max_score: Number(d.max_score ?? 10),
      score: entry?.score ?? null,
      comment: String(entry?.comment ?? ''),
    }
  })
}

function startEditScores() {
  const athleteId = scoreForm.value.athlete_id
  if (!athleteId) return
  scoreMode.value = 'edit'
  buildEditRowsForAthlete(athleteId)
}

function buildPendingRowsForAthlete(athleteId: number) {
  const pending = getPendingDrillsForAthlete(athleteId)
  pendingScoreRows.value = pending.map((d: any) => ({
    training_drill_id: d.training_drill_id,
    label: `${d.order}. ${d.name}`,
    max_score: Number(d.max_score ?? 10),
    score: null,
    comment: '',
  }))
}

async function fetchDashboard() {
  return fetchDashboardWith({ showLoading: true, clearDashboard: true })
}

async function fetchDashboardWith(opts: { showLoading: boolean; clearDashboard: boolean }) {
  if (opts.showLoading) loading.value = true
  error.value = null
  if (opts.clearDashboard) dashboard.value = null

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
    if (opts.showLoading) loading.value = false
  }
}

async function refreshDashboardAt(anchor: AnchorKey) {
  await fetchDashboardWith({ showLoading: false, clearDashboard: false })
  await nextTick()
  const el = anchors[anchor].value
  if (!el) return
  const headerEl = document.querySelector('.page-header') as HTMLElement | null
  const headerH = headerEl ? headerEl.getBoundingClientRect().height : 0

  const extraGap = 12
  const y = window.scrollY + el.getBoundingClientRect().top - headerH - extraGap
  window.scrollTo({ top: Math.max(0, y), behavior: 'auto' })
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
    attendanceEditorLoaded.value = true
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
    await refreshDashboardAt('attendance')
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

    await refreshDashboardAt('drills')
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
    await refreshDashboardAt('drills')
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

  if (!athleteId) {
    scoreError.value = 'Selecione um atleta.'
    return
  }

  const toSave = pendingScoreRows.value
    .filter((r) => r.score !== null && !Number.isNaN(Number(r.score)))
    .map((r) => ({
      training_drill: r.training_drill_id,
      athlete: athleteId,
      score: Number(r.score),
      comment: r.comment?.trim() ? r.comment.trim() : null,
      max_score: r.max_score,
      label: r.label,
    }))

  if (toSave.length === 0) {
    scoreError.value = 'Informe ao menos uma nota.'
    return
  }

  for (const it of toSave) {
    if (it.score < 0) {
      scoreError.value = `Nota inválida em ${it.label}.`
      return
    }
    if (typeof it.max_score === 'number' && it.score > it.max_score) {
      scoreError.value = `Nota maior que o máximo (${it.max_score}) em ${it.label}.`
      return
    }
  }

  savingScore.value = true
  const id = route.params.id
  const url = `/trainings/${id}/scores_bulk/`
  lastUrl.value = url
  try {
    await http.post(
      url,
      toSave.map((x) => ({
        training_drill: x.training_drill,
        athlete: x.athlete,
        score: x.score,
        comment: x.comment,
      }))
    )

    await refreshDashboardAt('scores')

    // Após salvar (inclusive no "refazer/editar"), volta para o modo padrão.
    // Assim a tabela não fica presa no estado de edição com valores preenchidos.
    scoreMode.value = 'pending'

    // Recarrega pendências; se acabou, remove atleta da seleção.
    const pending = getPendingDrillsForAthlete(athleteId)
    if (pending.length === 0) {
      pendingScoreRows.value = []
    } else {
      buildPendingRowsForAthlete(athleteId)
    }
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
    if (val && !attendanceEditorLoaded.value) fetchAttendanceEditorData()
  },
  { immediate: false }
)

onMounted(fetchCatalog)

watch(
  () => scoreForm.value.athlete_id,
  (athleteId) => {
    if (!athleteId) {
      pendingScoreRows.value = []
      return
    }
    scoreMode.value = 'pending'
    buildPendingRowsForAthlete(athleteId)
  }
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