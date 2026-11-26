# 3000 Soʻz — ingliz tilini oʻrganish uchun

Oʻzbek tilida soʻzlashuvchilar uchun ingliz tili dasturi. Unda 3000 ta eng kerakli inglizcha soʻz 150 ta darsga boʻlingan, har darsda 20 tadan soʻz bor. Darajalar: A1, A2 va B1.

**Dasturni ochish:** https://claude.ai/artifact/W8NYMAPiM7G5fAvxxMTJ34

## Toʻrt bosqich

1. **Soʻzlar.** Soʻz chiqadi va pastda 4 ta variant boʻladi. Masalan, «tezlik» chiqadi, siz **speed** ni tanlaysiz. Xato qilingan soʻz test oxirida yana soʻraladi. Eski soʻzlar maʼlum kunlardan keyin takrorlashga qaytadi.
2. **Gaplar.** Har bir darsning oʻz gaplari bor (11–20 tadan). Oʻzbekcha gap beriladi, siz inglizcha soʻzlarni toʻgʻri tartibda bosib gap tuzasiz. Shu boʻlimda 10 ta asosiy grammatika qoidasi ham bor.
3. **Tarjima.** Ikki yoʻnalishda: oʻzbekcha gapni inglizchaga yoki inglizcha gapni oʻzbekchaga tarjima qilasiz. Xatolar rangda koʻrsatiladi, Claude ularni oʻzbekcha tushuntiradi.
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
- `words.json` — 3000 ta soʻz: `["inglizcha", "oʻzbekcha", "turkum", "/talaffuz/"]`.
- `sentences.json` — 2616 ta gap: `["inglizcha", "oʻzbekcha", dars]`. 241 tasi umumiy (`dars` = 0, osondan qiyinga qarab), 2375 tasi 150 ta darsga biriktirilgan (har darsda 11–20 ta).
- `audio/` — barcha soʻzlar va tayyor gaplarning oldindan yozib olingan ovozi (oddiy va sekin). Ular telefondagi Claude ilovasida ham ishlaydi. `index.json` har bir soʻzning qaysi faylda va qaysi soniyada turganini koʻrsatadi.
- `manba/` — yuqoridagi fayllarning manbasi:
  - `sozlar-1.txt` … `sozlar-6.txt` — har qatorda `inglizcha|oʻzbekcha|turkum`;
  - `gaplar.txt` — umumiy gaplar, har qatorda `inglizcha|oʻzbekcha`;
  - `dars-gaplari-01.txt` … `dars-gaplari-15.txt` — darslar gaplari, har qatorda `dars|inglizcha|oʻzbekcha`;
  - `tekshir.js` — dars gaplarini tekshiradi: takrorlanmasligi va har gapda oʻsha dars soʻzi borligi;
  - `talaffuz.txt` — har soʻzning talaffuz yozuvi (IPA, AQSh talaffuzi);
  - `build.js` — JSON fayllarni qayta yigʻadi;
  - `ovoz.py` — ovoz fayllarini va talaffuz yozuvini yaratadi (Piper TTS, `en_US-lessac-medium` ochiq ovoz modeli; talaffuz CMU Pronouncing Dictionary asosida).

## Soʻz yoki tarjimani tuzatish

1. `manba/sozlar-*.txt`, `manba/gaplar.txt` yoki `manba/dars-gaplari-*.txt` faylida kerakli qatorni oʻzgartiring, keyin `node manba/tekshir.js` bilan tekshiring. Oʻzbekcha harflarni oddiy apostrof bilan yozsa boʻladi (`o'`, `g'`), skript ularni `oʻ`, `gʻ` ga oʻzi aylantiradi.
2. `node manba/build.js` buyrugʻini ishga tushiring.
3. Inglizcha soʻz yoki gap oʻzgargan boʻlsa, ovozni ham qayta yarating:
   ```
   python3 -m venv .venv && .venv/bin/pip install piper-tts cmudict
   .venv/bin/python manba/ovoz.py                    # hammasi
   .venv/bin/python manba/ovoz.py --sozlarni-qoldir  # faqat gaplar (soʻzlar oʻzgarmagan boʻlsa)
   node manba/build.js
   ```
   (`ffmpeg` oʻrnatilgan boʻlishi kerak; ovoz modeli birinchi marta oʻzi yuklab olinadi.)
4. Yangilangan `words.json`, `sentences.json` va `audio/` fayllarini commit qiling.

Turkum belgilari: `n` ot, `v` feʼl, `a` sifat, `d` ravish, `p` olmosh, `r` predlog, `c` bogʻlovchi, `x` boshqa.
