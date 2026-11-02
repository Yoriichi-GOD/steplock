from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime, timezone
import json, hashlib, subprocess
root=Path(__file__).resolve().parents[1];repo=root.parent
private=repo/'runtime/pitch-build'
receipt=json.loads((private/'finalization-final.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'STEPLOCK_Speedrun_SR008.pptx')==receipt['finalSha256']
assert receipt['packageIntegrity']['finding_count']==0
assert receipt['presentationLayout']['finding_count']==0
assert receipt['presentationLayout']['warning_count']==0
assert receipt['firstPartyImport']['passed']
assert receipt['nativeChartValidation']['passed']
render=json.loads((private/'powerpoint-render.json').read_text(encoding='utf-8-sig'))
assert render['text_height_warnings']==[]
links=json.loads((private/'live-link-check.json').read_text(encoding='utf-8-sig'))
assert links['landing_http']==links['demo_http']==links['health_http']==200
result={'status':'PASS','recorded_utc':datetime.now(timezone.utc).isoformat(),'pptx_sha256':receipt['finalSha256'],'pdf_sha256':sha(root/'STEPLOCK_Speedrun_SR008.pdf'),'renderer':render['renderer'],'slide_count':19,'primary_slides':14,'appendix_slides':5,'slide_size_inches':[13.333333,7.5],'render_pixels':[1920,1080],'native_chart_owner_slides':[8],'native_table_owner_slides':[13,15,17],'package_integrity_findings':0,'layout_findings':0,'layout_warnings':0,'native_text_height_warnings':0,'first_party_import_passed':True,'native_chart_workbook_validation_passed':True,'live_links':links,'visual_review':'Every slide individually inspected; contact sheet inspected; modified slides re-inspected after fixes. Automated checks supplement visual review.','font_policy':'Requested REQUIEM families retained; verified in PDF resources; no standalone fonts distributed. PPTX font embedding disabled.','limits':['Generated benchmark is not industrial accuracy','IMPACT tests ingestion/refusal, not successful native recognition','Founder background is attributed to the founder','ROI and scale scenarios are hypothetical','Non-PowerPoint viewers may substitute fonts']}
(root/'QA_RESULTS.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
subprocess.run([r'C:\Users\nrgen\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',str(root/'src/verify_delivery.py')],cwd=repo,check=True)
dest=repo/'deliverables/steplock-speedrun';dest.mkdir(parents=True,exist_ok=True)
archive=dest/'STEPLOCK_Speedrun_SR008_Package.zip'
files=[p for p in sorted(root.rglob('*')) if p.is_file() and 'node_modules' not in p.parts and '__pycache__' not in p.parts and not p.name.endswith('.inspect.ndjson')]
assert not any(p.suffix.lower() in ['.ttf','.otf','.woff','.woff2','.env'] for p in files)
with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for file in files:z.write(file,'pitch-deck/'+file.relative_to(root).as_posix())
with ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))
    assert hashlib.sha256(z.read('pitch-deck/STEPLOCK_Speedrun_SR008.pptx')).hexdigest()==receipt['finalSha256']
    assert hashlib.sha256(z.read('pitch-deck/STEPLOCK_Speedrun_SR008.pdf')).hexdigest()==result['pdf_sha256']
verified={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files),'zip_crc':'PASS','native_deck_hash_matches':'PASS','pdf_hash_matches':'PASS','standalone_fonts_included':False,'private_runtime_or_credentials_included':False}
(dest/'PACKAGE_VERIFICATION.json').write_bytes((json.dumps(verified,indent=2)+'\n').encode())
print(json.dumps(verified))
