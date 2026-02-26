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
          <v-list-item
            title="Meu Dashboard"
            prepend-icon="mdi-view-dashboard"
            :to="{ name: 'player-dashboard' }"
          />
          <v-list-item
            title="Meu Perfil"
            prepend-icon="mdi-account"
            :to="{ name: 'player-profile' }"
          />
        </template>

        <template v-else>
          <v-list-item
            title="Coach Dashboard"
            prepend-icon="mdi-chart-line"
            :to="{ name: 'coach-dashboard' }"
          />
          <v-list-item
            title="Treinos"
            prepend-icon="mdi-whistle"
            :to="{ name: 'coach-trainings' }"
          />
          <v-list-item
            title="Atletas"
            prepend-icon="mdi-account-group"
            :to="{ name: 'coach-athletes' }"
          />
          <v-list-item
            title="Catálogo de Drills"
            prepend-icon="mdi-format-list-bulleted"
            :to="{ name: 'coach-drills-catalog' }"
          />
        </template>

        <v-divider class="my-2" />
        <v-list-item
          title="Trocar senha"
          prepend-icon="mdi-lock-reset"
          @click="openChangePassword"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid class="py-4 py-md-6 px-2 px-md-6">
        <router-view />
      </v-container>
    </v-main>

    <ChangePasswordDialog v-model="changePasswordOpen" />
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ChangePasswordDialog from '../components/ChangePasswordDialog.vue'

const drawer = ref(false)
const changePasswordOpen = ref(false)
const auth = useAuthStore()
const router = useRouter()

function openChangePassword() {
  drawer.value = false
  changePasswordOpen.value = true
}

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>