<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-book-open-variant</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Coach</div>
            <div class="text-h6 font-weight-bold">Playbook</div>
          </div>
        </div>

        <v-btn color="primary" variant="flat" rounded="xl" @click="openCreate">
          <v-icon start>mdi-plus</v-icon>
          Nova Jogada
        </v-btn>
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
          Adicione jogadas com imagens e explicações
        </div>
        <v-btn class="mt-5" color="primary" variant="tonal" rounded="xl" @click="openCreate">
          <v-icon start>mdi-plus</v-icon>
          Adicionar Jogada
        </v-btn>
      </div>

      <v-row v-else density="comfortable">
        <v-col v-for="p in plays" :key="p.id" cols="12" sm="6" lg="4">
          <v-hover v-slot="{ isHovering, props }">
            <v-card v-bind="props" variant="tonal" rounded="xl" class="play-card">
              <div class="play-image">
                <template v-if="p.image_url">
                  <v-img :src="p.image_url" height="208" cover />
                </template>
                <template v-else>
                  <div class="play-image__placeholder">
                    <v-icon size="46" class="text-medium-emphasis">mdi-image-off-outline</v-icon>
                    <div class="text-body-2 text-medium-emphasis mt-2">Sem imagem</div>
                  </div>
                </template>

                <div class="play-actions" :class="{ 'play-actions--show': isHovering }">
                  <v-btn size="small" variant="tonal" @click.stop="openEdit(p)">
                    <v-icon start>mdi-pencil</v-icon>
                    Editar
                  </v-btn>
                  <v-btn
                    v-if="p.image_url"
                    size="small"
                    variant="tonal"
                    aria-label="Ver imagem"
                    @click.stop="openImageViewer(p.image_url)"
                  >
                    <v-icon>mdi-magnify-plus-outline</v-icon>
                  </v-btn>
                  <v-btn size="small" color="error" variant="tonal" @click.stop="requestRemovePlay(p)">
                    <v-icon>mdi-trash-can-outline</v-icon>
                  </v-btn>
                </div>

                <div v-if="p.category" class="play-badge">
                  <v-chip size="small" variant="tonal" :color="categoryColor(p.category)">
                    {{ p.category }}
                  </v-chip>
                </div>
              </div>

              <v-card-text>
                <div class="text-subtitle-1 font-weight-bold text-truncate">{{ p.title }}</div>
                <div v-if="p.description" class="text-body-2 text-medium-emphasis mt-1 line-clamp-3">
                  {{ p.description }}
                </div>
                <div v-else class="text-body-2 text-medium-emphasis mt-1 font-italic">
                  Sem descrição
                </div>
              </v-card-text>
            </v-card>
          </v-hover>
        </v-col>
      </v-row>
    </div>

    <v-dialog v-model="formOpen" max-width="900">
      <v-card rounded="xl" class="form-card">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="text-h6 font-weight-bold">
            {{ editingPlay ? 'Editar Jogada' : 'Nova Jogada' }}
          </div>
          <v-btn icon variant="text" @click="closeForm">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-alert v-if="formError" type="error" variant="tonal" class="mb-4">
            {{ formError }}
          </v-alert>

          <div
            class="dropzone"
            :class="{ 'dropzone--over': dragOver }"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="onDrop"
            @click="openFilePicker"
          >
            <template v-if="previewUrl">
              <div class="dropzone__preview">
                <img :src="previewUrl" alt="Preview" />
                <div class="dropzone__overlay" @click.stop>
                  <v-btn size="small" variant="tonal" @click="openFilePicker">
                    <v-icon start>mdi-upload</v-icon>
                    Trocar
                  </v-btn>
                  <v-btn size="small" color="error" variant="tonal" @click="requestClearImage">
                    <v-icon>mdi-trash-can-outline</v-icon>
                  </v-btn>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="dropzone__empty">
                <v-avatar size="64" variant="tonal">
                  <v-icon size="28">mdi-upload</v-icon>
                </v-avatar>
                <div class="text-subtitle-2 font-weight-bold mt-3">Clique para fazer upload</div>
                <div class="text-body-2 text-medium-emphasis">ou arraste a imagem aqui</div>
                <div class="text-caption text-medium-emphasis mt-1">PNG, JPG, GIF</div>
              </div>
            </template>

            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="d-none"
              @change="onFileChange"
            />
          </div>

          <v-row class="mt-4" density="comfortable">
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.title"
                label="Título da Jogada"
                variant="outlined"
                :disabled="saving"
                required
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="form.category"
                :items="categories"
                label="Categoria"
                variant="outlined"
                clearable
                :disabled="saving"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="form.description"
                label="Explicação"
                variant="outlined"
                rows="5"
                auto-grow
                :disabled="saving"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-btn class="flex-grow-1" variant="tonal" rounded="xl" :disabled="saving" @click="closeForm">
            Cancelar
          </v-btn>
          <v-btn
            class="flex-grow-1"
            color="primary"
            variant="flat"
            rounded="xl"
            :loading="saving"
            :disabled="!form.title"
            @click="submit"
          >
            <v-icon start>mdi-check</v-icon>
            {{ editingPlay ? 'Salvar' : 'Adicionar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="imageViewerOpen" max-width="1200">
      <v-card rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between">
          <div class="text-subtitle-1 font-weight-bold">Imagem</div>
          <div class="d-flex align-center ga-2">
            <v-btn
              v-if="imageViewerSrc"
              icon
              variant="text"
              aria-label="Girar imagem"
              @click="rotateImage"
            >
              <v-icon>mdi-rotate-right</v-icon>
            </v-btn>
            <v-btn icon variant="text" aria-label="Fechar" @click="imageViewerOpen = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-0">
          <div
            v-if="imageViewerSrc"
            class="image-viewer"
            :class="{ 'image-viewer--rotated': imageIsRotated }"
            :style="{ '--image-rotate': `${imageRotation}deg` }"
          >
            <img class="image-viewer__img" :src="imageViewerSrc" alt="Imagem" />
          </div>
          <div v-else class="pa-6 text-body-2 text-medium-emphasis">Sem imagem</div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmClearImageOpen" max-width="520">
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">Remover imagem?</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          Esta ação remove a imagem desta jogada. Você pode adicionar outra imagem depois.
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-btn
            class="flex-grow-1"
            variant="tonal"
            rounded="xl"
            :disabled="saving"
            @click="confirmClearImageOpen = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            class="flex-grow-1"
            color="error"
            variant="flat"
            rounded="xl"
            :disabled="saving"
            @click="confirmClearImage"
          >
            <v-icon start>mdi-trash-can-outline</v-icon>
            Remover
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmRemovePlayOpen" max-width="520">
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">Remover jogada?</v-card-title>
        <v-card-text class="text-body-2 text-medium-emphasis">
          Tem certeza que deseja remover a jogada
          <span class="font-weight-medium">"{{ playToRemove?.title }}"</span>?
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
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { http } from '../../api/http'
import { useProgressCircular } from '../../composables/useProgressCircular'

type Play = {
  id: number
  title: string
  description: string | null
  category: string | null
  image_url: string | null
}

const plays = ref<Play[]>([])
const loading = ref(false)
const { progressValue } = useProgressCircular(loading)
const error = ref<string | null>(null)

const formOpen = ref(false)
const editingPlay = ref<Play | null>(null)
const saving = ref(false)
const formError = ref<string | null>(null)

const confirmRemovePlayOpen = ref(false)
const playToRemove = ref<Play | null>(null)
const removingPlay = ref(false)

const categories = ['Ataque', 'Defesa']

const form = ref({
  title: '',
  description: '',
  category: '' as string | null | '',
})

const fileInput = ref<HTMLInputElement | null>(null)
const imageFile = ref<File | null>(null)
const dragOver = ref(false)
const clearImageFlag = ref(false)
const confirmClearImageOpen = ref(false)

const imageViewerOpen = ref(false)
const imageViewerSrc = ref<string | null>(null)
const imageRotation = ref(0)

const imageIsRotated = computed(() => imageRotation.value % 180 !== 0)

const previewUrl = computed(() => {
  if (imageFile.value) return URL.createObjectURL(imageFile.value)
  return editingPlay.value?.image_url ?? null
})

function categoryColor(category: string): string {
  switch (category) {
    case 'Ataque':
      return 'error'
    case 'Defesa':
      return 'info'
    case 'Bola Parada':
      return 'warning'
    case 'Transição':
      return 'success'
    case 'Posse':
      return 'secondary'
    default:
      return 'primary'
  }
}

function openImageViewer(src: string) {
  imageViewerSrc.value = src
  imageRotation.value = 0
  imageViewerOpen.value = true
}

function rotateImage() {
  imageRotation.value = (imageRotation.value + 90) % 360
}

async function fetchPlays() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/playbook/plays/?ordering=-created_at')
    plays.value = Array.isArray(data) ? data : []
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao carregar Playbook (HTTP ${status}).` : 'Falha ao carregar Playbook.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingPlay.value = null
  form.value = { title: '', description: '', category: '' }
  imageFile.value = null
  clearImageFlag.value = false
  formError.value = null
  formOpen.value = true
}

function openEdit(p: Play) {
  editingPlay.value = p
  form.value = {
    title: p.title ?? '',
    description: p.description ?? '',
    category: p.category ?? '',
  }
  imageFile.value = null
  clearImageFlag.value = false
  formError.value = null
  formOpen.value = true
}

function closeForm() {
  formOpen.value = false
  editingPlay.value = null
  imageFile.value = null
  clearImageFlag.value = false
  confirmClearImageOpen.value = false
  dragOver.value = false
}

function openFilePicker() {
  if (saving.value) return
  fileInput.value?.click()
}

function onDragOver() {
  if (saving.value) return
  dragOver.value = true
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  if (saving.value) return
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) return
  imageFile.value = file
  clearImageFlag.value = false
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) return
  imageFile.value = file
  clearImageFlag.value = false
  input.value = ''
}

function requestClearImage() {
  if (saving.value) return

  // Se existe imagem já salva, confirmar antes de marcar para remoção.
  if (editingPlay.value?.image_url) {
    confirmClearImageOpen.value = true
    return
  }

  // Caso contrário, é só limpar a seleção local (ex: criando jogada).
  imageFile.value = null
  clearImageFlag.value = false
}

function confirmClearImage() {
  imageFile.value = null
  clearImageFlag.value = true
  confirmClearImageOpen.value = false
}

async function submit() {
  if (!form.value.title?.trim()) return

  saving.value = true
  formError.value = null

  try {
    const fd = new FormData()
    fd.append('title', form.value.title.trim())
    fd.append('description', form.value.description?.trim() ? form.value.description.trim() : '')
    if (form.value.category) fd.append('category', String(form.value.category))

    if (imageFile.value) {
      fd.append('image', imageFile.value)
    }
    if (clearImageFlag.value) {
      fd.append('clear_image', 'true')
    }

    if (editingPlay.value?.id) {
      await http.patch(`/playbook/plays/${editingPlay.value.id}/`, fd)
    } else {
      await http.post('/playbook/plays/', fd)
    }

    await fetchPlays()
    closeForm()
  } catch (e: any) {
    const status = e?.response?.status
    formError.value = status ? `Falha ao salvar (HTTP ${status}).` : 'Falha ao salvar.'
  } finally {
    saving.value = false
  }
}

async function removePlay(p: Play) {
  try {
    await http.delete(`/playbook/plays/${p.id}/`)
    await fetchPlays()
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao remover (HTTP ${status}).` : 'Falha ao remover.'
  }
}

function requestRemovePlay(p: Play) {
  if (removingPlay.value) return
  playToRemove.value = p
  confirmRemovePlayOpen.value = true
}

async function confirmRemovePlay() {
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

onMounted(fetchPlays)
</script>

<style scoped>
.image-viewer {
  width: 100%;
  height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-viewer--rotated {
  height: min(80vh, 100vw);
}

.image-viewer__img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transform: rotate(var(--image-rotate, 0deg));
  transform-origin: center;
}
</style>

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

.play-image {
  position: relative;
  overflow: hidden;
}

.play-image__placeholder {
  height: 208px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.play-actions {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 160ms ease;
  background: rgba(0, 0, 0, 0.45);
}

.play-actions--show {
  opacity: 1;
}

.play-badge {
  position: absolute;
  top: 12px;
  left: 12px;
}

.form-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.dropzone {
  border-radius: 16px;
  border: 2px dashed rgba(var(--v-theme-on-surface), 0.25);
  background: rgba(var(--v-theme-surface), 0.40);
  cursor: pointer;
  overflow: hidden;
}

.dropzone--over {
  border-color: rgba(var(--v-theme-primary), 0.9);
  background: rgba(var(--v-theme-primary), 0.08);
}

.dropzone__empty {
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 18px;
}

.dropzone__preview {
  position: relative;
  height: 240px;
}

.dropzone__preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.dropzone__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.45);
  opacity: 0;
  transition: opacity 160ms ease;
}

.dropzone__preview:hover .dropzone__overlay {
  opacity: 1;
}

.line-clamp-3 {
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
