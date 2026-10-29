"""Loopback-only STEPLOCK application; implementation grows through tested milestones."""
from fastapi import FastAPI

app = FastAPI(title="STEPLOCK", version="0.1.0")


@app.get("/api/health")
def health():
    import cv2
    return {"status": "ok", "cv_version": cv2.__version__,
            "aruco_available": hasattr(cv2.aruco, "ArucoDetector"),
            "camera_active": False, "advisory_only": True}
