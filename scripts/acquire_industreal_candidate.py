"""Acquire one mirrored real video and a third-party research checkpoint.

This does not run recognition, authenticate the mirror against the official
archive, or establish a held-out evaluation. Media and weights stay in data/.
"""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import urllib.request
import zlib

ROOT = Path(__file__).resolve().parents[1]
HF_REV = "c408f6effaa96512bd4eb5036c871bb7601ddc3e"
MODEL_REV = "5fac256e7d29de2626a2b08e973a449fe6ea98a9"
ARCHIVE_SIZE = 2_505_914_072
VIDEO_NAME = "25_assy_0_1.mp4"
VIDEO_SHA256 = "9771261256d8995ea9c1144deb6dab31c14fb6f457fb16eb744c9607090f34a1"
MODEL_SHA256 = "53739cf329e5e3fb08b8584957cf81caf79ce8073c892437cb155e15fee735ce"
BASE = f"https://huggingface.co/datasets/Zzitang/IndustReal/resolve/{HF_REV}/IndustReal_videos.zip"
MODEL_URL = f"https://raw.githubusercontent.com/321thijs123/IndustReal-YOLO-VLM/{MODEL_REV}/yolo_weights/best.pt"


def bounded(url, start=None, size=None):
    limit = size if size is not None else 8_000_000
    if not 0 < limit <= 8_000_000:
        raise ValueError("Transfer limit exceeded")
    headers = {"User-Agent": "STEPLOCK-research/1.0"}
    if start is not None:
        headers["Range"] = f"bytes={start}-{start + limit - 1}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
        expected = f"bytes {start}-{start + limit - 1}/{ARCHIVE_SIZE}"
        if start is not None and (response.status != 206 or response.headers.get("Content-Range") != expected):
            raise ValueError("Server did not honor selected byte range")
        raw = response.read(limit + 1)
    if len(raw) > limit or (size is not None and len(raw) != size):
        raise ValueError("Unexpected transfer size")
    return raw


def selected_entry(tail, tail_start):
    end = tail.rfind(b"PK\x05\x06")
    if end < 0:
        raise ValueError("ZIP end directory missing")
    header = struct.unpack_from("<4s4H2LH", tail, end)
    if header[1:3] != (0, 0) or header[3] != header[4]:
        raise ValueError("Unsupported split ZIP")
    pos = header[6] - tail_start
    if pos < 0 or pos + header[5] > end:
        raise ValueError("ZIP directory outside bounded tail")
    entries = []
    for _ in range(header[4]):
        fields = struct.unpack_from("<4s6H3L5H2L", tail, pos)
        if fields[0] != b"PK\x01\x02":
            raise ValueError("Malformed ZIP directory")
        name_size, extra_size, comment_size = fields[10:13]
        name = tail[pos + 46:pos + 46 + name_size].decode("utf-8")
        if name == VIDEO_NAME:
            entries.append({"name": name, "compressed": fields[8], "size": fields[9], "offset": fields[-1], "crc32": fields[7], "method": fields[4]})
        pos += 46 + name_size + extra_size + comment_size
    if len(entries) != 1 or entries[0]["method"] != 8 or entries[0]["size"] != 37_472_124:
        raise ValueError("Unexpected selected ZIP member")
    return entries[0]


def verify_video(packed, entry):
    decoder = zlib.decompressobj(-15)
    raw = decoder.decompress(packed, entry["size"] + 1)
    if not decoder.eof or len(raw) != entry["size"] or zlib.crc32(raw) != entry["crc32"]:
        raise ValueError("ZIP member integrity failure")
    if hashlib.sha256(raw).hexdigest() != VIDEO_SHA256:
        raise ValueError("Pinned video hash mismatch")
    return raw


def video(out):
    path = out / VIDEO_NAME
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == VIDEO_SHA256:
        raw = path.read_bytes()
    else:
        tail_size = 262_144
        entry = selected_entry(bounded(BASE, ARCHIVE_SIZE - tail_size, tail_size), ARCHIVE_SIZE - tail_size)
        header = struct.unpack("<4s5H3L2H", bounded(BASE, entry["offset"], 30))
        if header[0] != b"PK\x03\x04" or header[3] != 8:
            raise ValueError("Unexpected ZIP local header")
        name_size, extra_size = header[-2:]
        if bounded(BASE, entry["offset"] + 30, name_size).decode() != VIDEO_NAME:
            raise ValueError("ZIP local name mismatch")
        start = entry["offset"] + 30 + name_size + extra_size
        block = 4 * 1024 * 1024
        spans = [(start + i, min(block, entry["compressed"] - i)) for i in range(0, entry["compressed"], block)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            packed = b"".join(pool.map(lambda pair: bounded(BASE, *pair), spans))
        raw = verify_video(packed, entry)
        path.write_bytes(raw)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": VIDEO_SHA256, "bytes": len(raw), "zip_crc32": f"{zlib.crc32(raw):08x}", "source": BASE, "mirror_provenance": "UNVERIFIED_AGAINST_OFFICIAL_ARCHIVE", "recording_split": "UNKNOWN_NOT_HELD_OUT"}


def model(out):
    path = out / "third_party_best.pt"
    raw = path.read_bytes() if path.exists() else bounded(MODEL_URL)
    if len(raw) != 6_230_378 or hashlib.sha256(raw).hexdigest() != MODEL_SHA256:
        raise ValueError("Published model hash mismatch")
    path.write_bytes(raw)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": MODEL_SHA256, "bytes": len(raw), "source": MODEL_URL, "publisher": "321thijs123 course project; NOT original IndustReal authors", "embedded_checkpoint_license": "AGPL-3.0 (https://ultralytics.com/license)", "publisher_license_file": "NOT_FOUND; weights are not redistributed"}


def main():
    out = ROOT / "data/external/industreal_candidate"
    out.mkdir(parents=True, exist_ok=True)
    receipt = {"checked_at": datetime.now(timezone.utc).isoformat(), "official_archive_access": "TIMEOUT_OBSERVED_2026_10_29", "population": "EXTERNAL_PHYSICAL_MIRROR_UNVERIFIED", "accuracy_claim": None}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {"video": pool.submit(video, out), "model": pool.submit(model, out)}
        for key, future in futures.items():
            try:
                receipt[key] = future.result()
            except Exception as error:
                receipt[key] = {"error": repr(error)}
            print(key, receipt[key], flush=True)
    (out / "acquisition_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    if any("error" in receipt[key] for key in ("video", "model")):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
