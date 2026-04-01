import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import threading
import time
import base64

class DrowsinessDetector:
    def __init__(self):
        # Initialize face detector and landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        # Eye aspect ratio threshold
        self.EAR_THRESHOLD = 0.25
        self.EAR_CONSEC_FRAMES = 3
        
        # Counter for consecutive frames with eyes closed
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
        
    def eye_aspect_ratio(self, eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        
        # Compute the euclidean distance between the horizontal eye landmark
        C = dist.euclidean(eye[0], eye[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def get_facial_landmarks(self, gray, rect):
        shape = self.predictor(gray, rect)
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        return landmarks
    
    def detect_drowsiness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)
        
        drowsy = False
        ear_value = 0
        
        for rect in rects:
            landmarks = self.get_facial_landmarks(gray, rect)
            
            # Extract left and right eye coordinates
            left_eye = landmarks[42:48]
            right_eye = landmarks[36:42]
            
            # Calculate EAR for both eyes
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            ear_value = (left_ear + right_ear) / 2.0
            
            # Check if EAR is below threshold
            if ear_value < self.EAR_THRESHOLD:
                self.counter += 1
                self.eye_status = "Closed"
                
                if self.counter >= self.EAR_CONSEC_FRAMES:
                    drowsy = True
                    self.status = "Critical"
                    if not self.alarm_on:
                        self.alarm_on = True
                        self.total_alerts += 1
                        self.fatigue_events.append({
                            'timestamp': time.time(),
                            'type': 'drowsy',
                            'duration': self.EAR_CONSEC_FRAMES
                        })
            else:
                self.counter = 0
                self.eye_status = "Open"
                self.alarm_on = False
                if self.status == "Critical":
                    self.status = "Warning"
                else:
                    self.status = "Normal"
        
        return drowsy, ear_value
    
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
detector = DrowsinessDetector()
