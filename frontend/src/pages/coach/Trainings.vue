<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        Treinos
        <v-btn color="primary" @click="dialog = true">Novo Treino</v-btn>
      </v-card-title>

      <v-card-text>
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
              <td>{{ t.date }}</td>
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
      </v-card-text>
    </v-card>

    <!-- Dialog Criar -->
    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>Novo Treino</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.date" label="Data (YYYY-MM-DD)" />
          <v-text-field v-model="form.location" label="Local" />
          <v-textarea v-model="form.notes" label="Observações" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog=false">Cancelar</v-btn>
          <v-btn color="primary" @click="createTraining">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '@/api/http'

const trainings = ref<any[]>([])
const dialog = ref(false)

const form = ref({
  date: '',
  location: '',
  notes: '',
})

async function fetchTrainings() {
  const { data } = await http.get('/api/trainings/?ordering=-date')
  trainings.value = data
}

async function createTraining() {
  await http.post('/api/trainings/', form.value)
  dialog.value = false
  form.value = { date: '', location: '', notes: '' }
  fetchTrainings()
}

onMounted(fetchTrainings)
</script>