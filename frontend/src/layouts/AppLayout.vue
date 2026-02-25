<template>
  <v-app>
    <v-app-bar density="comfortable" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>Mamutes F.A.</v-app-bar-title>
      <v-spacer />
      <v-chip v-if="auth.me" class="mr-3 d-none d-sm-flex" variant="tonal">
        {{ auth.me.username }} • {{ auth.me.role }}
      </v-chip>
      <v-btn size="small" variant="tonal" @click="onLogout">Sair</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" temporary>
      <v-list nav>
        <template v-if="auth.isPlayer">
          <v-list-item title="Meu Dashboard" :to="{ name: 'player-dashboard' }" />
        </template>

        <template v-else>
          <v-list-item title="Coach Dashboard" :to="{ name: 'coach-dashboard' }" />
          <v-list-item title="Treinos" :to="{ name: 'coach-trainings' }" />
          <v-list-item title="Atletas" :to="{ name: 'coach-athletes' }" />
        </template>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="py-4 py-md-6 px-2 px-md-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const drawer = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>