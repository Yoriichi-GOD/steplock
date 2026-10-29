import hashlib
import time
import cv2
import numpy as np
from steplock.schemas import FrameObservation, Observation
from .calibration import ANCHORS, calibrate, transform


def png_bytes(frame):
    ok, encoded = cv2.imencode(".png", frame)
    if not ok:
        raise ValueError("Frame PNG encoding failed")
    return encoded.tobytes()


class Detector:
    def __init__(self, recipe):
        self.recipe = recipe
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        self.parts = {p.aruco_marker_id: name for name, p in recipe.parts.items()}

    def analyze(self, frame, frame_index, timestamp_ms, source_kind, source_hash, manual_points=None):
        started = time.perf_counter()
        if frame is None or frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
            raise ValueError("Expected an 8-bit BGR image")
        h, w = frame.shape[:2]
        if not (80 <= min(w, h) and max(w, h) <= 4096):
            raise ValueError("Frame dimensions outside 80–4096 pixels")
        encoded = png_bytes(frame)
        digest = hashlib.sha256(encoded).hexdigest()
        fid = f"f{frame_index:06d}-{digest[:10]}"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        mean = float(gray.mean())
        saturation = float(np.mean(gray > 252))
        flags = []
        if focus < self.recipe.minimum_focus_variance:
            flags.append("LOW_FOCUS")
        if mean < 45 or mean > 250:
            flags.append("EXPOSURE_OUT_OF_RANGE")
        corners, raw_ids, rejected = self.detector.detectMarkers(gray)
        ids = [] if raw_ids is None else [int(x) for x in raw_ids.flatten()]
        if len(ids) != len(set(ids)):
            flags.append("DUPLICATE_MARKER_ID")
        found = {mid: np.asarray(c, np.float32).reshape(4, 2) for mid, c in zip(ids, corners)}
        points, matrix, mode = [], None, None
        if all(mid in found for mid in ANCHORS):
            points = [found[mid].mean(axis=0).tolist() for mid in ANCHORS]
            mode = "FOUR_ANCHOR_CENTERS"
        elif manual_points is not None:
            points = manual_points
            mode = "MANUAL_FOUR_POINT"
        else:
            flags.append("CALIBRATION_REQUIRED")
        if points:
            try:
                matrix = calibrate(points, frame.shape)
            except ValueError:
                flags.append("INVALID_CALIBRATION")
        cid = None if matrix is None else "cal-" + hashlib.sha256(np.round(matrix, 5).tobytes()).hexdigest()[:16]
        zone_pixels, empty, observations = {}, [], []
        warped = None
        if matrix is not None:
            inv = np.linalg.inv(matrix)
            scale = np.diag([800., 400., 1.])
            warped = cv2.warpPerspective(gray, scale @ matrix, (800, 400))
            for zone, (x1, y1, x2, y2) in self.recipe.zones.items():
                zone_pixels[zone] = transform([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], inv).tolist()
                # Only a bright, nearly uniform inset can support visible emptiness.
                # This is a controlled white-board heuristic, not general occlusion recognition.
                patch = warped[int((y1+.06)*400):int((y2-.06)*400), int((x1+.025)*800):int((x2-.025)*800)]
                if patch.size and patch.mean() > 170 and patch.std() < 18 and np.mean(patch < 130) < .02:
                    empty.append(zone)
        for mid, c in found.items():
            if mid in ANCHORS:
                continue
            area = abs(float(cv2.contourArea(c)))
            if area < 225 or min(np.linalg.norm(c - np.roll(c, 1, axis=0), axis=1)) < 12:
                flags.append("MARKER_TOO_SMALL")
            xy, zone = None, None
            if matrix is not None:
                xy = tuple(float(x) for x in transform([c.mean(axis=0)], matrix)[0])
                for zid, (x1, y1, x2, y2) in self.recipe.zones.items():
                    inset = self.recipe.zone_inset
                    polygon = np.float32([[x1+inset,y1+inset],[x2-inset,y1+inset],[x2-inset,y2-inset],[x1+inset,y2-inset]])
                    if cv2.pointPolygonTest(polygon, xy, False) > 0:
                        zone = zid
                if zone in empty:
                    empty.remove(zone)
            observations.append(Observation(observation_id=f"{fid}-tag{mid}", marker_id=mid,
                part_id=self.parts.get(mid, "UNKNOWN"), board_xy=xy, zone_id=zone,
                corners=c.tolist(), area_px2=area,
                quality_score=round(min(1., area / 2000) * min(1., focus / 200), 3)))
        if matrix is None:
            empty = []
        record = FrameObservation(frame_id=fid, frame_index=frame_index, captured_at_ms=timestamp_ms,
            source_kind=source_kind, source_sha256=source_hash, frame_sha256=digest,
            width=w, height=h, cv_version=cv2.__version__, usable=not flags,
            quality_flags=sorted(set(flags)), calibration_id=cid, calibration_points=points,
            calibration_mode=mode, focus_variance=round(focus, 2), mean_luminance=round(mean, 2),
            saturated_fraction=round(saturation, 4), observations=observations,
            clear_empty_zones=empty, zones_pixels=zone_pixels, marker_ids=sorted(ids),
            rejected_candidates=len(rejected), vision_ms=(time.perf_counter()-started)*1000)
        return record, encoded, self.overlay(frame, record)

    def overlay(self, frame, record):
        out = frame.copy()
        for name, points in record.zones_pixels.items():
            p = np.int32(points)
            cv2.polylines(out, [p], True, (130, 190, 120), 1, cv2.LINE_AA)
            cv2.putText(out, name.replace("_SLOT", ""), tuple(p[0]+[4, 17]), cv2.FONT_HERSHEY_SIMPLEX, .38, (100, 145, 80), 1, cv2.LINE_AA)
        for ob in record.observations:
            p = np.int32(ob.corners)
            color = (120, 230, 170) if ob.part_id != "UNKNOWN" and ob.zone_id else (100, 130, 255)
            cv2.polylines(out, [p], True, color, 2, cv2.LINE_AA)
            label = f"{ob.marker_id} {ob.part_id} / {ob.zone_id or 'OUTSIDE'}"
            cv2.putText(out, label, (max(0,int(p[0,0])-10), max(20,int(p[0,1])-10)), cv2.FONT_HERSHEY_SIMPLEX, .4, color, 1, cv2.LINE_AA)
        if record.quality_flags:
            cv2.rectangle(out, (0, out.shape[0]-34), (out.shape[1], out.shape[0]), (25, 25, 60), -1)
            cv2.putText(out, "HOLD: " + ", ".join(record.quality_flags), (12, out.shape[0]-12), cv2.FONT_HERSHEY_SIMPLEX, .48, (170, 200, 255), 1, cv2.LINE_AA)
        return out
