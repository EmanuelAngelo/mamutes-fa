<template>
  <v-container v-if="dashboard">
    <v-card class="mb-4">
      <v-card-title>
        Treino {{ dashboard.training.date }}
      </v-card-title>
      <v-card-text>
        <div><strong>Local:</strong> {{ dashboard.training.location || '-' }}</div>
        <div><strong>Média do treino:</strong> {{ dashboard.summary.training_weighted_average ?? '-' }}</div>
      </v-card-text>
    </v-card>

    <!-- Ranking -->
    <v-card class="mb-4">
      <v-card-title>Ranking</v-card-title>
      <v-card-text>
        <v-table>
          <thead>
            <tr>
              <th>#</th>
              <th>Atleta</th>
              <th>Posição</th>
              <th>Média</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in dashboard.ranking" :key="r.athlete_id">
              <td>{{ r.rank }}</td>
              <td>{{ r.athlete_name }}</td>
              <td>{{ r.position || '-' }}</td>
              <td>{{ r.weighted_average ?? '-' }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- Presença -->
    <v-card>
      <v-card-title>Presença</v-card-title>
      <v-card-text>
        <v-table>
          <thead>
            <tr>
              <th>Atleta</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in dashboard.attendance" :key="a.athlete_id">
              <td>{{ a.athlete_name }}</td>
              <td>{{ a.status }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>
  </v-container>

  <v-progress-circular v-else indeterminate />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '@/api/http'

const route = useRoute()
const dashboard = ref<any>(null)

async function fetchDashboard() {
  const { data } = await http.get(`/api/trainings/${route.params.id}/coach_dashboard/`)
  dashboard.value = data
}

onMounted(fetchDashboard)
</script>