<template>
  <div>
    <v-card>
      <v-card-title>Coach Dashboard</v-card-title>
      <v-card-text>
        <v-alert type="info" variant="tonal" class="mb-4">
          Selecione um treino para visualizar ranking, presença e matriz de notas.
        </v-alert>

        <v-btn
          variant="flat"
          color="primary"
          :to="{ name: 'coach-trainings' }"
        >
          Ir para Treinos
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
</script>