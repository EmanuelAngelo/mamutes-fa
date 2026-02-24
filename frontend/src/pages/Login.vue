<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="6" lg="4">
        <v-card elevation="2">
          <v-card-title>Entrar</v-card-title>
          <v-card-text>
            <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
              {{ error }}
            </v-alert>

            <v-text-field v-model="username" label="Usuário" autocomplete="username" />
            <v-text-field
              v-model="password"
              label="Senha"
              type="password"
              autocomplete="current-password"
            />
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn variant="text" @click="fillDemo">Demo</v-btn>
            <v-btn variant="flat" :loading="loading" @click="onLogin">Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

const auth = useAuthStore()
const router = useRouter()

function fillDemo() {
  username.value = 'admin'
  password.value = 'admin'
}

async function onLogin() {
  error.value = null
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(auth.me?.role === 'PLAYER' ? { name: 'player-dashboard' } : { name: 'coach-dashboard' })
  } catch {
    error.value = 'Falha no login. Verifique usuário e senha.'
  } finally {
    loading.value = false
  }
}
</script>