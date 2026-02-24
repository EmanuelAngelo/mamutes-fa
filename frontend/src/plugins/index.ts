import type { App } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'

// Vuetify (no template já vem)
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'

// Tailwind (template)
import '@/styles/main.css'

export function registerPlugins(app: App) {
  app.use(createPinia())
  app.use(router)

  const vuetify = createVuetify({
    components,
    directives,
  })
  app.use(vuetify)
}