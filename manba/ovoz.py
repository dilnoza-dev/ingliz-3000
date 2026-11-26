"""Soʻz va gaplar uchun ovoz fayllari hamda talaffuz yozuvini (IPA) yaratadi.

Ishlatish (repozitoriy ildizidan):
    python3 -m venv .venv && .venv/bin/pip install piper-tts cmudict
    .venv/bin/python manba/ovoz.py
    node manba/build.js

Natija:
    audio/*.mp3, audio/index.json  — dastur ishlatadigan ovozlar
    manba/talaffuz.txt             — har soʻzning IPA yozuvi (build.js uni words.json ga qoʻshadi)

Ovoz: Piper TTS, en_US-lessac-medium (ochiq model, birinchi ishga tushganda yuklab olinadi).
Talaffuz yozuvi: CMU Pronouncing Dictionary (AQSh talaffuzi).
"""
import json
import os
import subprocess
import sys
import urllib.request
import wave

import cmudict
from piper import PiperVoice, SynthesisConfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.environ.get('PIPER_MODEL_DIR', os.path.join(ROOT, '.venv', 'voices'))
MODEL = 'en_US-lessac-medium'
MODEL_URL = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/'
RATE = 22050
WORDS_PER_FILE = 100
SENTENCES_PER_FILE = 50
LESSONS_PER_FILE = 5     # dars gaplari: har faylda 5 ta darsning gaplari
SENTENCE_BITRATE = '24k'
GAP = 0.25          # clips orasidagi jimlik, soniya
PAD = 0.06          # clip boshidan/oxiridan qoldiriladigan zaxira

# Bir xil yoziladigan, lekin bizning tarjimamizdagi maʼnoda boshqacha oʻqiladigan soʻzlar.
# Ovoz uchun espeak IPA (Piper [[ ]] sintaksisi).
VOICE_OVERRIDE = {
    'live': 'lˈɪv', 'tear': 'tˈɛɹ', 'bow': 'bˈaʊ', 'close': 'klˈoʊz', 'use': 'jˈuːz',
    'separate': 'sˈɛpɚɹˌeɪt', 'estimate': 'ˈɛstɪmˌeɪt', 'increase': 'ɪŋkɹˈiːs', 'decrease': 'dɪkɹˈiːs',
    'import': 'ˈɪmpɔːɹt', 'insult': 'ɪnsˈʌlt', 'suspect': 'səspˈɛkt', 'transfer': 'tɹænsfˈɜː',
    'perfect': 'pˈɜːfɪkt', 'graduate': 'ɡɹˈædʒuːˌeɪt',
}
# Talaffuz yozuvi uchun CMU (ARPAbet) tanlovi.
CMU_OVERRIDE = {
    'live': 'L IH1 V', 'read': 'R IY1 D', 'lead': 'L IY1 D', 'tear': 'T EH1 R', 'bow': 'B AW1',
    'wound': 'W UW1 N D', 'close': 'K L OW1 Z', 'use': 'Y UW1 Z', 'minute': 'M IH1 N AH0 T',
    'present': 'P R EH1 Z AH0 N T', 'record': 'R EH1 K ER0 D', 'object': 'AA1 B JH EH0 K T',
    'desert': 'D EH1 Z ER0 T', 'content': 'K AA1 N T EH0 N T', 'perfect': 'P ER1 F IH0 K T',
    'separate': 'S EH1 P ER0 EY2 T', 'estimate': 'EH1 S T AH0 M EY2 T', 'produce': 'P R AH0 D UW1 S',
    'increase': 'IH0 N K R IY1 S', 'decrease': 'D IH0 K R IY1 S', 'export': 'EH1 K S P AO0 R T',
    'import': 'IH1 M P AO0 R T', 'protest': 'P R OW1 T EH0 S T', 'conflict': 'K AA1 N F L IH0 K T',
    'contest': 'K AA1 N T EH0 S T', 'progress': 'P R AA1 G R EH0 S', 'insult': 'IH0 N S AH1 L T',
    'suspect': 'S AH0 S P EH1 K T', 'transfer': 'T R AE0 N S F ER1', 'transport': 'T R AE1 N S P AO0 R T',
    'contract': 'K AA1 N T R AE0 K T', 'refuse': 'R IH0 F Y UW1 Z', 'excuse': 'IH0 K S K Y UW1 S',
    'wind': 'W IH1 N D', 'a': 'AH0', 'the': 'DH AH0', 'address': 'AE1 D R EH0 S',
    'research': 'R IY1 S ER0 CH', 'graduate': 'G R AE1 JH UW0 EY2 T',
    'analyse': 'AE1 N AH0 L AY2 Z', 'criticise': 'K R IH1 T IH0 S AY2 Z', 'flavour': 'F L EY1 V ER0',
    'pyjamas': 'P AH0 JH AA1 M AH0 Z', 'toothache': 'T UW1 TH EY2 K',
}
# Grammatika qoidalari, «Tovushlar» boʻlimi va sozlamalardagi misollar (index.html bilan bir xil boʻlishi kerak).
EXTRA = [
    'Hello! Let us learn English.', 'I eat apples.', 'She reads books.',
    'think', 'three', 'thank', 'this', 'they', 'mother', 'we', 'water', 'window', 'very', 'have', 'voice',
    'cat', 'apple', 'bag', 'cup', 'but', 'sun', 'about', 'the', 'banana', 'ship', 'sheep', 'sit', 'seat',
    'sing', 'morning', 'long', 'red', 'car', 'girl', 'sink', 'wine', 'west', 'vest',
]

IPA_V = {'AA': 'ɑː', 'AE': 'æ', 'AO': 'ɔː', 'AW': 'aʊ', 'AY': 'aɪ', 'EH': 'e', 'EY': 'eɪ', 'IH': 'ɪ',
         'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ'}
IPA_C = {'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'JH': 'dʒ', 'K': 'k',
         'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ', 'T': 't',
         'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
_ON = ('P L,B L,K L,G L,F L,S L,P R,B R,T R,D R,K R,G R,F R,TH R,SH R,S P,S T,S K,S M,S N,S W,'
       'T W,K W,D W,G W,TH W,P Y,B Y,K Y,G Y,M Y,F Y,V Y,HH Y,S P L,S P R,S T R,S K R,S K W,S K Y,S P Y')
ONSETS = {(c,) for c in IPA_C if c != 'NG'} | {tuple(x.split()) for x in _ON.split(',')}


def vowel_ipa(p):
    base, st = p[:-1], p[-1]
    if base == 'AH':
        return 'ʌ' if st in '12' else 'ə'
    if base == 'ER':
        return 'ɝː' if st in '12' else 'ɚ'
    if base == 'IY':
        return 'iː' if st in '12' else 'i'
    if base == 'UW':
        return 'uː' if st in '12' else 'u'
    return IPA_V[base]


def arpa_to_ipa(phones):
    phones = list(phones)
    prim = [i for i, p in enumerate(phones) if p.endswith('1')]
    for i in prim[:-1]:  # nineteen: N AY1 N T IY1 N -> /ˌnaɪnˈtiːn/
        phones[i] = phones[i][:-1] + '2'
    vowels = [i for i, p in enumerate(phones) if p[-1].isdigit()]
    primary = next((i for i in vowels if phones[i][-1] == '1'), len(phones))
    marks = {}
    if len(vowels) > 1:
        for vi in vowels:
            st = phones[vi][-1]
            # lugʻatlardagidek: ikkilamchi urgʻu faqat asosiy urgʻudan oldin koʻrsatiladi
            if st not in '12' or (st == '2' and vi > primary):
                continue
            j = vi
            while j > 0 and not phones[j - 1][-1].isdigit():
                j -= 1
            cluster = phones[j:vi]
            k = 0
            if j > 0:
                for s in range(len(cluster) + 1):
                    if s == len(cluster) or tuple(cluster[s:]) in ONSETS:
                        k = s
                        break
            marks[j + k] = 'ˈ' if st == '1' else 'ˌ'
    out = []
    for i, p in enumerate(phones):
        if i in marks:
            out.append(marks[i])
        out.append(vowel_ipa(p) if p[-1].isdigit() else IPA_C[p])
    return ''.join(out)


def word_ipa(cmu, voice, text):
    parts = []
    for raw in text.replace('-', ' ').split():
        key = raw.lower().strip("'")
        if key in CMU_OVERRIDE:
            phones = CMU_OVERRIDE[key].split()
        elif key in cmu:
            phones = cmu[key][0]
        else:
            print('  IPA topilmadi, espeak ishlatildi:', raw, file=sys.stderr)
            parts.append(''.join(''.join(s) for s in voice.phonemize(raw)).replace('ɹ', 'r'))
            continue
        parts.append(arpa_to_ipa(phones))
    return '/' + ' '.join(parts) + '/'


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    path = os.path.join(MODEL_DIR, MODEL + '.onnx')
    for name in (MODEL + '.onnx', MODEL + '.onnx.json'):
        dest = os.path.join(MODEL_DIR, name)
        if not os.path.exists(dest):
            print('Yuklanmoqda:', name)
            urllib.request.urlretrieve(MODEL_URL + name, dest)
    return path


def synth(voice, text, length_scale, override=None):
    import io
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        voice.synthesize_wav('[[ ' + override + ' ]]' if override else text, w,
                             syn_config=SynthesisConfig(length_scale=length_scale))
    buf.seek(0)
    with wave.open(buf, 'rb') as r:
        assert r.getframerate() == RATE and r.getnchannels() == 1 and r.getsampwidth() == 2
        data = r.readframes(r.getnframes())
    import array
    a = array.array('h')
    a.frombytes(data)
    # trim leading/trailing silence
    thr = 350
    first = next((i for i, x in enumerate(a) if abs(x) > thr), 0)
    last = next((i for i in range(len(a) - 1, -1, -1) if abs(a[i]) > thr), len(a) - 1)
    keep = int(0.02 * RATE)
    return a[max(0, first - keep):min(len(a), last + keep)]


def write_chunk(name, clips, bitrate='32k'):
    """clips: list of array('h'); returns [(start, dur), ...] and writes audio/<name>.mp3"""
    import array
    pcm = array.array('h', [0] * int(0.3 * RATE))
    gap = array.array('h', [0] * int(GAP * RATE))
    spans = []
    for c in clips:
        start = len(pcm) / RATE
        pcm.extend(c)
        spans.append((round(max(0, start - PAD), 3), round(len(c) / RATE + 2 * PAD, 3)))
        pcm.extend(gap)
    pcm.extend(array.array('h', [0] * int(0.3 * RATE)))
    out = os.path.join(ROOT, 'audio', name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 's16le', '-ar', str(RATE), '-ac', '1', '-i', '-',
                    '-codec:a', 'libmp3lame', '-b:a', bitrate, out], input=pcm.tobytes(), check=True)
    return spans


def main():
    words = json.load(open(os.path.join(ROOT, 'words.json'), encoding='utf8'))
    sentences = json.load(open(os.path.join(ROOT, 'sentences.json'), encoding='utf8'))
    voice = PiperVoice.load(ensure_model())
    cmu = cmudict.dict()
    os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)

    with open(os.path.join(ROOT, 'manba', 'talaffuz.txt'), 'w', encoding='utf8') as f:
        for w in words:
            f.write(w[0] + '|' + word_ipa(cmu, voice, w[0]) + '\n')
    print('talaffuz.txt tayyor')
    if '--faqat-ipa' in sys.argv:
        return

    files = []
    index = {'v': 2, 'files': files, 'w': [], 's': [None] * len(sentences), 'ss': [None] * len(sentences), 'x': {}}
    old = None
    if '--sozlarni-qoldir' in sys.argv:
        # soʻzlar oʻzgarmagan boʻlsa, ularning ovozini qayta yozmaymiz
        old = json.load(open(os.path.join(ROOT, 'audio', 'index.json'), encoding='utf8'))
        assert len(old['w']) == len(words)

    def add_chunk(name, texts, scale, overrides=None, bitrate='32k'):
        clips = [synth(voice, t, scale, (overrides or {}).get(t)) for t in texts]
        spans = write_chunk(name, clips, bitrate)
        fi = len(files)
        files.append(name)
        print(' ', name, len(texts), flush=True)
        return [[fi, st, du] for st, du in spans]

    # soʻzlar
    if old:
        remap = {}
        for e in old['w']:
            name = old['files'][e[0]]
            if name not in remap:
                remap[name] = len(files)
                files.append(name)
            index['w'].append([remap[name], e[1], e[2]])
    else:
        for n in range(0, len(words), WORDS_PER_FILE):
            index['w'].extend(add_chunk('w%02d.mp3' % (n // WORDS_PER_FILE),
                                        [w[0] for w in words[n:n + WORDS_PER_FILE]], 1.1, VOICE_OVERRIDE))
    # gaplar: umumiylari 50 tadan (s, ss), darslarniki 5 darsdan (d, ds)
    general = [i for i, r in enumerate(sentences) if len(r) < 3 or not r[2]]
    groups = [('s', 'ss', general[n:n + SENTENCES_PER_FILE], n // SENTENCES_PER_FILE)
              for n in range(0, len(general), SENTENCES_PER_FILE)]
    blocks = {}
    for i, r in enumerate(sentences):
        if len(r) > 2 and r[2]:
            blocks.setdefault((r[2] - 1) // LESSONS_PER_FILE, []).append(i)
    groups += [('d', 'ds', ids, b) for b, ids in sorted(blocks.items())]
    for normal, slow, ids, k in groups:
        texts = [sentences[i][0] for i in ids]
        for key, prefix, scale in (('s', normal, 1.1), ('ss', slow, 1.45)):
            for i, e in zip(ids, add_chunk('%s%02d.mp3' % (prefix, k), texts, scale, bitrate=SENTENCE_BITRATE)):
                index[key][i] = e
    for n in range(0, len(EXTRA), 100):
        for t, e in zip(EXTRA[n:n + 100], add_chunk('x%02d.mp3' % (n // 100), EXTRA[n:n + 100], 1.1)):
            index['x'][t] = e
    with open(os.path.join(ROOT, 'audio', 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))
    total = sum(os.path.getsize(os.path.join(ROOT, 'audio', n)) for n in files)
    print('audio: %d fayl, %.1f MB' % (len(files), total / 1e6))


if __name__ == '__main__':
    main()
