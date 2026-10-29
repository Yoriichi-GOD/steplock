import cv2
import numpy as np

ANCHORS = (40, 41, 42, 43)  # TL, TR, BR, BL marker centers; kit defines these correspondences.
UNIT = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])


def calibrate(points, shape):
    points = np.asarray(points, dtype=np.float32)
    if points.shape != (4, 2) or not np.isfinite(points).all():
        raise ValueError("Four finite calibration points are required")
    h, w = shape[:2]
    if np.any(points < 0) or np.any(points[:, 0] >= w) or np.any(points[:, 1] >= h):
        raise ValueError("Calibration points outside image")
    area = cv2.contourArea(points, oriented=True)
    if area < w * h * .08 or not cv2.isContourConvex(points):
        raise ValueError("Degenerate, reversed or very small calibration quadrilateral")
    edges = np.linalg.norm(points - np.roll(points, 1, axis=0), axis=1)
    if edges.min() < 35 or edges.max() / edges.min() > 12:
        raise ValueError("Extreme calibration perspective")
    matrix = cv2.getPerspectiveTransform(points, UNIT)
    if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-12:
        raise ValueError("Singular calibration")
    return matrix


def transform(points, matrix):
    return cv2.perspectiveTransform(np.float32(points).reshape(1, -1, 2), matrix)[0]
