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
            :model-value="progress"
            :rotate="360"
            :size="100"
            :width="15"
            color="teal"
          >
            {{ progress }}
          </v-progress-circular>
        </div>

        <template v-else>
          <template v-if="!showEdit">
            <div class="athlete-card athlete-card--preview">
              <div class="athlete-card__under" />

              <v-card class="athlete-card__main" rounded="xl">
                <div class="athlete-card__watermark">{{ jerseyText }}</div>

                <div class="athlete-card__photo">
                  <div class="athlete-card__glow" />
                  <div class="athlete-card__photo-inner">
                    <v-img v-if="cardPhotoUrl" :src="cardPhotoUrl" cover />
                    <div v-else class="athlete-card__photo-empty">
                      <v-icon size="44" class="opacity-60">mdi-account</v-icon>
                    </div>
                  </div>

                  <div class="athlete-card__badge">{{ jerseyText }}</div>
                </div>

                <div class="athlete-card__info">
                  <div class="athlete-card__name" :title="form.name">{{ form.name || '-' }}</div>
                  <div class="athlete-card__pos">{{ (form.current_position || '-').toString() }}</div>

                  <div class="athlete-card__status">
                    <span class="athlete-card__dot" :class="athleteActive ? 'dot--active' : 'dot--inactive'" />
                    <span class="text-medium-emphasis">{{ athleteActive ? 'Ativo' : 'Inativo' }}</span>
                  </div>

                  <div class="athlete-card__rating">
                    <div class="athlete-card__rating-title">
                      <v-icon size="16" class="athlete-card__star">mdi-star</v-icon>
                      <span>Desempenho</span>
                    </div>

                    <div class="athlete-card__rating-pill" :class="ratingClass">
                      <span class="athlete-card__rating-score">{{ ratingValue.toFixed(1) }}</span>
                      <span class="athlete-card__rating-label">{{ ratingLabel }}</span>
                    </div>
                  </div>

                  <div class="athlete-card__actions">
                    <v-btn size="small" variant="tonal" class="flex-grow-1" @click="startEdit">
                      <v-icon start size="16">mdi-pencil</v-icon>
                      Editar perfil
                    </v-btn>
                  </div>
                </div>
              </v-card>
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
import { usePageProgressLoading } from '@/composables/usePageProgressLoading'

const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const birthDateMenu = ref(false)

const firstLoad = ref(true)
const { value: progress, start: startLoading, stop: stopLoading } = usePageProgressLoading({
  minDurationMs: 5000,
})

const showEdit = ref(false)
const athleteRating = ref(0)
const athleteActive = ref(true)

const headerLoading = computed(() => showEdit.value && saving.value)

function onPrimaryAction() {
  if (showEdit.value) save()
  else startEdit()
}

function startEdit() {
  showEdit.value = true
}

async function onBack() {
  if (loading.value || saving.value) return
  success.value = false
  photo.value = null
  showEdit.value = false
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
  startLoading()
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
    await stopLoading({ minDurationMs: firstLoad.value ? 5000 : 0 })
    firstLoad.value = false
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

.athlete-card {
  position: relative;
  max-width: 360px;
  margin: 6px auto 0;
}

.athlete-card__under {
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-background), 0.9),
    rgba(var(--v-theme-surface), 0.9)
  );
  transform: rotate(1deg);
}

.athlete-card__main {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-surface), 1),
    rgba(var(--v-theme-background), 1)
  );
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
}

.athlete-card__watermark {
  position: absolute;
  top: 10px;
  right: 12px;
  font-weight: 900;
  font-size: 64px;
  line-height: 1;
  opacity: 0.08;
  color: rgba(var(--v-theme-on-surface), 1);
  pointer-events: none;
}

.athlete-card__photo {
  position: relative;
  padding: 18px 18px 10px;
  display: flex;
  justify-content: center;
}

.athlete-card__glow {
  position: absolute;
  width: 130px;
  height: 130px;
  border-radius: 999px;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(var(--v-theme-warning), 0.45),
    rgba(var(--v-theme-warning), 0)
  );
  filter: blur(10px);
  opacity: 0.55;
}

.athlete-card__photo-inner {
  width: 112px;
  height: 112px;
  border-radius: 999px;
  overflow: hidden;
  border: 4px solid rgba(var(--v-theme-warning), 0.25);
  background: rgba(var(--v-theme-on-surface), 0.06);
  position: relative;
}

.athlete-card__photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.athlete-card__badge {
  position: absolute;
  right: calc(50% - 56px);
  bottom: 2px;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  color: rgba(var(--v-theme-on-warning), 1);
  background: rgba(var(--v-theme-warning), 1);
  border: 2px solid rgba(var(--v-theme-surface), 1);
}

.athlete-card__info {
  padding: 10px 16px 16px;
}

.athlete-card__name {
  font-weight: 800;
  font-size: 16px;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.athlete-card__pos {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.athlete-card__status {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.athlete-card__dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}

.dot--active {
  background: rgba(var(--v-theme-success), 1);
}

.dot--inactive {
  background: rgba(var(--v-theme-error), 1);
}

.athlete-card__rating {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.athlete-card__rating-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 12px;
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.athlete-card__star {
  color: rgba(var(--v-theme-warning), 1);
}

.athlete-card__rating-pill {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.65);
}

.athlete-card__rating-score {
  font-weight: 900;
}

.athlete-card__rating-label {
  font-size: 12px;
  font-weight: 700;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

.rating--good {
  border-color: rgba(var(--v-theme-success), 0.35);
}

.rating--ok {
  border-color: rgba(var(--v-theme-info), 0.35);
}

.rating--mid {
  border-color: rgba(var(--v-theme-warning), 0.35);
}

.rating--bad {
  border-color: rgba(var(--v-theme-error), 0.35);
}

.athlete-card__actions {
  margin-top: 14px;
  display: flex;
}
</style>
