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

    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      :temporary="isMobile"
      :permanent="!isMobile"
      class="app-drawer"
      @click="rail = false"
    >
      <v-list>
        <v-list-item
          :title="auth.me?.username ?? 'Conta'"
          :subtitle="auth.me?.role ?? ''"
          :prepend-avatar="avatarUrl"
        >
          <template #append>
            <v-btn
              icon
              variant="text"
              :aria-label="rail ? 'Expandir menu' : 'Recolher menu'"
              @click.stop="rail = !rail"
            >
              <v-icon>{{ rail ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>

      <v-divider class="my-2" />

      <v-list density="compact" nav>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ChangePasswordDialog from '../components/ChangePasswordDialog.vue'
import { http } from '../api/http'

const drawer = ref(false)
const rail = ref(true)
const changePasswordOpen = ref(false)
const auth = useAuthStore()
const router = useRouter()
const display = useDisplay()

const isMobile = computed(() => display.smAndDown.value)

const athletePhotoUrl = ref<string | null>(null)

function resolveApiRoot(): string {
  const base = String(http.defaults.baseURL ?? '')
  return base.replace(/\/api\/?$/, '')
}

function absolutizeMaybeRelativeUrl(url: string): string {
  if (/^https?:\/\//i.test(url)) return url
  const root = resolveApiRoot() || window.location.origin
  return new URL(url.replace(/^\/+/, '/'), root).toString()
}

async function fetchAthletePhotoIfAny() {
  athletePhotoUrl.value = null
  if (!auth.me?.athlete_id) return

  try {
    const { data } = await http.get('/athletes/me/')
    const photo = (data as any)?.photo as string | null | undefined
    athletePhotoUrl.value = photo ? absolutizeMaybeRelativeUrl(photo) : null
  } catch {
    athletePhotoUrl.value = null
  }
}

const avatarUrl = computed(() => {
  if (athletePhotoUrl.value) return athletePhotoUrl.value
  const username = auth.me?.username
  if (!username) return undefined
  const seed = encodeURIComponent(username)
  return `https://api.dicebear.com/7.x/initials/svg?seed=${seed}`
})

watch(
  () => auth.me?.athlete_id,
  () => {
    if (typeof window === 'undefined') return
    fetchAthletePhotoIfAny()
  },
  { immediate: true },
)

onMounted(() => {
  fetchAthletePhotoIfAny()
})

function openChangePassword() {
  drawer.value = false
  changePasswordOpen.value = true
}

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.app-drawer {
  border-right: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  background: rgba(var(--v-theme-surface), 0.70);
  backdrop-filter: blur(12px);
}
</style>