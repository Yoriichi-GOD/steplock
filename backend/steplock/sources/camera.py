import time
import cv2
from steplock.config import MAX_SECONDS


def camera_frames(index, stop_event):
    if index not in range(9): raise ValueError("Camera index must be between 0 and 8")
    cap=cv2.VideoCapture(index,cv2.CAP_DSHOW if __import__('sys').platform=='win32' else cv2.CAP_ANY)
    try:
        if not cap.isOpened(): raise ValueError("Camera unavailable. Try browser camera or upload a recording.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
        started=time.monotonic()
        frame_index=0
        while not stop_event.is_set() and time.monotonic()-started<MAX_SECONDS:
            ok,image=cap.read()
            if not ok: raise ValueError("Camera stopped delivering images. Upload a recording or reconnect.")
            h,w=image.shape[:2]
            if max(h,w)>1280:
                image=cv2.resize(image,(round(w*1280/max(h,w)),round(h*1280/max(h,w))))
            yield frame_index,(time.monotonic()-started)*1000,image
            frame_index+=1
            stop_event.wait(.1)
    finally:
        cap.release()
