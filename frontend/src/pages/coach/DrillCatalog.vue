<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-format-list-bulleted</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Coach</div>
            <div class="text-h6 font-weight-bold">Catálogo de Drills</div>
          </div>
        </div>

        <v-btn class="mt-2 mt-sm-0" color="primary" variant="flat" rounded="xl" @click="openNew">
          <v-icon start>mdi-plus</v-icon>
          Novo Drill
        </v-btn>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
        <v-text-field
          v-model="q"
          label="Buscar"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          clearable
          @update:model-value="debouncedFetch"
        />

        <div class="table-scroll">
          <v-table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Descrição</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in drills" :key="d.id">
                <td>{{ d.name }}</td>
                <td>{{ d.category || '-' }}</td>
                <td class="text-truncate" style="max-width: 520px">{{ d.description || '-' }}</td>
                <td class="text-right">
                  <v-btn size="small" variant="tonal" class="mr-2" @click="openEdit(d)">Editar</v-btn>
                  <v-btn size="small" color="error" variant="text" @click="remove(d)">Excluir</v-btn>
                </td>
              </tr>
              <tr v-if="!drills.length && !loading">
                <td colspan="4" class="text-center text-medium-emphasis py-6">Nenhum drill encontrado</td>
              </tr>
            </tbody>
          </v-table>
        </div>

        <div v-if="loading" class="d-flex justify-center py-8">
          <v-progress-circular indeterminate />
        </div>
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" class="app-dialog" :fullscreen="display.smAndDown.value" max-width="560" scrollable>
      <v-card rounded="xl">
        <div class="app-dialog__header">
          <div class="text-h6 font-weight-bold">{{ editing ? 'Editar Drill' : 'Novo Drill' }}</div>
          <v-btn icon variant="text" :disabled="saving" @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text>
          <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>

          <v-text-field v-model="form.name" label="Nome" variant="outlined" density="comfortable" />
          <v-text-field v-model="form.category" label="Categoria (opcional)" variant="outlined" density="comfortable" />
          <v-textarea v-model="form.description" label="Descrição (opcional)" variant="outlined" density="comfortable" />
        </v-card-text>

        <v-card-actions>
          <div class="app-dialog__actions">
            <v-btn variant="outlined" rounded="lg" class="flex-grow-1" :disabled="saving" @click="dialog = false">
              Cancelar
            </v-btn>
            <v-btn color="primary" variant="flat" rounded="lg" class="flex-grow-1" :loading="saving" @click="save">
              {{ editing ? 'Salvar' : 'Adicionar' }}
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'

type DrillCatalog = {
  id: number
  name: string
  category?: string | null
  description?: string | null
}

const display = useDisplay()

const drills = ref<DrillCatalog[]>([])
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const editing = ref<DrillCatalog | null>(null)
const error = ref<string | null>(null)

const q = ref('')

const form = reactive({
  name: '',
  category: '',
  description: '',
})

function resetForm() {
  form.name = ''
  form.category = ''
  form.description = ''
  error.value = null
}

function openNew() {
  editing.value = null
  resetForm()
  dialog.value = true
}

function openEdit(d: DrillCatalog) {
  editing.value = d
  error.value = null
  form.name = d.name
  form.category = d.category ?? ''
  form.description = d.description ?? ''
  dialog.value = true
}

watch(dialog, (open) => {
  if (!open) {
    editing.value = null
    resetForm()
  }
})

async function fetchCatalog() {
  loading.value = true
  try {
    const params: any = { ordering: 'name' }
    if (q.value?.trim()) params.search = q.value.trim()
    const { data } = await http.get('/trainings/catalog/', { params })
    drills.value = data
  } finally {
    loading.value = false
  }
}

let debounceTimer: any = null
function debouncedFetch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchCatalog, 250)
}

async function save() {
  error.value = null
  if (!form.name.trim()) {
    error.value = 'Informe o nome.'
    return
  }

  saving.value = true
  try {
    const payload = {
      name: form.name.trim(),
      category: form.category.trim() || null,
      description: form.description.trim() || null,
    }

    if (editing.value) {
      await http.patch(`/trainings/catalog/${editing.value.id}/`, payload)
    } else {
      await http.post('/trainings/catalog/', payload)
    }

    dialog.value = false
    await fetchCatalog()
  } catch (e: any) {
    const msg = e?.response?.data?.name || e?.response?.data?.detail || 'Não foi possível salvar.'
    error.value = Array.isArray(msg) ? msg.join(' ') : String(msg)
  } finally {
    saving.value = false
  }
}

async function remove(d: DrillCatalog) {
  if (!confirm(`Excluir "${d.name}"?`)) return
  try {
    await http.delete(`/trainings/catalog/${d.id}/`)
    await fetchCatalog()
  } catch {
    alert('Não foi possível excluir.')
  }
}

onMounted(fetchCatalog)
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
