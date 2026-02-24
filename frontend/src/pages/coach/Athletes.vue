<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        Atletas
        <v-btn color="primary" @click="dialog=true">Novo</v-btn>
      </v-card-title>

      <v-card-text>
        <v-table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Camisa</th>
              <th>Posição</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in athletes" :key="a.id">
              <td>{{ a.name }}</td>
              <td>{{ a.jersey_number || '-' }}</td>
              <td>{{ a.current_position || '-' }}</td>
              <td>
                <v-btn size="small" variant="tonal" @click="edit(a)">
                  Editar
                </v-btn>
                <v-btn size="small" color="error" variant="text" @click="remove(a)">
                  Excluir
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>{{ editing ? 'Editar' : 'Novo' }} Atleta</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Nome" />
          <v-text-field v-model="form.jersey_number" label="Camisa" type="number" />
          <v-text-field v-model="form.current_position" label="Posição Atual" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog=false">Cancelar</v-btn>
          <v-btn color="primary" @click="save">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '@/api/http'

const athletes = ref<any[]>([])
const dialog = ref(false)
const editing = ref<any | null>(null)

const form = ref<any>({
  name: '',
  jersey_number: null,
  current_position: '',
})

async function fetchAthletes() {
  const { data } = await http.get('/api/athletes/?ordering=name')
  athletes.value = data
}

function edit(a: any) {
  editing.value = a
  form.value = { ...a }
  dialog.value = true
}

async function save() {
  if (editing.value) {
    await http.patch(`/api/athletes/${editing.value.id}/`, form.value)
  } else {
    await http.post('/api/athletes/', form.value)
  }
  dialog.value = false
  editing.value = null
  fetchAthletes()
}

async function remove(a: any) {
  if (!confirm(`Excluir ${a.name}?`)) return
  await http.delete(`/api/athletes/${a.id}/`)
  fetchAthletes()
}

onMounted(fetchAthletes)
</script>