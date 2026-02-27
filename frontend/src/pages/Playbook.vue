<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-book-open-variant</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Playbook</div>
            <div class="text-h6 font-weight-bold">Esquemas e Jogadas</div>
          </div>
        </div>

        <v-btn
          v-if="canEdit"
          color="primary"
          variant="flat"
          rounded="xl"
          @click="openNew"
        >
          <v-icon start>mdi-plus</v-icon>
          Nova Jogada
        </v-btn>
      </div>
    </v-sheet>

    <template v-if="error">
      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-title>Erro ao carregar playbook</v-card-title>
        <v-card-text>
          <v-alert type="error" variant="tonal">{{ error }}</v-alert>
          <v-btn class="mt-3" variant="tonal" @click="fetchPlays">Tentar novamente</v-btn>
        </v-card-text>
      </v-card>
    </template>

    <template v-else>
      <v-card variant="tonal" rounded="xl" class="mt-4">
        <v-card-text>
          <div class="d-flex flex-wrap ga-4">
            <v-text-field
              v-model="filters.q"
              label="Buscar"
              variant="outlined"
              density="comfortable"
              clearable
              prepend-inner-icon="mdi-magnify"
              class="flex-grow-1"
              style="min-width: 260px"
              @update:model-value="debouncedFetch"
            />

            <v-select
              v-model="filters.category"
              :items="categoryItems"
              item-title="label"
              item-value="value"
              label="Categoria"
              variant="outlined"
              density="comfortable"
              clearable
              style="min-width: 220px"
              @update:model-value="debouncedFetch"
            />
          </div>
        </v-card-text>
      </v-card>

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

      <v-alert v-else-if="!plays.length" type="info" variant="tonal" class="mt-4" rounded="xl">
        <div class="d-flex align-center ga-3">
          <v-icon>mdi-book-open-page-variant</v-icon>
          <div>
            <div class="font-weight-bold">Playbook vazio</div>
            <div class="text-body-2">Adicione jogadas com imagem e explicação.</div>
          </div>
        </div>

        <v-btn v-if="canEdit" class="mt-3" color="primary" variant="tonal" @click="openNew">
          <v-icon start>mdi-plus</v-icon>
          Adicionar Jogada
        </v-btn>
      </v-alert>

      <v-row v-else class="mt-2" density="comfortable">
      <v-col
        v-for="p in plays"
        :key="p.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card rounded="xl" variant="tonal" class="play-card">
          <div class="play-card__image">
            <v-img
              v-if="p.image_url"
              :src="toAbsoluteMediaUrl(p.image_url)"
              height="180"
              cover
              style="cursor: zoom-in"
              @click.stop="openImage(p)"
            />
            <div v-else class="play-card__image-empty d-flex flex-column align-center justify-center">
              <v-icon size="44" class="opacity-60">mdi-image-off</v-icon>
              <div class="text-body-2 text-medium-emphasis mt-1">Sem imagem</div>
            </div>

            <div v-if="p.category" class="play-card__chip">
              <v-chip
                :color="categoryColor(p.category)"
                variant="tonal"
                size="small"
                class="font-weight-medium"
              >
                {{ categoryLabel(p.category) }}
              </v-chip>
            </div>

            <div v-if="canEdit" class="play-card__actions">
              <v-btn
                icon
                size="small"
                variant="tonal"
                class="mr-2"
                @click.stop="openEdit(p)"
              >
                <v-icon size="18">mdi-pencil</v-icon>
              </v-btn>
              <v-btn
                icon
                size="small"
                color="error"
                variant="tonal"
                :loading="deletingId === p.id"
                @click.stop="askRemove(p)"
              >
                <v-icon size="18">mdi-trash-can</v-icon>
              </v-btn>
            </div>
          </div>

          <v-card-text>
            <div class="text-subtitle-1 font-weight-bold text-truncate" :title="p.title">
              {{ p.title }}
            </div>
            <div v-if="p.description" class="text-body-2 text-medium-emphasis mt-1 play-card__desc">
              {{ p.description }}
            </div>
            <div v-else class="text-body-2 text-medium-emphasis mt-1 font-italic">Sem descrição</div>
          </v-card-text>
        </v-card>
      </v-col>
      </v-row>
    </template>

    <v-dialog
      v-model="dialog"
      class="app-dialog"
      :fullscreen="display.smAndDown.value"
      max-width="720"
      scrollable
    >
      <v-card rounded="xl">
        <div class="app-dialog__header">
          <div class="text-h6 font-weight-bold">
            {{ editing ? 'Editar Jogada' : 'Nova Jogada' }}
          </div>
          <v-btn icon variant="text" :disabled="saving" @click="closeDialog">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text>
          <v-alert v-if="formError" type="error" variant="tonal" class="mb-3">{{ formError }}</v-alert>

          <div class="d-flex flex-wrap ga-4">
            <div class="flex-grow-1" style="min-width: 260px">
              <v-text-field
                v-model="form.title"
                label="Título"
                variant="outlined"
                density="comfortable"
                :disabled="saving"
              />
            </div>

            <div style="min-width: 220px">
              <v-select
                v-model="form.category"
                :items="categoryItems"
                item-title="label"
                item-value="value"
                label="Categoria"
                variant="outlined"
                density="comfortable"
                clearable
                :disabled="saving"
              />
            </div>
          </div>

          <v-textarea
            v-model="form.description"
            label="Explicação"
            variant="outlined"
            density="comfortable"
            rows="5"
            :disabled="saving"
          />

          <v-divider class="my-4" />

          <div class="text-subtitle-2 font-weight-medium mb-2">Imagem</div>

          <v-file-input
            v-model="imageFile"
            accept="image/*"
            label="Selecionar imagem"
            variant="outlined"
            density="comfortable"
            prepend-icon="mdi-upload"
            :disabled="saving"
            @update:model-value="onImagePicked"
          />

          <div v-if="previewUrl" class="mt-3">
            <v-img :src="previewUrl" height="240" cover rounded="lg" />
            <div class="d-flex justify-end mt-2">
              <v-btn
                size="small"
                color="error"
                variant="tonal"
                :disabled="saving"
                @click="clearImage"
              >
                <v-icon start size="18">mdi-trash-can</v-icon>
                Remover imagem
              </v-btn>
            </div>
          </div>
        </v-card-text>

        <v-card-actions>
          <div class="app-dialog__actions">
            <v-btn
              variant="outlined"
              rounded="lg"
              class="flex-grow-1"
              :disabled="saving"
              @click="closeDialog"
            >
              Cancelar
            </v-btn>
            <v-btn
              color="primary"
              variant="flat"
              rounded="lg"
              class="flex-grow-1"
              :loading="saving"
              @click="save"
            >
              {{ editing ? 'Salvar' : 'Adicionar' }}
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" class="app-dialog" max-width="520">
      <v-card rounded="xl" variant="tonal">
        <div class="app-dialog__header">
          <div class="d-flex align-center ga-3">
            <v-icon color="error">mdi-trash-can</v-icon>
            <div class="text-h6 font-weight-bold">Remover Jogada</div>
          </div>
          <v-btn icon variant="text" :disabled="isDeleting" @click="closeDelete">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text>
          <v-alert type="warning" variant="tonal" class="mb-3">
            Esta ação não pode ser desfeita.
          </v-alert>

          <div class="text-body-2">
            Tem certeza que deseja remover
            <strong>{{ deleteTarget?.title }}</strong> do playbook?
          </div>
        </v-card-text>

        <v-card-actions>
          <div class="app-dialog__actions">
            <v-btn
              variant="outlined"
              rounded="lg"
              class="flex-grow-1"
              :disabled="isDeleting"
              @click="closeDelete"
            >
              Cancelar
            </v-btn>
            <v-btn
              color="error"
              variant="tonal"
              rounded="lg"
              class="flex-grow-1"
              :loading="isDeleting"
              :disabled="!deleteTarget"
              @click="confirmRemove"
            >
              Excluir
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="imageDialog" class="app-dialog" max-width="980">
      <v-card rounded="xl" variant="tonal">
        <div class="app-dialog__header">
          <div class="text-h6 font-weight-bold text-truncate" :title="imageTitle">
            {{ imageTitle || 'Imagem' }}
          </div>
          <v-btn icon variant="text" @click="closeImage">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text>
          <v-img
            v-if="imageUrl"
            :src="imageUrl"
            max-height="78vh"
            contain
            class="rounded-lg"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { usePageProgressLoading } from '@/composables/usePageProgressLoading'

type Play = {
  id: number
  title: string
  description?: string
  category?: string
  image_url?: string
  created_at?: string
  updated_at?: string
}

const auth = useAuthStore()
const display = useDisplay()

const canEdit = computed(() => auth.isCoachOrAdmin)

const plays = ref<Play[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const filters = reactive({
  q: '',
  category: '' as string | '',
})

const firstLoad = ref(true)
const { value: progress, start: startLoading, stop: stopLoading } = usePageProgressLoading({
  minDurationMs: 5000,
})

const dialog = ref(false)
const editing = ref<Play | null>(null)
const saving = ref(false)
const deletingId = ref<number | null>(null)

const deleteDialog = ref(false)
const deleteTarget = ref<Play | null>(null)
const isDeleting = computed(() => !!deleteTarget.value && deletingId.value === deleteTarget.value.id)

const imageDialog = ref(false)
const imageUrl = ref<string | undefined>(undefined)
const imageTitle = ref<string | undefined>(undefined)

const formError = ref<string | null>(null)
const form = reactive({
  title: '',
  description: '',
  category: '' as string | '',
})

const imageFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const removeImage = ref(false)

const categoryItems = [
  { label: 'Ataque', value: 'ATAQUE' },
  { label: 'Defesa', value: 'DEFESA' },
//   { label: 'Bola Parada', value: 'BOLA_PARADA' },
//   { label: 'Transição', value: 'TRANSICAO' },
//   { label: 'Posse', value: 'POSSE' },
]

let debounceTimer: any = null
function debouncedFetch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchPlays, 250)
}

function categoryLabel(value: string) {
  return categoryItems.find((c) => c.value === value)?.label ?? value
}

function categoryColor(value: string) {
  switch (value) {
    case 'ATAQUE':
      return 'error'
    case 'DEFESA':
      return 'info'
    case 'BOLA_PARADA':
      return 'warning'
    case 'TRANSICAO':
      return 'success'
    case 'POSSE':
      return 'primary'
    default:
      return 'secondary'
  }
}

function apiOrigin(): string {
  const base = String(http.defaults.baseURL || '')
  if (!base) return ''
  return base.replace(/\/api\/?$/, '').replace(/\/+$/, '')
}

function toAbsoluteMediaUrl(url: string) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  const origin = apiOrigin()
  if (!origin) return url
  if (url.startsWith('/')) return `${origin}${url}`
  return `${origin}/${url}`
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.category = ''
  formError.value = null
  editing.value = null
  imageFile.value = null
  if (previewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(previewUrl.value)
    } catch {
      // ignore
    }
  }
  previewUrl.value = null
  removeImage.value = false
}

function openNew() {
  if (!canEdit.value) return
  resetForm()
  dialog.value = true
}

function openEdit(p: Play) {
  if (!canEdit.value) return
  resetForm()
  editing.value = p
  form.title = p.title
  form.description = p.description ?? ''
  form.category = p.category ?? ''
  previewUrl.value = p.image_url ? toAbsoluteMediaUrl(p.image_url) : null
  dialog.value = true
}

function closeDialog(force = false) {
  if (!force && saving.value) return
  dialog.value = false
  resetForm()
}

function onImagePicked(file: File | File[] | null) {
  const f = Array.isArray(file) ? file[0] : file
  if (!f) return
  removeImage.value = false
  imageFile.value = f
  if (previewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(previewUrl.value)
    } catch {
      // ignore
    }
  }
  previewUrl.value = URL.createObjectURL(f)
}

function clearImage() {
  if (previewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(previewUrl.value)
    } catch {
      // ignore
    }
  }

  imageFile.value = null
  previewUrl.value = null

  // se estava editando e já existia imagem, sinaliza para remover no backend
  if (editing.value?.image_url) {
    removeImage.value = true
  }
}

async function fetchPlays() {
  loading.value = true
  startLoading()
  error.value = null

  try {
    const params: any = { ordering: '-created_at' }
    if (filters.q?.trim()) params.search = filters.q.trim()
    if (filters.category) params.category = filters.category

    const { data } = await http.get('/playbook/plays/', { params })
    plays.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Não foi possível carregar o playbook.'
  } finally {
    loading.value = false
    await stopLoading({ minDurationMs: firstLoad.value ? 5000 : 0 })
    firstLoad.value = false
  }
}

function openImage(p: Play) {
  if (!p.image_url) return
  imageTitle.value = p.title
  imageUrl.value = toAbsoluteMediaUrl(p.image_url)
  imageDialog.value = true
}

function closeImage() {
  imageDialog.value = false
  imageTitle.value = undefined
  imageUrl.value = undefined
}

async function save() {
  if (!canEdit.value) return

  formError.value = null
  const title = form.title.trim()
  if (!title) {
    formError.value = 'Informe o título.'
    return
  }

  saving.value = true
  try {
    const endpoint = editing.value ? `/playbook/plays/${editing.value.id}/` : '/playbook/plays/'

    const useMultipart = !!imageFile.value || removeImage.value

    if (useMultipart) {
      const fd = new FormData()
      fd.append('title', title)
      fd.append('description', form.description?.trim() || '')
      if (form.category) fd.append('category', form.category)
      if (imageFile.value) fd.append('image', imageFile.value)
      if (removeImage.value) fd.append('remove_image', 'true')

      if (editing.value) await http.patch(endpoint, fd)
      else await http.post(endpoint, fd)
    } else {
      const payload: any = {
        title,
        description: form.description?.trim() || '',
        category: form.category || '',
      }
      if (editing.value) await http.patch(endpoint, payload)
      else await http.post(endpoint, payload)
    }

    // fecha imediatamente (mesmo enquanto saving=true)
    closeDialog(true)
    await fetchPlays()
  } catch (e: any) {
    const msg = e?.response?.data?.title || e?.response?.data?.detail || 'Não foi possível salvar.'
    formError.value = Array.isArray(msg) ? msg.join(' ') : String(msg)
  } finally {
    saving.value = false
  }
}

function askRemove(p: Play) {
  if (!canEdit.value) return
  deleteTarget.value = p
  deleteDialog.value = true
}

function closeDelete() {
  if (isDeleting.value) return
  deleteDialog.value = false
  deleteTarget.value = null
}

async function confirmRemove() {
  if (!canEdit.value) return
  if (!deleteTarget.value) return

  deletingId.value = deleteTarget.value.id
  try {
    await http.delete(`/playbook/plays/${deleteTarget.value.id}/`)
    closeDelete()
    await fetchPlays()
  } catch {
    alert('Não foi possível excluir.')
  } finally {
    deletingId.value = null
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

.play-card__image {
  position: relative;
}

.play-card__image-empty {
  height: 180px;
}

.play-card__chip {
  position: absolute;
  top: 12px;
  left: 12px;
}

.play-card__actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
}

.play-card__desc {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.app-dialog :deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.6) !important;
  backdrop-filter: blur(8px);
}

.app-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
}

.app-dialog__actions {
  width: 100%;
  display: flex;
  gap: 12px;
}
</style>
