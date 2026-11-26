// Dars gaplarini tekshiradi:  node manba/tekshir.js
//  - har qator: dars|inglizcha|oʻzbekcha
//  - har bir gapda shu darsning kamida bitta soʻzi bor
//  - gaplar takrorlanmaydi (umumiy gaplar bilan ham)
//  - har darsda kamida 10 ta gap
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const root = path.join(dir, '..');
const W = JSON.parse(fs.readFileSync(path.join(root, 'words.json'), 'utf8'));
const IDX = new Map();
W.forEach((x, i) => { const k = x[0].toLowerCase(); if (!IDX.has(k)) IDX.set(k, i); });
// index.html dagi lemma() va analyze() funksiyalari aynan shu yerda ishlatiladi
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const src = html.slice(html.indexOf('const IRR'), html.indexOf('/* ---------- text comparison'));
const { lemma, analyze } = new Function('IDX', src + '; return { lemma, analyze };')(IDX);

const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();
const seen = new Map();
for (const line of fs.readFileSync(path.join(dir, 'gaplar.txt'), 'utf8').split('\n')) {
  const en = line.split('|')[0].trim(); if (en) seen.set(norm(en), 'gaplar.txt');
}
const files = fs.readdirSync(dir).filter(f => /^dars-gaplari-\d+\.txt$/.test(f)).sort();
const perLesson = new Map();
const errors = [];
let total = 0;
for (const f of files) {
  fs.readFileSync(path.join(dir, f), 'utf8').split('\n').forEach((raw, n) => {
    const line = raw.trim();
    if (!line || line.startsWith('#')) return;
    const parts = line.split('|').map(s => s.trim());
    const where = f + ':' + (n + 1);
    if (parts.length !== 3 || !/^\d+$/.test(parts[0]) || !parts[1] || !parts[2]) { errors.push(where + ' format: ' + line); return; }
    const li = +parts[0];
    if (li < 1 || li > 150) { errors.push(where + ' dars raqami: ' + li); return; }
    const key = norm(parts[1]);
    if (seen.has(key)) errors.push(where + ' takror (' + seen.get(key) + '): ' + parts[1]);
    else seen.set(key, where);
    const lo = (li - 1) * 20, hi = lo + 20;
    const { idxs } = analyze(parts[1]);
    if (!idxs.some(i => i >= lo && i < hi)) errors.push(where + ' ' + li + '-dars soʻzi yoʻq: ' + parts[1]);
    perLesson.set(li, (perLesson.get(li) || 0) + 1);
    total++;
  });
}
const maxLesson = Math.max(0, ...perLesson.keys());
for (let li = 1; li <= maxLesson; li++) if ((perLesson.get(li) || 0) < 10) errors.push(li + '-darsda ' + (perLesson.get(li) || 0) + ' ta gap (kamida 10 kerak)');
console.log('Dars gaplari: ' + total + ' ta, ' + perLesson.size + ' ta dars');
if (errors.length) { console.log('Muammolar:\n  ' + errors.join('\n  ')); process.exitCode = 1; }
else console.log('Muammo yoʻq.');
