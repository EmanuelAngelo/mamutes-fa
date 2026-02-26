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

        <v-btn color="primary" variant="flat" rounded="xl" :loading="saving" :disabled="saving || loading" @click="save">
          <v-icon start>mdi-content-save</v-icon>
          Salvar
        </v-btn>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
        <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>
        <v-alert v-if="success" type="success" variant="tonal" class="mb-3">Dados atualizados.</v-alert>

        <div v-if="loading" class="d-flex justify-center py-10">
          <v-progress-circular indeterminate />
        </div>

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
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { http } from '../../api/http'

const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const birthDateMenu = ref(false)

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
</style>
