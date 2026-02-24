<template>
  <v-container
    fluid
    class="d-flex align-center justify-center login-page"
    style="min-height: 100vh"
  >
    <v-card
      elevation="2"
      class="pa-2 login-card"
      style="width: 100%; max-width: 440px"
    >
      <v-card-text class="text-center pt-6">
        <v-img
          v-if="showLogo"
          :src="logoUrl"
          alt="Mamutes F.A."
          width="140"
          height="140"
          class="mx-auto mb-4"
          cover
          @error="showLogo = false"
        />

        <div class="text-h6 text-high-emphasis">Mamutes F.A.</div>
        <div class="text-body-2 text-medium-emphasis mb-4">Acesso ao sistema</div>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4" density="compact">
          {{ error }}
        </v-alert>

        <v-text-field
          v-model="username"
          label="Usuário"
          autocomplete="username"
          variant="outlined"
          class="mb-2"
        />
        <v-text-field
          v-model="password"
          label="Senha"
          type="password"
          autocomplete="current-password"
          variant="outlined"
          @keyup.enter="onLogin"
        />

        <div class="d-flex justify-space-between align-center mt-4">
          <v-btn variant="text" @click="fillDemo">Demo</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="onLogin">
            Login
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>
.login-page {
  background-image: url('/Time_1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.login-card {
  background: rgba(var(--v-theme-surface), 0.72);
  color: rgb(var(--v-theme-on-surface));
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''
const logoUrl = `${apiBaseUrl.replace(/\/$/, '')}/media/brand/logo.png`
const showLogo = ref(true)

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