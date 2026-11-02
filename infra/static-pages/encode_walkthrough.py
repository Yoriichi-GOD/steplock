"""Package genuine CDP browser frames; never generate inspection observations.

Input: an actual screencast's JPEGs plus frames.json (CDP wall-clock timestamps).
Output: silent VP9 WebM at 15 fps, retaining captured timing within 1/15 second,
with the last captured frame held three seconds for reading. No verdict editing.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import cv2

parser=argparse.ArgumentParser()
parser.add_argument('--capture',type=Path,required=True)
parser.add_argument('--ffmpeg',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
fps=15
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
clips=[]
for name,folder,outcome,copy in [
    ('normal','', 'PASS','All four placements are supported before the explicit checkpoint.'),
    ('wrong-component','wrong-component','HOLD_FOR_REVIEW','The wrong tagged component blocks the procedure.'),
    ('correction','correction','PASS after CORRECTED','The later correction retains the original wrong-component event.'),
]:
    source=args.capture/folder
    captured_frames=json.loads((source/'frames.json').read_text())
    # The correction capture ends on a redraw/loading frame after the complete
    # source image and PASS were already visible. Preserve that raw frame in the
    # source ledger, but end the published clip on the preceding complete frame.
    frames=captured_frames[:-1] if name=='correction' else captured_frames
    assert len(frames)>10, 'Capture is incomplete'
    times=[f['timestamp']-frames[0]['timestamp'] for f in frames]
    assert all(a<=b for a,b in zip(times,times[1:])), 'Non-monotonic browser capture'
    image=cv2.imread(str(source/frames[0]['file']))
    h,w=image.shape[:2]
    output=args.output/(name+'.webm')
    command=[str(args.ffmpeg.resolve()),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-c:v','libvpx-vp9','-crf','31','-b:v','0','-pix_fmt','yuv420p',str(output.resolve())]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    total=round((times[-1]+3)*fps)
    index=0
    for tick in range(total):
        while index+1<len(frames) and times[index+1]<=tick/fps:
            index+=1
            image=cv2.imread(str(source/frames[index]['file']))
        assert image.shape[:2]==(h,w)
        proc.stdin.write(image.tobytes())
    proc.stdin.close()
    assert proc.wait()==0
    # The poster is an unedited authentic screenshot, not a rendered result.
    poster=args.output/(name+'.jpg')
    shutil.copyfile(source/frames[-1]['file'],poster)
    duration=total/fps
    end=f'00:{int(duration)//60:02d}:{int(duration)%60:02d}.000'
    (args.output/(name+'.vtt')).write_text(f'WEBVTT\n\n00:00:00.000 --> {end}\nRECORDED SOFTWARE TEST / GENERATED FIXTURE\n{copy}\n',encoding='utf-8')
    source_frames=[{'file':f['file'],'timestamp':f['timestamp'],'sha256':sha(source/f['file'])} for f in captured_frames]
    clips.append({'name':name,'observed_final_status':outcome,'captured_at_utc':datetime.fromtimestamp(frames[0]['timestamp'],timezone.utc).isoformat(),'captured_seconds':round(times[-1],6),'playback_seconds':duration,'frames_captured':len(captured_frames),'frames_used':len(frames),'editorial_cut':'Final redraw/loading frame omitted; preceding complete source frame retained.' if name=='correction' else None,'video_dimensions':[w,h],'video_sha256':sha(output),'poster_sha256':sha(poster),'video_bytes':output.stat().st_size,'source_frames':source_frames})
receipt={'population':'SYNTHETIC_FIXTURE','kind':'ACTUAL_APPLICATION_SCREEN_RECORDING','application_source_commit':'c8577afaba7ed8b5474e697294829dc85e2eed1e','application_image_digest':'sha256:fe77c48ef879350c0cc83c2c26413c5413da97aafd3d11c9e164caab226d8447','capture_method':'Browser CDP Page.startScreencast; UI actions through browser controls; original JPEG frames retained privately.','encoding':'VP9 WebM, silent, 15 fps, captured timing quantized to 1/15 s, final frame held for 3 s. No invented observations or edited verdicts.','limits':'Historical software demonstration only. Not physical camera footage, industrial accuracy, current workstation state, or a benchmark run.','clips':clips}
(args.output/'provenance.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:c[k] for k in ['name','playback_seconds','frames_captured','video_bytes']} for c in clips]))
