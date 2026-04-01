from flask import Flask, render_template, Response, jsonify, request, session
import cv2
import numpy as np
import base64
import json
import time
from datetime import datetime
import threading
from drowsiness_detection import detector

app = Flask(__name__)
app.secret_key = 'driver_drowsiness_secret_key_2023'

# Store session data
sessions_data = {}

def generate_frames():
    camera = cv2.VideoCapture(0)
    detector.running = True
    
    while detector.running:
        success, frame = camera.read()
        if not success:
            break
        
        # Detect drowsiness
        drowsy, ear_value = detector.detect_drowsiness(frame)
        
        # Add status overlay to frame
        status_color = (0, 255, 0) if detector.status == "Normal" else (0, 255, 255) if detector.status == "Warning" else (0, 0, 255)
        cv2.putText(frame, f"Status: {detector.status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Eye Status: {detector.eye_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"EAR: {ear_value:.3f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Add alert overlay if drowsy
        if drowsy:
            cv2.putText(frame, "DROWSINESS ALERT!", (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_detection')
def start_detection():
    detector.reset_session()
    return jsonify({'status': 'success', 'message': 'Detection started'})

@app.route('/stop_detection')
def stop_detection():
    detector.running = False
    
    # Save session data
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    metrics = detector.get_metrics()
    
    sessions_data[session_id] = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'duration': metrics['session_duration'],
        'alerts': metrics['total_alerts'],
        'fatigue_level': metrics['status']
    }
    
    return jsonify({'status': 'success', 'message': 'Detection stopped'})

@app.route('/get_metrics')
def get_metrics():
    metrics = detector.get_metrics()
    return jsonify(metrics)

@app.route('/get_sessions')
def get_sessions():
    return jsonify(sessions_data)

@app.route('/get_alarm_status')
def get_alarm_status():
    """Check if alarm should be triggered immediately"""
    return jsonify({
        'alarm_on': detector.alarm_on,
        'status': detector.status,
        'eye_status': detector.eye_status
    })

@app.route('/play_alarm')
def play_alarm():
    # This would trigger alarm sound on frontend
    return jsonify({'status': 'alarm_triggered'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
