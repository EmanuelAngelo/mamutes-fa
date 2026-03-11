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

self.addEventListener('push', (event) => {
	let payload = {}
	try {
		payload = event?.data ? event.data.json() : {}
	} catch {
		try {
			payload = event?.data ? { body: event.data.text() } : {}
		} catch {
			payload = {}
		}
	}

	const title = payload?.title || 'Mamutes F.A.'
	const options = {
		body: payload?.body || '',
		icon: '/web-app-manifest-192x192.png',
		badge: '/web-app-manifest-192x192.png',
		data: {
			url: payload?.url || '/notices',
			notice_id: payload?.notice_id,
		},
	}

	event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', (event) => {
	event.notification?.close?.()
	const url = event?.notification?.data?.url || '/'
	const target = new URL(url, self.location.origin).href

	event.waitUntil(
		clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
			for (const client of windowClients) {
				if ('focus' in client) {
					client.navigate?.(target)
					return client.focus()
				}
			}
			return clients.openWindow(target)
		}),
	)
})
