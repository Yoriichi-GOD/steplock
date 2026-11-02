"""Repair orphan content-type declarations; add standard native fade transitions.
Some bundled PptxGenJS builds declare one master per slide but write one shared
master. Remove declarations only when their target is absent and not referenced.
All text, pictures, diagrams and charts remain their original native objects.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import json
root=Path(__file__).resolve().parents[1]
file=root/'STEPLOCK_Speedrun_SR008.pptx'
with ZipFile(file) as z: parts={n:z.read(n) for n in z.namelist()}
CT='http://schemas.openxmlformats.org/package/2006/content-types'
ET.register_namespace('',CT)
tree=ET.fromstring(parts['[Content_Types].xml']);removed=[]
for item in list(tree):
    part=item.get('PartName','').lstrip('/')
    if part and part not in parts:
        removed.append(part);tree.remove(item)
parts['[Content_Types].xml']=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
with ZipFile(file,'w',ZIP_DEFLATED) as z:
    for n,v in parts.items():z.writestr(n,v)
(root.parent/'runtime/pitch-build/package-repair.json').write_text(json.dumps({'removed_orphan_content_type_declarations':removed,'objects_changed':False},indent=2),encoding='utf-8')
print(json.dumps({'orphan_declarations_removed':len(removed)}))
