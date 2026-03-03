<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-book-open-variant</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">{{ readOnly ? 'Player' : 'Coach' }}</div>
            <div class="text-h6 font-weight-bold">Playbook</div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-btn variant="tonal" rounded="xl" :loading="downloadingAllPdf" @click="downloadPdfAll">
            <v-icon start>mdi-file-pdf-box</v-icon>
            Imprimir PDF
          </v-btn>

          <v-btn v-if="!readOnly" color="primary" variant="flat" rounded="xl" @click="openCreate">
            <v-icon start>mdi-plus</v-icon>
            Nova Jogada
          </v-btn>
        </div>
      </div>
    </v-sheet>

    <v-alert v-if="error" type="error" variant="tonal" class="mt-4">
      {{ error }}
    </v-alert>

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

    <div v-else class="mt-4">
      <div v-if="plays.length === 0" class="text-center py-12">
        <div class="d-flex justify-center mb-4">
          <v-avatar size="72" variant="tonal">
            <v-icon size="34">mdi-book-open-variant</v-icon>
          </v-avatar>
        </div>
        <div class="text-h6 font-weight-bold">Playbook vazio</div>
        <div class="text-body-2 text-medium-emphasis mt-1">
          Adicione jogadas com formações, jogadores e rotas
        </div>
        <v-btn
          v-if="!readOnly"
          class="mt-5"
          color="primary"
          variant="tonal"
          rounded="xl"
          @click="openCreate"
        >
          <v-icon start>mdi-plus</v-icon>
          Adicionar Jogada
        </v-btn>
      </div>

      <v-row v-else density="comfortable">
        <v-col v-for="p in plays" :key="p.id" cols="12" sm="6" lg="4">
          <v-hover v-slot="{ isHovering, props }">
            <v-card v-bind="props" variant="tonal" rounded="xl" class="play-card">
              <div class="play-preview">
                <svg class="play-preview__svg" viewBox="0 0 500 700" aria-label="Preview da jogada">
                  <defs>
                    <filter id="pbShadow" x="-20%" y="-20%" width="140%" height="140%">
                      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.35)" />
                    </filter>
                  </defs>
                  <rect x="0" y="0" width="500" height="700" class="play-preview__field" />
                  <g class="play-preview__lines">
                    <line v-for="y in [70, 150, 230, 310, 390, 470, 550, 630]" :key="y" x1="0" :y1="y" x2="500" :y2="y" />
                  </g>
                  <g>
                    <polyline
                      v-for="(r, idx) in p.routes || []"
                      :key="`r-${p.id}-${idx}`"
                      :points="routePointsAttr(r)"
                      fill="none"
                      :stroke="routeStroke(r)"
                      stroke-width="7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      :stroke-dasharray="r.type === 'block' ? '10 10' : undefined"
                      opacity="0.95"
                    />
                    <polygon
                      v-for="(r, idx) in p.routes || []"
                      :key="`a-${p.id}-${idx}`"
                      :points="routeArrowPointsAttr(r)"
                      :fill="routeStroke(r)"
                      opacity="0.95"
                    />
                  </g>
                  <g>
                    <circle
                      v-for="pl in p.players || []"
                      :key="`p-${p.id}-${pl.id}`"
                      :cx="pl.x"
                      :cy="pl.y"
                      r="18"
                      :fill="pl.team === 'defense' ? 'rgb(var(--v-theme-error))' : 'rgb(var(--v-theme-info))'"
                      stroke="rgba(255,255,255,0.85)"
                      stroke-width="3"
                      filter="url(#pbShadow)"
                    />
                    <text
                      v-for="pl in p.players || []"
                      :key="`t-${p.id}-${pl.id}`"
                      :x="pl.x"
                      :y="pl.y"
                      text-anchor="middle"
                      dominant-baseline="middle"
                      class="play-preview__label"
                    >
                      {{ playerLabel(pl) }}
                    </text>
                  </g>
                </svg>

                <div class="play-actions" :class="{ 'play-actions--show': isHovering }">
                  <div class="play-actions__panel">
                    <div class="d-flex justify-end ga-2">
                      <v-btn size="small" color="primary" variant="flat" rounded="lg" @click.stop="openView(p)">
                        <v-icon start>mdi-eye</v-icon>
                        Ver
                      </v-btn>

                      <v-btn
                        size="small"
                        variant="tonal"
                        icon
                        aria-label="Baixar PDF"
                        :loading="downloadingPdfId === p.id"
                        :disabled="downloadingPdfId === p.id"
                        @click.stop="downloadPdfOne(p)"
                      >
                        <v-icon>mdi-file-pdf-box</v-icon>
                      </v-btn>
                    </div>

                    <div v-if="!readOnly" class="d-flex justify-end ga-2 mt-2">
                      <v-btn size="small" variant="tonal" icon aria-label="Editar" @click.stop="openEdit(p)">
                        <v-icon>mdi-pencil</v-icon>
                      </v-btn>

                      <v-btn
                        size="small"
                        variant="tonal"
                        icon
                        aria-label="Duplicar"
                        :loading="cloningPlayId === p.id"
                        :disabled="cloningPlayId === p.id"
                        @click.stop="requestClonePlay(p)"
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>

                      <v-btn size="small" color="error" variant="tonal" icon aria-label="Remover" @click.stop="requestRemovePlay(p)">
                        <v-icon>mdi-trash-can-outline</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>

              <v-card-text>
                <div class="d-flex align-center justify-space-between ga-2">
                  <div class="text-subtitle-1 font-weight-bold text-truncate">{{ p.name }}</div>
                  <div class="d-flex align-center ga-2">
                    <v-chip v-if="p.category" size="small" variant="tonal" :color="categoryColor(p.category)">
                      {{ p.category }}
                    </v-chip>
                    <v-chip size="small" variant="tonal" :color="playTypeColor(p.play_type)">
                      {{ playTypeLabel(p.play_type) }}
                    </v-chip>
                  </div>
                </div>
                <div v-if="p.description" class="text-body-2 text-medium-emphasis mt-1 line-clamp-3">
                  {{ p.description }}
                </div>
                <div v-else class="text-body-2 text-medium-emphasis mt-1 font-italic">
                  Sem descrição
                </div>

                <div v-if="p.tags.length" class="d-flex flex-wrap ga-2 mt-3">
                  <v-chip
                    v-for="(t, idx) in p.tags.slice(0, 4)"
                    :key="`${p.id}-tag-${idx}`"
                    size="x-small"
                    variant="tonal"
                  >
                    {{ t }}
                  </v-chip>
                </div>
              </v-card-text>
            </v-card>
          </v-hover>
        </v-col>
      </v-row>
    </div>

    <v-dialog v-if="!readOnly" v-model="designerOpen" max-width="1200" scrollable>
      <v-card rounded="xl" class="designer-card">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="text-h6 font-weight-bold">
            {{ editingPlay ? 'Editar Jogada' : 'Nova Jogada' }}
          </div>
          <v-btn icon variant="text" @click="closeDesigner">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider />

        <v-card-text>
          <v-alert v-if="formError" type="error" variant="tonal" class="mb-4">
            {{ formError }}
          </v-alert>

          <v-row density="comfortable">
            <v-col cols="12" lg="8">
              <FieldCanvas
                :players="players"
                :routes="routes"
                :selected-player-id="selectedPlayerId"
                :mode="mode"
                :route-color="routeColor"
                :route-type="routeType"
                :drawing-route="drawingRoute"
                @playerMove="onPlayerMove"
                @playerSelect="selectedPlayerId = $event"
                @routeAdd="onRouteAdd"
                @routeErase="onRouteErase"
                @update:drawingRoute="drawingRoute = $event"
              />

              <v-card variant="tonal" rounded="xl" class="mt-4">
                <v-card-text class="text-body-2 text-medium-emphasis">
                  <div><b>Mover:</b> arraste os jogadores.</div>
                  <div><b>Rota:</b> clique para pontos e duplo-clique para finalizar.</div>
                  <div><b>Apagar:</b> clique próximo a uma rota para remover.</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" lg="4">
              <PlayToolbar
                :mode="mode"
                :route-color="routeColor"
                :route-type="routeType"
                :drawing="Boolean(drawingRoute)"
                :saving="saving"
                @update:mode="mode = $event"
                @update:routeColor="routeColor = $event"
                @update:routeType="routeType = $event"
                @finishRoute="finishRoute"
                @cancelRoute="cancelRoute"
                @clearRoutes="routes = []"
                @save="openMetaDialog"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="viewerOpen" max-width="1200" scrollable>
      <v-card rounded="xl" class="designer-card">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="text-h6 font-weight-bold">{{ viewingPlay?.name || 'Jogada' }}</div>
          <v-btn icon variant="text" @click="closeView">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-row density="comfortable">
            <v-col cols="12" lg="8">
              <FieldCanvas
                :players="viewerPlayers"
                :routes="viewerRoutes"
                :selected-player-id="null"
                mode="move"
                route-color="warning"
                route-type="route"
                :drawing-route="null"
                :read-only="true"
              />
            </v-col>
            <v-col cols="12" lg="4">
              <v-card variant="tonal" rounded="xl">
                <v-card-text>
                  <div class="d-flex flex-wrap ga-2">
                    <v-chip v-if="viewingPlay?.category" size="small" variant="tonal" :color="categoryColor(viewingPlay.category)">
                      {{ viewingPlay.category }}
                    </v-chip>
                    <v-chip v-if="viewingPlay?.play_type" size="small" variant="tonal" :color="playTypeColor(viewingPlay.play_type)">
                      {{ playTypeLabel(viewingPlay.play_type) }}
                    </v-chip>
                    <v-chip v-if="viewingPlay?.formation" size="small" variant="tonal">
                      {{ viewingPlay.formation }}
                    </v-chip>
                  </div>

                  <div v-if="(viewingPlay?.tags ?? []).length" class="d-flex flex-wrap ga-2 mt-3">
                    <v-chip
                      v-for="(t, idx) in (viewingPlay?.tags ?? []).slice(0, 10)"
                      :key="`view-tag-${idx}`"
                      size="x-small"
                      variant="tonal"
                    >
                      {{ t }}
                    </v-chip>
                  </div>

                  <div class="text-body-2 text-medium-emphasis mt-3" v-if="viewingPlay?.description">
                    {{ viewingPlay.description }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis mt-3 font-italic" v-else>
                    Sem descrição
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-if="!readOnly" v-model="metaOpen" max-width="640">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-bold">Salvar jogada</v-card-title>
        <v-divider />
        <v-card-text>
          <v-row density="comfortable">
            <v-col cols="12" md="6">
              <v-text-field v-model="meta.name" label="Nome da jogada" variant="outlined" :disabled="saving" required />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="meta.category"
                :items="categoryItems"
                label="Lado (Ataque/Defesa)"
                variant="outlined"
                clearable
                :disabled="saving"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-combobox
                v-model="meta.play_type"
                :items="playTypeItems"
                label="Tipo (pode cadastrar na hora)"
                variant="outlined"
                :disabled="saving"
                clearable
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-combobox
                v-model="meta.formation"
                :items="formationItems"
                label="Formação (pode cadastrar na hora)"
                variant="outlined"
                :disabled="saving"
                clearable
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="meta.tagsText"
                label="Tags (vírgula)"
                variant="outlined"
                :disabled="saving"
                placeholder="red zone, 3rd down"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea v-model="meta.description" label="Descrição" variant="outlined" :disabled="saving" rows="4" auto-grow />
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-btn class="flex-grow-1" variant="tonal" rounded="xl" :disabled="saving" @click="metaOpen = false">Cancelar</v-btn>
          <v-btn class="flex-grow-1" color="primary" variant="flat" rounded="xl" :loading="saving" :disabled="!meta.name.trim()" @click="submit">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="!readOnly" v-model="confirmRemovePlayOpen" max-width="520">
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">Remover jogada?</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          Tem certeza que deseja remover a jogada
          <span class="font-weight-medium">"{{ playToRemove?.name }}"</span>?
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-btn
            class="flex-grow-1"
            variant="tonal"
            rounded="xl"
            :disabled="removingPlay"
            @click="confirmRemovePlayOpen = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            class="flex-grow-1"
            color="error"
            variant="flat"
            rounded="xl"
            :loading="removingPlay"
            :disabled="!playToRemove"
            @click="confirmRemovePlay"
          >
            <v-icon start>mdi-trash-can-outline</v-icon>
            Remover
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-if="!readOnly" v-model="confirmCloneOpen" max-width="520">
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">Duplicar jogada?</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          Quer criar uma cópia da jogada
          <span class="font-weight-medium">"{{ playToClone?.name }}"</span>?
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-btn
            class="flex-grow-1"
            variant="tonal"
            rounded="xl"
            :disabled="Boolean(cloningPlayId)"
            @click="confirmCloneOpen = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            class="flex-grow-1"
            color="primary"
            variant="flat"
            rounded="xl"
            :loading="Boolean(cloningPlayId)"
            :disabled="!playToClone"
            @click="confirmClone"
          >
            <v-icon start>mdi-content-copy</v-icon>
            Duplicar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { http } from '../../api/http'
import { useProgressCircular } from '../../composables/useProgressCircular'
import FieldCanvas from '../../components/playbook/FieldCanvas.vue'
import PlayToolbar from '../../components/playbook/PlayToolbar.vue'

const props = withDefaults(defineProps<{ readOnly?: boolean }>(), {
  readOnly: false,
})

const readOnly = computed(() => props.readOnly)

type Play = {
  id: number
  name: string
  description: string | null
  formation: string
  play_type: string
  tags: string[]
  players: Array<{ id: string; x: number; y: number; role?: string; team?: string; label?: string }>
  routes: Array<{ player_id: string; points: Array<{ x: number; y: number }>; type?: string; color?: string }>
  category?: string | null
  image_url?: string | null
}

const plays = ref<Play[]>([])
const loading = ref(false)
const { progressValue } = useProgressCircular(loading)
const error = ref<string | null>(null)

const designerOpen = ref(false)
const editingPlay = ref<Play | null>(null)
const saving = ref(false)
const formError = ref<string | null>(null)

const viewerOpen = ref(false)
const viewingPlay = ref<Play | null>(null)
const viewerPlayers = ref<Player[]>([])
const viewerRoutes = ref<Route[]>([])

const confirmRemovePlayOpen = ref(false)
const playToRemove = ref<Play | null>(null)
const removingPlay = ref(false)

const cloningPlayId = ref<number | null>(null)
const confirmCloneOpen = ref(false)
const playToClone = ref<Play | null>(null)

const downloadingAllPdf = ref(false)
const downloadingPdfId = ref<number | null>(null)

type Player = { id: string; x: number; y: number; role?: string; team?: string; label?: string }
type Route = { player_id: string; points: Array<{ x: number; y: number }>; type?: string; color?: string }

const DEFAULT_PLAYERS: Player[] = [
  { id: 'qb', x: 250, y: 400, role: 'QB', team: 'offense', label: 'QB' },
  { id: 'c', x: 250, y: 440, role: 'C', team: 'offense', label: 'C' },
  { id: 'wr1', x: 80, y: 400, role: 'WR', team: 'offense', label: 'W1' },
  { id: 'wr2', x: 420, y: 400, role: 'WR', team: 'offense', label: 'W2' },
  { id: 'rb', x: 250, y: 470, role: 'RB', team: 'offense', label: 'RB' },
  { id: 'db1', x: 80, y: 350, role: 'DB', team: 'defense', label: 'D1' },
  { id: 'db2', x: 420, y: 350, role: 'DB', team: 'defense', label: 'D2' },
  { id: 'lb', x: 250, y: 360, role: 'LB', team: 'defense', label: 'LB' },
  { id: 's1', x: 160, y: 300, role: 'S', team: 'defense', label: 'S1' },
  { id: 's2', x: 340, y: 300, role: 'S', team: 'defense', label: 'S2' },
]

const players = ref<Player[]>([])
const routes = ref<Route[]>([])
const selectedPlayerId = ref<string | null>(null)
const mode = ref<'move' | 'route' | 'erase'>('move')
const routeColor = ref<string>('warning')
const routeType = ref<string>('route')
const drawingRoute = ref<Route | null>(null)

const metaOpen = ref(false)
const meta = ref({
  name: '',
  description: '',
  category: '' as string | '',
  formation: 'shotgun',
  play_type: 'pass',
  tagsText: '',
})

const categoryItems = ['Ataque', 'Defesa']

const formationItems = computed(() => {
  const base = ['shotgun', 'pistol', 'i_formation', 'trips_right', 'trips_left', 'spread']
  const fromPlays = plays.value.map((p) => String(p.formation || '').trim()).filter(Boolean)
  return Array.from(new Set([...base, ...fromPlays]))
})

const playTypeItems = computed(() => {
  const base = ['pass', 'run', 'trick']
  const fromPlays = plays.value.map((p) => String(p.play_type || '').trim()).filter(Boolean)
  return Array.from(new Set([...base, ...fromPlays]))
})

function playTypeLabel(t: string): string {
  const v = String(t || '').trim().toLowerCase()
  if (v === 'pass') return 'Passe'
  if (v === 'run') return 'Corrida'
  if (v === 'trick') return 'Trick'
  return String(t || '').trim() || 'Passe'
}

function playTypeColor(t: string): string {
  const v = String(t || '').trim().toLowerCase()
  if (v === 'run') return 'success'
  if (v === 'trick') return 'secondary'
  return 'info'
}

function categoryColor(category: string): string {
  if (category === 'Ataque') return 'error'
  if (category === 'Defesa') return 'info'
  return 'primary'
}

function routeStroke(r: any): string {
  const c = String(r?.color ?? 'warning')
  if (c.startsWith('#') || c.startsWith('rgb')) return c
  if (c === 'white') return 'rgb(255,255,255)'
  return `rgb(var(--v-theme-${c}))`
}

function routePointsAttr(r: any): string {
  const pts = Array.isArray(r?.points) ? r.points : []
  return pts.map((p: any) => `${Number(p.x) || 0},${Number(p.y) || 0}`).join(' ')
}

function routeArrowPointsAttr(r: any): string {
  const pts = Array.isArray(r?.points) ? r.points : []
  if (pts.length < 2) return ''
  const last = pts[pts.length - 1]
  const prev = pts[pts.length - 2]
  if (!last || !prev) return ''

  const x2 = Number(last.x) || 0
  const y2 = Number(last.y) || 0
  const x1 = Number(prev.x) || 0
  const y1 = Number(prev.y) || 0

  const angle = Math.atan2(y2 - y1, x2 - x1)
  const len = 16
  const spread = 0.55
  const ax1 = x2 - len * Math.cos(angle - spread)
  const ay1 = y2 - len * Math.sin(angle - spread)
  const ax2 = x2 - len * Math.cos(angle + spread)
  const ay2 = y2 - len * Math.sin(angle + spread)

  return `${x2},${y2} ${ax1},${ay1} ${ax2},${ay2}`
}

function playerLabel(pl: any): string {
  const label = String(pl?.label ?? '').trim()
  if (label) return label
  const role = String(pl?.role ?? '').trim()
  if (role) return role.slice(0, 2).toUpperCase()
  return String(pl?.id ?? '?').slice(0, 2).toUpperCase()
}

async function fetchPlays() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/playbook/plays/?ordering=-created_at')
    const items = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : []
    plays.value = items.map((p: any) => ({
      ...p,
      tags: Array.isArray(p?.tags) ? p.tags : [],
      players: Array.isArray(p?.players) ? p.players : [],
      routes: Array.isArray(p?.routes) ? p.routes : [],
      formation: typeof p?.formation === 'string' ? p.formation : 'shotgun',
      play_type: typeof p?.play_type === 'string' ? p.play_type : 'pass',
    }))
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao carregar Playbook (HTTP ${status}).` : 'Falha ao carregar Playbook.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  if (readOnly.value) return
  editingPlay.value = null
  players.value = DEFAULT_PLAYERS.map((p) => ({ ...p }))
  routes.value = []
  selectedPlayerId.value = null
  mode.value = 'move'
  routeColor.value = 'warning'
  routeType.value = 'route'
  drawingRoute.value = null
  meta.value = { name: '', description: '', category: '', formation: 'shotgun', play_type: 'pass', tagsText: '' }
  formError.value = null
  designerOpen.value = true
}

function openEdit(p: Play) {
  if (readOnly.value) return
  editingPlay.value = p
  players.value = Array.isArray(p.players) && p.players.length ? p.players.map((x) => ({ ...x })) : DEFAULT_PLAYERS.map((x) => ({ ...x }))
  routes.value = Array.isArray(p.routes) ? p.routes.map((x) => ({ ...x })) : []
  selectedPlayerId.value = null
  mode.value = 'move'
  routeColor.value = 'warning'
  routeType.value = 'route'
  drawingRoute.value = null
  meta.value = {
    name: p.name ?? '',
    description: p.description ?? '',
    category: (p.category ?? '') as any,
    formation: typeof p.formation === 'string' ? p.formation : 'shotgun',
    play_type: typeof p.play_type === 'string' ? p.play_type : 'pass',
    tagsText: Array.isArray(p.tags) ? p.tags.join(', ') : '',
  }
  formError.value = null
  designerOpen.value = true
}

function closeDesigner() {
  designerOpen.value = false
  editingPlay.value = null
  metaOpen.value = false
  drawingRoute.value = null
}

function openMetaDialog() {
  if (readOnly.value) return
  metaOpen.value = true
}

function openView(p: Play) {
  viewingPlay.value = p
  viewerPlayers.value = Array.isArray(p.players) ? p.players.map((x) => ({ ...x })) : []
  viewerRoutes.value = Array.isArray(p.routes) ? p.routes.map((x) => ({ ...x })) : []
  viewerOpen.value = true
}

function closeView() {
  viewerOpen.value = false
  viewingPlay.value = null
  viewerPlayers.value = []
  viewerRoutes.value = []
}

function onPlayerMove(id: string, x: number, y: number) {
  players.value = players.value.map((p) => (p.id === id ? { ...p, x, y } : p))
}

function onRouteAdd(r: Route) {
  routes.value = [...routes.value, r]
  drawingRoute.value = null
}

function onRouteErase(index: number) {
  routes.value = routes.value.filter((_, i) => i !== index)
}

function cancelRoute() {
  drawingRoute.value = null
}

function finishRoute() {
  if (!drawingRoute.value) return
  if ((drawingRoute.value.points ?? []).length < 2) return
  routes.value = [...routes.value, drawingRoute.value]
  drawingRoute.value = null
}

async function submit() {
  if (readOnly.value) return
  if (!meta.value.name?.trim()) return

  saving.value = true
  formError.value = null

  try {
    const tags = meta.value.tagsText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)

    const payload = {
      name: meta.value.name.trim(),
      description: meta.value.description?.trim() ? meta.value.description.trim() : '',
      category: meta.value.category ? String(meta.value.category) : null,
      formation: String((meta.value as any).formation ?? '').trim() || 'shotgun',
      play_type: String((meta.value as any).play_type ?? '').trim() || 'pass',
      tags,
      players: players.value,
      routes: routes.value,
    }

    if (editingPlay.value?.id) {
      await http.patch(`/playbook/plays/${editingPlay.value.id}/`, payload)
    } else {
      await http.post('/playbook/plays/', payload)
    }

    await fetchPlays()
    metaOpen.value = false
    closeDesigner()
  } catch (e: any) {
    const status = e?.response?.status
    formError.value = status ? `Falha ao salvar (HTTP ${status}).` : 'Falha ao salvar.'
  } finally {
    saving.value = false
  }
}

async function removePlay(p: Play) {
  if (readOnly.value) return
  try {
    await http.delete(`/playbook/plays/${p.id}/`)
    await fetchPlays()
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao remover (HTTP ${status}).` : 'Falha ao remover.'
  }
}

function requestRemovePlay(p: Play) {
  if (readOnly.value) return
  if (removingPlay.value) return
  playToRemove.value = p
  confirmRemovePlayOpen.value = true
}

async function confirmRemovePlay() {
  if (readOnly.value) return
  const p = playToRemove.value
  if (!p?.id) return

  removingPlay.value = true
  try {
    await removePlay(p)
    confirmRemovePlayOpen.value = false
    playToRemove.value = null
  } finally {
    removingPlay.value = false
  }
}

async function clonePlay(p: Play) {
  if (readOnly.value) return
  if (cloningPlayId.value) return

  cloningPlayId.value = p.id
  try {
    await http.post(`/playbook/plays/${p.id}/clone/`, {})
    await fetchPlays()
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao duplicar jogada (HTTP ${status}).` : 'Falha ao duplicar jogada.'
  } finally {
    cloningPlayId.value = null
  }
}

function requestClonePlay(p: Play) {
  if (readOnly.value) return
  if (cloningPlayId.value) return
  playToClone.value = p
  confirmCloneOpen.value = true
}

async function confirmClone() {
  const p = playToClone.value
  if (!p) return
  await clonePlay(p)
  confirmCloneOpen.value = false
  playToClone.value = null
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function safeFilename(name: string): string {
  const base = (name || '').trim() || 'playbook'
  return base.replace(/[\\/:*?"<>|]+/g, '-').slice(0, 80)
}

async function downloadPdfAll() {
  if (downloadingAllPdf.value) return
  downloadingAllPdf.value = true
  try {
    const res = await http.get('/playbook/plays/export/pdf/', { responseType: 'blob' })
    downloadBlob(res.data as Blob, 'playbook.pdf')
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao gerar PDF (HTTP ${status}).` : 'Falha ao gerar PDF.'
  } finally {
    downloadingAllPdf.value = false
  }
}

async function downloadPdfOne(p: Play) {
  if (downloadingPdfId.value) return
  downloadingPdfId.value = p.id
  try {
    const res = await http.get(`/playbook/plays/${p.id}/export/pdf/`, { responseType: 'blob' })
    downloadBlob(res.data as Blob, `${safeFilename(p.name)}.pdf`)
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao gerar PDF (HTTP ${status}).` : 'Falha ao gerar PDF.'
  } finally {
    downloadingPdfId.value = null
  }
}

onMounted(fetchPlays)
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

.play-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.play-preview {
  position: relative;
  overflow: hidden;
  height: 208px;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.play-preview__svg {
  width: 100%;
  height: 100%;
  display: block;
}

.play-preview__field {
  fill: rgba(var(--v-theme-success), 0.22);
}

.play-preview__lines line {
  stroke: rgba(255, 255, 255, 0.18);
  stroke-width: 4;
}

.play-preview__label {
  fill: rgba(255, 255, 255, 0.95);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.play-actions {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 12px;
  opacity: 0;
  transition: opacity 160ms ease;
  background: rgba(0, 0, 0, 0.45);
}

.play-actions__panel {
  padding: 10px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.30);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
}

.play-actions--show {
  opacity: 1;
}

.play-badge {
  position: absolute;
  top: 12px;
  left: 12px;
}

.designer-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.line-clamp-3 {
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
