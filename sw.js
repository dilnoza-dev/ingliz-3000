// Avtomatik yaratilgan: node manba/ilova.js. Qoʻlda tahrir qilmang.
const CORE = 'ingliz3000-core-f63383b648';
const AUDIO = 'ingliz3000-audio-0864f236ee';
// Telefon xotirasini band qilmaslik uchun faqat oxirgi eshitilgan shuncha ovoz fayli saqlanadi (bir necha MB).
const AUDIO_KEEP = 16;
const CORE_FILES = ['./', 'index.html', 'words.json', 'sentences.json', 'grammatika.json', 'audio/index.json', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CORE).then(c => c.addAll(CORE_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('ingliz3000-') && k !== CORE && k !== AUDIO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
async function trimAudio(c) {
  const keys = await c.keys();
  for (const k of keys.slice(0, Math.max(0, keys.length - AUDIO_KEEP))) await c.delete(k);
}
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Ovoz fayllari: oxirgi AUDIO_KEEP tasi keshda turadi (ular internetsiz ham ishlaydi), qolganlari kerak boʻlganda yuklanadi
  if (url.origin === location.origin && url.pathname.includes('/audio/') && url.pathname.endsWith('.mp3')) {
    e.respondWith(caches.open(AUDIO).then(async c => {
      const hit = await c.match(req);
      if (hit) {
        // eng soʻnggi ishlatilgan deb belgilash: oʻchirib, oxiriga qayta qoʻyamiz
        e.waitUntil(hit.clone().blob().then(b => c.delete(req).then(() => c.put(req, new Response(b, { headers: hit.headers })))).catch(() => {}));
        return hit;
      }
      const res = await fetch(req);
      if (res.ok) e.waitUntil(c.put(req, res.clone()).then(() => trimAudio(c)).catch(() => {}));
      return res;
    }));
    return;
  }
  // Ilovaning oʻz fayllari: avval internetdan (yangilanishlar uchun), boʻlmasa keshdan
  if (url.origin === location.origin) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CORE).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html'))));
    return;
  }
  // Shriftlar: keshdan, orqa fonda yangilanadi
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(CORE).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(res => { c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
  }
});
