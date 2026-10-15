'use strict';
const CACHE = 'ciftlikpro-app-edition-2.0.8';
const STATIC = ['/app-assets/offline.html','/app-assets/icon-192.png','/app-assets/icon-512.png'];
self.addEventListener('install',event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(STATIC)).then(() => self.skipWaiting()));
});
self.addEventListener('activate',event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('ciftlikpro-app-edition-') && key!==CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
// Business pages and POST requests are always handled by the live Enterprise server.
self.addEventListener('fetch',event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(() => caches.match('/app-assets/offline.html')));
  } else if (STATIC.includes(new URL(event.request.url).pathname)) {
    event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
  }
});
