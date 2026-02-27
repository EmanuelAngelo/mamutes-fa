<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-view-dashboard</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Player</div>
            <div class="text-h6 font-weight-bold">Meu Dashboard</div>
          </div>
        </div>
      </div>
    </v-sheet>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-text>
        <div v-if="pageLoading" class="d-flex justify-center py-10">
          <v-progress-circular
            :model-value="progress"
            :rotate="360"
            :size="100"
            :width="15"
            color="teal"
          >
            {{ progress }}
          </v-progress-circular>
        </div>

        <div v-else>
          <div v-if="latest">
            <v-chip class="mb-3" variant="tonal">
              Último treino: {{ formatDateBR(latest.training.date) }}
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

          <div v-else class="text-body-2 text-medium-emphasis">
            Nenhum treino encontrado.
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '../../api/http'
import { usePageProgressLoading } from '@/composables/usePageProgressLoading'
function formatDateBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const m = /^\d{4}-\d{2}-\d{2}$/.exec(iso)
  if (!m) return iso
  const [y, mm, dd] = iso.split('-')
  return `${dd}/${mm}/${y}`
}

const latest = ref<any>(null)
const { loading: pageLoading, value: progress, start: startLoading, stop: stopLoading } = usePageProgressLoading({
  minDurationMs: 5000,
})

async function fetchLatest() {
  startLoading()
  try {
    const { data } = await http.get('/dashboard/my/latest-training/')
    latest.value = data
  } catch (err) {
    console.error(err)
  } finally {
    await stopLoading()
  }
}

onMounted(fetchLatest)
</script>

<style scoped>
.page-header {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 16px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.70);
  backdrop-filter: blur(12px);
}

.page-header__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(var(--v-theme-on-primary), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 1),
    rgba(var(--v-theme-primary), 0.75)
  );
}
</style>