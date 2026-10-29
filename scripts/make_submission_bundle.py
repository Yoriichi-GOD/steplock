"""Bundle public tracked source and the reviewed build; never runtime or keys."""
import bootstrap
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=bootstrap.ROOT


def main():
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out=ROOT/'runtime/submission';out.mkdir(parents=True,exist_ok=True)
    path=out/f'steplock-nebius-{commit[:8]}.zip'
    subprocess.run(['git','archive','--format=zip','--output',str(path),commit],cwd=ROOT,check=True)
    with zipfile.ZipFile(path,'a',zipfile.ZIP_DEFLATED) as archive:
        for file in (ROOT/'frontend/dist').rglob('*'):
            if file.is_file():archive.write(file,file.relative_to(ROOT).as_posix())
        names=archive.namelist()
        if any(name.startswith(('runtime/','data/','ui/','docs/judging/','.git/')) for name in names):raise ValueError('Private or runtime content in bundle')
        archive.writestr('BUILD_RECEIPT.json',json.dumps({'commit':commit,'created_at':datetime.now(timezone.utc).isoformat(),'credential_included':False,'provider_calls_performed_by_packager':0,'deployment':'NOT_DEPLOYED'},indent=2))
    receipt={'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'commit':commit}
    (out/'bundle_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))


if __name__=='__main__':main()
