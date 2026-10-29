"""Deterministic software imagery. This module is NOT imported by perception/engine."""
import cv2
import numpy as np

WIDTH, HEIGHT = 960, 600
ANCHOR_PIXELS = {40: (60, 70), 41: (900, 70), 42: (900, 470), 43: (60, 470)}
SLOTS = {"BASE_SLOT": (.24,.47), "SPACER_SLOT": (.51,.47), "COVER_SLOT": (.725,.47), "FASTENER_SLOT": (.895,.47)}
ZONES = {"BASE_SLOT": (.08,.16,.40,.78), "SPACER_SLOT": (.40,.16,.62,.78), "COVER_SLOT": (.62,.16,.83,.78), "FASTENER_SLOT": (.83,.16,.96,.78)}


def board_point(x, y):
    return (round(60 + x * 840), round(70 + y * 400))


def paste_marker(canvas, marker_id, center, size=56):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(dictionary, marker_id, size)
    x, y = int(center[0]-size//2), int(center[1]-size//2)
    cv2.rectangle(canvas, (x-8, y-8), (x+size+8, y+size+8), (255,255,255), -1)
    canvas[y:y+size,x:x+size] = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)


def render_board(placements=(), *, seed=0, variant=0, blur=0, occluded=None, anchors=True, watermark=True):
    frame = np.full((HEIGHT, WIDTH, 3), 235, np.uint8)
    cv2.rectangle(frame, (26,28), (934,503), (250,250,250), -1)
    cv2.putText(frame, "STEPLOCK / TAGGED PLACEMENT BENCH", (105,36), cv2.FONT_HERSHEY_SIMPLEX, .58, (65,70,75), 1, cv2.LINE_AA)
    for name, box in ZONES.items():
        p1, p2 = board_point(box[0],box[1]), board_point(box[2],box[3])
        cv2.rectangle(frame, p1, p2, (205,214,210), 1)
    if anchors:
        for mid, center in ANCHOR_PIXELS.items():
            paste_marker(frame, mid, center, 46)
    for mid, zone in placements:
        center = board_point(*SLOTS[zone]) if isinstance(zone,str) else board_point(*zone)
        paste_marker(frame, mid, center, 56)
    if occluded:
        x1,y1,x2,y2 = ZONES[occluded]
        cv2.rectangle(frame, board_point(x1+.01,y1+.01), board_point(x2-.01,y2-.01), (115,119,122), -1)
    if watermark:
        cv2.putText(frame, "SYNTHETIC SOFTWARE TEST / NOT CAMERA FOOTAGE", (105,548), cv2.FONT_HERSHEY_SIMPLEX, .6, (70,75,85), 1, cv2.LINE_AA)
        cv2.putText(frame, "Marker identity is tag identity. Advisory only.", (105,575), cv2.FONT_HERSHEY_SIMPLEX, .43, (95,100,110), 1, cv2.LINE_AA)
    if variant:
        rng = np.random.default_rng(seed)
        tilt = min(variant, 5) * 2.5
        src = np.float32([[0,0],[WIDTH-1,0],[WIDTH-1,HEIGHT-1],[0,HEIGHT-1]])
        dst = src + np.float32([[tilt,tilt],[0,tilt*1.3],[-tilt,0],[tilt,0]])
        frame = cv2.warpPerspective(frame, cv2.getPerspectiveTransform(src,dst), (WIDTH,HEIGHT), borderValue=(225,225,225))
        alpha = max(.64, 1 - variant*.055)
        frame = np.uint8(np.clip(frame.astype(np.float32)*alpha,0,255))
    # Distinct synthetic exposures: small camera movement changes actual tag geometry.
    # Seed does not encode scenario labels, and no truth is painted into the frame.
    if seed:
        rng = np.random.default_rng(seed)
        matrix = cv2.getRotationMatrix2D((WIDTH/2,HEIGHT/2), float(rng.uniform(-.12,.12)), 1.)
        matrix[:,2] += rng.uniform(-1.2,1.2,2)
        frame = cv2.warpAffine(frame,matrix,(WIDTH,HEIGHT),borderValue=(235,235,235))
    if blur:
        frame = cv2.GaussianBlur(frame,(blur|1,blur|1),0)
    return frame


def scenario_stages(family):
    b=(10,"BASE_SLOT"); s=(11,"SPACER_SLOT"); c=(12,"COVER_SLOT"); f=(13,"FASTENER_SLOT"); w=(14,"FASTENER_SLOT")
    normal=[[],[b],[b,s],[b,s,c],[b,s,c,f]]
    return {
        "normal": normal,
        "wrong_component": normal[:-1]+[[b,s,c,w]],
        "wrong_zone": [[],[b],[b,(11,"COVER_SLOT")]],
        "wrong_order": [[],[b],[b,c],[b,s,c],[b,s,c,f]],
        "missing_fastener": normal[:-1],
        "correction": normal[:-1]+[[b,s,c,w],[b,s,c],[b,s,c,f]],
        "occlusion": normal+normal[-1:],
        "frozen_capture": [normal[-1]],
    }[family]


def scenario_frames(family, variant=0, seed=2626):
    stages = scenario_stages(family)
    frames_per_stage = 6  # 1.2 seconds @ 5fps; temporal support isn't a single-frame shortcut.
    for index in range(len(stages)*frames_per_stage):
        stage = index//frames_per_stage
        exposure_seed = 0 if family == "frozen_capture" else seed+index+1
        occluded = "SPACER_SLOT" if family == "occlusion" and stage == len(stages)-1 else None
        frame = render_board(stages[stage],seed=exposure_seed,variant=variant,occluded=occluded)
        yield index, index*200., frame, stages[stage], occluded
