<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-whistle</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Coach</div>
            <div class="text-h6 font-weight-bold">Treinos</div>
          </div>
        </div>

        <v-btn class="mt-2 mt-sm-0" color="primary" variant="flat" rounded="xl" @click="openNew">
          <v-icon start>mdi-plus</v-icon>
          Novo Treino
        </v-btn>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
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

        <div class="table-scroll">
          <v-table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Local</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in trainings" :key="t.id">
                <td>{{ formatDateBR(t.date) }}</td>
                <td>{{ t.location || '-' }}</td>
                <td>
                  <v-btn
                    size="small"
                    variant="tonal"
                    :to="{ name: 'coach-training-detail', params: { id: t.id } }"
                  >
                    Abrir
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>
      </v-card-text>
    </v-card>

    <!-- Dialog Criar -->
    <v-dialog v-model="dialog" class="app-dialog" :fullscreen="display.smAndDown.value" max-width="560" scrollable>
      <v-card rounded="xl">
        <div class="app-dialog__header">
          <div class="text-h6 font-weight-bold">Novo Treino</div>
          <v-btn icon variant="text" :disabled="saving" @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text>
          <v-menu v-model="dateMenu" :close-on-content-click="false" location="bottom">
            <template #activator="{ props }">
              <v-text-field
                v-bind="props"
                :model-value="formatDateBR(form.date)"
                label="Data"
                readonly
                clearable
                prepend-inner-icon="mdi-calendar"
                variant="outlined"
                density="comfortable"
                @click:clear="clearDate"
              />
            </template>
            <v-date-picker :model-value="form.date" @update:model-value="onPickDate" />
          </v-menu>
          <v-text-field v-model="form.location" label="Local" variant="outlined" density="comfortable" />
          <v-textarea v-model="form.notes" label="Observações" variant="outlined" density="comfortable" />
        </v-card-text>

        <v-card-actions>
          <div class="app-dialog__actions">
            <v-btn variant="outlined" rounded="lg" class="flex-grow-1" :disabled="saving" @click="dialog = false">
              Cancelar
            </v-btn>
            <v-btn color="primary" variant="flat" rounded="lg" class="flex-grow-1" :loading="saving" @click="createTraining">
              Salvar
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'
import { usePageProgressLoading } from '@/composables/usePageProgressLoading'

const trainings = ref<any[]>([])
const loading = ref(false)
const dialog = ref(false)
const display = useDisplay()
const dateMenu = ref(false)
const saving = ref(false)

const firstLoad = ref(true)
const { value: progress, start: startLoading, stop: stopLoading } = usePageProgressLoading({
  minDurationMs: 5000,
})

function formatDateBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const m = /^\d{4}-\d{2}-\d{2}$/.exec(iso)
  if (!m) return iso
  const [y, mm, dd] = iso.split('-')
  return `${dd}/${mm}/${y}`
}

function clearDate() {
  form.value.date = ''
}

function normalizeDate(value: unknown): string {
  const v = Array.isArray(value) ? value[0] : value
  if (!v) return ''
  if (v instanceof Date) return v.toISOString().slice(0, 10)
  if (typeof v === 'string') return v.includes('T') ? v.slice(0, 10) : v
  return String(v)
}

function onPickDate(value: unknown) {
  form.value.date = normalizeDate(value)
  dateMenu.value = false
}

function emptyForm() {
  return {
    date: '',
    location: '',
    notes: '',
  }
}

const form = ref(emptyForm())

function openNew() {
  form.value = emptyForm()
  dialog.value = true
}

watch(dialog, (isOpen) => {
  if (!isOpen) {
    form.value = emptyForm()
  }
})

async function fetchTrainings() {
  loading.value = true
  startLoading()
  try {
    const { data } = await http.get('/trainings/?ordering=-date')
    trainings.value = data
  } finally {
    loading.value = false
    await stopLoading({ minDurationMs: firstLoad.value ? 5000 : 0 })
    firstLoad.value = false
  }
}

async function createTraining() {
  if (saving.value) return
  saving.value = true
  try {
    await http.post('/trainings/', form.value)
    dialog.value = false
    form.value = emptyForm()
    await fetchTrainings()
  } finally {
    saving.value = false
  }
}

onMounted(fetchTrainings)
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