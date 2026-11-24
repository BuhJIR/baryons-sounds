#!/usr/bin/env python3
"""baryons-sounds: build index.json — every pack, every sound with sha256, duration and gain (to a −3 dBFS peak).
The app never ships sounds and never takes your own files: it only installs packs listed here."""
import hashlib, json, os, re, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__))
PACKS = {
    'eleven': {'name': 'Eleven · металл и затворы', 'about': 'сгенерировано в ElevenLabs Sound Effects'},
    'claude-synth': {'name': 'Claude · синтез', 'about': 'синтез в synth.py: механизм Glock, кольцо о титан'},
}
SLOTS = {'incoming': 'обращение к пульту', 'hold': 'удержание фона', 'rec_press': 'тест: внимание',
         'rec_release': 'тест: пошёл', 'rec_stop': 'тест: конец', 'loading': 'загрузка / смена сессии'}

def probe(p):
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout or 0)
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'max_volume: (-?[0-9.]+) dB', out)
    return d, float(m.group(1)) if m else 0.0

def title(f):
    t = re.sub(r'^\d+-', '', os.path.splitext(f)[0]).replace('-', ' ')
    return re.sub(r'\bn(\d)\b', r'#\1', t).strip().capitalize()

index = {'version': 1, 'slots': SLOTS, 'packs': []}
for pid, meta in PACKS.items():
    d = os.path.join(ROOT, 'packs', pid); sounds = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(('.mp3', '.ogg', '.wav')): continue
        p = os.path.join(d, f); dur, peak = probe(p)
        sounds.append({'id': os.path.splitext(f)[0], 'file': f, 'title': title(f), 'sha256': hashlib.sha256(open(p, 'rb').read()).hexdigest(),
                       'size': os.path.getsize(p), 'duration': round(dur, 2), 'gain_db': round(-3.0 - peak, 1)})
    index['packs'].append({'id': pid, **meta, 'sounds': sounds})
json.dump(index, open(os.path.join(ROOT, 'index.json'), 'w'), ensure_ascii=False, indent=1)
print({p['id']: len(p['sounds']) for p in index['packs']})
