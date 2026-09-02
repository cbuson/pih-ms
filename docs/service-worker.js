/* SPDX-License-Identifier: AGPL-3.0-or-later */
const SHELL_CACHE = 'pih-ms-shell-v271000';
const RUNTIME_CACHE = 'pih-ms-runtime-v271000';
const APP_SHELL = [
  './',
  './index.html',
  './offline.html',
  './manifest.webmanifest',
  './assets/css/pih.css?v=271000',
  './assets/css/pih-mobile.css?v=271000',
  './assets/css/pih-visual-controls.css?v=271000',
  './assets/css/pih-v27.css?v=271000',
  './assets/css/pih-v271.css?v=271000',
  './assets/js/pih.js?v=271000',
  './assets/js/metric-help.js?v=271000',
  './assets/js/pih-mobile.js?v=271000',
  './assets/js/pih-visual-controls.js?v=271000',
  './assets/js/pih-stats-visual.js?v=271000',
  './assets/js/pih-stats-full.js?v=271000',
  './assets/js/pih-pwa.js?v=271000',
  './assets/img/mi-posicao-ms.svg',
  './assets/img/pih-ms-icon.svg',
  './assets/img/pih-ms-icon-192.png',
  './assets/img/pih-ms-icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(SHELL_CACHE).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => ![SHELL_CACHE, RUNTIME_CACHE].includes(key)).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const relativePath = url.pathname.replace(self.registration.scope.replace(url.origin, ''), '');
  const scientificData = relativePath.startsWith('data/') || /\.(?:csv|geojson|xlsx|zip)$/i.test(relativePath);
  if (scientificData) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const copy = response.clone();
          caches.open(RUNTIME_CACHE).then(cache => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request).then(response => response || caches.match('./offline.html')))
    );
    return;
  }

  if (!/\.(?:css|js|svg|png|jpg|jpeg|webp|woff2?|webmanifest)$/i.test(relativePath)) return;
  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(response => {
      if (!response || !response.ok) return response;
      const copy = response.clone();
      caches.open(RUNTIME_CACHE).then(cache => cache.put(request, copy));
      return response;
    }))
  );
});
