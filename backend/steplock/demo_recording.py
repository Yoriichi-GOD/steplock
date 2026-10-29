"""Optional local real-video preset. Dataset bytes stay outside the repository."""
import hashlib
from .config import ROOT

PINNED_ID="physical_recording"
RECORDING_PATH=ROOT/"data/external/impact_v1_1/presentation_excerpt/real_assembly_excerpt.avi"
RECORDING_SHA256="e3494ad487d458923b71e4bb265ff5ab2435f416ceab252cc6aff9cc2a8ea8a6"


def pinned_recording():
    if not RECORDING_PATH.is_file(): return None
    if hashlib.sha256(RECORDING_PATH.read_bytes()).hexdigest()!=RECORDING_SHA256: return None
    return {"id":PINNED_ID,"title":"Real video · IMPACT (untagged)",
            "source_kind":"REPLAY_TAGGED","source_sha256":RECORDING_SHA256,"duration_ms":12000,
            "population":"EXTERNAL_PHYSICAL_UNTAGGED","tagged_fixture":False,
            "dataset":"IMPACT v1.1","source_video_id":"AL07EJ17_Reassembly_A_002_front",
            "attribution":"Wen et al., IMPACT dataset",
            "source_url":"https://github.com/Kratos-Wen/IMPACT",
            "license":"CC BY-NC-SA 4.0","license_url":"https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "derivation":"Source 55s..67s; 60 actual frames at 5Hz, resized to 640x360, MJPEG re-encoding. No generated scene or tags.",
            "notice":"Real untagged footage. STEPLOCK anchors are absent; calibration is required. This clip cannot demonstrate a fixture PASS."}
