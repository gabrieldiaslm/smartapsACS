const CACHE_NAME = 'smart-aps-v2'; // Mudei para v2 para forçar atualização
const OFFLINE_URL = '/offline/';

const ASSETS_TO_CACHE = [
    OFFLINE_URL,
    '/static/images/wip.jpg',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    // ATENÇÃO: Esta versão DEVE ser idêntica à do base.html
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

self.addEventListener('install', (event) => {
    self.skipWaiting(); // Força atualização imediata
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    console.log('Removendo cache antigo:', key);
                    return caches.delete(key);
                }
            }));
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Ignora requisições que não sejam GET (ex: POST de formulários)
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // CHECAGEM DE SEGURANÇA:
                // Se não for sucesso (200) ou se for um tipo estranho, NÃO salva no cache.
                // Isso evita o erro "Glyph bbox" (salvar erro 404 como fonte)
                if (!response || response.status !== 200 || response.type === 'error') {
                    return response;
                }

                // Se for a fonte problemática (woff2), só salva se for perfeita
                if (event.request.url.includes('woff2') && response.headers.get('content-type') && !response.headers.get('content-type').includes('font')) {
                     return response; 
                }

                const responseToCache = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return response;
            })
            .catch(() => {
                return caches.match(event.request).then((cachedResponse) => {
                    if (cachedResponse) return cachedResponse;
                    if (event.request.mode === 'navigate') return caches.match(OFFLINE_URL);
                });
            })
    );
});