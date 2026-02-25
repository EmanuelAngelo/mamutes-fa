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
              <v-autocomplete
                v-model="form.user"
                :items="users"
                :loading="usersLoading"
                item-title="label"
                item-value="id"
                label="Usuário (opcional)"
                clearable
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-switch v-model="form.is_active" label="Ativo" inset />
            </v-col>
          </v-row>

          <v-btn variant="tonal" size="small" class="mb-4" @click="openCreateUser">Criar usuário</v-btn>

          <v-textarea v-model="form.career_notes" label="Observações" />

          <v-file-input v-model="form.photo" label="Foto (opcional)" accept="image/*" prepend-icon="" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="save">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="createUserDialog" :fullscreen="display.smAndDown.value" max-width="560" scrollable>
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
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'

const athletes = ref<any[]>([])
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

const users = ref<UserItem[]>([])
const usersLoading = ref(false)

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

function toUserLabel(u: any): string {
  const email = u.email ? ` • ${u.email}` : ''
  return `${u.username}${email}`
}

async function fetchUsers(includeId?: number | null) {
  usersLoading.value = true
  try {
    const params: any = { ordering: 'username', unlinked: 1 }
    if (includeId) params.include = includeId
    const { data } = await http.get('/accounts/users/', { params })
    users.value = (data || []).map((u: any) => ({ ...u, label: toUserLabel(u) }))
  } finally {
    usersLoading.value = false
  }
}

function openNew() {
  editing.value = null
  form.value = emptyForm()
  dialog.value = true
  fetchUsers(null)
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
  fetchUsers(a.user)
}

watch(dialog, (isOpen) => {
  if (!isOpen) {
    editing.value = null
    form.value = emptyForm()
  }
})

function openCreateUser() {
  createUserError.value = null
  createUserForm.value = { username: '', email: '', first_name: '', last_name: '', password: '' }
  createUserDialog.value = true
}

async function createUser() {
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
    users.value = [...users.value, item].sort((a, b) => a.username.localeCompare(b.username))
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
onMounted(() => fetchUsers(null))
</script>