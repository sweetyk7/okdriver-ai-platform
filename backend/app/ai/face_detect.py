"""
Face Detection Module.
Uses OpenCV's DNN-based face detector (Caffe model).
Falls back to Haar cascade if DNN model files are not available.
"""
import cv2
import numpy as np
import os


# Paths for DNN face detector (download these for production)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
PROTOTXT_PATH = os.path.join(MODEL_DIR, "deploy.prototxt")
CAFFEMODEL_PATH = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

# Try loading DNN model, fallback to Haar cascade
_net = None
_use_dnn = False

try:
    if os.path.exists(PROTOTXT_PATH) and os.path.exists(CAFFEMODEL_PATH):
        _net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, CAFFEMODEL_PATH)
        _use_dnn = True
except:
    pass


def detect_faces(frame, min_confidence=0.5):
    """
    Detect faces in a video frame.
    Returns: list of {"bbox": [x, y, w, h], "confidence": float}
    """
    if _use_dnn and _net is not None:
        return _detect_faces_dnn(frame, min_confidence)
    else:
        return _detect_faces_cascade(frame)


def _detect_faces_dnn(frame, min_confidence=0.5):
    """DNN-based face detection (more accurate)."""
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104, 177, 123))
    _net.setInput(blob)
    detections = _net.forward()

    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > min_confidence:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            faces.append({
                "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                "confidence": round(float(confidence), 3)
            })

    return faces


def _detect_faces_cascade(frame):
    """Haar cascade fallback (always available, less accurate)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if cascade.empty():
        return []

    detected = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    faces = []
    for (x, y, w, h) in detected:
        faces.append({
            "bbox": [int(x), int(y), int(w), int(h)],
            "confidence": 0.75  # Cascade doesn't provide confidence
        })

    return faces
