"""Acquire only the official IMPACT v1.1 sample; verify before selective extraction.

No credentials, models, training, full-dataset downloads, or media publication.
Raw data and upstream tooling stay in the ignored data/ directory.
"""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import urllib.request
import zipfile

REPO_COMMIT = "4fed5faa5f05f7aece55712e458defa1f372b248"
DATA_COMMIT = "628d3ad7a366879f3fdab37648d5df271317c9c0"
SAMPLE = "sample/IMPACT-v1.1-sample.zip"
EXPECTED_BYTES = 2997108593
EXPECTED_SHA256 = "d22f64abfde8797c3d49cf86aea2ceb83e8581c571e6d5d1c3bad53aa2e13cfd"
BASE = f"https://huggingface.co/datasets/KratosWen/IMPACT/resolve/{DATA_COMMIT}/v1.1/"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_small(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "STEPLOCK-research/1"}), timeout=40) as response:
        data = response.read(2 * 1024**2 + 1)
    if len(data) > 2 * 1024**2:
        raise ValueError("Metadata exceeds size bound")
    return data


def verify_file(path, expected_size=EXPECTED_BYTES, expected_hash=EXPECTED_SHA256):
    if Path(path).stat().st_size != expected_size:
        raise ValueError("Archive size differs from the pinned official manifest")
    actual = sha256(path)
    if actual != expected_hash:
        raise ValueError(f"Archive SHA-256 mismatch: {actual}")
    return actual


def safe_member(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or any(":" in part for part in path.parts):
        raise ValueError("Unsafe ZIP member path")
    return path


def extract_relevant(archive, dest):
    """Extract RGB video and annotations/metadata only, preserving all media bytes."""
    dest = Path(dest).resolve()
    files = []
    with zipfile.ZipFile(archive) as zipped:
        members = zipped.infolist()
        if len(members) > 20000 or sum(item.file_size for item in members) > 24 * 1024**3:
            raise ValueError("Unexpected archive expansion")
        for item in members:
            relative = safe_member(item.filename)
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("ZIP symlinks are not accepted")
            selected = not item.is_dir() and any(p in relative.parts for p in ("videos", "annotations", "metadata"))
            record = {"path": item.filename, "bytes": item.file_size, "selected": selected}
            if selected:
                target = dest.joinpath(*relative.parts)
                if not target.resolve().is_relative_to(dest):
                    raise ValueError("Extraction escaped destination")
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    if target.stat().st_size != item.file_size:
                        raise ValueError("Existing extraction differs; select a new destination")
                    # Re-read ZIP CRC and compare bytes on a resumed acquisition.
                    digest = hashlib.sha256()
                    with zipped.open(item) as source:
                        for block in iter(lambda: source.read(4 * 1024**2), b""):
                            digest.update(block)
                    if digest.hexdigest() != sha256(target):
                        raise ValueError("Existing extracted file hash differs")
                else:
                    with zipped.open(item) as source, target.open("xb") as output:
                        shutil.copyfileobj(source, output, 4 * 1024**2)
                record["sha256"] = sha256(target)
            files.append(record)
    return files


def download(dest):
    dest = Path(dest).resolve()
    if not dest.is_relative_to((bootstrap.ROOT / "data").resolve()):
        raise ValueError("Acquisition must remain under ignored data/")
    dest.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(dest).free < 8 * 1024**3:
        raise ValueError("At least 8 GiB free space is required for archive plus selected extraction")
    metadata = {}
    for filename in ("MANIFEST.tsv", "SHA256SUMS"):
        content = fetch_small(BASE + filename)
        (dest / filename).write_bytes(content)
        metadata[filename] = content.decode("utf-8")
    entries = {line.split("\t", 1)[1]: int(line.split("\t", 1)[0]) for line in metadata["MANIFEST.tsv"].splitlines()[1:] if line.strip()}
    hashes = {line.split(maxsplit=1)[1].lstrip("* "): line.split(maxsplit=1)[0] for line in metadata["SHA256SUMS"].splitlines() if line.strip()}
    if entries.get(SAMPLE) != EXPECTED_BYTES or hashes.get(SAMPLE) != EXPECTED_SHA256:
        raise ValueError("Pinned release metadata changed; inspect before downloading")
    upstream = f"https://raw.githubusercontent.com/Kratos-Wen/IMPACT/{REPO_COMMIT}/"
    license_text = fetch_small(upstream + "LICENSE-DATA")
    if b"creativecommons.org/licenses/by-nc-sa/4.0" not in license_text:
        raise ValueError("Dataset license differs from reviewed CC BY-NC-SA 4.0")
    (dest / "LICENSE-DATA").write_bytes(license_text)
    # Retain the exact official commands as provenance, not executable dependencies.
    for filename in ("download_impact.py", "verify_release.py"):
        (dest / ("upstream_" + filename)).write_bytes(fetch_small(upstream + "tools/" + filename))
    archive = dest / "IMPACT-v1.1-sample.zip"
    partial = archive.with_suffix(".zip.part")
    if not archive.exists():
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"User-Agent": "STEPLOCK-research/1"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(BASE + SAMPLE, headers=headers)
        with urllib.request.urlopen(request, timeout=90) as response:
            resume = offset > 0 and response.status == 206
            if resume and not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                raise ValueError("Server returned an unexpected byte range")
            total = offset if resume else 0
            last_report = total
            with partial.open("ab" if resume else "wb") as output:
                for block in iter(lambda: response.read(4 * 1024**2), b""):
                    total += len(block)
                    if total > EXPECTED_BYTES:
                        raise ValueError("Download exceeded official size bound")
                    output.write(block)
                    if total - last_report >= 128 * 1024**2:
                        print(f"Downloaded {total}/{EXPECTED_BYTES} bytes ({100*total/EXPECTED_BYTES:.1f}%)", flush=True)
                        last_report = total
        verify_file(partial)
        partial.rename(archive)
    verify_file(archive)
    files = extract_relevant(archive, dest / "extracted")
    receipt = {"dataset": "IMPACT", "release": "v1.1", "data_revision": DATA_COMMIT,
               "repository_commit": REPO_COMMIT, "official_source": "https://github.com/Kratos-Wen/IMPACT",
               "download_url": BASE + SAMPLE, "archive_bytes": EXPECTED_BYTES, "archive_sha256": EXPECTED_SHA256,
               "checksum_verified": True, "license": "CC BY-NC-SA 4.0", "acquired_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "extraction": "RGB videos, annotations, metadata only; no depth/audio/eye-tracking/features extraction",
               "attribution": "Wen et al., IMPACT: A Dataset for Multi-Granularity Human Procedural Action Understanding in Industrial Assembly; official repository citation",
               "files": files, "raw_media_publication": False}
    (dest / "acquisition.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "files"}, indent=2), flush=True)
    print(f"Extracted {sum(f['selected'] for f in files)} of {len(files)} members", flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=bootstrap.ROOT / "data/external/impact_v1_1")
    args = parser.parse_args()
    download(args.dest)
