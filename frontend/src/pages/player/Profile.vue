<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-account</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Player</div>
            <div class="text-h6 font-weight-bold">Meu Perfil</div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-btn
            v-if="showEdit"
            variant="outlined"
            rounded="xl"
            :disabled="loading || saving"
            @click="onBack"
          >
            <v-icon start>mdi-arrow-left</v-icon>
            Voltar
          </v-btn>

          <v-btn
            color="primary"
            variant="flat"
            rounded="xl"
            :loading="headerLoading"
            :disabled="loading || (showEdit && saving)"
            @click="onPrimaryAction"
          >
            <v-icon start>{{ showEdit ? 'mdi-content-save' : 'mdi-pencil' }}</v-icon>
            {{ showEdit ? 'Salvar' : 'Editar perfil' }}
          </v-btn>
        </div>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
        <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>
        <v-alert v-if="success" type="success" variant="tonal" class="mb-3">Dados atualizados.</v-alert>

        <div v-if="loading" class="d-flex justify-center py-10">
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

        <template v-else>
          <template v-if="!showEdit">
            <div class="athlete-fc" :style="fcCardVars" :aria-busy="cardTearing ? 'true' : 'false'">
              <div class="athlete-fc__glow" />

              <div
                class="athlete-fc__card"
                :class="{ 'is-flipped': cardFlipped }"
                role="button"
                tabindex="0"
                aria-label="Toque para virar o card"
                @click="toggleCardFlip"
                @keydown.enter.prevent="toggleCardFlip"
                @keydown.space.prevent="toggleCardFlip"
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
                    <div class="athlete-fc__ovr-num">{{ fcOvr }}</div>
                    <div class="athlete-fc__ovr-pos">{{ fcPosShort }}</div>
                    <div class="athlete-fc__ovr-badge">
                      <span v-if="hasJersey" class="athlete-fc__ovr-jersey">{{ jerseyText }}</span>
                      <span v-else class="athlete-fc__ovr-dot" />
                    </div>
                  </div>

                  <div class="athlete-fc__photo">
                    <img
                      v-if="cardPhotoUrl"
                      :src="cardPhotoUrl"
                      :alt="form.name"
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
                      <div class="athlete-fc__name" :title="form.name">{{ form.name || '-' }}</div>
                    </div>

                    <div class="athlete-fc__attrs">
                      <div v-for="(lbl, i) in FC_ATTRS" :key="lbl" class="athlete-fc__attr">
                        <div class="athlete-fc__attr-val">{{ fcAttrs[i] }}</div>
                        <div class="athlete-fc__attr-lbl">{{ lbl }}</div>
                      </div>
                    </div>

                    <div class="athlete-fc__meta">
                      <span class="athlete-fc__dot" :class="statusDotClass" />
                      <span class="athlete-fc__meta-text">
                        {{ athleteActive ? 'Ativo' : 'Inativo' }}
                        <template v-if="hasJersey">· #{{ jerseyText }}</template>
                      </span>
                    </div>
                  </div>
                  </div>

                  <div class="athlete-fc__face athlete-fc__face--back" aria-hidden="true">
                    <div class="athlete-fc__back">
                      <div class="athlete-fc__back-title">Detalhes</div>
                      <div class="athlete-fc__back-top">
                        <div class="athlete-fc__back-name" :title="form.name">{{ form.name || '-' }}</div>
                        <div class="athlete-fc__back-sub">
                          {{ (form.current_position || '-').toString() }}
                          <template v-if="hasJersey">· #{{ jerseyText }}</template>
                        </div>
                        <div class="athlete-fc__back-sub2">
                          OVR: {{ fcOvr }}
                          · Nota: {{ ratingBackText }}
                        </div>
                      </div>

                      <div class="athlete-fc__back-grid">
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Nascimento</div>
                          <div class="athlete-fc__back-v">{{ formatDateBR(form.birth_date) || '-' }}</div>
                        </div>
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Cidade</div>
                          <div class="athlete-fc__back-v">{{ (form.birth_city || '-').toString() }}</div>
                        </div>
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Altura</div>
                          <div class="athlete-fc__back-v">{{ form.height_m ? `${form.height_m} m` : '-' }}</div>
                        </div>
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Peso</div>
                          <div class="athlete-fc__back-v">{{ form.weight_kg ? `${form.weight_kg} kg` : '-' }}</div>
                        </div>
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Desejada</div>
                          <div class="athlete-fc__back-v">{{ (form.desired_position || '-').toString() }}</div>
                        </div>
                        <div class="athlete-fc__back-item">
                          <div class="athlete-fc__back-k">Status</div>
                          <div class="athlete-fc__back-v">{{ athleteActive ? 'Ativo' : 'Inativo' }}</div>
                        </div>
                      </div>

                      <div class="athlete-fc__back-notes">
                        <div class="athlete-fc__back-k">Observações</div>
                        <div class="athlete-fc__back-notes-v">{{ careerNotesText }}</div>
                      </div>

                      <div class="athlete-fc__back-hint">Toque para voltar</div>
                    </div>
                  </div>
                </div>

                <div v-if="cardTearing" class="athlete-fc__tear" aria-hidden="true">
                  <div class="athlete-fc__tear-half athlete-fc__tear-half--left" />
                  <div class="athlete-fc__tear-half athlete-fc__tear-half--right" />
                </div>
              </div>

              <div class="athlete-fc__actions">
                <v-btn size="small" variant="tonal" class="flex-grow-1" @click.stop="startEditWithTear">
                  <v-icon start size="16">mdi-pencil</v-icon>
                  Editar perfil
                </v-btn>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="profile-photo">
              <v-avatar size="96" class="profile-photo__avatar">
                <v-img v-if="photoPreviewUrl" :src="photoPreviewUrl" cover />
                <div v-else class="profile-photo__empty">
                  <v-icon size="44" class="opacity-60">mdi-account</v-icon>
                </div>
              </v-avatar>
            </div>

            <v-text-field v-model="form.name" label="Nome" variant="outlined" density="comfortable" />

            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="form.jersey_number"
                  label="Camisa"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.current_position"
                  label="Posição Atual"
                  disabled
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.desired_position"
                  label="Posição Desejada"
                  disabled
                  variant="outlined"
                  density="comfortable"
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

            <v-textarea v-model="form.career_notes" label="Observações" variant="outlined" density="comfortable" />

            <v-file-input
              v-model="photo"
              label="Foto (opcional)"
              accept="image/*"
              prepend-icon=""
              :disabled="saving"
            />
          </template>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { http } from '../../api/http'
import { useProgressCircular } from '../../composables/useProgressCircular'

const loading = ref(false)
const { progressValue } = useProgressCircular(loading)
const saving = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const birthDateMenu = ref(false)

const showEdit = ref(false)
const athleteRating = ref(0)
const athleteActive = ref(true)

const headerLoading = computed(() => showEdit.value && saving.value)

function onPrimaryAction() {
  if (showEdit.value) save()
  else startEditWithTear()
}

function startEdit() {
  showEdit.value = true
}

const cardFlipped = ref(false)
const cardTearing = ref(false)

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return true
  return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches)
}

function toggleCardFlip() {
  if (cardTearing.value) return
  cardFlipped.value = !cardFlipped.value
}

function startEditWithTear() {
  if (loading.value || saving.value) return
  if (cardTearing.value) return

  cardFlipped.value = false
  if (prefersReducedMotion()) {
    startEdit()
    return
  }

  cardTearing.value = true
  window.setTimeout(() => {
    cardTearing.value = false
    startEdit()
  }, 420)
}

async function onBack() {
  if (loading.value || saving.value) return
  success.value = false
  photo.value = null
  showEdit.value = false
  cardFlipped.value = false
  await fetchMeAthlete()
}

const form = ref<any>({
  name: '',
  jersey_number: null,
  birth_date: '',
  birth_city: '',
  height_m: null,
  weight_kg: null,
  career_notes: '',
  current_position: '',
  desired_position: '',
})

const photo = ref<File | null>(null)
const existingPhoto = ref<string | null>(null)

function apiOrigin(): string {
  const base = String(http.defaults.baseURL || '')
  if (!base) return ''
  return base.replace(/\/api\/?$/, '').replace(/\/+$/, '')
}

function absoluteMediaUrl(path: string | null | undefined): string | null {
  if (!path || typeof path !== 'string') return null
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const origin = apiOrigin()
  if (!origin) return path
  if (path.startsWith('/')) return `${origin}${path}`
  return `${origin}/${path}`
}

const photoPreviewUrl = ref<string | null>(null)
const cardPhotoUrl = computed(() => absoluteMediaUrl(existingPhoto.value))

const jerseyText = computed(() => {
  const n = form.value?.jersey_number
  if (n === null || n === undefined || n === '') return '-'
  return String(n)
})

const hasJersey = computed(() => jerseyText.value !== '-')

const ratingValue = computed(() => {
  const n = Number(athleteRating.value)
  return Number.isFinite(n) ? Math.max(0, Math.min(10, n)) : 0
})

const ratingClass = computed(() => {
  const r = ratingValue.value
  if (r >= 8) return 'rating--good'
  if (r >= 6) return 'rating--ok'
  if (r >= 4) return 'rating--mid'
  return 'rating--bad'
})

const ratingLabel = computed(() => {
  const r = ratingValue.value
  if (r >= 9) return 'Excelente'
  if (r >= 7) return 'Muito bom'
  if (r >= 5) return 'Regular'
  if (r >= 3) return 'Fraco'
  return 'Crítico'
})

const ratingBackText = computed(() => {
  const r = ratingValue.value
  if (!r) return '--'
  return `${r.toFixed(1)} • ${ratingLabel.value}`
})

const ovrText = computed(() => {
  const r = ratingValue.value
  if (!r) return '--'
  return String(Math.round(r * 10))
})

const FC_ATTRS = ['VEL', 'PAS', 'REC', 'BLO', 'COB', 'FOR'] as const

const fcOvr = computed(() => ovrText.value)

const fcPosShort = computed(() => {
  const p = String(form.value?.current_position || '').trim()
  if (!p) return 'POS'
  return p.slice(0, 3).toUpperCase()
})

function deriveFcAttrs(rating: number, positionCode: string | null | undefined): number[] {
  const base = Math.round((rating || 5) * 9) // ~0-90
  const clamp = (o: number) => Math.min(99, Math.max(25, base + o))
  const pos = String(positionCode || '').toUpperCase()

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

const fcAttrs = computed(() => deriveFcAttrs(ratingValue.value, form.value?.current_position))

const fcCardVars = computed<Record<string, string>>(() => {
  const r = ratingValue.value
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
})

const statusDotClass = computed(() => (athleteActive.value ? 'dot--active' : 'dot--inactive'))

const careerNotesText = computed(() => {
  const raw = String(form.value?.career_notes || '')
  const trimmed = raw.trim()
  return trimmed || '-'
})

function updatePhotoPreview() {
  if (photoPreviewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(photoPreviewUrl.value)
    } catch {
      // ignore
    }
  }

  if (photo.value instanceof File) {
    photoPreviewUrl.value = URL.createObjectURL(photo.value)
    return
  }

  photoPreviewUrl.value = absoluteMediaUrl(existingPhoto.value)
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

async function fetchMeAthlete() {
  loading.value = true
  try {
    const { data } = await http.get('/athletes/me/')
    form.value = {
      name: data.name ?? '',
      jersey_number: data.jersey_number ?? null,
      birth_date: data.birth_date ?? '',
      birth_city: data.birth_city ?? '',
      height_m: data.height_m ?? null,
      weight_kg: data.weight_kg ?? null,
      career_notes: data.career_notes ?? '',
      current_position: data.current_position ?? '',
      desired_position: data.desired_position ?? '',
    }
    existingPhoto.value = data.photo ?? null
    athleteRating.value = Number(data.rating ?? 0)
    athleteActive.value = Boolean(data.is_active ?? true)
    updatePhotoPreview()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Não foi possível carregar seu perfil.'
  } finally {
    loading.value = false
  }
}

async function save() {
  success.value = false
  error.value = null
  saving.value = true
  try {
    const endpoint = '/athletes/me/'
    const hasPhoto = photo.value instanceof File

    if (hasPhoto) {
      const fd = new FormData()
      fd.append('photo', photo.value as File)

      for (const [k, v] of Object.entries(form.value)) {
        if (v === null || v === undefined || v === '') continue
        if (k === 'current_position' || k === 'desired_position') continue
        fd.append(k, String(v))
      }

      await http.patch(endpoint, fd)
    } else {
      const payload: any = { ...form.value }
      delete payload.current_position
      delete payload.desired_position
      await http.patch(endpoint, payload)
    }

    photo.value = null
    success.value = true
    await fetchMeAthlete()
    showEdit.value = false
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Não foi possível salvar.'
    error.value = Array.isArray(msg) ? msg.join(' ') : String(msg)
  } finally {
    saving.value = false
  }
}

watch(photo, () => updatePhotoPreview())

onMounted(fetchMeAthlete)
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

.profile-photo {
  display: flex;
  justify-content: center;
  margin: 8px 0 12px;
}

.profile-photo__avatar {
  border: 4px solid rgba(var(--v-theme-primary), 0.22);
  background: rgba(var(--v-theme-surface-variant), 1);
}

.profile-photo__empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot--active {
  background: rgba(var(--v-theme-success), 1);
}

.dot--inactive {
  background: rgba(var(--v-theme-on-surface), 0.35);
}

.athlete-fc {
  --fc-g1: rgba(var(--v-theme-warning), 1);
  --fc-g2: rgba(var(--v-theme-warning), 0.75);
  --fc-g3: rgba(var(--v-theme-warning), 0.55);
  --fc-border: rgba(var(--v-theme-warning), 0.55);
  --fc-glow: rgba(var(--v-theme-warning), 0.45);
  --fc-text: rgba(var(--v-theme-on-surface), 1);
  --fc-sub: rgba(var(--v-theme-on-surface), 0.75);

  /* Dimensões maiores no Meu Perfil */
  --fc-card-w: 260px;
  --fc-card-h: 365px;
  --fc-footer-h: 106px;

  position: relative;
  perspective: 900px;
  -webkit-perspective: 900px;
  width: var(--fc-card-w);
  margin: 6px auto 0;
  padding-bottom: 52px;
  animation: athleteFadeUp 320ms ease both;
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

.athlete-fc__card {
  position: relative;
  width: var(--fc-card-w);
  height: var(--fc-card-h);
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

.athlete-fc__back-title {
  font-weight: 950;
  font-size: 11px;
  color: rgba(var(--v-theme-on-surface), 0.80);
  text-transform: uppercase;
  letter-spacing: 1.2px;
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
  bottom: var(--fc-footer-h);
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
  min-height: var(--fc-footer-h);
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

@media (hover: none) {
  .athlete-fc__actions {
    opacity: 1;
    transform: translateY(0);
  }
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
