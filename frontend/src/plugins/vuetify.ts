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
    themes: {
      light: {
        colors: {
          cashViolet50: '#f5f3ff',
          cashViolet500: '#8b5cf6',
          cashIndigo600: '#4f46e5',
          cashSky400: '#38bdf8',
          cashBlue600: '#2563eb',
          cashAmber500: '#f59e0b',
          cashOrange600: '#ea580c',
          cashEmerald500: '#10b981',
          cashGreen600: '#16a34a',
          cashRose400: '#fb7185',
          cashPink600: '#db2777',
          cashRed600: '#dc2626',
          cashSlate400: '#94a3b8',
          cashSlate600: '#475569',
        },
      },
      dark: {
        colors: {
          cashViolet50: '#1a1630',
          cashViolet500: '#8b5cf6',
          cashIndigo600: '#6366f1',
          cashSky400: '#38bdf8',
          cashBlue600: '#3b82f6',
          cashAmber500: '#fbbf24',
          cashOrange600: '#fb923c',
          cashEmerald500: '#34d399',
          cashGreen600: '#22c55e',
          cashRose400: '#fb7185',
          cashPink600: '#ec4899',
          cashRed600: '#ef4444',
          cashSlate400: '#94a3b8',
          cashSlate600: '#64748b',
        },
      },
    },
  },
})
