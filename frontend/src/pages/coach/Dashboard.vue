<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">Coach Dashboard</h1>

    <v-alert type="info" variant="tonal">
      Abra um treino para ver ranking, presença, matriz de notas e export PDF.
    </v-alert>

    <v-btn variant="flat" :to="{ name: 'coach-trainings' }">Ir para Treinos</v-btn>
  </div>
</template>