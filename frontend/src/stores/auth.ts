import { defineStore } from 'pinia'
import { http } from '../api/http'

type Role = 'ADMIN' | 'COACH' | 'PLAYER'

type Me = {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: Role
  athlete_id?: number
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') as string | null,
    refreshToken: localStorage.getItem('refreshToken') as string | null,
    me: null as Me | null,
    loadingMe: false,
  }),

  getters: {
    isAuthenticated: (s) => !!s.accessToken,
    role: (s) => s.me?.role ?? null,
    isCoachOrAdmin: (s) => s.me?.role === 'COACH' || s.me?.role === 'ADMIN',
    isPlayer: (s) => s.me?.role === 'PLAYER',
  },

  actions: {
    async login(username: string, password: string) {
      const { data } = await http.post('/api/accounts/login/', { username, password })
      this.accessToken = data.access
      this.refreshToken = data.refresh
      localStorage.setItem('accessToken', this.accessToken!)
      localStorage.setItem('refreshToken', this.refreshToken!)
      await this.fetchMe()
    },

    async fetchMe() {
      this.loadingMe = true
      try {
        const { data } = await http.get('/api/accounts/me/')
        this.me = data
      } finally {
        this.loadingMe = false
      }
    },

    async refresh(): Promise<boolean> {
      if (!this.refreshToken) return false
      try {
        const { data } = await http.post('/api/accounts/refresh/', { refresh: this.refreshToken })
        this.accessToken = data.access
        localStorage.setItem('accessToken', this.accessToken!)
        return true
      } catch {
        return false
      }
    },

    async logout() {
      this.accessToken = null
      this.refreshToken = null
      this.me = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
  },
})