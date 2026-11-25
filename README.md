# 3000 Soʻz — ingliz tilini oʻrganish uchun

Oʻzbek tilida soʻzlashuvchilar uchun ingliz tili dasturi. Unda 3000 ta eng kerakli inglizcha soʻz 150 ta darsga boʻlingan, har darsda 20 tadan soʻz bor. Darajalar: A1, A2 va B1.

**Dasturni ochish:** https://claude.ai/artifact/W8NYMAPiM7G5fAvxxMTJ34

## Toʻrt bosqich

1. **Soʻzlar.** Soʻz chiqadi va pastda 4 ta variant boʻladi. Masalan, «tezlik» chiqadi, siz **speed** ni tanlaysiz. Xato qilingan soʻz test oxirida yana soʻraladi. Eski soʻzlar maʼlum kunlardan keyin takrorlashga qaytadi.
2. **Gaplar.** Oʻzbekcha gap beriladi, siz inglizcha soʻzlarni toʻgʻri tartibda bosib gap tuzasiz. Shu boʻlimda 10 ta asosiy grammatika qoidasi ham bor.
3. **Tarjima.** Oʻzbekcha gapni inglizcha yozasiz. Xatolar rangda koʻrsatiladi, Claude ularni oʻzbekcha tushuntiradi.
4. **Talaffuz.** Mikrofonni bosib, gapni inglizcha aytasiz. Dastur nima eshitganini koʻrsatadi va qaysi tovushda qiynalayotganingizni aytadi.

Bosh sahifada kunlik reja, oʻrganilgan soʻzlar soni va «Kamchiliklarim» boʻlimi bor. U yerda koʻp xato qilinadigan soʻzlar, talaffuzda qiynalgan soʻzlar va grammatik eslatmalar yigʻilib boradi.

Dastur avtomatik ravishda **boshlangʻich rejimda** ishlaydi: gaplar oddiy boʻladi, ovoz sekinroq chiqadi, tarjima va talaffuzda «Yordam» tugmasi bor. Sozlamalarda darajani «Oʻrta» ga oʻtkazish mumkin.

## Qayerda nima ishlaydi

| Imkoniyat | claude.ai havolasi orqali | Oddiy veb-sayt sifatida (GitHub Pages) |
|---|---|---|
| Soʻz testi, gap tuzish, tarjima | ✓ | ✓ |
| Claude tuzgan yangi gaplar va xatolarni tushuntirish | ✓ | — |
| Mikrofon (talaffuz) | ✓ kompyuterda Chrome yoki Edge'da | ✓ faqat Chrome'da |
| Natijalarni hisobda saqlash (boshqa qurilmada davom ettirish) | ✓ | — natija faqat shu brauzerda saqlanadi |

Veb-sayt sifatida ochish uchun: repozitoriyning **Settings → Pages** boʻlimida `main` branch va `/ (root)` papkasini tanlang.

## Fayllar

- `index.html` — dasturning oʻzi (bitta sahifa, qoʻshimcha kutubxonalar kerak emas).
- `words.json` — 3000 ta soʻz: `["inglizcha", "oʻzbekcha", "turkum"]`.
- `sentences.json` — 241 ta tayyor gap, osondan qiyinga qarab tartiblangan.
- `manba/` — yuqoridagi ikki faylning manbasi:
  - `sozlar-1.txt` … `sozlar-6.txt` — har qatorda `inglizcha|oʻzbekcha|turkum`;
  - `gaplar.txt` — har qatorda `inglizcha|oʻzbekcha`;
  - `build.js` — JSON fayllarni qayta yigʻadi.

## Soʻz yoki tarjimani tuzatish

1. `manba/sozlar-*.txt` yoki `manba/gaplar.txt` faylida kerakli qatorni oʻzgartiring. Oʻzbekcha harflarni oddiy apostrof bilan yozsa boʻladi (`o'`, `g'`), skript ularni `oʻ`, `gʻ` ga oʻzi aylantiradi.
2. `node manba/build.js` buyrugʻini ishga tushiring.
3. Yangilangan `words.json` va `sentences.json` fayllarini commit qiling.

Turkum belgilari: `n` ot, `v` feʼl, `a` sifat, `d` ravish, `p` olmosh, `r` predlog, `c` bogʻlovchi, `x` boshqa.
