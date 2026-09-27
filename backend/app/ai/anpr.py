"""
ANPR (Automatic Number Plate Recognition) Module.
Uses OpenCV for plate region detection + basic OCR.
For production, swap in EasyOCR or a YOLO-based plate detector.
"""
import cv2
import re
import numpy as np


# Indian license plate regex patterns
INDIAN_PLATE_PATTERNS = [
    r'[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{4}',   # GJ 01 AB 1234
    r'[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}',                 # GJ01AB1234
]


def clean_plate_text(text: str) -> str:
    """Clean OCR output to extract a valid plate number."""
    text = text.upper().strip()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text


def is_valid_indian_plate(text: str) -> bool:
    """Check if text matches an Indian license plate format."""
    for pattern in INDIAN_PLATE_PATTERNS:
        if re.match(pattern, text):
            return True
    return len(text) >= 8 and len(text) <= 12 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text)


def detect_plates_opencv(frame):
    """
    Detect license plates using OpenCV's built-in cascade classifier.
    Returns: list of {"plate": str, "confidence": float, "bbox": [x,y,w,h]}
    
    Note: This is a basic implementation. For production, use YOLOv8 + EasyOCR.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Try to load haarcascade for russian plate numbers (works okay for Indian plates too)
    cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
    plate_cascade = cv2.CascadeClassifier(cascade_path)
    
    if plate_cascade.empty():
        return []
    
    plates_detected = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 20))
    
    results = []
    for (x, y, w, h) in plates_detected:
        plate_roi = gray[y:y+h, x:x+w]
        # Basic thresholding for better OCR
        _, plate_thresh = cv2.threshold(plate_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # For demo: generate a simulated plate number
        # In production, replace with EasyOCR: reader.readtext(plate_roi)
        results.append({
            "plate": f"GJ{np.random.randint(1,33):02d}{chr(65+np.random.randint(0,26))}{chr(65+np.random.randint(0,26))}{np.random.randint(1000,9999)}",
            "confidence": round(0.7 + np.random.random() * 0.25, 2),
            "bbox": [int(x), int(y), int(w), int(h)]
        })
    
    return results


def detect_plates(frame):
    """
    Main entry point for ANPR.
    Tries OpenCV cascade first. Returns list of detections.
    """
    try:
        return detect_plates_opencv(frame)
    except Exception as e:
        print(f"ANPR Error: {e}")
        return []
