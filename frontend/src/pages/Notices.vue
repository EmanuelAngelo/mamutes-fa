<template>
  <div class="avisos-page">
    <header class="avisos-header">
      <div class="max-wrap">
        <div class="d-flex align-center justify-space-between py-3 px-4">
          <div class="d-flex align-center ga-2">
            <v-btn class="btn-back" icon variant="text" @click="goBack">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>

            <div class="d-flex align-center ga-2">
              <div class="header-icon">
                <v-icon color="white" size="18">mdi-megaphone</v-icon>
              </div>
              <div>
                <div class="text-body-2 font-weight-bold" style="line-height: 1.1">Avisos</div>
                <div class="text-caption text-medium-emphasis" style="margin-top: 2px">
                  {{ notices.length }} publicações
                </div>
              </div>
            </div>
          </div>

          <v-btn
            class="btn-notify"
            :class="isPushSubscribed ? 'btn-notify--on' : ''"
            :loading="pushLoading"
            rounded="pill"
            size="small"
            variant="outlined"
            @click="togglePush"
          >
            <v-icon size="18" start>
              {{ isPushSubscribed ? 'mdi-bell' : 'mdi-bell-off' }}
            </v-icon>
            <span class="d-none d-sm-inline text-caption">
              {{ isPushSubscribed ? 'Notificando' : 'Notificar' }}
            </span>
          </v-btn>
        </div>
      </div>
    </header>

    <main class="max-wrap px-4 py-6">
      <v-alert v-if="error" class="mb-4" type="error" variant="tonal">
        {{ error }}
      </v-alert>

      <v-alert v-if="pushError" class="mb-4" type="error" variant="tonal">
        {{ pushError }}
      </v-alert>

      <section v-if="auth.isCoachOrAdmin" class="mb-6">
        <div v-if="!newOpen" class="new-closed" @click="openNew">
          <div class="new-closed__icon">
            <v-icon color="rgb(var(--v-theme-cashIndigo600))" size="18">mdi-megaphone</v-icon>
          </div>
          <div class="text-body-2 font-weight-medium">Publicar novo aviso...</div>
        </div>

        <v-expand-transition>
          <v-card v-if="newOpen" class="new-open" rounded="xl" variant="elevated">
            <v-card-text>
              <div class="d-flex align-center ga-2 mb-4">
                <div class="new-open__badge">
                  <v-icon color="white" size="18">mdi-megaphone</v-icon>
                </div>
                <div class="text-subtitle-2 font-weight-bold">Novo Aviso</div>
              </div>

              <v-alert v-if="publishError" class="mb-3" type="error" variant="tonal">
                {{ publishError }}
              </v-alert>

              <div class="mb-3">
                <div class="field-label">TÍTULO</div>
                <v-text-field
                  v-model="form.title"
                  class="rounded-xl"
                  density="comfortable"
                  hide-details
                  placeholder="Título do aviso"
                  variant="outlined"
                />
              </div>

              <div>
                <div class="field-label">DESCRIÇÃO</div>
                <v-textarea
                  v-model="form.body"
                  auto-grow
                  class="rounded-xl"
                  density="comfortable"
                  hide-details
                  placeholder="Escreva o conteúdo..."
                  rows="3"
                  variant="outlined"
                />
              </div>

              <div class="d-flex ga-2 mt-4">
                <v-btn
                  class="flex-1"
                  rounded="xl"
                  variant="outlined"
                  @click="cancelNew"
                >
                  Cancelar
                </v-btn>
                <v-btn
                  class="flex-1 btn-publish"
                  :disabled="!canPublish"
                  :loading="publishing"
                  rounded="xl"
                  @click="publish"
                >
                  <v-icon size="18" start>mdi-send</v-icon>
                  {{ publishing ? 'Publicando...' : 'Publicar' }}
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-expand-transition>
      </section>

      <section>
        <div v-if="loading" class="d-flex justify-center py-12">
          <div class="spin" />
        </div>

        <Transition name="fade">
          <div v-if="!loading && sortedNotices.length === 0" class="empty">
            <div class="empty__circle">
              <v-icon color="rgb(var(--v-theme-cashIndigo600))" size="44">mdi-megaphone</v-icon>
            </div>
            <div class="text-subtitle-1 font-weight-bold mt-4">Nenhum aviso publicado</div>
            <div v-if="auth.isCoachOrAdmin" class="text-body-2 text-medium-emphasis">
              Publique o primeiro aviso acima.
            </div>
            <div v-else class="text-body-2 text-medium-emphasis">
              Aguarde novos avisos do coach.
            </div>
          </div>
        </Transition>

        <div v-if="!loading && sortedNotices.length > 0" class="d-flex flex-column ga-4">
          <TransitionGroup class="d-flex flex-column ga-4" name="card" tag="div">
            <v-card
              v-for="(a, idx) in sortedNotices"
              :key="a.id"
              class="card"
              :class="a.pinned ? 'card--pinned' : ''"
              rounded="xl"
              :style="{ transitionDelay: `${Math.min(idx * 60, 240)}ms` }"
              variant="elevated"
            >
              <div v-if="a.pinned" class="card-pin">
                <v-icon color="rgb(var(--v-theme-cashIndigo600))" size="14">mdi-pin</v-icon>
                <span>Fixado</span>
              </div>

              <v-card-text>
                <div class="d-flex align-center ga-3 mb-3">
                  <div class="avatar" :style="{ background: avatarColor(a.created_by?.username) }">
                    {{ initials(a.created_by?.username) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-body-2 font-weight-bold text-truncate">
                      {{ a.created_by?.username || 'Administrador' }}
                    </div>
                    <div class="d-flex align-center ga-2">
                      <div class="text-caption text-medium-emphasis">{{ timeAgo(a.created_at) }}</div>
                      <div class="dot">·</div>
                      <div class="text-caption text-medium-emphasis">{{ dayMonth(a.created_at) }}</div>
                    </div>
                  </div>
                </div>

                <div class="text-subtitle-1 font-weight-bold mb-2">
                  {{ a.title }}
                </div>
                <div class="text-body-2 text-medium-emphasis pre">
                  {{ a.body }}
                </div>

                <div class="card-actions">
                  <button
                    class="pill"
                    :class="a.liked_by_me ? 'pill--liked' : ''"
                    :disabled="likeLoadingId === a.id"
                    @click="onLike(a)"
                  >
                    <v-icon :icon="a.liked_by_me ? 'mdi-heart' : 'mdi-heart-outline'" size="18" />
                    <span class="pill__count">{{ a.likes_count || '' }}</span>
                  </button>

                  <button class="pill" @click="openComments(a)">
                    <v-icon icon="mdi-message-reply-text-outline" size="18" />
                    <span class="pill__count">{{ a.comments_count || '' }}</span>
                  </button>
                </div>
              </v-card-text>
            </v-card>
          </TransitionGroup>
        </div>
      </section>
    </main>

    <v-bottom-sheet v-model="commentsOpen" inset>
      <v-card class="sheet" rounded="xl">
        <div class="sheet__header">
          <div class="text-subtitle-2 font-weight-bold">
            Comentários
            <span class="text-body-2 text-medium-emphasis">({{ activeComments.length }})</span>
          </div>
          <div v-if="selected" class="text-body-2 text-medium-emphasis text-truncate">
            {{ selected.title }}
          </div>
        </div>

        <div class="sheet__body">
          <div v-if="commentsLoading" class="d-flex justify-center py-10">
            <div class="spin" />
          </div>

          <div v-else-if="activeComments.length === 0" class="sheet-empty">
            <div class="sheet-empty__circle">
              <v-icon color="rgba(var(--v-theme-on-surface), 0.35)" size="26">mdi-send</v-icon>
            </div>
            <div class="text-body-2 text-medium-emphasis">Nenhum comentário ainda.</div>
          </div>

          <div v-else class="d-flex flex-column ga-3">
            <div v-for="c in activeComments" :key="c.id" class="comment-row">
              <div class="avatar avatar--sm" :style="{ background: avatarColor(c.user?.username) }">
                {{ initials(c.user?.username) }}
              </div>
              <div class="comment">
                <div class="d-flex align-center justify-space-between ga-3 mb-1">
                  <div class="text-body-2 font-weight-bold">
                    {{ c.user?.username || 'Usuário' }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ timeAgo(c.created_at) }}
                  </div>
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  {{ c.text }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="sheet__footer">
          <form class="d-flex ga-2" @submit.prevent="sendComment">
            <v-text-field
              v-model="commentText"
              class="flex-1"
              density="comfortable"
              :disabled="commentSending"
              hide-details
              placeholder="Escreva um comentário..."
              variant="outlined"
            />
            <v-btn
              class="btn-send"
              :disabled="!commentText.trim()"
              icon
              :loading="commentSending"
              type="submit"
            >
              <v-icon color="white">mdi-send</v-icon>
            </v-btn>
          </form>
        </div>
      </v-card>
    </v-bottom-sheet>

    <v-snackbar v-model="snack.open" location="top" :timeout="1800">
      {{ snack.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { http } from '../api/http'
  import { useAuthStore } from '../stores/auth'

  const auth = useAuthStore()
  const router = useRouter()

  type NoticeUser = { id: number, username: string }
  type NoticeComment = { id: number, user: NoticeUser | null, text: string, created_at: string }
  type Notice = {
    id: number
    title: string
    body: string
    pinned: boolean
    created_by: NoticeUser | null
    created_at: string
    likes_count: number
    comments_count: number
    liked_by_me: boolean
  }

  const loading = ref(false)
  const error = ref<string | null>(null)
  const notices = ref<Notice[]>([])
  const likeLoadingId = ref<number | null>(null)

  const snack = ref({ open: false, text: '' })

  const pushLoading = ref(false)
  const pushError = ref<string | null>(null)
  const isPushSubscribed = ref(false)

  const pushAvailable = computed(() => {
    return (
      typeof window !== 'undefined'
      && 'serviceWorker' in navigator
      && 'PushManager' in window
      && 'Notification' in window
    )
  })

  const newOpen = ref(false)
  const publishing = ref(false)
  const publishError = ref<string | null>(null)
  const form = ref({ title: '', body: '' })

  const commentsOpen = ref(false)
  const selected = ref<Notice | null>(null)
  const commentsLoading = ref(false)
  const commentsByNotice = ref<Record<number, NoticeComment[]>>({})
  const commentText = ref('')
  const commentSending = ref(false)

  const canPublish = computed(() => {
    return Boolean(form.value.title.trim()) && Boolean(form.value.body.trim())
  })

  const sortedNotices = computed(() => {
    const list = Array.isArray(notices.value) ? [...notices.value] : []
    const pinned = list.filter(n => n.pinned)
    const others = list.filter(n => !n.pinned)
    return [...pinned, ...others]
  })

  function apiHint (): string {
    const base = String((http as any)?.defaults?.baseURL || '')
    return base ? ` (API: ${base})` : ''
  }

  function isProbablyHtml (data: unknown, contentType: string): boolean {
    const ct = (contentType || '').toLowerCase()
    if (ct.includes('text/html')) return true
    if (typeof data !== 'string') return false
    const s = data.trim().slice(0, 200).toLowerCase()
    return s.startsWith('<!doctype html') || s.startsWith('<html') || s.includes('<head')
  }

  function isNotice (data: any): data is Notice {
    return Boolean(data)
      && typeof data === 'object'
      && typeof data.id === 'number'
      && typeof data.title === 'string'
      && typeof data.body === 'string'
      && typeof data.created_at === 'string'
  }

  const activeComments = computed(() => {
    const id = selected.value?.id
    if (!id) return []
    return commentsByNotice.value[id] || []
  })

  function goBack () {
    router.back()
  }

  function openNew () {
    newOpen.value = true
  }

  function cancelNew () {
    newOpen.value = false
    form.value = { title: '', body: '' }
    publishError.value = null
  }

  function urlBase64ToUint8Array (base64String: string) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)
    for (let i = 0; i < rawData.length; i += 1) outputArray[i] = rawData.codePointAt(i) ?? 0
    return outputArray
  }

  async function getServiceWorkerRegistration (): Promise<ServiceWorkerRegistration | null> {
    if (typeof window === 'undefined') return null
    if (!('serviceWorker' in navigator)) return null
    try {
      // `ready` can hang if the page isn't controlled by a SW yet.
      const reg = await navigator.serviceWorker.getRegistration()
      return reg || null
    } catch {
      return null
    }
  }

  async function refreshPushStatus () {
    pushError.value = null
    if (!pushAvailable.value) {
      isPushSubscribed.value = false
      return
    }
    try {
      const reg = await getServiceWorkerRegistration()
      if (!reg) {
        isPushSubscribed.value = false
        return
      }
      const sub = await reg.pushManager.getSubscription()
      isPushSubscribed.value = Boolean(sub)
    } catch (error_: any) {
      isPushSubscribed.value = false
      const status = error_?.response?.status
      pushError.value = status ? `Falha ao verificar notificações (HTTP ${status}).` : 'Falha ao verificar notificações.'
    }
  }

  async function subscribePush () {
    pushError.value = null
    if (!pushAvailable.value) {
      snack.value = { open: true, text: 'Notificações não suportadas neste dispositivo.' }
      return
    }

    if (Notification.permission === 'denied') {
      snack.value = { open: true, text: 'Notificações estão bloqueadas no navegador.' }
      return
    }

    pushLoading.value = true
    try {
      const perm = await Notification.requestPermission()
      if (perm !== 'granted') {
        snack.value = { open: true, text: 'Permissão de notificações não concedida.' }
        return
      }

      const { data } = await http.get('/notices/push/public-key/')
      const publicKey = String((data as any)?.publicKey || '')
      if (!publicKey) {
        pushError.value = 'Servidor sem chave pública VAPID configurada.'
        return
      }

      const reg = await getServiceWorkerRegistration()
      if (!reg) {
        pushError.value = 'Service Worker não está ativo neste navegador.'
        return
      }
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
      snack.value = { open: true, text: 'Notificações ativadas' }
    } catch (error_: any) {
      const status = error_?.response?.status
      pushError.value = status ? `Falha ao ativar notificações (HTTP ${status}).` : 'Falha ao ativar notificações.'
      await refreshPushStatus()
    } finally {
      pushLoading.value = false
    }
  }

  async function unsubscribePush () {
    pushError.value = null
    if (!pushAvailable.value) {
      isPushSubscribed.value = false
      return
    }

    pushLoading.value = true
    try {
      const reg = await getServiceWorkerRegistration()
      if (!reg) {
        isPushSubscribed.value = false
        return
      }
      const sub = await reg.pushManager.getSubscription()
      if (!sub) {
        isPushSubscribed.value = false
        return
      }
      const endpoint = (sub.toJSON() as any)?.endpoint
      await sub.unsubscribe()
      if (endpoint) await http.post('/notices/push/unsubscribe/', { endpoint })
      isPushSubscribed.value = false
      snack.value = { open: true, text: 'Notificações desativadas' }
    } catch (error_: any) {
      const status = error_?.response?.status
      pushError.value = status ? `Falha ao desativar notificações (HTTP ${status}).` : 'Falha ao desativar notificações.'
      await refreshPushStatus()
    } finally {
      pushLoading.value = false
    }
  }

  async function togglePush () {
    if (pushLoading.value) return
    if (isPushSubscribed.value) {
      await unsubscribePush()
      return
    }
    await subscribePush()
  }

  async function fetchNotices () {
    loading.value = true
    error.value = null
    try {
      const res = await http.get('/notices/', {
        params: { ordering: '-created_at' },
        headers: { Accept: 'application/json' },
      })

      const contentType = String((res as any)?.headers?.['content-type'] || '')
      if (isProbablyHtml(res.data, contentType)) {
        throw new Error('html_response')
      }

      const data = res.data as any
      if (data && typeof data === 'object' && typeof data.detail === 'string') {
        const msg = String(data.detail || '').trim()
        throw new Error(msg ? `api_detail:${msg}` : 'api_detail')
      }
      const items = Array.isArray(data) ? data : (data?.results ?? [])
      if (!Array.isArray(items)) throw new Error('invalid_shape')
      if (items.length === 0 && data && typeof data === 'object' && Number(data?.count ?? 0) > 0) {
        throw new Error('invalid_shape')
      }
      notices.value = items as Notice[]
    } catch (error_: any) {
      const status = error_?.response?.status
      if (error_?.message === 'html_response') {
        error.value = `Falha ao carregar avisos: resposta HTML (API incorreta?).${apiHint()}`
      } else if (typeof error_?.message === 'string' && error_?.message.startsWith('api_detail:')) {
        error.value = `Falha ao carregar avisos: ${error_?.message.slice('api_detail:'.length)}.${apiHint()}`
      } else if (error_?.message === 'invalid_shape') {
        error.value = `Falha ao carregar avisos: resposta inesperada.${apiHint()}`
      } else {
        error.value = status
          ? `Falha ao carregar avisos (HTTP ${status}).${apiHint()}`
          : `Falha ao carregar avisos.${apiHint()}`
      }
      notices.value = []
    } finally {
      loading.value = false
    }
  }

  async function publish () {
    if (!auth.isCoachOrAdmin) return
    if (!canPublish.value) return

    publishing.value = true
    publishError.value = null
    try {
      const payload = { title: form.value.title.trim(), body: form.value.body.trim() }
      const res = await http.post('/notices/', payload, { headers: { Accept: 'application/json' } })
      const contentType = String((res as any)?.headers?.['content-type'] || '')
      if (isProbablyHtml(res.data, contentType)) {
        throw new Error('html_response')
      }
      if (!isNotice(res.data)) {
        throw new Error('invalid_shape')
      }

      notices.value = [res.data as Notice, ...notices.value]
      cancelNew()
    } catch (error_: any) {
      const status = error_?.response?.status
      if (error_?.message === 'html_response') {
        publishError.value = `Falha ao publicar: resposta HTML (API incorreta?).${apiHint()}`
      } else if (error_?.message === 'invalid_shape') {
        publishError.value = `Falha ao publicar: resposta inesperada.${apiHint()}`
      } else {
        publishError.value = status
          ? `Falha ao publicar (HTTP ${status}).${apiHint()}`
          : `Falha ao publicar.${apiHint()}`
      }
    } finally {
      publishing.value = false
    }
  }

  async function onLike (a: Notice) {
    if (likeLoadingId.value) return
    likeLoadingId.value = a.id
    try {
      const { data } = await http.post(`/notices/${a.id}/like/`, {})
      a.liked_by_me = Boolean((data as any)?.liked)
      a.likes_count = Number((data as any)?.likes_count ?? a.likes_count)
    } finally {
      likeLoadingId.value = null
    }
  }

  async function openComments (a: Notice) {
    selected.value = a
    commentsOpen.value = true
    commentText.value = ''
    await ensureCommentsLoaded(a.id)
  }

  async function ensureCommentsLoaded (noticeId: number) {
    if (Array.isArray(commentsByNotice.value[noticeId])) return
    commentsLoading.value = true
    try {
      const { data } = await http.get(`/notices/${noticeId}/comments/`)
      commentsByNotice.value = {
        ...commentsByNotice.value,
        [noticeId]: Array.isArray(data) ? (data as NoticeComment[]) : [],
      }
    } finally {
      commentsLoading.value = false
    }
  }

  async function sendComment () {
    const a = selected.value
    const text = commentText.value.trim()
    if (!a || !text) return

    commentSending.value = true
    try {
      const { data } = await http.post(`/notices/${a.id}/comments/`, { text })
      const comment = (data as any)?.comment as NoticeComment | undefined
      const nextCount = Number((data as any)?.comments_count ?? a.comments_count)
      a.comments_count = nextCount

      if (comment) {
        const prev = commentsByNotice.value[a.id] || []
        commentsByNotice.value = {
          ...commentsByNotice.value,
          [a.id]: [...prev, comment],
        }
      } else {
        await ensureCommentsLoaded(a.id)
      }
      commentText.value = ''
    } finally {
      commentSending.value = false
    }
  }

  function initials (name: string | null | undefined): string {
    const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
    if (parts.length === 0) return '?'
    return parts
      .slice(0, 2)
      .map(p => p[0]?.toUpperCase())
      .join('')
  }

  function avatarColor (seed: string | null | undefined): string {
    const s = String(seed || 'x')
    const palette = [
      'rgb(var(--v-theme-cashViolet500))',
      'rgb(var(--v-theme-cashIndigo600))',
      'rgb(var(--v-theme-cashSky400))',
      'rgb(var(--v-theme-cashEmerald500))',
      'rgb(var(--v-theme-cashAmber500))',
      'rgb(var(--v-theme-cashRose400))',
    ]
    const code = s.codePointAt(0) ?? 0
    return palette[code % palette.length] ?? palette[0] ?? 'rgb(var(--v-theme-cashIndigo600))'
  }

  function timeAgo (iso: string): string {
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return ''
    const diffSeconds = Math.round((Date.now() - d.getTime()) / 1000)
    const abs = Math.abs(diffSeconds)

    // Past-only style like the reference UI.
    if (abs < 60) return 'agora'
    const mins = Math.round(abs / 60)
    if (mins < 60) return `há ${mins} min`
    const hours = Math.round(abs / 3600)
    if (hours < 24) return `há ${hours} h`
    const days = Math.round(abs / 86_400)
    return `há ${days} dias`
  }

  function dayMonth (iso: string): string {
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return ''
    const day = String(d.getDate()).padStart(2, '0')
    const monthRaw = new Intl.DateTimeFormat('pt-BR', { month: 'short' }).format(d)
    const month = monthRaw.replace('.', '')
    return `${day} de ${month}`
  }

  onMounted(async () => {
    // Never block notices list on Service Worker readiness.
    void refreshPushStatus()
    await fetchNotices()
  })
</script>

<style scoped>
.avisos-page {
  min-height: 100vh;
  background: linear-gradient(
    180deg,
    rgba(var(--v-theme-cashViolet50), 1) 0%,
    rgba(var(--v-theme-surface), 1) 55%,
    rgba(var(--v-theme-surface), 1) 100%
  );
}

.max-wrap {
  max-width: 720px;
  margin: 0 auto;
}

.avisos-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: rgba(var(--v-theme-surface), 0.78);
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  backdrop-filter: blur(14px);
}

.btn-back {
  border-radius: 999px;
}

.header-icon {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashIndigo600), 1),
    rgba(var(--v-theme-cashViolet500), 1)
  );
}

.btn-notify {
  border-color: rgba(var(--v-theme-on-surface), 0.14);
}

.btn-notify--on {
  color: rgb(var(--v-theme-cashIndigo600));
  background: rgba(var(--v-theme-cashIndigo600), 0.06);
  border-color: rgba(var(--v-theme-cashIndigo600), 0.25);
}

.new-closed {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  background: rgba(var(--v-theme-surface), 1);
  border: 1px dashed rgba(var(--v-theme-cashIndigo600), 0.35);
  border-radius: 18px;
  color: rgba(var(--v-theme-cashIndigo600), 1);
  transition: all 0.18s ease;
}

.new-closed:hover {
  border-color: rgba(var(--v-theme-cashIndigo600), 0.55);
  background: rgba(var(--v-theme-cashIndigo600), 0.04);
}

.new-closed__icon {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  background: rgba(var(--v-theme-cashIndigo600), 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}

.new-open {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}

.new-open__badge {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashIndigo600), 1),
    rgba(var(--v-theme-cashViolet500), 1)
  );
}

.field-label {
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.55);
  font-weight: 700;
  margin-bottom: 6px;
}

.btn-publish {
  color: white;
  background: linear-gradient(
    90deg,
    rgba(var(--v-theme-cashIndigo600), 1),
    rgba(var(--v-theme-cashViolet500), 1)
  );
}

.spin {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 4px solid rgba(var(--v-theme-cashIndigo600), 0.12);
  border-top-color: rgba(var(--v-theme-cashIndigo600), 1);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 80px 16px;
}

.empty__circle {
  width: 80px;
  height: 80px;
  border-radius: 999px;
  background: rgba(var(--v-theme-cashIndigo600), 0.09);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  box-shadow: 0 10px 22px rgba(var(--v-theme-on-surface), 0.05);
  transition: box-shadow 0.18s ease, transform 0.18s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 34px rgba(var(--v-theme-on-surface), 0.08);
}

.card--pinned {
  border-color: rgba(var(--v-theme-cashIndigo600), 0.25);
  box-shadow: 0 10px 22px rgba(var(--v-theme-cashIndigo600), 0.08);
}

.card-pin {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(var(--v-theme-cashIndigo600), 0.08);
  border-bottom: 1px solid rgba(var(--v-theme-cashIndigo600), 0.18);
  color: rgba(var(--v-theme-cashIndigo600), 1);
  font-size: 12px;
  font-weight: 700;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
}

.avatar--sm {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.dot {
  color: rgba(var(--v-theme-on-surface), 0.22);
}

.pre {
  white-space: pre-line;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  margin-top: 16px;
  padding-top: 12px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  background: transparent;
  color: rgba(var(--v-theme-on-surface), 0.45);
  transition: background 0.18s ease, color 0.18s ease;
}

.pill:hover {
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.pill--liked {
  background: rgba(var(--v-theme-cashRose400), 0.12);
  color: rgba(var(--v-theme-cashRed600), 1);
}

.pill__count {
  font-weight: 800;
}

.sheet {
  height: 85vh;
  border-top-left-radius: 26px;
  border-top-right-radius: 26px;
  overflow: hidden;
}

.sheet__header {
  padding: 16px 18px;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}

.sheet__body {
  padding: 16px 18px;
  overflow-y: auto;
  height: calc(85vh - 140px);
}

.sheet-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}

.sheet-empty__circle {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}

.comment-row {
  display: flex;
  gap: 12px;
}

.comment {
  flex: 1;
  background: rgba(var(--v-theme-on-surface), 0.04);
  border-radius: 18px;
  border-top-left-radius: 6px;
  padding: 12px 14px;
}

.sheet__footer {
  padding: 14px 18px;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  background: rgba(var(--v-theme-surface), 1);
}

.btn-send {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashIndigo600), 1),
    rgba(var(--v-theme-cashViolet500), 1)
  );
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.card-enter-active,
.card-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.card-enter-from,
.card-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
