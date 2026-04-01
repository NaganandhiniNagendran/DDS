import cv2
import numpy as np
from scipy.spatial import distance as dist
import threading
import time
import base64

class SimpleDrowsinessDetector:
    def __init__(self):
        # Use OpenCV's built-in face and eye detectors
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Eye aspect ratio threshold (simplified)
        self.EYE_CLOSED_THRESHOLD = 5  # Increased from 3 to reduce false alarms
        self.counter = 0
        self.alarm_on = False
        self.status = "Normal"
        self.eye_status = "Open"
        
        # Metrics
        self.total_alerts = 0
        self.session_start = time.time()
        self.fatigue_events = []
        
        # Thread control
        self.running = False
        self.lock = threading.Lock()
        
    def detect_eyes(self, gray, face_rect):
        """Detect eyes within face region"""
        eyes = self.eye_cascade.detectMultiScale(
            gray[face_rect[1]:face_rect[1]+face_rect[3], 
             face_rect[0]:face_rect[0]+face_rect[2]])
        return eyes
    
    def _is_good_face_quality(self, face_region):
        """Check if face region has good quality for reliable detection"""
        # Check if face region has sufficient contrast and detail
        if face_region.size == 0:
            return False
        
        # Calculate histogram to check contrast
        hist = cv2.calcHist([face_region], [0], None, [256], [0, 256])
        hist_std = np.std(hist)
        
        # Check if there's enough variation (contrast)
        if hist_std < 50:  # Low contrast indicates poor lighting
            return False
        
        # Check brightness (not too dark or too bright)
        mean_brightness = np.mean(face_region)
        if mean_brightness < 40 or mean_brightness > 220:  # Too dark or too bright
            return False
        
        return True
    
    def detect_drowsiness(self, frame):
        """Improved drowsiness detection with better false positive handling"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        drowsy = False
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Detect eyes within face region
            eyes = self.detect_eyes(gray, (x, y, w, h))
            
            # More robust eye detection logic
            if len(eyes) >= 1:
                # Eyes detected (even one eye is enough to consider eyes open)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
                
                self.counter = 0
                self.eye_status = "Open"
                self.alarm_on = False
                if self.status == "Critical":
                    self.status = "Warning"
                else:
                    self.status = "Normal"
            else:
                # No eyes detected - but don't immediately assume closed
                # Only increment counter if we have a good face detection
                if w > 100 and h > 100:  # Reasonable face size check
                    self.counter += 1
                    self.eye_status = "Possibly Closed"
                    
                    # Require more consecutive frames before triggering alarm
                    if self.counter >= self.EYE_CLOSED_THRESHOLD:
                        # Double check with face quality before triggering alarm
                        face_region = gray[y:y+h, x:x+w]
                        if self._is_good_face_quality(face_region):
                            drowsy = True
                            self.status = "Critical"
                            self.eye_status = "Closed"
                            if not self.alarm_on:
                                self.alarm_on = True
                                self.total_alerts += 1
                                self.fatigue_events.append({
                                    'timestamp': time.time(),
                                    'type': 'drowsy',
                                    'duration': self.EYE_CLOSED_THRESHOLD
                                })
                        else:
                            # Poor face quality, reset counter
                            self.counter = 0
                            self.eye_status = "Open"
                else:
                    # Face too small, reset counter
                    self.counter = 0
                    self.eye_status = "Open"
        
        return drowsy, len(faces)
    
    def get_metrics(self):
        current_time = time.time()
        session_duration = int(current_time - self.session_start)
        
        return {
            'total_alerts': self.total_alerts,
            'session_duration': session_duration,
            'status': self.status,
            'eye_status': self.eye_status,
            'fatigue_events': len(self.fatigue_events)
        }
    
    def reset_session(self):
        self.counter = 0
        self.alarm_on = False
        self.status = "Normal"
        self.eye_status = "Open"
        self.total_alerts = 0
        self.session_start = time.time()
        self.fatigue_events = []

# Global detector instance
detector = SimpleDrowsinessDetector()
