/* ==========================================================================
   Service Worker — Ядро офлайн-устойчивости (Этап 4, шаг 4.3)
   Путь отдачи: GET /sw.js (FastAPI, Cache-Control: no-cache, Service-Worker-Allowed: /)
   Скоп 152-ФЗ: /api/* и не-GET запросы SW НЕ перехватывает (сеть напрямую).
   ========================================================================== */
const CACHE_NAME = 'cmz-cache-v1';

const PRECACHE_URLS = [
    '/offline',
    '/static/css/style.css',
    '/static/css/article.css',
    '/static/js/bubbles.js'
];

// Установка: precache критического ядра оболочки
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Активация: ротация кэшей — удаляем всё, кроме текущей версии
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            ))
            .then(() => self.clients.claim())
    );
});

// Обработка запросов
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Защита API и чувствительных данных (152-ФЗ): мимо кэша, напрямую в сеть
    if (url.pathname.startsWith('/api/') || request.method !== 'GET') {
        return;
    }

    // HTML-навигация: Network-First с офлайн-фоллбэком /offline
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .then((response) => response)
                .catch(() => caches.match('/offline'))
        );
        return;
    }

    // Статические ресурсы: Cache-First + параллельное обновление (SWR)
    if (url.pathname.startsWith('/static/')) {
        // Свежая версия тянемся в фоне и кладем в кэш (если сеть жива)
        const networkUpdate = fetch(request)
            .then((response) => {
                if (response && response.ok) {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
                }
                return response;
            })
            .catch(() => null);
        event.waitUntil(networkUpdate);
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) {
                    return cached;
                }
                // Нет в кэше: ждем ответ из сети, иначе сетевая ошибка
                return networkUpdate.then((response) => response || Response.error());
            })
        );
    }
});
