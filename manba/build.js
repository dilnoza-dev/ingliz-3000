// So'zlar va gaplar bazasini qayta yig'adi:
//   node manba/build.js
// manba/sozlar-*.txt  (inglizcha|o'zbekcha|turkum)  -> words.json  (birinchi 3000 ta noyob so'z, A1–B1)
// manba/b2-sozlar-*.txt (xuddi shu format)            -> words.json  (keyingi 1000 ta B2 so'zi, 151–200-darslar)
// manba/gaplar.txt    (inglizcha|o'zbekcha)          -> sentences.json (umumiy gaplar)
// manba/dars-gaplari-*.txt (dars|inglizcha|o'zbekcha) -> sentences.json (har bir darsning gaplari)
// Turkumlar: n ot, v fe'l, a sifat, d ravish, p olmosh, r predlog, c bog'lovchi, x boshqa.
// O'zbekcha matnda oddiy apostrof yoziladi: o' va g' -> oʻ, gʻ; qolganlari -> ʼ (tutuq belgisi).
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const root = path.join(dir, '..');
const POS = new Set(['n', 'v', 'a', 'd', 'p', 'r', 'c', 'x']);
const uzFix = s => s.replace(/([oOgG])'/g, (m, l) => l + 'ʻ').replace(/'/g, 'ʼ');

const problems = [];
const keyOf = en => en === 'May' ? 'May' : en.toLowerCase();
// Berilgan fayllardagi noyob soʻzlar (seen dagilar tashlab ketiladi)
function readWords(re, seen) {
  const files = fs.readdirSync(dir).filter(f => re.test(f)).sort((a, b) => parseInt(a.match(/\d+/)) - parseInt(b.match(/\d+/)));
  const out = [];
  for (const f of files) {
    for (const raw of fs.readFileSync(path.join(dir, f), 'utf8').split('\n')) {
      const line = raw.trim();
      if (!line || line.startsWith('#')) continue;
      const parts = line.split('|').map(s => s.trim());
      if (parts.length !== 3 || !POS.has(parts[2])) { problems.push(f + ': ' + line); continue; }
      const [en, uz, pos] = parts;
      if (seen.has(keyOf(en))) continue;
      seen.add(keyOf(en));
      out.push([en, uzFix(uz), pos]);
    }
  }
  return out;
}
const base = readWords(/^sozlar-\d+\.txt$/, new Set());
if (base.length < 3000) console.warn('Diqqat: faqat ' + base.length + ' ta soʻz bor.');
const main = base.slice(0, 3000);
const b2 = readWords(/^b2-sozlar-\d+\.txt$/, new Set(main.map(w => keyOf(w[0])))).slice(0, 1000);
if (problems.length) { console.error('Notoʻgʻri qatorlar:\n' + problems.join('\n')); process.exit(1); }
if (b2.length < 1000) console.warn('Diqqat: B2 darajasida faqat ' + b2.length + ' ta soʻz bor.');
const list = main.concat(b2);
// Talaffuz yozuvi (IPA): manba/talaffuz.txt, uni manba/ovoz.py yaratadi.
const ipaFile = path.join(dir, 'talaffuz.txt');
if (fs.existsSync(ipaFile)) {
  const ipa = new Map(fs.readFileSync(ipaFile, 'utf8').split('\n').filter(Boolean).map(l => l.split('|')));
  let missing = 0;
  for (const w of list) { if (ipa.has(w[0])) w.push(ipa.get(w[0])); else missing++; }
  if (missing) console.warn('Diqqat: ' + missing + ' ta soʻzning talaffuz yozuvi yoʻq. manba/ovoz.py ni qayta ishga tushiring.');
}
fs.writeFileSync(path.join(root, 'words.json'), '[\n' + list.map(w => JSON.stringify(w)).join(',\n') + '\n]\n');

// Umumiy gaplar (dars raqami 0) va har bir darsning gaplari: [inglizcha, oʻzbekcha, dars]
const sentences = fs.readFileSync(path.join(dir, 'gaplar.txt'), 'utf8').split('\n').map(l => l.trim()).filter(Boolean).map(l => {
  const [en, uz] = l.split('|').map(s => s && s.trim());
  if (!en || !uz) { console.error('Notoʻgʻri gap: ' + l); process.exit(1); }
  return [en, uzFix(uz), 0];
});
const lessonFiles = fs.readdirSync(dir).filter(f => /^dars-gaplari-\d+\.txt$/.test(f)).sort();
const lessonRows = [];
for (const f of lessonFiles) {
  for (const raw of fs.readFileSync(path.join(dir, f), 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const [li, en, uz] = line.split('|').map(s => s && s.trim());
    if (!/^\d+$/.test(li || '') || !en || !uz) { console.error('Notoʻgʻri dars gapi (' + f + '): ' + line); process.exit(1); }
    lessonRows.push([en, uzFix(uz), +li]);
  }
}
lessonRows.sort((a, b) => a[2] - b[2]);
sentences.push(...lessonRows);
fs.writeFileSync(path.join(root, 'sentences.json'), '[\n' + sentences.map(r => JSON.stringify(r)).join(',\n') + '\n]\n');
console.log('words.json: ' + list.length + ' ta soʻz (' + b2.length + ' tasi B2), sentences.json: ' + sentences.length + ' ta gap (' + lessonRows.length + ' tasi darslarga biriktirilgan)');
