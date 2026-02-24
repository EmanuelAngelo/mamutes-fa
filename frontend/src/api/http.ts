import axios, { AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 20000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

let isRefreshing = false
let refreshQueue: Array<(token: string | null) => void> = []

function resolveQueue(token: string | null) {
  refreshQueue.forEach((cb) => cb(token))
  refreshQueue = []
}

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const auth = useAuthStore()
    const status = error.response?.status
    const originalConfig: any = error.config

    if (status === 401 && !originalConfig?._retry && auth.refreshToken) {
      originalConfig._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((token) => {
            if (!token) return reject(error)
            originalConfig.headers.Authorization = `Bearer ${token}`
            resolve(http(originalConfig))
          })
        })
      }

      isRefreshing = true
      try {
        const ok = await auth.refresh()
        isRefreshing = false
        resolveQueue(ok ? auth.accessToken : null)

        if (ok && auth.accessToken) {
          originalConfig.headers.Authorization = `Bearer ${auth.accessToken}`
          return http(originalConfig)
        }
      } catch {
        isRefreshing = false
        resolveQueue(null)
      }

      await auth.logout()
    }

    return Promise.reject(error)
  }
)