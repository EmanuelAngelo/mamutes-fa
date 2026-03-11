<template>
  <v-container>
    <v-sheet class="page-header" rounded="xl">
      <div class="d-flex flex-wrap align-center justify-space-between ga-4">
        <div class="d-flex align-center ga-3">
          <div class="page-header__icon">
            <v-icon size="26">mdi-bell</v-icon>
          </div>
          <div>
            <div class="text-body-2 text-medium-emphasis">Equipe</div>
            <div class="text-h6 font-weight-bold">Avisos</div>
          </div>
        </div>

        <div class="d-flex flex-wrap align-center ga-2">
          <v-btn
            v-if="pushAvailable"
            variant="tonal"
            :color="isPushSubscribed ? 'primary' : undefined"
            :loading="pushLoading"
            @click="togglePush"
          >
            <v-icon start>{{ isPushSubscribed ? 'mdi-bell-off' : 'mdi-bell-ring' }}</v-icon>
            {{ isPushSubscribed ? 'Desativar notificações' : 'Ativar notificações' }}
          </v-btn>

          <v-btn v-if="auth.isCoachOrAdmin" color="primary" variant="tonal" :to="backTarget" rounded="xl">
            <v-icon start>mdi-arrow-left</v-icon>
            Voltar
          </v-btn>
          <v-btn v-else variant="tonal" :to="backTarget" rounded="xl">
            <v-icon start>mdi-arrow-left</v-icon>
            Voltar
          </v-btn>
        </div>
      </div>
    </v-sheet>

    <v-alert v-if="pushError" type="error" variant="tonal" class="mt-4">
      {{ pushError }}
    </v-alert>

    <v-card v-if="auth.isCoachOrAdmin" variant="tonal" rounded="xl" class="mt-4">
      <v-card-title class="d-flex flex-wrap align-center justify-space-between">
        Publicar aviso
        <v-btn
          color="primary"
          variant="tonal"
          :loading="publishing"
          :disabled="!noticeForm.body.trim()"
          @click="publishNotice"
        >
          Publicar
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-alert v-if="noticeError" type="error" variant="tonal" class="mb-3">
          {{ noticeError }}
        </v-alert>

        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="noticeForm.title"
              label="Título (opcional)"
              variant="outlined"
              density="comfortable"
              clearable
            />
          </v-col>
          <v-col cols="12" md="8">
            <v-textarea
              v-model="noticeForm.body"
              label="Escreva um aviso para o time"
              variant="outlined"
              auto-grow
              rows="2"
              density="comfortable"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card variant="tonal" rounded="xl" class="mt-4">
      <v-card-title>Avisos</v-card-title>
      <v-card-text>
        <v-alert v-if="noticesError" type="error" variant="tonal" class="mb-3">
          {{ noticesError }}
        </v-alert>

        <div v-if="noticesLoading" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else-if="notices.length === 0" class="text-body-2 text-medium-emphasis">
          Nenhum aviso no momento.
        </div>

        <div v-else class="d-flex flex-column ga-3">
          <v-card
            v-for="n in notices"
            :key="n.id"
            variant="outlined"
            rounded="xl"
            class="notice-item"
          >
            <v-card-title class="py-3">
              <div class="d-flex align-center justify-space-between w-100 ga-3">
                <div class="d-flex flex-column">
                  <div class="text-subtitle-1 font-weight-bold">
                    {{ n.title?.trim() ? n.title : 'Aviso' }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    {{ n.created_by?.username ?? 'Coach' }} • {{ formatDateTimeBR(n.created_at) }}
                  </div>
                </div>

                <v-btn
                  size="small"
                  variant="tonal"
                  :color="n.liked_by_me ? 'primary' : undefined"
                  :loading="likeLoadingId === n.id"
                  @click="toggleLike(n)"
                >
                  <v-icon start size="16">mdi-thumb-up-outline</v-icon>
                  {{ n.likes_count }}
                </v-btn>
              </div>
            </v-card-title>

            <v-card-text class="pt-0">
              <div class="white-space-prewrap mb-3">{{ n.body }}</div>

              <div class="text-body-2 text-medium-emphasis mb-2">
                {{ n.comments_count }} comentários
              </div>

              <div v-if="n.recent_comments?.length" class="d-flex flex-column ga-2 mb-3">
                <div v-for="c in n.recent_comments" :key="c.id" class="notice-comment">
                  <div class="text-body-2">
                    <strong>{{ c.user?.username ?? 'User' }}:</strong>
                    {{ c.text }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatDateTimeBR(c.created_at) }}
                  </div>
                </div>
              </div>

              <v-text-field
                v-model="commentDrafts[n.id]"
                label="Comentar"
                density="comfortable"
                variant="outlined"
                hide-details
                :disabled="commentLoadingId === n.id"
                @keydown.enter.prevent="submitComment(n)"
              />
              <div class="d-flex justify-end mt-2">
                <v-btn
                  size="small"
                  variant="tonal"
                  color="primary"
                  :loading="commentLoadingId === n.id"
                  :disabled="!(commentDrafts[n.id] || '').trim()"
                  @click="submitComment(n)"
                >
                  Enviar
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()

type NoticeUser = { id: number; username: string }
type NoticeComment = { id: number; user: NoticeUser | null; text: string; created_at: string }
type Notice = {
  id: number
  title: string
  body: string
  created_by: NoticeUser | null
  created_at: string
  likes_count: number
  comments_count: number
  liked_by_me: boolean
  recent_comments: NoticeComment[]
}

const notices = ref<Notice[]>([])
const noticesLoading = ref(false)
const noticesError = ref<string | null>(null)
const likeLoadingId = ref<number | null>(null)
const commentLoadingId = ref<number | null>(null)
const commentDrafts = ref<Record<number, string>>({})

const publishing = ref(false)
const noticeError = ref<string | null>(null)
const noticeForm = ref({ title: '', body: '' })

const backTarget = computed(() => {
  return auth.isPlayer ? { name: 'player-dashboard' } : { name: 'coach-dashboard' }
})

const pushAvailable = computed(() => {
  return (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  )
})

const pushLoading = ref(false)
const pushError = ref<string | null>(null)
const isPushSubscribed = ref(false)

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i)
  return outputArray
}

async function refreshPushStatus() {
  if (!pushAvailable.value) return
  try {
    const reg = await navigator.serviceWorker.ready
    const sub = await reg.pushManager.getSubscription()
    isPushSubscribed.value = Boolean(sub)
  } catch {
    isPushSubscribed.value = false
  }
}

async function subscribePush() {
  pushError.value = null
  if (!pushAvailable.value) return

  if (Notification.permission === 'denied') {
    pushError.value = 'Notificações estão bloqueadas no navegador.'
    return
  }

  pushLoading.value = true
  try {
    const perm = await Notification.requestPermission()
    if (perm !== 'granted') {
      pushError.value = 'Permissão de notificações não concedida.'
      return
    }

    const { data } = await http.get('/notices/push/public-key/')
    const publicKey = String((data as any)?.publicKey || '')
    if (!publicKey) {
      pushError.value = 'Servidor sem chave pública VAPID configurada.'
      return
    }

    const reg = await navigator.serviceWorker.ready
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey),
    })

    const json = sub.toJSON() as any
    await http.post('/notices/push/subscribe/', {
      endpoint: json?.endpoint,
      keys: json?.keys,
      user_agent: navigator.userAgent,
    })

    isPushSubscribed.value = true
  } catch (e: any) {
    const status = e?.response?.status
    pushError.value = status ? `Falha ao ativar notificações (HTTP ${status}).` : 'Falha ao ativar notificações.'
    await refreshPushStatus()
  } finally {
    pushLoading.value = false
  }
}

async function unsubscribePush() {
  pushError.value = null
  if (!pushAvailable.value) return

  pushLoading.value = true
  try {
    const reg = await navigator.serviceWorker.ready
    const sub = await reg.pushManager.getSubscription()
    if (!sub) {
      isPushSubscribed.value = false
      return
    }
    const endpoint = (sub.toJSON() as any)?.endpoint
    await sub.unsubscribe()
    if (endpoint) {
      await http.post('/notices/push/unsubscribe/', { endpoint })
    }
    isPushSubscribed.value = false
  } catch (e: any) {
    const status = e?.response?.status
    pushError.value = status ? `Falha ao desativar notificações (HTTP ${status}).` : 'Falha ao desativar notificações.'
    await refreshPushStatus()
  } finally {
    pushLoading.value = false
  }
}

async function togglePush() {
  if (pushLoading.value) return
  if (isPushSubscribed.value) return unsubscribePush()
  return subscribePush()
}

function formatDateTimeBR(iso: string | null | undefined): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return String(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${dd}/${mm}/${yy} ${hh}:${mi}`
}

async function fetchNotices() {
  noticesLoading.value = true
  noticesError.value = null
  try {
    const { data } = await http.get('/notices/', { params: { ordering: '-created_at' } })
    notices.value = Array.isArray(data) ? data : (data?.results ?? [])
  } catch (e: any) {
    const status = e?.response?.status
    noticesError.value = status ? `Falha ao carregar avisos (HTTP ${status}).` : 'Falha ao carregar avisos.'
    notices.value = []
  } finally {
    noticesLoading.value = false
  }
}

async function publishNotice() {
  noticeError.value = null
  const body = noticeForm.value.body.trim()
  if (!body) return

  publishing.value = true
  try {
    const payload = { title: noticeForm.value.title?.trim() || '', body }
    const { data } = await http.post('/notices/', payload)
    notices.value = [data as Notice, ...notices.value]
    noticeForm.value = { title: '', body: '' }
  } catch (e: any) {
    const status = e?.response?.status
    noticeError.value = status ? `Falha ao publicar aviso (HTTP ${status}).` : 'Falha ao publicar aviso.'
  } finally {
    publishing.value = false
  }
}

async function toggleLike(n: Notice) {
  if (likeLoadingId.value) return
  likeLoadingId.value = n.id
  try {
    const { data } = await http.post(`/notices/${n.id}/like/`, {})
    n.liked_by_me = Boolean(data?.liked)
    n.likes_count = Number(data?.likes_count ?? n.likes_count)
  } finally {
    likeLoadingId.value = null
  }
}

async function submitComment(n: Notice) {
  if (commentLoadingId.value) return
  const text = (commentDrafts.value[n.id] || '').trim()
  if (!text) return

  commentLoadingId.value = n.id
  try {
    const { data } = await http.post(`/notices/${n.id}/comments/`, { text })
    const comment = data?.comment as NoticeComment | undefined
    n.comments_count = Number(data?.comments_count ?? n.comments_count)
    if (comment) {
      const current = Array.isArray(n.recent_comments) ? n.recent_comments : []
      n.recent_comments = [...current, comment].slice(-3)
    }
    commentDrafts.value[n.id] = ''
  } finally {
    commentLoadingId.value = null
  }
}

function markNoticesSeenFromList(list: Notice[]) {
  const meId = auth.me?.id
  if (!meId) return
  const latest = list[0]?.created_at
  if (!latest) return
  try {
    localStorage.setItem(`notices_last_seen_at:${meId}`, String(latest))
  } catch {
    // ignore
  }
}

onMounted(async () => {
  await fetchNotices()
  markNoticesSeenFromList(notices.value)
  await refreshPushStatus()
})

watch(
  () => route.fullPath,
  async () => {
    // When returning to this page, refresh list.
    await fetchNotices()
    markNoticesSeenFromList(notices.value)
  }
)
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

.white-space-prewrap {
  white-space: pre-wrap;
}

.notice-comment {
  border-left: 3px solid rgba(var(--v-theme-primary), 0.55);
  padding-left: 10px;
}
</style>
