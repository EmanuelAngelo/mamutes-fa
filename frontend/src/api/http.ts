import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

// URL principal (produção)
export const API_BASE_URL = 'https://ruthusky.pythonanywhere.com'

// URL local (dev)
// export const LOCAL_API_BASE_URL = 'http://127.0.0.1:8000/api'

function resolveApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    // if (host === 'localhost' || host === '127.0.0.1') return LOCAL_API_BASE_URL
  }
  return joinUrl(API_BASE_URL, 'api')
}

function joinUrl(base: string, path: string): string {
  const b = base.replace(/\/+$/, '')
  const p = path.replace(/^\/+/, '')
  return `${b}/${p}`
}

function getAccessToken(): string | null {
  return localStorage.getItem('accessToken')
}

function getRefreshToken(): string | null {
  return localStorage.getItem('refreshToken')
}

function setAccessToken(token: string) {
  localStorage.setItem('accessToken', token)
}

function clearTokens() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
}

export const http = axios.create({
  baseURL: resolveApiBaseUrl(),
  timeout: 20000,
})

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof config.url === 'string') {
    if (config.url.startsWith('/api/')) config.url = config.url.slice(4)
    if (config.url.startsWith('api/')) config.url = config.url.slice(3)
  }
  const token = getAccessToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
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
    const status = error.response?.status
    const originalConfig: any = error.config

    if (status !== 401 || !originalConfig) return Promise.reject(error)

    const originalUrl: string = String(originalConfig.url ?? '')
    if (originalUrl.includes('/accounts/login/') || originalUrl.includes('/accounts/refresh/')) {
      return Promise.reject(error)
    }

    if (originalConfig._retry) return Promise.reject(error)
    originalConfig._retry = true

    const refresh = getRefreshToken()
    if (!refresh) {
      clearTokens()
      if (typeof window !== 'undefined') window.location.href = '/login'
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push((token) => {
          if (!token) return reject(error)
          originalConfig.headers = originalConfig.headers ?? {}
          originalConfig.headers.Authorization = `Bearer ${token}`
          resolve(http(originalConfig))
        })
      })
    }

    isRefreshing = true
    try {
      const baseUrl = resolveApiBaseUrl()
      const { data } = await axios.post(joinUrl(baseUrl, 'accounts/refresh/'), { refresh })
      const newAccess = (data as any)?.access as string | undefined
      if (!newAccess) throw error

      setAccessToken(newAccess)
      resolveQueue(newAccess)

      originalConfig.headers = originalConfig.headers ?? {}
      originalConfig.headers.Authorization = `Bearer ${newAccess}`
      return http(originalConfig)
    } catch (e) {
      resolveQueue(null)
      clearTokens()
      if (typeof window !== 'undefined') window.location.href = '/login'
      return Promise.reject(e)
    } finally {
      isRefreshing = false
    }
  },
)
