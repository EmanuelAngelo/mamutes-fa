<template>
  <div>
    <v-card class="mb-4">
      <v-card-title>Meu Dashboard</v-card-title>
      <v-card-text>
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>

        <div v-else>
          <div v-if="latest">
            <v-chip class="mb-3" variant="tonal">
              Último treino: {{ latest.training.date }}
            </v-chip>

            <div class="text-h5 mb-4">
              Média do treino:
              <strong>{{ latest.day_weighted_average ?? '-' }}</strong>
            </div>

            <div class="table-scroll">
              <v-table density="comfortable">
              <thead>
                <tr>
                  <th>Drill</th>
                  <th>Nota</th>
                  <th>Comentário</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in latest.drills" :key="d.training_drill_id">
                  <td>{{ d.drill_name }}</td>
                  <td>{{ d.score ?? '-' }}</td>
                  <td>{{ d.comment ?? '-' }}</td>
                </tr>
              </tbody>
              </v-table>
            </div>
          </div>

          <div v-else>
            Nenhum treino encontrado.
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '../../api/http'

const latest = ref<any>(null)
const loading = ref(false)

async function fetchLatest() {
  loading.value = true
  try {
    const { data } = await http.get('/api/dashboard/my/latest-training/')
    latest.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchLatest)
</script>