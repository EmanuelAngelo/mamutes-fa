/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import { createVuetify } from 'vuetify'
// Styles
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: (() => {
      try {
        const v = localStorage.getItem('theme_preference')
        if (v === 'light' || v === 'dark') return v
      } catch {
        // ignore
      }
      return 'system'
    })(),
  },
})
