<template>
  <v-container>
    <v-sheet class="athletes-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="athletes-header__icon">
            <v-icon size="26">mdi-trophy</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Gestão de Atletas</div>
          </div>
        </div>

        <v-btn color="primary" variant="flat" rounded="xl" @click="openNew">
          <v-icon start>mdi-plus</v-icon>
          Novo Atleta
        </v-btn>
      </div>
    </v-sheet>

    <v-row density="comfortable" class="mt-4">
      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--info">
              <v-icon>mdi-account-group</v-icon>
            </div>
            <div>
              <div class="text-body-2 text-medium-emphasis">Total de Atletas</div>
              <div class="text-h5 font-weight-bold">{{ statsTotal }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--success">
              <v-icon>mdi-trending-up</v-icon>
            </div>
            <div>
              <div class="text-body-2 text-medium-emphasis">Média Geral</div>
              <div class="text-h5 font-weight-bold">{{ statsAvgRating }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card variant="tonal" class="stats-card" rounded="xl">
          <v-card-text class="d-flex align-center ga-4">
            <div class="stats-card__icon stats-card__icon--warning">
              <v-icon>mdi-trophy</v-icon>
            </div>
            <div class="flex-grow-1">
              <div class="text-body-2 text-medium-emphasis">Melhor Desempenho</div>
              <div class="text-subtitle-1 font-weight-bold text-truncate">
                {{ statsTopPerformerName }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row density="comfortable" class="mt-2">
      <v-col cols="12" sm="8">
        <v-text-field
          v-model="search"
          label="Buscar atleta..."
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-magnify"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="positionFilter"
          :items="positionFilterItems"
          item-title="label"
          item-value="value"
          label="Posição"
          variant="outlined"
          prepend-inner-icon="mdi-filter"
        />
      </v-col>
    </v-row>

    <v-row density="comfortable" class="mt-2">
      <template v-if="loadingAthletes">
        <v-col v-for="i in 8" :key="i" cols="12" sm="6" md="4" lg="3">
          <v-skeleton-loader type="card" class="rounded-xl" />
        </v-col>
      </template>

      <template v-else-if="filteredAthletes.length">
        <v-col
          v-for="(a, index) in filteredAthletes"
          :key="a.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <div class="athlete-card" :style="{ '--delay': `${index * 50}ms` }">
            <div class="athlete-card__under" />

            <v-card class="athlete-card__main" rounded="xl">
              <div class="athlete-card__watermark">{{ jerseyText(a) }}</div>

              <div class="athlete-card__photo">
                <div class="athlete-card__glow" />
                <div class="athlete-card__photo-inner">
                  <v-img v-if="athletePhotoUrl(a)" :src="athletePhotoUrl(a)" cover />
                  <div v-else class="athlete-card__photo-empty">
                    <v-icon size="44" class="opacity-60">mdi-account</v-icon>
                  </div>
                </div>

                <div class="athlete-card__badge">{{ jerseyText(a) }}</div>
              </div>

              <div class="athlete-card__info">
                <div class="athlete-card__name" :title="a.name">{{ a.name }}</div>
                <div class="athlete-card__pos">{{ (a.current_position || '-').toString() }}</div>

                <div class="athlete-card__status">
                  <span class="athlete-card__dot" :class="statusDotClass(a)" />
                  <span class="text-medium-emphasis">{{ a.is_active ? 'Ativo' : 'Inativo' }}</span>
                </div>

                <div class="athlete-card__rating">
                  <div class="athlete-card__rating-title">
                    <v-icon size="16" class="athlete-card__star">mdi-star</v-icon>
                    <span>Desempenho</span>
                  </div>

                  <div class="athlete-card__rating-pill" :class="ratingClass(a)">
                    <span class="athlete-card__rating-score">{{ ratingValue(a).toFixed(1) }}</span>
                    <span class="athlete-card__rating-label">{{ ratingLabel(ratingValue(a)) }}</span>
                  </div>
                </div>

                <div class="athlete-card__actions">
                  <v-btn size="small" variant="tonal" class="flex-grow-1" @click.stop="edit(a)">
                    <v-icon start size="16">mdi-pencil</v-icon>
                    Editar
                  </v-btn>
                  <v-btn size="small" variant="tonal" color="error" @click.stop="askRemove(a)">
                    <v-icon size="16">mdi-trash-can</v-icon>
                  </v-btn>
                </div>
              </div>
            </v-card>
          </div>
        </v-col>
      </template>

      <v-col v-else cols="12">
        <div class="text-center py-10">
          <div class="empty-state__icon mb-4">
            <v-icon size="40" class="opacity-60">mdi-account-group</v-icon>
          </div>
          <div class="text-h6 font-weight-bold">
            {{ search || positionFilter !== 'all' ? 'Nenhum atleta encontrado' : 'Nenhum atleta cadastrado' }}
          </div>
          <div class="text-body-2 text-medium-emphasis mt-1 mb-4">
            {{
              search || positionFilter !== 'all'
                ? 'Tente ajustar os filtros de busca'
                : 'Comece adicionando seu primeiro atleta ao time'
            }}
          </div>
          <v-btn v-if="!search && positionFilter === 'all'" color="primary" variant="tonal" @click="openNew">
            <v-icon start>mdi-plus</v-icon>
            Adicionar Atleta
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-dialog
      v-model="dialog"
      class="athlete-form-dialog"
      max-width="560"
      transition="scale-transition"
      scrollable
    >
      <v-card class="athlete-form-card" rounded="xl">
        <div class="athlete-form__header">
          <div class="text-h6 font-weight-bold">
            {{ editing ? 'Editar Atleta' : 'Novo Atleta' }}
          </div>
          <v-btn
            icon
            variant="text"
            :disabled="saving"
            class="athlete-form__close"
            @click="dialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider />

        <v-card-text class="athlete-form__body">
          <form @submit.prevent="save">
            <div class="athlete-form__photo">
              <button
                type="button"
                class="athlete-form__photo-btn"
                :disabled="saving"
                @click="pickPhoto"
              >
                <div class="athlete-form__photo-ring">
                  <v-avatar size="96" class="athlete-form__photo-avatar">
                    <v-img v-if="photoPreviewUrl" :src="photoPreviewUrl" cover />
                    <div v-else class="athlete-form__photo-empty">
                      <v-icon size="44" class="opacity-60">mdi-account</v-icon>
                    </div>
                  </v-avatar>
                </div>

                <div class="athlete-form__photo-overlay" :class="{ 'is-visible': saving }">
                  <v-progress-circular
                    v-if="saving && hasNewPhoto"
                    indeterminate
                    size="26"
                    width="3"
                  />
                  <v-icon v-else size="26">mdi-upload</v-icon>
                </div>
              </button>

              <input
                ref="photoInput"
                class="athlete-form__photo-input"
                type="file"
                accept="image/*"
                :disabled="saving"
                @change="onPhotoPicked"
              />
            </div>

            <v-text-field
              v-model="form.name"
              label="Nome do Atleta"
              variant="outlined"
              density="comfortable"
              class="mt-2"
            />

            <v-row density="comfortable">
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="form.jersey_number"
                  label="Número"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.current_position"
                  :items="positionItems"
                  item-title="label"
                  item-value="value"
                  label="Posição"
                  variant="outlined"
                  density="comfortable"
                  clearable
                />
              </v-col>
            </v-row>

            <v-row density="comfortable">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.is_active"
                  :items="statusItems"
                  item-title="label"
                  item-value="value"
                  label="Status"
                  variant="outlined"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.desired_position"
                  :items="positionItems"
                  item-title="label"
                  item-value="value"
                  label="Posição Desejada"
                  variant="outlined"
                  density="comfortable"
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

            <v-autocomplete
              :model-value="linkedUserDisplay"
              :loading="linkedUserLoading"
              label="Usuário"
              variant="outlined"
              density="comfortable"
              readonly
              hint="No cadastro, o usuário é criado aqui e vinculado automaticamente. Na edição, este vínculo é travado."
              persistent-hint
            />

            <v-btn
              v-if="!editing"
              variant="tonal"
              size="small"
              class="mb-4"
              :disabled="saving || !!form.user"
              @click="openCreateUser"
            >
              Criar usuário e vincular
            </v-btn>

            <v-textarea
              v-model="form.career_notes"
              label="Observações"
              variant="outlined"
              density="comfortable"
            />

            <div class="athlete-form__actions">
              <v-btn
                variant="outlined"
                rounded="lg"
                class="flex-grow-1"
                :disabled="saving"
                @click="dialog = false"
              >
                Cancelar
              </v-btn>
              <v-btn
                type="submit"
                color="primary"
                variant="flat"
                rounded="lg"
                class="flex-grow-1"
                :loading="saving"
              >
                {{ editing ? 'Salvar' : 'Adicionar' }}
              </v-btn>
            </div>
          </form>
        </v-card-text>
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

    <v-dialog v-model="deleteDialog" max-width="520">
      <v-card>
        <v-card-title>Remover Atleta</v-card-title>
        <v-card-text>
          Tem certeza que deseja remover
          <strong>{{ deleteTarget?.name }}</strong>
          do time? Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" :disabled="deleting" @click="closeDelete">Cancelar</v-btn>
          <v-btn color="error" variant="tonal" :loading="deleting" @click="confirmRemove">Remover</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'

const athletes = ref<any[]>([])
const loadingAthletes = ref(false)

const loadingStats = ref(false)
const stats = ref<{ total: number; avg_rating: number; top_performer: { id: number; name: string; rating: number } | null }>({
  total: 0,
  avg_rating: 0,
  top_performer: null,
})
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

const linkedUserItem = ref<UserItem | null>(null)
const linkedUserLoading = ref(false)

const saving = ref(false)

const search = ref('')
const positionFilter = ref<'all' | string>('all')

const deleteDialog = ref(false)
const deleteTarget = ref<any | null>(null)
const deleting = ref(false)

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

function jerseyText(a: any): string {
  const n = a?.jersey_number
  if (n === null || n === undefined || n === '') return '-'
  return String(n)
}

function ratingValue(a: any): number {
  const v = a?.rating
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) ? Math.max(0, Math.min(10, n)) : 0
}

function ratingClass(a: any): string {
  const r = ratingValue(a)
  if (r >= 8) return 'rating--good'
  if (r >= 6) return 'rating--ok'
  if (r >= 4) return 'rating--mid'
  return 'rating--bad'
}

function ratingLabel(r: number): string {
  if (r >= 9) return 'Excelente'
  if (r >= 7) return 'Muito bom'
  if (r >= 5) return 'Regular'
  if (r >= 3) return 'Fraco'
  return 'Crítico'
}

function statusDotClass(a: any): string {
  return a?.is_active ? 'dot--active' : 'dot--inactive'
}

function apiOrigin(): string {
  const base = String(http.defaults.baseURL || '')
  if (!base) return ''
  return base.replace(/\/api\/?$/, '').replace(/\/+$/, '')
}

function athletePhotoUrl(a: any): string | undefined {
  const photo = a?.photo
  if (!photo || typeof photo !== 'string') return undefined
  if (photo.startsWith('http://') || photo.startsWith('https://')) return photo
  const origin = apiOrigin()
  if (!origin) return photo
  if (photo.startsWith('/')) return `${origin}${photo}`
  return `${origin}/${photo}`
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

const statusItems = [
  { label: 'Ativo', value: true },
  { label: 'Inativo', value: false },
]

const photoInput = ref<HTMLInputElement | null>(null)
const photoPreviewUrl = ref<string | null>(null)

function pickPhoto() {
  if (saving.value) return
  photoInput.value?.click()
}

function onPhotoPicked(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  form.value.photo = file
  input.value = ''
}

function updatePhotoPreview() {
  if (photoPreviewUrl.value?.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(photoPreviewUrl.value)
    } catch {
      // ignore
    }
  }

  const f = form.value?.photo
  if (f instanceof File) {
    photoPreviewUrl.value = URL.createObjectURL(f)
    return
  }

  if (editing.value?.photo) {
    photoPreviewUrl.value = athletePhotoUrl(editing.value) || null
    return
  }

  photoPreviewUrl.value = null
}

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

const positionFilterItems = computed(() => [
  { label: 'Todas posições', value: 'all' },
  ...positionItems,
])

const filteredAthletes = computed(() => {
  return athletes.value
})

const hasNewPhoto = computed(() => form.value.photo instanceof File)

const statsTotal = computed(() => stats.value.total ?? 0)
const statsAvgRating = computed(() => Number(stats.value.avg_rating ?? 0).toFixed(1))
const statsTopPerformerName = computed(() => stats.value.top_performer?.name || '-')

function buildAthletesParams() {
  const params: any = { ordering: 'name' }
  const q = search.value.trim()
  if (q) params.search = q
  if (positionFilter.value !== 'all') params.current_position = positionFilter.value
  return params
}

async function fetchAthletes() {
  loadingAthletes.value = true
  try {
    const params = buildAthletesParams()
    const { data } = await http.get('/athletes/', { params })
    athletes.value = data
  } finally {
    loadingAthletes.value = false
  }
}

async function fetchStats() {
  loadingStats.value = true
  try {
    const params = buildAthletesParams()
    const { data } = await http.get('/athletes/stats/', { params })
    stats.value = {
      total: data?.total ?? 0,
      avg_rating: Number(data?.avg_rating ?? 0),
      top_performer: data?.top_performer ?? null,
    }
  } finally {
    loadingStats.value = false
  }
}

async function refreshAthletesAndStats() {
  await Promise.all([fetchAthletes(), fetchStats()])
}

function toUserLabel(u: any): string {
  const email = u.email ? ` • ${u.email}` : ''
  return `${u.username}${email}`
}

async function fetchLinkedUser(userId?: number | null) {
  if (!userId) {
    linkedUserItem.value = null
    return
  }

  linkedUserLoading.value = true
  try {
    const params: any = { ordering: 'username', unlinked: 0, include: userId }
    const { data } = await http.get('/accounts/users/', { params })
    const items: UserItem[] = (data || []).map((u: any) => ({ ...u, label: toUserLabel(u) }))
    linkedUserItem.value = items.find((u) => u.id === userId) ?? null
  } finally {
    linkedUserLoading.value = false
  }
}

const linkedUserDisplay = computed(() => {
  if (linkedUserItem.value) return linkedUserItem.value.label
  if (!form.value?.user) return ''
  return `ID ${String(form.value.user)}`
})

function openNew() {
  editing.value = null
  form.value = emptyForm()
  dialog.value = true
  linkedUserItem.value = null
  updatePhotoPreview()
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
  fetchLinkedUser(a.user)
  updatePhotoPreview()
}

watch(dialog, (isOpen) => {
  if (!isOpen) {
    editing.value = null
    form.value = emptyForm()
    updatePhotoPreview()
  }
})

watch(
  () => form.value?.photo,
  () => updatePhotoPreview()
)

function openCreateUser() {
  if (editing.value) return
  if (form.value?.user) return
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
    form.value.user = item.id
    linkedUserItem.value = item
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
  if (saving.value) return
  saving.value = true
  const hasPhoto = form.value.photo instanceof File
  const endpoint = editing.value ? `/athletes/${editing.value.id}/` : '/athletes/'

  try {
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
    await refreshAthletesAndStats()
  } catch {
    alert('Não foi possível salvar.')
  } finally {
    saving.value = false
  }
}

function askRemove(a: any) {
  deleteTarget.value = a
  deleteDialog.value = true
}

function closeDelete() {
  deleteDialog.value = false
  deleteTarget.value = null
}

async function confirmRemove() {
  if (!deleteTarget.value || deleting.value) return
  deleting.value = true
  try {
    await http.delete(`/athletes/${deleteTarget.value.id}/`)
    closeDelete()
    await fetchAthletes()
  } catch {
    alert('Não foi possível excluir.')
  } finally {
    deleting.value = false
  }
}

onMounted(fetchAthletes)
onMounted(fetchStats)

let filterTimer: any = null
watch([search, positionFilter], () => {
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    refreshAthletesAndStats()
  }, 250)
})
</script>

<style scoped>
.athletes-header {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 16px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.70);
  backdrop-filter: blur(12px);
}

.athletes-header__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(var(--v-theme-on-warning), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-warning), 1),
    rgba(var(--v-theme-warning), 0.75)
  );
}

.stats-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.55);
  backdrop-filter: blur(10px);
}

.stats-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-card__icon--info {
  background: rgba(var(--v-theme-info), 0.18);
  color: rgba(var(--v-theme-info), 1);
}

.stats-card__icon--success {
  background: rgba(var(--v-theme-success), 0.18);
  color: rgba(var(--v-theme-success), 1);
}

.stats-card__icon--warning {
  background: rgba(var(--v-theme-warning), 0.18);
  color: rgba(var(--v-theme-warning), 1);
}

.athlete-form-dialog :deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.6) !important;
  backdrop-filter: blur(8px);
}

.athlete-form-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.98);
}

.athlete-form__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
}

.athlete-form__close {
  opacity: 0.8;
}

.athlete-form__body {
  padding: 18px;
}

.athlete-form__photo {
  display: flex;
  justify-content: center;
}

.athlete-form__photo-btn {
  position: relative;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.athlete-form__photo-btn:disabled {
  cursor: default;
  opacity: 0.9;
}

.athlete-form__photo-ring {
  padding: 4px;
  border-radius: 999px;
  background: rgba(var(--v-theme-primary), 0.22);
}

.athlete-form__photo-avatar {
  background: rgba(var(--v-theme-surface-variant), 1);
}

.athlete-form__photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.athlete-form__photo-overlay {
  position: absolute;
  inset: 4px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  color: white;
  opacity: 0;
  transition: opacity 120ms ease;
}

.athlete-form__photo-btn:hover .athlete-form__photo-overlay {
  opacity: 1;
}

.athlete-form__photo-overlay.is-visible {
  opacity: 1;
}

.athlete-form__photo-input {
  display: none;
}

.athlete-form__actions {
  display: flex;
  gap: 12px;
  padding-top: 12px;
}

.empty-state__icon {
  width: 80px;
  height: 80px;
  border-radius: 999px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.55);
}

.athlete-card {
  position: relative;
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
  transition: transform 220ms ease;
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
  transition: transform 220ms ease;
  animation: athleteFadeUp 320ms ease both;
  animation-delay: var(--delay, 0ms);
}

.athlete-card:hover .athlete-card__under {
  transform: rotate(2deg);
}

.athlete-card:hover .athlete-card__main {
  transform: translateY(-8px) scale(1.02);
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
  font-weight: 800;
  color: rgba(var(--v-theme-on-warning), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-warning), 1),
    rgba(var(--v-theme-warning), 0.75)
  );
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.22);
}

.athlete-card__info {
  padding: 8px 18px 16px;
  text-align: center;
}

.athlete-card__name {
  font-size: 18px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.athlete-card__pos {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-warning), 0.95);
}

.athlete-card__status {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
}

.athlete-card__dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.dot--active {
  background: rgba(var(--v-theme-success), 1);
}

.dot--inactive {
  background: rgba(var(--v-theme-on-surface), 0.35);
}

.athlete-card__rating {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.athlete-card__rating-title {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.athlete-card__star {
  color: rgba(var(--v-theme-warning), 1);
}

.athlete-card__rating-pill {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  color: rgba(var(--v-theme-on-primary), 1);
}

.athlete-card__rating-score {
  font-size: 22px;
  font-weight: 900;
}

.athlete-card__rating-label {
  font-size: 11px;
  opacity: 0.9;
  font-weight: 700;
}

.rating--good {
  background: linear-gradient(90deg, rgba(var(--v-theme-success), 1), rgba(var(--v-theme-success), 0.78));
}

.rating--ok {
  background: linear-gradient(90deg, rgba(var(--v-theme-warning), 1), rgba(var(--v-theme-warning), 0.78));
}

.rating--mid {
  background: linear-gradient(90deg, rgba(var(--v-theme-primary), 1), rgba(var(--v-theme-primary), 0.78));
}

.rating--bad {
  background: linear-gradient(90deg, rgba(var(--v-theme-error), 1), rgba(var(--v-theme-error), 0.78));
}

.athlete-card__actions {
  margin-top: 14px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 220ms ease, transform 220ms ease;
}

.athlete-card:hover .athlete-card__actions {
  opacity: 1;
  transform: translateY(0);
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