<template>
  <v-container>
    <v-card>
      <v-card-title class="d-flex flex-wrap justify-space-between align-center">
        Treinos
        <v-btn class="mt-2 mt-sm-0" color="primary" @click="openNew">Novo Treino</v-btn>
      </v-card-title>

      <v-card-text>
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
        </div>
      </v-card-text>
    </v-card>

    <!-- Dialog Criar -->
    <v-dialog v-model="dialog" :fullscreen="display.smAndDown.value" max-width="500" scrollable>
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
import { onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { http } from '../../api/http'

const trainings = ref<any[]>([])
const dialog = ref(false)
const display = useDisplay()

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
  const { data } = await http.get('/trainings/?ordering=-date')
  trainings.value = data
}

async function createTraining() {
  await http.post('/trainings/', form.value)
  dialog.value = false
  form.value = emptyForm()
  fetchTrainings()
}

onMounted(fetchTrainings)
</script>