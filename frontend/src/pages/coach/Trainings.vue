<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold">Treinos</h1>
      <v-btn variant="flat" @click="createDialog = true">Novo treino</v-btn>
    </div>

    <v-card>
      <v-card-text>
        <v-table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Local</th>
              <th>Obs.</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in trainings" :key="t.id">
              <td>{{ t.date }}</td>
              <td>{{ t.location || '-' }}</td>
              <td class="max-w-[420px] truncate">{{ t.notes || '-' }}</td>
              <td class="text-right">
                <v-btn size="small" variant="tonal" :to="{ name: 'coach-training-detail', params: { id: t.id } }">
                  Abrir
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="createDialog" max-width="520">
      <v-card>
        <v-card-title>Novo treino</v-card-title>
        <v-card-text class="space-y-3">
          <v-text-field v-model="form.date" label="Data (YYYY-MM-DD)" />
          <v-text-field v-model="form.start_time" label="Horário (HH:MM:SS)" />
          <v-text-field v-model="form.location" label="Local" />
          <v-textarea v-model="form.notes" label="Observações" />
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="createDialog=false">Cancelar</v-btn>
          <v-btn variant="flat" :loading="saving" @click="createTraining">Criar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '@/api/http'

const trainings = ref<any[]>([])
const createDialog = ref(false)
const saving = ref(false)

const form = ref({
  date: '',
  start_time: '',
  location: '',
  notes: '',
})

async function fetchTrainings() {
  const { data } = await http.get('/api/trainings/?ordering=-date')
  trainings.value = data
}

async function createTraining() {
  saving.value = true
  try {
    const { data } = await http.post('/api/trainings/', form.value)
    createDialog.value = false
    form.value = { date: '', start_time: '', location: '', notes: '' }
    await fetchTrainings()
  } finally {
    saving.value = false
  }
}

onMounted(fetchTrainings)
</script>