<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex flex-wrap justify-space-between align-center">
        Catálogo de Drills
        <v-btn class="mt-2 mt-sm-0" color="primary" @click="openNew">Novo Drill</v-btn>
      </v-card-title>

      <v-card-text>
        <v-text-field
          v-model="q"
          label="Buscar"
          variant="outlined"
          density="compact"
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

        <v-progress-circular v-if="loading" indeterminate class="mt-4" />
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" :fullscreen="display.smAndDown.value" max-width="640" scrollable>
      <v-card>
        <v-card-title>{{ editing ? 'Editar' : 'Novo' }} Drill</v-card-title>
        <v-card-text>
          <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>

          <v-text-field v-model="form.name" label="Nome" />
          <v-text-field v-model="form.category" label="Categoria (opcional)" />
          <v-textarea v-model="form.description" label="Descrição (opcional)" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" :disabled="saving" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="saving" @click="save">Salvar</v-btn>
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
