// So'zlar va gaplar bazasini qayta yig'adi:
//   node manba/build.js
// manba/sozlar-*.txt  (inglizcha|o'zbekcha|turkum)  -> words.json  (birinchi 3000 ta noyob so'z)
// manba/gaplar.txt    (inglizcha|o'zbekcha)          -> sentences.json
// Turkumlar: n ot, v fe'l, a sifat, d ravish, p olmosh, r predlog, c bog'lovchi, x boshqa.
// O'zbekcha matnda oddiy apostrof yoziladi: o' va g' -> oʻ, gʻ; qolganlari -> ʼ (tutuq belgisi).
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const root = path.join(dir, '..');
const POS = new Set(['n', 'v', 'a', 'd', 'p', 'r', 'c', 'x']);
const uzFix = s => s.replace(/([oOgG])'/g, (m, l) => l + 'ʻ').replace(/'/g, 'ʼ');

const files = fs.readdirSync(dir).filter(f => /^sozlar-\d+\.txt$/.test(f)).sort((a, b) => parseInt(a.match(/\d+/)) - parseInt(b.match(/\d+/)));
const seen = new Set();
const words = [];
const problems = [];
for (const f of files) {
  for (const raw of fs.readFileSync(path.join(dir, f), 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const parts = line.split('|').map(s => s.trim());
    if (parts.length !== 3 || !POS.has(parts[2])) { problems.push(f + ': ' + line); continue; }
    const [en, uz, pos] = parts;
    const key = en === 'May' ? 'May' : en.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    words.push([en, uzFix(uz), pos]);
  }
}
if (problems.length) { console.error('Notoʻgʻri qatorlar:\n' + problems.join('\n')); process.exit(1); }
if (words.length < 3000) console.warn('Diqqat: faqat ' + words.length + ' ta soʻz bor.');
const list = words.slice(0, 3000);
fs.writeFileSync(path.join(root, 'words.json'), '[\n' + list.map(w => JSON.stringify(w)).join(',\n') + '\n]\n');

const sentences = fs.readFileSync(path.join(dir, 'gaplar.txt'), 'utf8').split('\n').map(l => l.trim()).filter(Boolean).map(l => {
  const [en, uz] = l.split('|').map(s => s && s.trim());
  if (!en || !uz) { console.error('Notoʻgʻri gap: ' + l); process.exit(1); }
  return [en, uzFix(uz)];
});
fs.writeFileSync(path.join(root, 'sentences.json'), '[\n' + sentences.map(r => JSON.stringify(r)).join(',\n') + '\n]\n');
console.log('words.json: ' + list.length + ' ta soʻz, sentences.json: ' + sentences.length + ' ta gap');
