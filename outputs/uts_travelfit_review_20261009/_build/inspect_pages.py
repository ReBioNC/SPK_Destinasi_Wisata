from pathlib import Path
import hashlib
import json
import sys

import pypdfium2 as pdfium
from pypdf import PdfReader

build = Path(__file__).resolve().parent
qa = build / 'qa'
source = pdfium.PdfDocument(str(qa/'source.pdf'))
revised_path = Path(sys.argv[1]) if len(sys.argv) > 1 else qa/'revised.pdf'
revised = pdfium.PdfDocument(str(revised_path))
reader = PdfReader(revised_path)
pages = []
changed = []
for index, page in enumerate(revised):
    img = page.render(scale=1.5).to_pil()
    img.save(qa/f'page-{index+1:02}.png')
    if index < len(source):
        original_page = source[index]
        original = original_page.render(scale=1.5).to_pil()
        if original.size != img.size or hashlib.sha256(original.tobytes()).digest() != hashlib.sha256(img.tobytes()).digest():
            changed.append(index+1)
        original_page.close()
    else:
        changed.append(index+1)
    txt = reader.pages[index].extract_text()
    pages.append({'page':index+1, 'chars':len(txt), 'first':txt[:110], 'last':txt[-130:]})
    page.close()
source.close()
revised.close()
proof = json.loads((build/'verification.json').read_text(encoding='utf-8'))
proof.update({'rendered_pages':len(pages), 'changed_visual_pages':changed})
(build/'verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':pages,'changed_visual_pages':changed},ensure_ascii=False))
