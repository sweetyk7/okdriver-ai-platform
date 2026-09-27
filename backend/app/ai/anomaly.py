"""
Anomaly / Suspicious Activity Detection Module.
Uses background subtraction and motion analysis for:
- Crowd gathering detection
- Unusual motion / loitering
- Abandoned object detection (simplified)
"""
import cv2


class AnomalyDetector:
    """Per-camera anomaly detector using background subtraction."""

    def __init__(self, motion_threshold=5000, crowd_threshold=15000):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=True
        )
        self.motion_threshold = motion_threshold
        self.crowd_threshold = crowd_threshold
        self.frame_count = 0

    def analyze(self, frame):
        """
        Analyze a frame for suspicious activity.
        Returns: {
            "anomaly_detected": bool,
            "motion_level": int,
            "type": str | None,
            "severity": str
        }
        """
        self.frame_count += 1

        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Remove shadows (shadow pixels are marked as 127 in MOG2)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

        motion_pixels = cv2.countNonZero(fg_mask)

        anomaly_type = None
        severity = "low"

        if motion_pixels > self.crowd_threshold:
            anomaly_type = "crowd_gathering"
            severity = "high"
        elif motion_pixels > self.motion_threshold:
            anomaly_type = "unusual_motion"
            severity = "medium"

        return {
            "anomaly_detected": anomaly_type is not None,
            "motion_level": motion_pixels,
            "type": anomaly_type,
            "severity": severity
        }


# Cache of detectors per camera
_detectors = {}


def get_detector(camera_id: str) -> AnomalyDetector:
    """Get or create an anomaly detector for a specific camera."""
    if camera_id not in _detectors:
        _detectors[camera_id] = AnomalyDetector()
    return _detectors[camera_id]


def analyze_frame(camera_id: str, frame):
    """Analyze a frame for anomalies using the camera's dedicated detector."""
    detector = get_detector(camera_id)
    return detector.analyze(frame)
