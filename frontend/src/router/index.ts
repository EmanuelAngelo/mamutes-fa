import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/pages/Login.vue') },

  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    children: [
      { path: '', redirect: '/player' },

      // PLAYER
      {
        path: 'player',
        name: 'player-dashboard',
        component: () => import('@/pages/player/Dashboard.vue'),
        meta: { requiresAuth: true, roles: ['PLAYER'] },
      },
      {
        path: 'player/profile',
        name: 'player-profile',
        component: () => import('@/pages/player/Profile.vue'),
        meta: { requiresAuth: true, roles: ['PLAYER'] },
      },

      // COACH / ADMIN
      {
        path: 'coach',
        name: 'coach-dashboard',
        component: () => import('@/pages/coach/Dashboard.vue'),
        meta: { requiresAuth: true, roles: ['COACH', 'ADMIN'] },
      },
      {
        path: 'coach/trainings',
        name: 'coach-trainings',
        component: () => import('@/pages/coach/Trainings.vue'),
        meta: { requiresAuth: true, roles: ['COACH', 'ADMIN'] },
      },
      {
        path: 'coach/trainings/:id',
        name: 'coach-training-detail',
        component: () => import('@/pages/coach/TrainingDetail.vue'),
        meta: { requiresAuth: true, roles: ['COACH', 'ADMIN'] },
      },
      {
        path: 'coach/athletes',
        name: 'coach-athletes',
        component: () => import('@/pages/coach/Athletes.vue'),
        meta: { requiresAuth: true, roles: ['COACH', 'ADMIN'] },
      },
      {
        path: 'coach/drills-catalog',
        name: 'coach-drills-catalog',
        component: () => import('@/pages/coach/DrillCatalog.vue'),
        meta: { requiresAuth: true, roles: ['COACH', 'ADMIN'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!auth.accessToken) return { name: 'login' }

    if (!auth.me && !auth.loadingMe) {
      try {
        await auth.fetchMe()
      } catch {
        await auth.logout()
        return { name: 'login' }
      }
    }

    const roles = (to.meta.roles as string[] | undefined) ?? []
    if (roles.length && auth.me && !roles.includes(auth.me.role)) {
      return auth.me.role === 'PLAYER'
        ? { name: 'player-dashboard' }
        : { name: 'coach-dashboard' }
    }
  }

  if (to.name === 'login' && auth.accessToken) {
    if (!auth.me) await auth.fetchMe()
    return auth.me?.role === 'PLAYER'
      ? { name: 'player-dashboard' }
      : { name: 'coach-dashboard' }
  }

  return true
})

export default router