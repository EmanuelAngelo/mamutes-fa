<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold">Atletas</h1>
      <v-btn variant="flat" @click="openCreate">Novo atleta</v-btn>
    </div>

    <v-card>
      <v-card-text>
        <v-text-field v-model="q" label="Buscar" density="compact" class="mb-3" />
        <v-table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Camisa</th>
              <th>Posição</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>{{ a.name }}</td>
              <td>{{ a.jersey_number || '-' }}</td>
              <td>{{ a.current_position || '-' }}</td>
              <td>
                <v-chip :color="a.is_active ? 'success' : 'warning'" variant="tonal" size="small">
                  {{ a.is_active ? 'Ativo' : 'Inativo' }}
                </v-chip>
              </td>
              <td class="text-right">
                <v-btn size="small" variant="tonal" @click="openEdit(a)">Editar</v-btn>
                <v-btn size="small" variant="text" color="error" @click="remove(a)">Excluir</v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" max-width="700">
      <v-card>
        <v-card-title>{{ editing?.id ? 'Editar atleta' : 'Novo atleta' }}</v-card-title>
        <v-card-text class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <v-text-field v-model="form.name" label="Nome" />
          <v-text-field v-model="form.jersey_number" label="Número camisa" type="number" />
          <v-select v-model="form.current_position" label="Posição atual" :items="positions" />
          <v-select v-model="form.desired_position" label="Posição desejada" :items="positions" />
          <v-text-field v-model="form.birth_city" label="Cidade nascimento" />
          <v-text-field v-model="form.birth_date" label="Data nascimento (YYYY-MM-DD)" />
          <v-text-field v-model="form.height_m" label="Altura (m)" />
          <v-text-field v-model="form.weight_kg" label="Peso (kg)" />
          <v-switch v-model="form.is_active" label="Ativo" />
          <v-textarea v-model="form.career_notes" label="Carreira / campeonatos" class="md:col-span-2" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog=false">Cancelar</v-btn>
          <v-btn variant="flat" :loading="saving" @click="save">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { http } from '@/api/http'

const athletes = ref<any[]>([])
const q = ref('')
const dialog = ref(false)
const saving = ref(false)
const editing = ref<any | null>(null)

const positions = [
  { title: 'Quarterback', value: 'QB' },
  { title: 'Center', value: 'C' },
  { title: 'Wide receiver', value: 'WR' },
  { title: 'Running back', value: 'RB' },
  { title: 'Defensive back', value: 'DB' },
  { title: 'Blitz/Rusher', value: 'R' },
  { title: 'Safety', value: 'S' },
  { title: 'Corne back', value: 'CB' },
]

const form = ref<any>({
  name: '',
  jersey_number: null,
  current_position: null,
  desired_position: null,
  birth_city: '',
  birth_date: '',
  height_m: '',
  weight_kg: '',
  career_notes: '',
  is_active: true,
})

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  if (!term) return athletes.value
  return athletes.value.filter(a => (a.name || '').toLowerCase().includes(term))
})

async function fetchAthletes() {
  const { data } = await http.get('/api/athletes/?ordering=name')
  athletes.value = data
}

function openCreate() {
  editing.value = null
  form.value = {
    name: '',
    jersey_number: null,
    current_position: null,
    desired_position: null,
    birth_city: '',
    birth_date: '',
    height_m: '',
    weight_kg: '',
    career_notes: '',
    is_active: true,
  }
  dialog.value = true
}

function openEdit(a: any) {
  editing.value = a
  form.value = { ...a }
  dialog.value = true
}

async function save() {
  saving.value = true
  try {
    if (editing.value?.id) {
      await http.patch(`/api/athletes/${editing.value.id}/`, form.value)
    } else {
      await http.post('/api/athletes/', form.value)
    }
    dialog.value = false
    await fetchAthletes()
  } finally {
    saving.value = false
  }
}

async function remove(a: any) {
  if (!confirm(`Excluir atleta ${a.name}?`)) return
  await http.delete(`/api/athletes/${a.id}/`)
  await fetchAthletes()
}

onMounted(fetchAthletes)
</script>