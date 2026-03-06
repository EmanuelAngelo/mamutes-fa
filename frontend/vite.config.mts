import { fileURLToPath, URL } from 'node:url'
import Vue from '@vitejs/plugin-vue'
import Fonts from 'unplugin-fonts/vite'
import { defineConfig, type Plugin } from 'vite'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import { VitePWA } from 'vite-plugin-pwa'

function stripMdiFontPreloads(): Plugin {
  const preloadRegex =
    /<link\b[^>]*rel=["']preload["'][^>]*href=["'][^"']*materialdesignicons-webfont-[^"']+\.(?:woff2|woff|ttf|eot)(?:\?[^"']*)?["'][^>]*>\s*/gi

  return {
    name: 'strip-mdi-font-preloads',
    enforce: 'post',
    transformIndexHtml(html) {
      // Chrome warns if a preloaded font isn't used shortly after load.
      // MDI webfont is often only needed after route/components mount.
      return html.replace(preloadRegex, '')
    },
    generateBundle(_options, bundle) {
      for (const chunk of Object.values(bundle)) {
        if (chunk.type !== 'asset') continue
        if (!chunk.fileName.endsWith('.html')) continue

        const source =
          typeof chunk.source === 'string'
            ? chunk.source
            : Buffer.from(chunk.source).toString('utf8')

        const updated = source.replace(preloadRegex, '')
        if (updated !== source) chunk.source = updated
      }
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Vue({
      template: { transformAssetUrls },
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/styles/settings.scss',
      },
    }),
    VitePWA({
      registerType: 'autoUpdate',
      srcDir: 'src',
      filename: 'sw.js',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Mamutes FA',
        short_name: 'Mamutes FA',
        description: 'Gerenciamento de atletas e treinos para futebol americano',
        theme_color: '#111757',
        background_color: '#ffffffff',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        icons: [
          {
            src: '/web-app-manifest-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/web-app-manifest-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: '/web-app-manifest-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
    }),
    Fonts({
      fontsource: {
        families: [
          {
            name: 'Roboto',
            weights: [100, 300, 400, 500, 700, 900],
            styles: ['normal', 'italic'],
          },
        ],
      },
    }),
    stripMdiFontPreloads(),
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('src', import.meta.url)),
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue',
    ],
  },
  server: {
    port: 3000,
  },
})
