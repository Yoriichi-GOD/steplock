"""Generate printable assets and verify every marker with the production detector API."""
import bootstrap
from pathlib import Path
import cv2
import numpy as np
from scripts.fixture_lib import render_board, paste_marker


def main():
    dest=bootstrap.ROOT/"demo_kit"
    dest.mkdir(exist_ok=True)
    board=render_board(watermark=False)
    cv2.imwrite(str(dest/"printable_board.png"),board)
    sheet=np.full((1120,960,3),255,np.uint8)
    labels={10:"BASE",11:"SPACER",12:"COVER",13:"FASTENER",14:"WRONG TYPE",30:"UNKNOWN",40:"TOP LEFT",41:"TOP RIGHT",42:"BOTTOM RIGHT",43:"BOTTOM LEFT"}
    detector=cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50))
    for i,(mid,label) in enumerate(labels.items()):
        center=(100+(i%5)*190,135+(i//5)*420)
        paste_marker(sheet,mid,center,130)
        cv2.putText(sheet,f"{mid} {label}",(center[0]-82,center[1]+105),cv2.FONT_HERSHEY_SIMPLEX,.42,(30,30,30),1,cv2.LINE_AA)
        tile=np.full((280,280,3),255,np.uint8)
        paste_marker(tile,mid,(140,140),200)
        _,ids,_=detector.detectMarkers(tile)
        assert ids is not None and mid in ids, f"Generated tag {mid} failed decoding"
        for turns in (1,2,3):
            _,rotated,_=detector.detectMarkers(np.rot90(tile,turns).copy())
            assert rotated is not None and mid in rotated
        cv2.imwrite(str(dest/f"tag_{mid}.png"),tile)
    cv2.putText(sheet,"Cut cards; keep white border. Place each in its matching slot.",(32,930),cv2.FONT_HERSHEY_SIMPLEX,.62,(30,30,30),1,cv2.LINE_AA)
    cv2.putText(sheet,"Board anchor centers define normalized coordinates; do not move anchors.",(32,975),cv2.FONT_HERSHEY_SIMPLEX,.54,(30,30,30),1,cv2.LINE_AA)
    cv2.putText(sheet,"ADVISORY DEMO / NO ENERGIZED MACHINERY",(32,1020),cv2.FONT_HERSHEY_SIMPLEX,.68,(30,30,30),1,cv2.LINE_AA)
    cv2.imwrite(str(dest/"markers.png"),sheet)
    print(f"Verified 10 markers × four orientations. Kit: {dest}")


if __name__=="__main__":
    main()
