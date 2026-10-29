"""Optimize the user-supplied REQUIEM pack; never alter evidence imagery.

Usage: python scripts/prepare_requiem_assets.py <extracted-pack-directory>
Requires Pillow in the existing development environment. Raw originals stay in
the supplied ZIP, outside public/. The manifest records both sides of conversion.
"""
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('backgrounds/celestial-arches-master.png', 'celestial-arches.webp', 1691),
    ('branding/steplock-ornate-logo-master.png', 'steplock-ornate-logo.webp', 900),
    ('branding/steplock-crest-compact.png', 'steplock-crest-compact.webp', 128),
    ('branding/procedure-studio-ornate-title-master.png', 'procedure-studio-ornate-title.webp', 1100),
    ('ornaments/right-arch-landscape-master.png', 'right-arch-landscape.webp', 300),
    ('empty-state/floating-flower-master.png', 'floating-flower.webp', 600),
    ('ornaments/corner-florals-master.png', 'corner-florals.webp', 600),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pack = Path(sys.argv[1]).resolve()
    supplied = json.loads((pack / 'ASSET_MANIFEST.json').read_text(encoding='utf-8'))
    records = {item['path']: item for item in supplied['assets']}
    target = ROOT / 'frontend/public/assets/requiem'
    target.mkdir(parents=True, exist_ok=True)
    files = []
    for source, name, width in SOURCES:
        original = pack / source
        assert digest(original) == records[source]['sha256'], source
        with Image.open(original) as image:
            source_size = list(image.size)
            image.thumbnail((width, width * 4), Image.Resampling.LANCZOS)
            output = target / name
            image.save(output, 'WEBP', quality=85, method=6, exact=True)
            files.append(dict(path=name, bytes=output.stat().st_size,
                              sha256=digest(output), size_px=list(image.size),
                              source=source, source_sha256=digest(original),
                              source_size_px=source_size))
    manifest = dict(source_pack='STEPLOCK_REQUIEM_UI_ASSETS_AND_CODEX.zip',
                    source_pack_sha256='078739888fb88fb44bd14b83de415f6157c14e3b8cd67b6206ee06c636edcbaf',
                    provenance='User-supplied generated decorative art. Never inspection evidence.',
                    conversion='Pillow, LANCZOS thumbnail, WebP quality=85 method=6 exact=True',
                    files=files)
    (target / 'manifest.json').write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(dict(files=len(files), bytes=sum(item['bytes'] for item in files))))


if __name__ == '__main__':
    main()
