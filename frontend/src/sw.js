/* eslint-disable no-undef */
import { clientsClaim } from 'workbox-core'
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'

clientsClaim()
cleanupOutdatedCaches()

self.addEventListener('message', (event) => {
	if (event?.data && event.data.type === 'SKIP_WAITING') self.skipWaiting()
})

self.skipWaiting()

// Precache assets injected by VitePWA during build
precacheAndRoute(self.__WB_MANIFEST)
