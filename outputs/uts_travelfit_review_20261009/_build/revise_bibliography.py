"""Replace only bibliography paragraphs in the user's revised report."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re
import zipfile

from lxml import etree

SOURCE = Path('C:/Users/ASUS/Downloads/Laporan_UTS_TravelFit.docx')
OUT = Path(__file__).resolve().parent.parent
DEST = OUT / 'Laporan_UTS_TravelFit_Revisi_Daftar_Pustaka.docx'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'
REPO = 'https://github.com/ReBioNC/SPK_Destinasi_Wisata'

# Retain original access dates for retained sources. Project references reviewed
# locally today are explicitly labeled as local access, not verified public URLs.
REFS = [
    ('aprabowo (n.d.) ', 'Indonesia Tourism Destination',
     '. Kaggle. Tersedia pada: https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination (Diakses: 1 Oktober 2026).'),
    ('Hwang, C.L. dan Yoon, K. (1981) ', 'Multiple Attribute Decision Making: Methods and Applications A State-of-the-Art Survey',
     '. Berlin dan Heidelberg: Springer-Verlag. doi: https://doi.org/10.1007/978-3-642-48318-9.'),
    ('IBM (n.d.) ', 'CRISP-DM Help Overview',
     '. IBM SPSS Modeler. Tersedia pada: https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview (Diakses: 1 Oktober 2026).'),
    ('Kelompok TravelFit (2026a) ', 'TravelFit Rekomendasi Destinasi Wisata Jawa dan evaluasi K-Means Java443',
     '. Repository proyek, branch new. Tersedia pada: '+REPO+' (Diakses secara lokal: 9 Oktober 2026).'),
    ('Kelompok TravelFit (2026b) ', 'Dokumentasi data aktif TravelFit Java443',
     '. Dokumentasi.md dan dokumentasi kurasi gabungan Jawa. Tersedia pada: '+REPO+'/blob/new/Dokumentasi.md (Diakses secara lokal: 9 Oktober 2026).'),
    ('Kelompok TravelFit (2026c) ', 'Keputusan budget tiket dan implementasi rekomendasi',
     '. Dokumen proyek tanggal 5 Oktober 2026, docs/decisions/2026-10-05-ticket-budget.md dan recommender/views.py. Tersedia pada: '+REPO+'/blob/new/docs/decisions/2026-10-05-ticket-budget.md (Diakses secara lokal: 9 Oktober 2026).'),
    ('Kelompok TravelFit (2026d) ', 'Verifikasi integrasi Java443 30 September 2026',
     '. reports/java443_final_verification.md. Tersedia pada: '+REPO+'/blob/new/reports/java443_final_verification.md (Diakses secara lokal: 9 Oktober 2026).'),
    ('OpenStreetMap Foundation (n.d.) ', 'Copyright and License',
     '. Tersedia pada: https://www.openstreetmap.org/copyright (Diakses: 1 Oktober 2026).'),
    ('Pemerintah Kabupaten Lebak (2025) ', 'Peraturan Daerah Kabupaten Lebak Nomor 1 Tahun 2025',
     '. Lampiran tarif Museum Multatuli, hlm. 232 PDF. Tersedia pada: https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Kabupaten Ngawi (2023) ', 'Peraturan Daerah Kabupaten Ngawi Nomor 10 Tahun 2023 tentang Pajak Daerah dan Retribusi Daerah',
     '. Lampiran II tarif Museum Trinil, hlm. 122 PDF. Tersedia pada: https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Kabupaten Purworejo (2026) ', 'Peraturan Daerah Kabupaten Purworejo Nomor 1 Tahun 2026',
     '. Lampiran tarif destinasi wisata, hlm. 242 PDF. Tersedia pada: https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Provinsi Banten (2024) ', 'Peraturan Daerah Provinsi Banten Nomor 1 Tahun 2024',
     '. Lampiran tarif Taman Hutan Raya Banten, hlm. 261 PDF. Tersedia pada: https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Saaty, T.L. (2008) ', 'Decision making with the analytic hierarchy process',
     '. International Journal of Services Sciences, 1(1), hlm. 83–98. doi: https://doi.org/10.1504/IJSSCI.2008.017590.'),
    ('scikit-learn developers (n.d.) ', 'Clustering',
     '. scikit-learn documentation. Tersedia pada: https://scikit-learn.org/stable/modules/clustering.html (Diakses: 1 Oktober 2026).'),
]

source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
with zipfile.ZipFile(SOURCE) as package:
    members = {i.filename: package.read(i.filename) for i in package.infolist()}
    infos = package.infolist()

doc = etree.fromstring(members['word/document.xml'])
rels = etree.fromstring(members['word/_rels/document.xml.rels'])
body = doc.find(W + 'body')
index = next(i for i, element in enumerate(body)
             if element.tag == W+'p' and ''.join(element.xpath('.//w:t/text()', namespaces=NS)).strip().upper() == 'DAFTAR PUSTAKA')
protected = [etree.tostring(el, method='c14n') for el in list(body)[:index+1]]
bib = [el for el in list(body)[index+1:] if el.tag == W+'p']
assert len(bib) == 15, 'Unexpected source bibliography; inspect before editing.'
template = deepcopy(bib[0].find(W+'pPr'))
for el in bib:
    body.remove(el)

counter = max([int(el.get('Id')[3:]) for el in rels if re.fullmatch(r'rId\d+', el.get('Id', ''))] or [0])

def run(text, italic=False):
    element = etree.Element(W+'r')
    props = etree.SubElement(element, W+'rPr')
    fonts = etree.SubElement(props, W+'rFonts')
    for name in ['ascii', 'hAnsi', 'cs']:
        fonts.set(W+name, 'Times New Roman')
    etree.SubElement(props, W+'sz').set(W+'val', '24')
    etree.SubElement(props, W+'color').set(W+'val', '000000')
    if italic:
        etree.SubElement(props, W+'i')
    t = etree.SubElement(element, W+'t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return element

def linked_text(p, text):
    global counter
    last = 0
    for match in re.finditer(r'https?://[^\s]+', text):
        # Sentence-ending periods are not part of a DOI's URL.
        url = match.group().rstrip('.')
        start, end = match.start(), match.start()+len(url)
        if start > last:
            p.append(run(text[last:start]))
        counter += 1
        rid = 'rId'+str(counter)
        rel = etree.SubElement(rels, REL+'Relationship')
        rel.set('Id', rid)
        rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink')
        rel.set('Target', url)
        rel.set('TargetMode', 'External')
        h = etree.SubElement(p, W+'hyperlink')
        h.set(R+'id', rid)
        h.append(run(url))
        last = end
    if last < len(text):
        p.append(run(text[last:]))

for offset, (author, title, rest) in enumerate(REFS):
    p = etree.Element(W+'p')
    props = deepcopy(template) if template is not None else etree.Element(W+'pPr')
    for tag in ['spacing', 'jc', 'keepNext', 'keepLines', 'widowControl']:
        for el in props.findall(W+tag):
            props.remove(el)
    spacing = etree.SubElement(props, W+'spacing')
    spacing.set(W+'line', '276'); spacing.set(W+'lineRule', 'auto')
    spacing.set(W+'after', '160')
    etree.SubElement(props, W+'jc').set(W+'val', 'both')
    etree.SubElement(props, W+'keepLines')
    etree.SubElement(props, W+'widowControl')
    p.append(props)
    p.append(run(author))
    if author.startswith('Saaty,'):
        p.append(run("'"+title+"'"))
        p.append(run('. '))
        p.append(run('International Journal of Services Sciences', italic=True))
        linked_text(p, rest.removeprefix('. International Journal of Services Sciences'))
    else:
        p.append(run(title, italic=True))
        linked_text(p, rest)
    body.insert(index+1+offset, p)

assert protected == [etree.tostring(el, method='c14n') for el in list(body)[:index+1]], 'Body content changed.'
bib_text = ' '.join(''.join(p.xpath('.//w:t/text()', namespaces=NS)) for p in list(body)[index+1:] if p.tag == W+'p')
assert all(word not in bib_text for word in ['OSRM', 'audit_biaya', 'estimasi biaya perjalanan', 'd5fce97'])
changed = {'word/document.xml': etree.tostring(doc, encoding='UTF-8', xml_declaration=True, standalone=True),
           'word/_rels/document.xml.rels': etree.tostring(rels, encoding='UTF-8', xml_declaration=True, standalone=True)}
with zipfile.ZipFile(DEST, 'w', compression=zipfile.ZIP_DEFLATED) as result:
    for info in infos:
        result.writestr(info, changed.get(info.filename, members[info.filename]))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
with zipfile.ZipFile(DEST) as result:
    assert all(result.read(name) == value for name, value in members.items() if name not in changed)

proof = {'source_sha256': source_hash, 'source_unchanged': True,
         'body_children_unchanged': len(protected), 'tables_unchanged': len(doc.xpath('//w:tbl', namespaces=NS)),
         'old_references': 15, 'new_references': len(REFS),
         'only_changed_package_parts': list(changed),
         'removed_reference': 'Project OSRM', 'replaced_reference': 'Kelompok TravelFit (2026c): budget tiket',
         'github_links_reviewed_locally_not_publicly_verified': True}
(Path(__file__).parent/'verification.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(DEST), **proof}, ensure_ascii=False))
