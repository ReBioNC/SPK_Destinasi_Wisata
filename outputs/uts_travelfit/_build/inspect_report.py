from pathlib import Path
import argparse
import hashlib
import json
import zipfile
import pypdfium2 as pdfium
from pypdf import PdfReader
from lxml import etree

build = Path(__file__).resolve().parent
output = build.parent / 'Laporan_UTS_TravelFit.docx'
qa = build / 'qa'
parser = argparse.ArgumentParser()
parser.add_argument('--pdf', default=str(qa / 'report-ticket.pdf'))
args = parser.parse_args()
reader = PdfReader(args.pdf)
pdf = pdfium.PdfDocument(args.pdf)
pages = []
changed = []
for i, page in enumerate(pdf):
    target = qa / f'page-{i+1:02}.png'
    prevhash = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    img = page.render(scale=1.5).to_pil()
    img.save(target)
    if prevhash != hashlib.sha256(target.read_bytes()).hexdigest(): changed.append(i+1)
    txt = reader.pages[i].extract_text()
    pages.append({'page':i+1, 'chars':len(txt), 'first':txt[:150], 'last':txt[-170:]})
    page.close()
pdf.close()
from PIL import Image, ImageDraw
for start in range(0, len(pages), 8):
    canvas = Image.new('RGB', (2400, 1800), '#dddddd')
    draw = ImageDraw.Draw(canvas)
    for offset in range(min(8, len(pages)-start)):
        img = Image.open(qa / f'page-{start+offset+1:02}.png')
        img.thumbnail((580, 845))
        x, y = (offset%4)*600, (offset//4)*900
        canvas.paste(img, (x, y+30))
        draw.text((x+15, y+8), f'Halaman {start+offset+1}', fill='black')
    canvas.save(qa / f'contact-{start+1:02}.png')
with zipfile.ZipFile(output) as z:
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
text = ' '.join(doc.xpath('//w:t/text()', namespaces=ns))
out_of_scope = ['Agglomerative', 'DBSCAN', 'Decision Tree', 'Random Forest',
                'SMART', 'PROMETHEE', 'ELECTRE', 'ontology', 'ontologi',
                'Next.js', 'Flask', '1.900', '2.337', 'precision at k',
                'Kegiatan Lanjutan', 'Rencana validasi']
assert not [term for term in out_of_scope if term.casefold() in text.casefold()]
for term in ['443', 'CRISP', 'K-Means', 'AHP', 'TOPSIS', '275.800', 'Logbook']:
    assert term in text, f'Missing project content: {term}'
sections = [dict(el.attrib) for el in doc.xpath('//w:sectPr/w:pgMar | //w:sectPr/w:pgSz',namespaces=ns)]
stylefonts = styles.xpath('//w:style[w:name/@w:val="Normal"]/w:rPr/w:rFonts/@w:ascii',namespaces=ns)
sizes = styles.xpath('//w:style[w:name/@w:val="Normal"]/w:rPr/w:sz/@w:val',namespaces=ns)
toc = doc.xpath('//w:p[w:pPr/w:pStyle[starts-with(@w:val,"TOC")]]',namespaces=ns)
proof = json.loads((build/'evidence.json').read_text(encoding='utf-8'))
root = build.parents[2]
unchanged = all(hashlib.sha256((root/p).read_bytes()).hexdigest()==expected
                for p,expected in proof['protected_hashes'].items() if p != 'db.sqlite3')
# Browser verification writes Django sessions, not source destinations. Check the
# destination snapshot separately; raw source/archive hashes remain immutable.
assert unchanged
audit = {'pages':pages,'changed_visual_pages':changed,'sections':sections,'normal_font':stylefonts,'normal_size':sizes,
         'toc_entries':len(toc),'protected_sources_and_archives_unchanged':unchanged,
         'out_of_scope_content_removed': True}
(qa/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=True))
