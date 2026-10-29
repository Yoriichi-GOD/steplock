"""Small annotation-only inventory. No raw video, training, or visual benchmark claim."""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path,PurePosixPath
import urllib.request
import zipfile


def fetch(url,limit=16*1024*1024):
    request=urllib.request.Request(url,headers={"User-Agent":"STEPLOCK-research-inventory"})
    with urllib.request.urlopen(request,timeout=25) as response:
        data=response.read(limit+1)
    if len(data)>limit: raise ValueError("Annotation download exceeds bounded size limit")
    return data


def parse_annotations(payload):
    columns=("start","end","verb","this","that","label","remark")
    raw=[row for row in csv.reader(io.StringIO(payload.decode("utf-8-sig"))) if any(cell.strip() for cell in row)]
    if raw and tuple(cell.strip().lower() for cell in raw[0][:2])==("start","end"): raw=raw[1:]
    records=[]
    for row in raw:
        if not 6<=len(row)<=7: raise ValueError("Unexpected annotation field count")
        row=[cell.strip() for cell in row]+[""]*(7-len(row))
        float(row[0]);float(row[1])  # Validate numeric boundaries without guessing their unit.
        records.append(dict(zip(columns,row)))
    return records


def acquire(dest):
    dest=Path(dest).resolve()
    # A repeat can inspect existing annotations, but never overwrite an acquisition.
    if dest.exists() and any(dest.iterdir()): raise ValueError("Destination is nonempty; select a new acquisition directory")
    dest.mkdir(parents=True,exist_ok=True)
    api="https://api.github.com/repos/assembly-101/assembly101-mistake-detection/commits/main"
    commit=json.loads(fetch(api,1024*1024))["sha"]
    url=f"https://codeload.github.com/assembly-101/assembly101-mistake-detection/zip/{commit}"
    archive=fetch(url)
    labels=collections.Counter();rows=0;files=[];license_text=None
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        names=zipped.namelist()
        license_name=next((n for n in names if PurePosixPath(n).name=="LICENSE"),None)
        if not license_name: raise ValueError("Source license missing")
        license_text=zipped.read(license_name).decode("utf-8-sig")
        if "creativecommons.org/licenses/by-nc/4.0" not in license_text:
            raise ValueError("License differs from the reviewed CC BY-NC 4.0 terms; stop and inspect")
        for item in zipped.infolist():
            parts=PurePosixPath(item.filename).parts
            if ".." in parts or PurePosixPath(item.filename).is_absolute(): raise ValueError("Unsafe archive path")
            if "annots" not in parts or not item.filename.endswith(".csv"): continue
            if item.file_size>2*1024*1024: raise ValueError("Unexpectedly large annotation CSV")
            payload=zipped.read(item)
            relative=Path(*parts[parts.index("annots"):])
            target=dest/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(payload)
            records=parse_annotations(payload)
            rows+=len(records)
            for row in records: labels[row.get("label","MISSING_LABEL_COLUMN")]+=1
            files.append({"path":relative.as_posix(),"rows":len(records),"columns":list(records[0]) if records else [],"sha256":hashlib.sha256(payload).hexdigest()})
    if not files: raise ValueError("Expected annots/ CSV hierarchy was not found")
    (dest/"LICENSE").write_text(license_text,encoding="utf-8")
    inventory={"source":"assembly101-mistake-detection","source_url":url,"source_commit":commit,
        "archive_sha256":hashlib.sha256(archive).hexdigest(),"download_bytes":len(archive),"license":"CC BY-NC 4.0",
        "attribution":"Sener et al., Assembly101 (CVPR 2022); Ding et al., Every Mistake Counts in Assembly (2023)",
        "license_url":"https://creativecommons.org/licenses/by-nc/4.0/","acquired_at":dt.datetime.now(dt.timezone.utc).isoformat(),
        "sequence_csv_count":len(files),"annotation_rows":rows,"labels":dict(labels),"files":files,
        "visual_benchmark":"NOT_RUN","action_annotation_benchmark":"NOT_RUN — no defensible mapping from toy actions to the four tagged placement recipe",
        "raw_video_downloaded":False,"redistribution":"Raw annotations remain local under ignored data/; inventory contains counts and hashes only"}
    (dest/"inventory.json").write_text(json.dumps(inventory,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in inventory.items() if k!="files"},indent=2))
    return inventory


def reinventory(dest):
    dest=Path(dest).resolve()
    original=json.loads((dest/"inventory.json").read_text(encoding="utf-8"))
    files=[];labels=collections.Counter();rows=0
    for path in sorted((dest/"annots").rglob("*.csv")):
        payload=path.read_bytes();records=parse_annotations(payload)
        rows+=len(records)
        labels.update(row["label"] for row in records)
        files.append({"path":path.relative_to(dest).as_posix(),"rows":len(records),"sha256":hashlib.sha256(payload).hexdigest()})
    updated={**original,"sequence_csv_count":len(files),"annotation_rows":rows,"labels":dict(labels),"files":files,
             "parser":"headerless seven-column CSV; first annotation retained; boundary units not assumed",
             "inventory_corrected_at":dt.datetime.now(dt.timezone.utc).isoformat(),
             "prior_inventory_status":"Original used DictReader and treated first data row as header; retained for audit, superseded by this inventory"}
    output=dest/f"inventory-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
    output.write_text(json.dumps(updated,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in updated.items() if k!="files"},indent=2))
    print(f"Saved {output}")
    return updated


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",choices=["assembly101"],default="assembly101")
    parser.add_argument("--dest",default="data/external/assembly101_mistakes")
    parser.add_argument("--inventory-only",action="store_true",help="Reparse an existing acquisition without overwriting its first inventory")
    args=parser.parse_args()
    reinventory(args.dest) if args.inventory_only else acquire(args.dest)
