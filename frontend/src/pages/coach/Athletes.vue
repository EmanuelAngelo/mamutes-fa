<template>
  <v-container>
    <v-sheet class="athletes-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="athletes-header__icon">
            <v-icon size="26">mdi-trophy</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Gestão de Atletas</div>
          </div>
        </div>

        <v-btn color="primary" variant="flat" rounded="xl" @click="openNew">
          <v-icon start>mdi-plus</v-icon>
          Novo Atleta
        </v-btn>
      </div>
    </v-sheet>

    <v-row density="comfortable" class="mt-4">
      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--info">
              <v-icon>mdi-account-group</v-icon>
            </div>
            <div>
              <div class="text-body-2 text-medium-emphasis">Total de Atletas</div>
              <div class="text-h5 font-weight-bold">{{ statsTotal }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--success">
              <v-icon>mdi-trending-up</v-icon>
            </div>
            <div>
              <div class="text-body-2 text-medium-emphasis">Média Geral</div>
              <div class="text-h5 font-weight-bold">{{ statsAvgRating }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--warning">
              <v-icon>mdi-trophy</v-icon>
            </div>
            <div class="flex-grow-1">
              <div class="text-body-2 text-medium-emphasis">Melhor Desempenho</div>
              <div class="text-subtitle-1 font-weight-bold text-truncate">
                {{ statsTopPerformerName }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row density="comfortable" class="mt-2">
      <v-col cols="12" sm="8">
        <v-text-field
          v-model="search"
          label="Buscar atleta..."
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-magnify"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="positionFilter"
          :items="positionFilterItems"
          item-title="label"
          item-value="value"
          label="Posição"
          variant="outlined"
          prepend-inner-icon="mdi-filter"
        />
      </v-col>
    </v-row>

    <v-row density="comfortable" class="mt-2">
      <template v-if="loadingAthletes">
        <v-col v-for="i in 8" :key="i" cols="12" sm="6" md="4" lg="3">
          <v-skeleton-loader type="card" class="rounded-xl" />
        </v-col>
      </template>

      <template v-else-if="filteredAthletes.length">
        <v-col
          v-for="(a, index) in filteredAthletes"
          :key="a.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <div class="athlete-fc" :style="[fcCardVars(a), { '--delay': `${index * 50}ms` }]">
            <div class="athlete-fc__glow" />

            <div
              class="athlete-fc__card"
              :class="{ 'is-flipped': isAthleteCardFlipped(a.id) }"
              role="button"
              tabindex="0"
              @click="toggleAthleteCardFlip(a.id)"
              @keydown.enter.prevent="toggleAthleteCardFlip(a.id)"
              @keydown.space.prevent="toggleAthleteCardFlip(a.id)"
            >
              <div class="athlete-fc__inner">
                <div class="athlete-fc__face athlete-fc__face--front">
                <svg
                  class="athlete-fc__pattern"
                  viewBox="0 0 220 310"
                  preserveAspectRatio="xMidYMid slice"
                  aria-hidden="true"
                >
                  <polygon
                    points="110,30 190,80 190,180 110,230 30,180 30,80"
                    fill="none"
                    stroke="rgba(255,255,255,0.6)"
                    stroke-width="1.5"
                  />
                  <polygon
                    points="110,55 165,90 165,170 110,205 55,170 55,90"
                    fill="none"
                    stroke="rgba(255,255,255,0.5)"
                    stroke-width="1"
                  />
                  <polygon
                    points="110,75 145,105 145,155 110,185 75,155 75,105"
                    fill="none"
                    stroke="rgba(255,255,255,0.35)"
                    stroke-width="0.8"
                  />
                  <line x1="0" y1="0" x2="220" y2="155" stroke="rgba(255,255,255,0.15)" stroke-width="40" />
                  <line x1="0" y1="93" x2="132" y2="0" stroke="rgba(255,255,255,0.10)" stroke-width="20" />
                </svg>

                <div class="athlete-fc__shine" />

                <div class="athlete-fc__ovr">
                  <div class="athlete-fc__ovr-num">{{ fcOvr(a) }}</div>
                  <div class="athlete-fc__ovr-pos">{{ fcPosShort(a) }}</div>
                  <div class="athlete-fc__ovr-badge">
                    <span
                      v-if="a.jersey_number !== null && a.jersey_number !== undefined && a.jersey_number !== ''"
                      class="athlete-fc__ovr-jersey"
                    >
                      {{ jerseyText(a) }}
                    </span>
                    <span v-else class="athlete-fc__ovr-dot" />
                  </div>
                </div>

                <div class="athlete-fc__photo">
                  <img
                    v-if="athletePhotoUrl(a)"
                    :src="athletePhotoUrl(a)"
                    :alt="a.name"
                    class="athlete-fc__img"
                    loading="lazy"
                  />
                  <div v-else class="athlete-fc__img-empty">
                    <v-icon size="80" class="opacity-35">mdi-account</v-icon>
                  </div>
                </div>

                <div class="athlete-fc__footer">
                  <div class="athlete-fc__divider" />

                  <div class="athlete-fc__name-wrap">
                    <div class="athlete-fc__name" :title="a.name">{{ a.name }}</div>
                  </div>

                  <div class="athlete-fc__attrs">
                    <div v-for="(lbl, i) in FC_ATTRS" :key="lbl" class="athlete-fc__attr">
                      <div class="athlete-fc__attr-val">{{ fcAttrs(a)[i] }}</div>
                      <div class="athlete-fc__attr-lbl">{{ lbl }}</div>
                    </div>
                  </div>

                  <div class="athlete-fc__meta">
                    <span class="athlete-fc__dot" :class="statusDotClass(a)" />
                    <span class="athlete-fc__meta-text">
                      {{ a.is_active ? 'Ativo' : 'Inativo' }}
                      <template v-if="a.jersey_number !== null && a.jersey_number !== undefined && a.jersey_number !== ''">
                        · #{{ jerseyText(a) }}
                      </template>
                    </span>
                  </div>
                </div>
                </div>

                <div class="athlete-fc__face athlete-fc__face--back" aria-hidden="true">
                  <div class="athlete-fc__back">
                    <div class="athlete-fc__back-top">
                      <div class="athlete-fc__back-name" :title="a.name">{{ a.name }}</div>
                      <div class="athlete-fc__back-sub">
                        {{ a.current_position || '-' }}
                        <template v-if="a.jersey_number !== null && a.jersey_number !== undefined && a.jersey_number !== ''">
                          · #{{ jerseyText(a) }}
                        </template>
                      </div>
                      <div class="athlete-fc__back-sub2">
                        OVR: {{ fcOvr(a) }}
                        · Nota: {{ ratingBackText(a) }}
                      </div>
                    </div>

                    <div class="athlete-fc__back-grid">
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Nascimento</div>
                        <div class="athlete-fc__back-v">{{ a.birth_date ? formatDateBR(a.birth_date) : '-' }}</div>
                      </div>
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Cidade</div>
                        <div class="athlete-fc__back-v">{{ a.birth_city || '-' }}</div>
                      </div>
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Altura</div>
                        <div class="athlete-fc__back-v">{{ a.height_m ? `${a.height_m} m` : '-' }}</div>
                      </div>
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Peso</div>
                        <div class="athlete-fc__back-v">{{ a.weight_kg ? `${a.weight_kg} kg` : '-' }}</div>
                      </div>
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Desejada</div>
                        <div class="athlete-fc__back-v">{{ a.desired_position || '-' }}</div>
                      </div>
                      <div class="athlete-fc__back-item">
                        <div class="athlete-fc__back-k">Status</div>
                        <div class="athlete-fc__back-v">{{ a.is_active ? 'Ativo' : 'Inativo' }}</div>
                      </div>
                    </div>

                    <!-- <div class="athlete-fc__back-notes">
                      <div class="athlete-fc__back-k">Observações</div>
                      <div class="athlete-fc__back-notes-v">{{ String(a.career_notes || '').trim() || '-' }}</div>
                    </div> -->

                    <div class="athlete-fc__back-hint">Toque para voltar</div>
                  </div>
                </div>
              </div>

              <div v-if="isAthleteCardTearing(a.id)" class="athlete-fc__tear" aria-hidden="true">
                <div class="athlete-fc__tear-half athlete-fc__tear-half--left" />
                <div class="athlete-fc__tear-half athlete-fc__tear-half--right" />
              </div>
            </div>

            <div class="athlete-fc__actions">
              <v-btn size="small" variant="tonal" class="flex-grow-1" @click.stop="onEditAthlete(a)">
                <v-icon start size="16">mdi-pencil</v-icon>
                Editar
              </v-btn>
              <v-btn size="small" variant="tonal" color="error" @click.stop="askRemove(a)">
                <v-icon size="16">mdi-trash-can</v-icon>
              </v-btn>
            </div>
          </div>
        </v-col>
      </template>

      <v-col v-else cols="12">
        <div class="text-center py-10">
          <div class="empty-state__icon mb-4">
            <v-icon size="40" class="opacity-60">mdi-account-group</v-icon>
          </div>
          <div class="text-h6 font-weight-bold">
            {{ search || positionFilter !== 'all' ? 'Nenhum atleta encontrado' : 'Nenhum atleta cadastrado' }}
          </div>
          <div class="text-body-2 text-medium-emphasis mt-1 mb-4">
            {{
              search || positionFilter !== 'all'
                ? 'Tente ajustar os filtros de busca'
                : 'Comece adicionando seu primeiro atleta ao time'
            }}
          </div>
          <v-btn v-if="!search && positionFilter === 'all'" color="primary" variant="tonal" @click="openNew">
            <v-icon start>mdi-plus</v-icon>
            Adicionar Atleta
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-dialog
      v-model="dialog"
      class="athlete-form-dialog"
      max-width="560"
      transition="scale-transition"
      scrollable
    >
      <v-card class="athlete-form-card" rounded="xl">
        <div class="athlete-form__header">
          <div class="text-h6 font-weight-bold">
            {{ editing ? 'Editar Atleta' : 'Novo Atleta' }}
          </div>
          <v-btn
            icon
            variant="text"
            :disabled="saving"
            class="athlete-form__close"
            @click="dialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text class="athlete-form__body">
          <form @submit.prevent="save">
            <div class="athlete-form__photo">
              <button
                type="button"
                class="athlete-form__photo-btn"
                :disabled="saving"
                @click="pickPhoto"
              >
                <div class="athlete-form__photo-ring">
                  <v-avatar size="96" class="athlete-form__photo-avatar">
                    <v-img v-if="photoPreviewUrl" :src="photoPreviewUrl" cover />
                    <div v-else class="athlete-form__photo-empty">
                      <v-icon size="44" class="opacity-60">mdi-account</v-icon>
                    </div>
                  </v-avatar>
                </div>

                <div class="athlete-form__photo-overlay" :class="{ 'is-visible': saving }">
                  <v-progress-circular
                    v-if="saving && hasNewPhoto"
                    :model-value="progressValue"
                    :rotate="360"
                    size="26"
                    width="3"
                    color="primary"
                  />
                  <v-icon v-else size="26">mdi-upload</v-icon>
                </div>
              </button>

              <input
                ref="photoInput"
                class="athlete-form__photo-input"
                type="file"
                accept="image/*"
                :disabled="saving"
                @change="onPhotoPicked"
              />
            </div>

            <v-text-field
              v-model="form.name"
              label="Nome do Atleta"
              variant="outlined"
              density="comfortable"
              class="mt-2"
            />

            <v-row density="comfortable">
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="form.jersey_number"
                  label="Número"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.current_position"
                  :items="positionItems"
                  item-title="label"
                  item-value="value"
                  label="Posição"
                  variant="outlined"
                  density="comfortable"
                  clearable
                />
              </v-col>
            </v-row>

            <v-row density="comfortable">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.is_active"
                  :items="statusItems"
                  item-title="label"
                  item-value="value"
                  label="Status"
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.desired_position"
                  :items="positionItems"
                  item-title="label"
                  item-value="value"
                  label="Posição Desejada"
                  variant="outlined"
                  density="comfortable"
                  clearable
                />
              </v-col>
            </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-menu v-model="birthDateMenu" :close-on-content-click="false" location="bottom">
                <template #activator="{ props }">
                  <v-text-field
                    v-bind="props"
                    :model-value="formatDateBR(form.birth_date)"
                    label="Data de nascimento"
                    readonly
                    clearable
                    prepend-inner-icon="mdi-calendar"
                    variant="outlined"
                    density="comfortable"
                    @click:clear="clearBirthDate"
                  />
                </template>
                <v-date-picker :model-value="form.birth_date" @update:model-value="onPickBirthDate" />
              </v-menu>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.birth_city"
                label="Cidade de nascimento"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="form.height_m"
                label="Altura (m)"
                type="number"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model.number="form.weight_kg"
                label="Peso (kg)"
                type="number"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

            <template v-if="!editing">
              <v-text-field
                :model-value="createdUserLabel"
                label="Usuário (opcional)"
                variant="outlined"
                density="comfortable"
                readonly
              />

              <v-btn
                variant="tonal"
                size="small"
                class="mb-4"
                :disabled="saving"
                @click="openCreateUser"
              >
                Criar usuário
              </v-btn>
            </template>

            <v-textarea
              v-model="form.career_notes"
              label="Observações"
              variant="outlined"
              density="comfortable"
            />

            <div class="athlete-form__actions">
              <v-btn
                variant="outlined"
                rounded="lg"
                class="flex-grow-1"
                :disabled="saving"
                @click="dialog = false"
              >
                Cancelar
              </v-btn>
              <v-btn
                type="submit"
                color="primary"
                variant="flat"
                rounded="lg"
                class="flex-grow-1"
                :loading="saving"
              >
                {{ editing ? 'Salvar' : 'Adicionar' }}
              </v-btn>
            </div>
          </form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog
      v-if="!editing"
      v-model="createUserDialog"
      :fullscreen="display.smAndDown.value"
      max-width="560"
      scrollable
    >
      <v-card>
        <v-card-title>Novo usuário</v-card-title>
        <v-card-text>
          <v-alert v-if="createUserError" type="error" variant="tonal" class="mb-3">{{ createUserError }}</v-alert>

          <v-text-field v-model="createUserForm.username" label="Username" />
          <v-text-field v-model="createUserForm.email" label="Email (opcional)" />
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="createUserForm.first_name" label="Nome (opcional)" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="createUserForm.last_name" label="Sobrenome (opcional)" />
            </v-col>
          </v-row>
          <v-text-field v-model="createUserForm.password" label="Senha" type="password" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" :disabled="createUserLoading" @click="createUserDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="createUserLoading" @click="createUser">Criar e vincular</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="520">
      <v-card>
        <v-card-title>Remover Atleta</v-card-title>
        <v-card-text>
          Tem certeza que deseja remover
          <strong>{{ deleteTarget?.name }}</strong>
          do time? Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" :disabled="deleting" @click="closeDelete">Cancelar</v-btn>
          <v-btn color="error" variant="tonal" :loading="deleting" @click="confirmRemove">Remover</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'
import { useProgressCircular } from '../../composables/useProgressCircular'

const athletes = ref<any[]>([])
const loadingAthletes = ref(false)

const flippedAthleteId = ref<number | null>(null)
const tearingAthleteId = ref<number | null>(null)

function isAthleteCardFlipped(id: number): boolean {
  return flippedAthleteId.value === id
}

function toggleAthleteCardFlip(id: number) {
  if (tearingAthleteId.value === id) return
  flippedAthleteId.value = flippedAthleteId.value === id ? null : id
}

function isAthleteCardTearing(id: number): boolean {
  return tearingAthleteId.value === id
}

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches)
}

async function onEditAthlete(a: any) {
  if (!a?.id) return
  if (tearingAthleteId.value) return

  // If user prefers reduced motion, skip the animation.
  if (prefersReducedMotion()) {
    edit(a)
    return
  }

  flippedAthleteId.value = null
  tearingAthleteId.value = Number(a.id)
  // Match CSS animation duration.
  await new Promise((r) => window.setTimeout(r, 420))
  tearingAthleteId.value = null
  edit(a)
}

const loadingStats = ref(false)
const stats = ref<{ total: number; avg_rating: number; top_performer: { id: number; name: string; rating: number } | null }>({
  total: 0,
  avg_rating: 0,
  top_performer: null,
})
type UserItem = {
  id: number
  username: string
  email?: string | null
  first_name?: string | null
  last_name?: string | null
  role?: string
  athlete_id?: number | null
  label: string
}

const createdUser = ref<UserItem | null>(null)
const createdUserLabel = computed(() => createdUser.value?.label ?? '')

const saving = ref(false)

const search = ref('')
const positionFilter = ref<'all' | string>('all')

const deleteDialog = ref(false)
const deleteTarget = ref<any | null>(null)
const deleting = ref(false)

const dialog = ref(false)
const editing = ref<any | null>(null)
const display = useDisplay()
const birthDateMenu = ref(false)

const createUserDialog = ref(false)
const createUserLoading = ref(false)
const createUserError = ref<string | null>(null)
const createUserForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
})

function jerseyText(a: any): string {
  const n = a?.jersey_number
  if (n === null || n === undefined || n === '') return '-'
  return String(n)
}

function ratingValue(a: any): number {
  const v = a?.rating
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) ? Math.max(0, Math.min(10, n)) : 0
}

function ratingClass(a: any): string {
  const r = ratingValue(a)
  if (r >= 8) return 'rating--good'
  if (r >= 6) return 'rating--ok'
  if (r >= 4) return 'rating--mid'
  return 'rating--bad'
}

function ratingLabel(r: number): string {
  if (r >= 9) return 'Excelente'
  if (r >= 7) return 'Muito bom'
  if (r >= 5) return 'Regular'
  if (r >= 3) return 'Fraco'
  return 'Crítico'
}

function ratingBackText(a: any): string {
  const r = ratingValue(a)
  if (!r) return '--'
  return `${r.toFixed(1)} · ${ratingLabel(r)}`
}

// Card estilo “OVR” (derivado da nota e posição)
// Atributos em siglas focadas em Futebol Americano:
// VEL (velocidade), PAS (passe/lançamento), REC (recepção), BLO (bloqueio), COB (cobertura/defesa no passe), FOR (força/físico)
const FC_ATTRS = ['VEL', 'PAS', 'REC', 'BLO', 'COB', 'FOR'] as const

function fcOvr(a: any): string {
  const r = ratingValue(a)
  const ovr = Math.round(r * 10)
  return ovr > 0 ? String(ovr) : '--'
}

function fcPosShort(a: any): string {
  const p = String(a?.current_position || '').trim()
  if (!p) return 'POS'
  return p.slice(0, 3).toUpperCase()
}

function deriveFcAttrs(rating: number, positionCode: string | null | undefined): number[] {
  const base = Math.round((rating || 5) * 9) // ~0-90
  const clamp = (o: number) => Math.min(99, Math.max(25, base + o))
  const pos = String(positionCode || '').toUpperCase()

  // PERFIS (QB/C/WR/RB/DB/R/S/CB)
  // Ordem: VEL, PAS, REC, BLO, COB, FOR
  if (pos === 'QB') return [clamp(-4), clamp(+20), clamp(-10), clamp(-14), clamp(-16), clamp(+8)]
  if (pos === 'C') return [clamp(-14), clamp(-18), clamp(-18), clamp(+22), clamp(+8), clamp(+18)]
  if (pos === 'WR') return [clamp(+20), clamp(-10), clamp(+18), clamp(-10), clamp(-10), clamp(+4)]
  if (pos === 'RB') return [clamp(+18), clamp(-6), clamp(+10), clamp(-6), clamp(-10), clamp(+10)]
  if (pos === 'DB') return [clamp(+14), clamp(-16), clamp(+8), clamp(-12), clamp(+20), clamp(+6)]
  if (pos === 'R') return [clamp(+10), clamp(-18), clamp(-14), clamp(+10), clamp(+12), clamp(+20)]
  if (pos === 'S') return [clamp(+12), clamp(-14), clamp(+6), clamp(-8), clamp(+18), clamp(+12)]
  if (pos === 'CB') return [clamp(+16), clamp(-16), clamp(+10), clamp(-12), clamp(+18), clamp(+6)]
  return [clamp(0), clamp(0), clamp(0), clamp(0), clamp(0), clamp(0)]
}

function fcAttrs(a: any): number[] {
  return deriveFcAttrs(ratingValue(a), a?.current_position)
}

function fcCardVars(a: any): Record<string, string> {
  const r = ratingValue(a)
  // Tema do card baseado na nota (sem hardcode de cores: usa tokens do Vuetify)
  // Faixas pedidas: 0–6 (cinza), 7 (vermelho), 8–9 (verde claro), 10 (dourado)
  const isTen = r >= 9.95

  if (isTen) {
    return {
      '--fc-g1': 'rgba(var(--v-theme-warning), 1)',
      '--fc-g2': 'rgba(var(--v-theme-warning), 0.78)',
      '--fc-g3': 'rgba(var(--v-theme-warning), 0.52)',
      '--fc-border': 'rgba(var(--v-theme-warning), 0.65)',
      '--fc-glow': 'rgba(var(--v-theme-warning), 0.55)',
    }
  }

  if (r >= 8) {
    return {
      '--fc-g1': 'rgba(var(--v-theme-success), 0.90)',
      '--fc-g2': 'rgba(var(--v-theme-success), 0.68)',
      '--fc-g3': 'rgba(var(--v-theme-success), 0.44)',
      '--fc-border': 'rgba(var(--v-theme-success), 0.55)',
      '--fc-glow': 'rgba(var(--v-theme-success), 0.45)',
    }
  }

  if (r >= 7) {
    return {
      '--fc-g1': 'rgba(var(--v-theme-error), 0.92)',
      '--fc-g2': 'rgba(var(--v-theme-error), 0.70)',
      '--fc-g3': 'rgba(var(--v-theme-error), 0.48)',
      '--fc-border': 'rgba(var(--v-theme-error), 0.58)',
      '--fc-glow': 'rgba(var(--v-theme-error), 0.48)',
    }
  }

  return {
    '--fc-g1': 'rgba(var(--v-theme-surface-variant), 1)',
    '--fc-g2': 'rgba(var(--v-theme-on-surface), 0.18)',
    '--fc-g3': 'rgba(var(--v-theme-on-surface), 0.10)',
    '--fc-border': 'rgba(var(--v-theme-on-surface), 0.20)',
    '--fc-glow': 'rgba(var(--v-theme-on-surface), 0.24)',
  }
}

function statusDotClass(a: any): string {
  return a?.is_active ? 'dot--active' : 'dot--inactive'
}

function apiOrigin(): string {
  const base = String(http.defaults.baseURL || '')
  if (!base) return ''
  return base.replace(/\/api\/?$/, '').replace(/\/+$/, '')
}

function athletePhotoUrl(a: any): string | undefined {
  const photo = a?.photo
  if (!photo || typeof photo !== 'string') return undefined
  if (photo.startsWith('http://') || photo.startsWith('https://')) return photo
  const origin = apiOrigin()
  if (!origin) return photo
  if (photo.startsWith('/')) return `${origin}${photo}`
  return `${origin}/${photo}`
}

function formatDateBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const m = /^\d{4}-\d{2}-\d{2}$/.exec(iso)
  if (!m) return iso
  const [y, mm, dd] = iso.split('-')
  return `${dd}/${mm}/${y}`
}

function clearBirthDate() {
  form.value.birth_date = ''
}

function normalizeDate(value: unknown): string {
  const v = Array.isArray(value) ? value[0] : value
  if (!v) return ''
  if (v instanceof Date) return v.toISOString().slice(0, 10)
  if (typeof v === 'string') return v.includes('T') ? v.slice(0, 10) : v
  return String(v)
}

function onPickBirthDate(value: unknown) {
  form.value.birth_date = normalizeDate(value)
  birthDateMenu.value = false
}

function emptyForm() {
  return {
    name: '',
    jersey_number: null,
    photo: null,
    birth_date: '',
    birth_city: '',
    height_m: null,
    weight_kg: null,
    current_position: null,
    desired_position: null,
    career_notes: '',
    is_active: true,
    user: null,
  }
}

const form = ref<any>(emptyForm())

const statusItems = [
  { label: 'Ativo', value: true },
  { label: 'Inativo', value: false },
]

const photoInput = ref<HTMLInputElement | null>(null)
const photoPreviewUrl = ref<string | null>(null)

function pickPhoto() {
  if (saving.value) return
  photoInput.value?.click()
}

function onPhotoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  form.value.photo = file
  input.value = ''
}

function updatePhotoPreview() {
  if (photoPreviewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(photoPreviewUrl.value)
    } catch {
      // ignore
    }
  }

  const f = form.value?.photo
  if (f instanceof File) {
    photoPreviewUrl.value = URL.createObjectURL(f)
    return
  }

  if (editing.value?.photo) {
    photoPreviewUrl.value = athletePhotoUrl(editing.value) || null
    return
  }

  photoPreviewUrl.value = null
}

const positionItems = [
  { label: 'QB', value: 'QB' },
  { label: 'C', value: 'C' },
  { label: 'WR', value: 'WR' },
  { label: 'RB', value: 'RB' },
  { label: 'DB', value: 'DB' },
  { label: 'R', value: 'R' },
  { label: 'S', value: 'S' },
  { label: 'CB', value: 'CB' },
]

const positionFilterItems = computed(() => [
  { label: 'Todas posições', value: 'all' },
  ...positionItems,
])

const filteredAthletes = computed(() => {
  return athletes.value
})

const hasNewPhoto = computed(() => form.value.photo instanceof File)

const uploadLoading = computed(() => saving.value && hasNewPhoto.value)
const { progressValue } = useProgressCircular(uploadLoading)

const statsTotal = computed(() => stats.value.total ?? 0)
const statsAvgRating = computed(() => Number(stats.value.avg_rating ?? 0).toFixed(1))
const statsTopPerformerName = computed(() => stats.value.top_performer?.name || '-')

function buildAthletesParams() {
  const params: any = { ordering: 'name' }
  const q = search.value.trim()
  if (q) params.search = q
  if (positionFilter.value !== 'all') params.current_position = positionFilter.value
  return params
}

async function fetchAthletes() {
  loadingAthletes.value = true
  try {
    const params = buildAthletesParams()
    const { data } = await http.get('/athletes/', { params })
    athletes.value = data
    if (flippedAthleteId.value && !athletes.value.some((a: any) => a?.id === flippedAthleteId.value)) {
      flippedAthleteId.value = null
    }
    if (tearingAthleteId.value && !athletes.value.some((a: any) => a?.id === tearingAthleteId.value)) {
      tearingAthleteId.value = null
    }
  } finally {
    loadingAthletes.value = false
  }
}

async function fetchStats() {
  loadingStats.value = true
  try {
    const params = buildAthletesParams()
    const { data } = await http.get('/athletes/stats/', { params })
    stats.value = {
      total: data?.total ?? 0,
      avg_rating: Number(data?.avg_rating ?? 0),
      top_performer: data?.top_performer ?? null,
    }
  } finally {
    loadingStats.value = false
  }
}

async function refreshAthletesAndStats() {
  await Promise.all([fetchAthletes(), fetchStats()])
}

function toUserLabel(u: any): string {
  const email = u.email ? ` • ${u.email}` : ''
  return `${u.username}${email}`
}

function openNew() {
  editing.value = null
  createUserDialog.value = false
  form.value = emptyForm()
  createdUser.value = null
  dialog.value = true
  updatePhotoPreview()
}

function edit(a: any) {
  editing.value = a
  createUserDialog.value = false
  form.value = {
    ...a,
    photo: null,
    birth_date: a.birth_date ?? '',
    birth_city: a.birth_city ?? '',
    career_notes: a.career_notes ?? '',
  }
  createdUser.value = null
  dialog.value = true
  updatePhotoPreview()
}

watch(dialog, (isOpen) => {
  if (!isOpen) {
    editing.value = null
    createUserDialog.value = false
    form.value = emptyForm()
    createdUser.value = null
    updatePhotoPreview()
  }
})

watch(
  () => form.value?.photo,
  () => updatePhotoPreview()
)

function openCreateUser() {
  if (editing.value) return
  createUserError.value = null
  createUserForm.value = { username: '', email: '', first_name: '', last_name: '', password: '' }
  createUserDialog.value = true
}

async function createUser() {
  if (editing.value) return
  createUserError.value = null
  if (!createUserForm.value.username.trim() || !createUserForm.value.password) {
    createUserError.value = 'Informe username e senha.'
    return
  }

  createUserLoading.value = true
  try {
    const { data } = await http.post('/accounts/users/', {
      username: createUserForm.value.username.trim(),
      password: createUserForm.value.password,
      email: createUserForm.value.email.trim() || '',
      first_name: createUserForm.value.first_name.trim() || '',
      last_name: createUserForm.value.last_name.trim() || '',
    })
    const item: UserItem = { ...data, label: toUserLabel(data) }
    createdUser.value = item
    form.value.user = item.id
    createUserDialog.value = false
  } catch (e: any) {
    const msg =
      e?.response?.data?.username ||
      e?.response?.data?.detail ||
      'Não foi possível criar o usuário.'
    createUserError.value = Array.isArray(msg) ? msg.join(' ') : String(msg)
  } finally {
    createUserLoading.value = false
  }
}

async function save() {
  if (saving.value) return
  saving.value = true
  const hasPhoto = form.value.photo instanceof File
  const endpoint = editing.value ? `/athletes/${editing.value.id}/` : '/athletes/'

  try {
    if (hasPhoto) {
      const fd = new FormData()
      for (const [k, v] of Object.entries(form.value)) {
        if (v === null || v === undefined || v === '') continue
        if (editing.value && k === 'user') continue
        if (k === 'photo') fd.append('photo', v as File)
        else fd.append(k, String(v))
      }

      if (editing.value) await http.patch(endpoint, fd)
      else await http.post(endpoint, fd)
    } else {
      const payload = { ...form.value }
      delete payload.photo
      if (editing.value) delete (payload as any).user
      if (editing.value) await http.patch(endpoint, payload)
      else await http.post(endpoint, payload)
    }

    dialog.value = false
    await refreshAthletesAndStats()
  } catch {
    alert('Não foi possível salvar.')
  } finally {
    saving.value = false
  }
}

function askRemove(a: any) {
  deleteTarget.value = a
  deleteDialog.value = true
}

function closeDelete() {
  deleteDialog.value = false
  deleteTarget.value = null
}

async function confirmRemove() {
  if (!deleteTarget.value || deleting.value) return
  deleting.value = true
  try {
    await http.delete(`/athletes/${deleteTarget.value.id}/`)
    closeDelete()
    await fetchAthletes()
  } catch {
    alert('Não foi possível excluir.')
  } finally {
    deleting.value = false
  }
}

onMounted(fetchAthletes)
onMounted(fetchStats)

let filterTimer: any = null
watch([search, positionFilter], () => {
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    refreshAthletesAndStats()
  }, 250)
})
</script>

<style scoped>
.athletes-header {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 16px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.70);
  backdrop-filter: blur(12px);
}

.athletes-header__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(var(--v-theme-on-warning), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-warning), 1),
    rgba(var(--v-theme-warning), 0.75)
  );
}

.stats-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.55);
  backdrop-filter: blur(10px);
}

.stats-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-card__icon--info {
  background: rgba(var(--v-theme-info), 0.18);
  color: rgba(var(--v-theme-info), 1);
}

.stats-card__icon--success {
  background: rgba(var(--v-theme-success), 0.18);
  color: rgba(var(--v-theme-success), 1);
}

.stats-card__icon--warning {
  background: rgba(var(--v-theme-warning), 0.18);
  color: rgba(var(--v-theme-warning), 1);
}

.athlete-form-dialog :deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.6) !important;
  backdrop-filter: blur(8px);
}

.athlete-form-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.98);
}

.athlete-form__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
}

.athlete-form__close {
  opacity: 0.8;
}

.athlete-form__body {
  padding: 18px;
}

.athlete-form__photo {
  display: flex;
  justify-content: center;
}

.athlete-form__photo-btn {
  position: relative;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.athlete-form__photo-btn:disabled {
  cursor: default;
  opacity: 0.9;
}

.athlete-form__photo-ring {
  padding: 4px;
  border-radius: 999px;
  background: rgba(var(--v-theme-primary), 0.22);
}

.athlete-form__photo-avatar {
  background: rgba(var(--v-theme-surface-variant), 1);
}

.athlete-form__photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.athlete-form__photo-overlay {
  position: absolute;
  inset: 4px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  color: white;
  opacity: 0;
  transition: opacity 120ms ease;
}

.athlete-form__photo-btn:hover .athlete-form__photo-overlay {
  opacity: 1;
}

.athlete-form__photo-overlay.is-visible {
  opacity: 1;
}

.athlete-form__photo-input {
  display: none;
}

.athlete-form__actions {
  display: flex;
  gap: 12px;
  padding-top: 12px;
}

.empty-state__icon {
  width: 80px;
  height: 80px;
  border-radius: 999px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.55);
}

.athlete-fc {
  --fc-g1: rgba(var(--v-theme-warning), 1);
  --fc-g2: rgba(var(--v-theme-warning), 0.75);
  --fc-g3: rgba(var(--v-theme-warning), 0.55);
  --fc-border: rgba(var(--v-theme-warning), 0.55);
  --fc-glow: rgba(var(--v-theme-warning), 0.45);
  /* Texto sempre segue o tema (light/dark), não a cor da nota */
  --fc-text: rgba(var(--v-theme-on-surface), 1);
  --fc-sub: rgba(var(--v-theme-on-surface), 0.75);

  position: relative;
  perspective: 900px;
  -webkit-perspective: 900px;
  width: 220px;
  margin: 0 auto;
  padding-bottom: 44px;
  animation: athleteFadeUp 320ms ease both;
  animation-delay: var(--delay, 0ms);
}

.athlete-fc__glow {
  position: absolute;
  inset: -6px;
  border-radius: 24px;
  background: radial-gradient(ellipse, var(--fc-glow) 0%, transparent 70%);
  filter: blur(14px);
  z-index: 0;
  opacity: 0.7;
}

/*
  EFEITO “FOGO” (desativado a pedido)

  Mantido aqui comentado caso queiram reativar futuramente.

  .athlete-fc__glow::before,
  .athlete-fc__glow::after { ... }
  @keyframes fcFlameDrift { ... }
  @keyframes fcFlameFlicker { ... }
  @media (prefers-reduced-motion: reduce) { ... }
*/

.athlete-fc__card {
  position: relative;
  width: 220px;
  height: 310px;
  border-radius: 18px;
  background: linear-gradient(155deg, var(--fc-g1) 0%, var(--fc-g2) 55%, var(--fc-g3) 100%);
  box-shadow:
    0 0 0 2px var(--fc-border),
    0 12px 40px var(--fc-glow),
    inset 0 1px 0 rgba(255, 255, 255, 0.45);
  overflow: hidden;
  z-index: 1;
  transition: transform 360ms cubic-bezier(.2,.8,.2,1);
  will-change: transform;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.athlete-fc__inner {
  position: absolute;
  inset: 0;
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d;
  transition: transform 360ms cubic-bezier(.2,.8,.2,1);
  will-change: transform;
}

.athlete-fc__tear {
  position: absolute;
  inset: 0;
  z-index: 40;
  pointer-events: none;
}

.athlete-fc__tear-half {
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: linear-gradient(155deg, var(--fc-g1) 0%, var(--fc-g2) 55%, var(--fc-g3) 100%);
  box-shadow:
    0 0 0 2px var(--fc-border),
    0 12px 40px var(--fc-glow),
    inset 0 1px 0 rgba(255, 255, 255, 0.45);
}

.athlete-fc__tear-half--left {
  clip-path: polygon(
    0 0,
    54% 0,
    50% 6%,
    56% 13%,
    49% 20%,
    57% 28%,
    50% 36%,
    58% 45%,
    49% 55%,
    56% 64%,
    50% 74%,
    58% 84%,
    50% 92%,
    54% 100%,
    0 100%
  );
  transform-origin: 54% 50%;
  animation: fcTearLeft 420ms cubic-bezier(.2,.8,.2,1) forwards;
}

.athlete-fc__tear-half--right {
  clip-path: polygon(
    46% 0,
    100% 0,
    100% 100%,
    46% 100%,
    50% 92%,
    42% 84%,
    50% 74%,
    44% 64%,
    51% 55%,
    42% 45%,
    50% 36%,
    43% 28%,
    51% 20%,
    44% 13%,
    50% 6%
  );
  transform-origin: 46% 50%;
  animation: fcTearRight 420ms cubic-bezier(.2,.8,.2,1) forwards;
}

@keyframes fcTearLeft {
  0% {
    transform: translateX(0) rotate(0deg);
    filter: blur(0);
    opacity: 1;
  }
  55% {
    transform: translateX(-18px) rotate(-6deg);
    opacity: 1;
  }
  100% {
    transform: translateX(-46px) rotate(-10deg);
    filter: blur(0.6px);
    opacity: 0;
  }
}

@keyframes fcTearRight {
  0% {
    transform: translateX(0) rotate(0deg);
    filter: blur(0);
    opacity: 1;
  }
  55% {
    transform: translateX(18px) rotate(6deg);
    opacity: 1;
  }
  100% {
    transform: translateX(46px) rotate(10deg);
    filter: blur(0.6px);
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .athlete-fc__tear-half--left,
  .athlete-fc__tear-half--right {
    animation: none;
    opacity: 0;
  }
}

.athlete-fc:hover .athlete-fc__card {
  transform: translateY(-10px) scale(1.04);
}

.athlete-fc__card.is-flipped .athlete-fc__inner {
  transform: rotateY(180deg);
}

.athlete-fc__card:focus-visible {
  outline: 2px solid rgba(var(--v-theme-primary), 0.70);
  outline-offset: 3px;
}

.athlete-fc__face {
  position: absolute;
  inset: 0;
  border-radius: 18px;
  overflow: hidden;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}

.athlete-fc__face--back {
  transform: rotateY(180deg);
}

.athlete-fc__back {
  position: absolute;
  inset: 0;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.athlete-fc__back-top {
  padding: 10px 10px 8px;
  border-radius: 14px;
  background: rgba(var(--v-theme-surface), 0.42);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.18);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px);
}

.athlete-fc__back-name {
  font-weight: 950;
  font-size: 14px;
  color: var(--fc-text);
  text-transform: uppercase;
  letter-spacing: 1.1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.athlete-fc__back-sub {
  margin-top: 4px;
  font-size: 10px;
  color: var(--fc-sub);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 750;
}

.athlete-fc__back-sub2 {
  margin-top: 4px;
  font-size: 9px;
  color: rgba(var(--v-theme-on-surface), 0.70);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 800;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.athlete-fc__back-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.athlete-fc__back-item {
  padding: 10px 10px 9px;
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.60);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.14);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.08);
}

.athlete-fc__back-k {
  font-weight: 800;
  font-size: 9px;
  color: var(--fc-sub);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.athlete-fc__back-v {
  margin-top: 3px;
  font-weight: 950;
  font-size: 12px;
  color: var(--fc-text);
  line-height: 1.15;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.athlete-fc__back-notes {
  padding: 10px 10px 9px;
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.60);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.14);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.08);
}

.athlete-fc__back-notes-v {
  margin-top: 3px;
  font-weight: 750;
  font-size: 11px;
  color: rgba(var(--v-theme-on-surface), 0.88);
  line-height: 1.2;
  display: -webkit-box;
  line-clamp: 4;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
}

.athlete-fc__back-hint {
  margin-top: auto;
  text-align: center;
  font-size: 9px;
  color: rgba(var(--v-theme-on-surface), 0.70);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  font-weight: 800;
  opacity: 0.9;
}

.athlete-fc__pattern {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.2;
  pointer-events: none;
}

.athlete-fc__shine {
  position: absolute;
  top: 0;
  left: 0;
  width: 60%;
  height: 50%;
  background: radial-gradient(ellipse at 20% 20%, rgba(255, 255, 255, 0.30) 0%, transparent 70%);
  pointer-events: none;
}

.athlete-fc__ovr {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 10;
  line-height: 1;
  text-align: center;
  padding: 10px 10px 8px;
  border-radius: 14px;
  background: rgba(var(--v-theme-surface), 0.35);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.18);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px);
}

.athlete-fc__ovr-num {
  font-size: 46px;
  font-weight: 900;
  color: var(--fc-text);
  line-height: 1;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  font-style: italic;
}

.athlete-fc__ovr-pos {
  font-size: 11px;
  font-weight: 800;
  color: var(--fc-sub);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-top: 2px;
}

.athlete-fc__ovr-badge {
  margin-top: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--fc-g2), var(--fc-g3));
  border: 1.5px solid var(--fc-border);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.30);
}

.athlete-fc__ovr-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
}

.athlete-fc__ovr-jersey {
  font-weight: 950;
  font-size: 12px;
  color: rgba(var(--v-theme-on-surface), 1);
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.18);
}

.athlete-fc__photo {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 90px;
  z-index: 5;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  overflow: hidden;
}

.athlete-fc__photo::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 30%, rgba(0, 0, 0, 0.18), transparent 60%),
    linear-gradient(180deg, rgba(0, 0, 0, 0.06) 0%, rgba(0, 0, 0, 0.22) 100%);
  pointer-events: none;
  z-index: 0;
}

.athlete-fc__img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
  transform: scale(1.08);
  transition: transform 220ms ease;
  filter: contrast(1.02) saturate(1.02);
}

.athlete-fc:hover .athlete-fc__img {
  transform: scale(1.14);
}

.athlete-fc__img-empty {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.athlete-fc__footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  background: linear-gradient(
    0deg,
    rgba(var(--v-theme-surface), 0.92) 0%,
    rgba(var(--v-theme-surface), 0.64) 60%,
    rgba(var(--v-theme-surface), 0) 100%
  );
  padding-top: 20px;
  padding-bottom: 12px;
  padding-left: 10px;
  padding-right: 10px;
}

.athlete-fc__divider {
  height: 1px;
  background: rgba(var(--v-theme-on-surface), 0.22);
  margin: 0 8px 6px;
}

.athlete-fc__name-wrap {
  margin: 0 8px 8px;
  padding: 7px 10px;
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.72);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.18);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.10);
  position: relative;
  overflow: hidden;
}

.athlete-fc__name-wrap::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(var(--v-theme-on-surface), 0.10) 45%, transparent 100%);
  transform: translateX(-60%);
  opacity: 0;
  transition: transform 260ms ease, opacity 260ms ease;
  pointer-events: none;
}

.athlete-fc:hover .athlete-fc__name-wrap::after {
  transform: translateX(60%);
  opacity: 1;
}

.athlete-fc__name {
  text-align: center;
  font-weight: 950;
  font-size: 14px;
  color: var(--fc-text);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  text-shadow:
    0 2px 0 rgba(0, 0, 0, 0.18),
    0 8px 20px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.athlete-fc__attrs {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 3px;
  padding-bottom: 4px;
}

.athlete-fc__attr {
  text-align: center;
}

.athlete-fc__attr-val {
  font-weight: 900;
  font-size: 13px;
  color: var(--fc-text);
  line-height: 1;
}

.athlete-fc__attr-lbl {
  font-weight: 700;
  font-size: 8px;
  color: var(--fc-sub);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 1px;
}

.athlete-fc__meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 4px;
}

.athlete-fc__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.athlete-fc__meta-text {
  font-size: 8px;
  color: var(--fc-sub);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 700;
}

.dot--active {
  background: rgba(var(--v-theme-success), 1);
}

.dot--inactive {
  background: rgba(var(--v-theme-on-surface), 0.35);
}

.athlete-fc__actions {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  gap: 8px;
  padding: 0 4px;
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 220ms ease, transform 220ms ease;
  z-index: 20;
}

.athlete-fc:hover .athlete-fc__actions {
  opacity: 1;
  transform: translateY(0);
}

@keyframes athleteFadeUp {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>