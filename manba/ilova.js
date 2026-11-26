// Telefon/kompyuterga oʻrnatiladigan ilova (PWA) fayllarini yigʻadi:
//   node manba/ilova.js
// manba/sahifa.html (Claude'dagi artifact bilan bir xil sahifa) -> index.html (toʻliq HTML hujjat)
// va sw.js (internetsiz ishlash uchun kesh). sahifa.html oʻzgarganda qayta ishga tushiring.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const dir = __dirname;
const root = path.join(dir, '..');
const read = f => fs.readFileSync(path.join(root, f));
const sha = buf => crypto.createHash('sha1').update(buf).digest('hex');

const page = fs.readFileSync(path.join(dir, 'sahifa.html'), 'utf8');
const cut = page.indexOf('<style>');
if (cut < 0) throw new Error('sahifa.html da <style> topilmadi');
const preamble = page.slice(0, cut)
  .split('\n')
  .filter(l => l.trim() && !/charset=|name="viewport"|claude:/.test(l))
  .join('\n');
const body = page.slice(cut);

const icons = ['icon-192.png', 'icon-512.png', 'maskable-512.png', 'apple-touch-icon.png'].map(f => sha(read('icons/' + f))).join('');
const version = sha(page + sha(read('words.json')) + sha(read('sentences.json')) + sha(read('audio/index.json')) + icons).slice(0, 10);
const audioVersion = sha(read('audio/index.json')).slice(0, 10);

const html = `<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="4000 ta inglizcha soʻzni (A1 dan B2 gacha) oʻzbek tilida oʻrgatadigan ilova: 4 variantli test, gap tuzish, tarjima va talaffuz.">
<meta name="theme-color" content="#17357A">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="3000 B2">
${preamble}
<style>
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); color-scheme: light; }
body { margin: 0; font-size: 14px; }
img { max-width: 100%; }
[hidden] { display: none !important; }
.install-btn {
  position: fixed; left: 50%; transform: translateX(-50%); z-index: 30;
  bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; border: 0; border-radius: 999px;
  background: #17357A; color: #fff; font: 700 15px/1 system-ui, sans-serif; box-shadow: 0 6px 20px rgba(0,0,0,.3);
}
</style>
</head>
<body>
${body}
<button class="install-btn" id="installBtn" type="button" hidden>⬇ Ilovani oʻrnatish</button>
<script>
(() => {
  // App version ${version}
  let deferred = null;
  const btn = document.getElementById('installBtn');
  window.addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; btn.hidden = false; });
  btn.addEventListener('click', async () => {
    if (!deferred) return;
    deferred.prompt();
    try { await deferred.userChoice; } catch (e) { /* ignore */ }
    deferred = null; btn.hidden = true;
  });
  window.addEventListener('appinstalled', () => { btn.hidden = true; });
  if ('serviceWorker' in navigator) window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
})();
</script>
</body>
</html>
`;

const sw = `// Avtomatik yaratilgan: node manba/ilova.js. Qoʻlda tahrir qilmang.
const CORE = 'ingliz3000-core-${version}';
const AUDIO = 'ingliz3000-audio-${audioVersion}';
const CORE_FILES = ['./', 'index.html', 'words.json', 'sentences.json', 'audio/index.json', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CORE).then(c => c.addAll(CORE_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('ingliz3000-') && k !== CORE && k !== AUDIO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Ovoz fayllari: bir marta yuklangach keshdan olinadi (internetsiz ham ishlaydi)
  if (url.origin === location.origin && url.pathname.includes('/audio/') && url.pathname.endsWith('.mp3')) {
    e.respondWith(caches.open(AUDIO).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) await c.put(req, res.clone());
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
`;

fs.writeFileSync(path.join(root, 'index.html'), html);
fs.writeFileSync(path.join(root, 'sw.js'), sw);
console.log('index.html va sw.js tayyor (versiya ' + version + ', ovoz ' + audioVersion + ')');
