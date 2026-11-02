"""Read-only native-object, evidence, arithmetic and final-artifact checks."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
from datetime import datetime, timezone
import json, hashlib, math, re
from PIL import Image
from pypdf import PdfReader
from openpyxl import load_workbook
root=Path(__file__).resolve().parents[1];repo=root.parent
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
C='http://schemas.openxmlformats.org/drawingml/2006/chart'
ns={'p':P,'a':A,'c':C}
presentation=root/'STEPLOCK_Speedrun_SR008.pptx'
with ZipFile(presentation) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith(('.xml','.rels')):E.fromstring(z.read(name))
    slides=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n).group(1)))
    assert len(slides)==19
    size=E.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz',ns)
    assert (size.get('cx'),size.get('cy'))==('12192000','6858000')
    stats=[]
    for number,name in enumerate(slides,1):
        tree=E.fromstring(z.read(name))
        for ext in tree.findall('.//a:ext',ns):
            assert int(ext.get('cx','0'))>=0 and int(ext.get('cy','0'))>=0,(number,ext.attrib)
        texts=[e.text or '' for e in tree.findall('.//a:t',ns)]
        stats.append({'slide':number,'text_runs':len(texts),'editable_shapes':len(tree.findall('.//p:sp',ns)),'native_tables':len(tree.findall('.//a:tbl',ns)),'native_charts':len(tree.findall('.//c:chart',ns))})
        assert len(texts)>3,number
        assert f'ppt/notesSlides/notesSlide{number}.xml' in z.namelist()
    assert stats[7]['native_charts']==1
    assert all(stats[i-1]['native_tables']==1 for i in [13,15,17])
    charts=[n for n in z.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml',n)]
    cache=E.fromstring(z.read(charts[0]))
    numbers=[float(e.text) for e in cache.findall('.//c:val/c:numRef/c:numCache/c:pt/c:v',ns)]
    assert numbers==[24,28,32],numbers
    assert any(n.startswith('ppt/embeddings/') and n.endswith('.xlsx') for n in z.namelist())
    assert not any(n.startswith('ppt/fonts/') for n in z.namelist())
    binary_hashes={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
    actual=hashlib.sha256((repo/'screenshots/readme/inspection-native.png').read_bytes()).hexdigest()
    assert actual in binary_hashes,'Source PNG must remain byte-identical in the PPTX'
reader=PdfReader(root/'STEPLOCK_Speedrun_SR008.pdf');assert len(reader.pages)==19
for page in reader.pages:
    assert abs(float(page.mediabox.width)-960)<1 and abs(float(page.mediabox.height)-540)<1
assert '32/32' in ''.join(p.extract_text() or '' for p in reader.pages)
for i in range(1,20):
    with Image.open(root/f'previews/slide-{i:02}.png') as image:assert image.size==(1920,1080)
scenarios=json.loads((root/'charts/scenarios.json').read_text())['scenarios']
wb=load_workbook(root/'STEPLOCK_Illustrative_Economics.xlsx',data_only=False)
cached=load_workbook(root/'STEPLOCK_Illustrative_Economics.xlsx',data_only=True)
for col,s in zip('BCD',scenarios):
    assert wb['Station economics'][f'{col}15'].data_type=='f'
    assert math.isclose(cached['Station economics'][f'{col}15'].value,s['hours'],abs_tol=1e-6)
    assert math.isclose(cached['Station economics'][f'{col}21'].value,s['net_first_year'],abs_tol=1e-6)
assert cached['Scale sensitivity']['B7'].value==72000000
assert not list(root.rglob('*.ttf')) and not list(root.rglob('*.woff*'))
render=json.loads((repo/'runtime/pitch-build/powerpoint-render.json').read_text(encoding='utf-8-sig'))
assert render['text_height_warnings']==[]
files=[]
for file in sorted(root.rglob('*')):
    if file.is_file() and file.name!='DELIVERY_MANIFEST.json' and 'node_modules' not in file.parts:
        files.append({'path':file.relative_to(root).as_posix(),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
report={'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','slides':19,'primary_slides':14,'appendix_slides':5,'native_editability':stats,'chart_values_verified':numbers,'actual_screenshot_byte_identical':True,'text_height_warnings':0,'pdf_pages':19,'all_previews_px':[1920,1080],'standalone_fonts_distributed':False,'financial_scenarios':'HYPOTHETICAL_NOT_MEASURED','limitations':'Founder credentials are founder-reported; real factory accuracy and customer ROI unvalidated. Physical PowerPoint rendering was performed; other viewers can substitute fonts.','files':files}
(root/'DELIVERY_MANIFEST.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in report.items() if k not in ['files','native_editability']}))
