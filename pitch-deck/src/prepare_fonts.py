"""Convert existing Fontsource WOFF2 subsets for this machine's private rendering.
No font files are included in pitch-deck or embedded in the PPTX.
"""
from pathlib import Path
import json
from fontTools.ttLib import TTFont
root=Path(__file__).resolve().parents[2]
dest=root/'runtime/pitch-build/fonts'
dest.mkdir(parents=True,exist_ok=True)
items=[('geist',400,'normal'),('geist',500,'normal'),('instrument-serif',400,'italic'),('ibm-plex-mono',400,'normal'),('space-grotesk',500,'normal')]
result=[]
for family,weight,style in items:
    name=f'{family}-latin-{weight}-{style}'
    src=root/f'frontend/node_modules/@fontsource/{family}/files/{name}.woff2'
    font=TTFont(src);font.flavor=None
    out=dest/f'{name}.ttf';font.save(out)
    names={str(i):font['name'].getDebugName(i) for i in [1,2,4,6,16,17]}
    result.append({'file':str(out),'names':names,'source':str(src.relative_to(root))})
(dest.parent/'font-inventory.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
