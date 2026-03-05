/* eslint-disable no-undef */
import { precacheAndRoute } from 'workbox-precaching'

// Precache assets injected by VitePWA during build
precacheAndRoute(self.__WB_MANIFEST)
