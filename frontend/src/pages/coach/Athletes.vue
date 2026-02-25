<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex flex-wrap justify-space-between">
        Atletas
        <v-btn class="mt-2 mt-sm-0" color="primary" @click="openNew">Novo</v-btn>
      </v-card-title>

      <v-card-text>
        <div class="table-scroll">
          <v-table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Camisa</th>
                <th>Posição</th>
                <th>Ativo</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in athletes" :key="a.id">
                <td>{{ a.name }}</td>
                <td>{{ a.jersey_number || '-' }}</td>
                <td>{{ a.current_position || '-' }}</td>
                <td>{{ a.is_active ? 'Sim' : 'Não' }}</td>
                <td>
                  <v-btn size="small" variant="tonal" @click="edit(a)">Editar</v-btn>
                  <v-btn size="small" color="error" variant="text" @click="remove(a)">Excluir</v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" :fullscreen="display.smAndDown.value" max-width="600" scrollable>
      <v-card>
        <v-card-title>{{ editing ? 'Editar' : 'Novo' }} Atleta</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Nome" />

          <v-row>
            <v-col cols="12" md="4">
              <v-text-field v-model.number="form.jersey_number" label="Camisa" type="number" />
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="form.current_position"
                :items="positionItems"
                item-title="label"
                item-value="value"
                label="Posição Atual"
                clearable
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="form.desired_position"
                :items="positionItems"
                item-title="label"
                item-value="value"
                label="Posição Desejada"
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
                    @click:clear="clearBirthDate"
                  />
                </template>
                <v-date-picker :model-value="form.birth_date" @update:model-value="onPickBirthDate" />
              </v-menu>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.birth_city" label="Cidade de nascimento" />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model.number="form.height_m" label="Altura (m)" type="number" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model.number="form.weight_kg" label="Peso (kg)" type="number" />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model.number="form.user" label="User ID (opcional)" type="number" />
            </v-col>
            <v-col cols="12" md="6">
              <v-switch v-model="form.is_active" label="Ativo" inset />
            </v-col>
          </v-row>

          <v-textarea v-model="form.career_notes" label="Observações" />

          <v-file-input v-model="form.photo" label="Foto (opcional)" accept="image/*" prepend-icon="" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="save">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'

const athletes = ref<any[]>([])
const dialog = ref(false)
const editing = ref<any | null>(null)
const display = useDisplay()
const birthDateMenu = ref(false)

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

async function fetchAthletes() {
  const { data } = await http.get('/athletes/?ordering=name')
  athletes.value = data
}

function openNew() {
  editing.value = null
  form.value = emptyForm()
  dialog.value = true
}

function edit(a: any) {
  editing.value = a
  form.value = {
    ...a,
    photo: null,
    birth_date: a.birth_date ?? '',
    birth_city: a.birth_city ?? '',
    career_notes: a.career_notes ?? '',
  }
  dialog.value = true
}

watch(dialog, (isOpen) => {
  if (!isOpen) {
    editing.value = null
    form.value = emptyForm()
  }
})

async function save() {
  const hasPhoto = form.value.photo instanceof File
  const endpoint = editing.value ? `/athletes/${editing.value.id}/` : '/athletes/'

  if (hasPhoto) {
    const fd = new FormData()
    for (const [k, v] of Object.entries(form.value)) {
      if (v === null || v === undefined || v === '') continue
      if (k === 'photo') fd.append('photo', v as File)
      else fd.append(k, String(v))
    }

    if (editing.value) await http.patch(endpoint, fd)
    else await http.post(endpoint, fd)
  } else {
    const payload = { ...form.value }
    delete payload.photo
    if (editing.value) await http.patch(endpoint, payload)
    else await http.post(endpoint, payload)
  }

  dialog.value = false
  await fetchAthletes()
}

async function remove(a: any) {
  if (!confirm(`Excluir ${a.name}?`)) return
  await http.delete(`/athletes/${a.id}/`)
  await fetchAthletes()
}

onMounted(fetchAthletes)
</script>