<template>
  <v-card>
    <v-card-title>Matriz de Notas</v-card-title>
    <v-card-text>
      <div class="overflow-auto">
        <table class="min-w-full text-sm border">
          <thead>
            <tr class="bg-gray-50">
              <th class="p-2 border text-left">Atleta</th>
              <th class="p-2 border">Pos</th>
              <th class="p-2 border">Status</th>
              <th v-for="d in drills" :key="d.training_drill_id" class="p-2 border">
                {{ d.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in attendance" :key="a.athlete_id">
              <td class="p-2 border">{{ a.athlete_name }}</td>
              <td class="p-2 border text-center">{{ a.position || '-' }}</td>
              <td class="p-2 border text-center">{{ a.status }}</td>
              <td
                v-for="d in drills"
                :key="d.training_drill_id"
                class="p-2 border text-center"
                :title="getCell(a.athlete_id, d.training_drill_id)?.comment || ''"
              >
                {{ getCell(a.athlete_id, d.training_drill_id)?.score ?? '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="text-xs text-gray-500 mt-2">
        Dica: passe o mouse na célula para ver o comentário.
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps<{
  attendance: any[]
  drills: any[]
  scoreMap: Record<string, { score: number; comment: string | null }>
}>()

function key(athleteId: number, drillId: number) {
  // backend envia score_map com chave (athlete_id, drill_id) como tupla.
  // No JSON isso pode chegar como string tipo "1,10" dependendo do serializer.
  // Aqui suportamos 2 formatos:
  return `${athleteId},${drillId}`
}

function getCell(athleteId: number, drillId: number) {
  return props.scoreMap[key(athleteId, drillId)] ?? null
}
</script>