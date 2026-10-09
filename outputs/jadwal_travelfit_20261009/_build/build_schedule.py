"""Create a report-ready schedule from verified commits, excluding website work."""
from datetime import date, timedelta
from pathlib import Path
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent
ROOT = Path(__file__).resolve().parents[3]
ROWS = [
    ('Perencanaan awal', ['cf5eee2', '579956e']),
    ('Kerangka CRISP-DM', ['9b07e6c']),
    ('Metode dan rumus', ['d34b8d1', '10d995a']),
    ('Preprocessing awal', ['49ad222', 'c8870e4']),
    ('Perhitungan AHP dan TOPSIS', ['e8850eb', '44f2824']),
    ('Kurasi dan preprocessing 443 data', ['75d040a', '7a26cd2', '6be2aaf', '437a5df']),
    ('Pelatihan dan evaluasi K-Means', ['7da9c1f']),
    ('Pembaruan notebook', ['d5fce97', '9565e0a']),
    ('Penyesuaian konsep budget tiket', ['59e1a5d', '9565e0a']),
    ('Spreadsheet dan revisi laporan', ['f811dbe', '93a6a0f', 'aae3166']),
    ('README dan daftar pustaka', ['d613750', '94f5281']),
]

records = []
for label, refs in ROWS:
    commits = []
    for ref in refs:
        raw = subprocess.check_output(
            ['git', 'show', '-s', '--format=%H|%ad|%s', '--date=short', ref],
            cwd=ROOT, text=True, encoding='utf-8',
        ).strip()
        sha, when, subject = raw.split('|', 2)
        commits.append({'sha': sha, 'date': when, 'subject': subject})
    dates = [date.fromisoformat(c['date']) for c in commits]
    records.append({'activity': label, 'start': min(dates).isoformat(),
                    'end': max(dates).isoformat(), 'commits': commits})

start, finish = date(2026, 9, 1), date(2026, 10, 9)
assert min(r['start'] for r in records) == start.isoformat()
assert max(r['end'] for r in records) == finish.isoformat()
assert all('website' not in r['activity'].lower() for r in records)

width, height = 2700, 1750
image = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(image)
regular = 'C:/Windows/Fonts/times.ttf'
bold = 'C:/Windows/Fonts/timesbd.ttf'
fonts = {'title': ImageFont.truetype(bold, 66),
         'subtitle': ImageFont.truetype(regular, 43),
         'label': ImageFont.truetype(regular, 48),
         'tick': ImageFont.truetype(regular, 39),
         'note': ImageFont.truetype(regular, 40)}

draw.text((65, 45), 'Jadwal Kegiatan TravelFit', font=fonts['title'], fill='#222222')
draw.text((65, 140), 'Perencanaan, data, metode, dan dokumentasi | 1 September–9 Oktober 2026',
          font=fonts['subtitle'], fill='#444444')
left, right, top, pitch = 915, 2600, 330, 112
axis_end = finish + timedelta(days=1)
def xpos(d):
    return left + (d-start).days / (axis_end-start).days * (right-left)

ticks = [date(2026, 9, d) for d in (1, 9, 16, 23, 30)] + [date(2026, 10, d) for d in (5, 9)]
for tick in ticks:
    x = xpos(tick)
    draw.line((x, top-25, x, top+pitch*(len(records)-1)+75), fill='#DADADA', width=3)
    draw.text((x, top-92), tick.strftime('%d/%m'), anchor='mm',
              font=fonts['tick'], fill='#333333')

label_boxes = []
for i, record in enumerate(records):
    y = top+i*pitch
    label = record['activity']
    box = draw.textbbox((65, y), label, font=fonts['label'])
    assert box[2] < left-35, f'Label exceeds reserved area: {label}'
    label_boxes.append(box)
    draw.text((65, y), label, font=fonts['label'], fill='#222222')
    a, b = date.fromisoformat(record['start']), date.fromisoformat(record['end'])
    xa, xb = xpos(a), xpos(b+timedelta(days=1))
    assert left <= xa < xb <= right
    draw.rectangle((round(xa), y+9, round(xb), y+57), fill='#5E6570')

draw.text((65, 1610), 'Tanggal commit tahun 2026. Rentang bar menunjukkan tanggal bukti awal dan akhir,',
          font=fonts['note'], fill='#444444')
draw.text((65, 1665), 'bukan durasi kerja harian. Aktivitas pengembangan website tidak ditampilkan.',
          font=fonts['note'], fill='#444444')

dest = OUT/'Jadwal_Kegiatan_TravelFit_Tanpa_Website.png'
image.save(dest, dpi=(300, 300))
with Image.open(dest) as check:
    check.verify()
proof = {'period': [start.isoformat(), finish.isoformat()], 'activities': records,
         'excluded': ['prototipe peta', 'pengembangan website', 'integrasi UI dan peta'],
         'meaning': 'Rentang tanggal commit yang terkait, bukan jam atau durasi kerja harian.',
         'image_size': [width, height], 'dpi': 300}
(OUT/'_build'/'evidence.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(dest), 'activities': len(records), 'size': [width, height]}, ensure_ascii=False))
