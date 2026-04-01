from flask import Flask, render_template, Response, jsonify, request, session
import cv2
import numpy as np
import base64
import json
import time
from datetime import datetime
import threading
from drowsiness_detection_simple import detector
from database import db

app = Flask(__name__)
app.secret_key = 'driver_drowsiness_secret_key_2023'

# Store session data
sessions_data = {}
camera = None
camera_lock = threading.Lock()
current_user = None

def generate_frames():
    global camera
    
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
    
    detector.running = True
    
    while detector.running:
        with camera_lock:
            if camera is None or not camera.isOpened():
                camera = cv2.VideoCapture(0)
            
            success, frame = camera.read()
        
        if not success:
            break
        
        # Detect drowsiness
        drowsy, face_count = detector.detect_drowsiness(frame)
        
        # Add status overlay to frame
        status_color = (0, 255, 0) if detector.status == "Normal" else (0, 255, 255) if detector.status == "Warning" else (0, 0, 255)
        cv2.putText(frame, f"Status: {detector.status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Eye Status: {detector.eye_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Faces: {face_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Counter: {detector.counter}/{detector.EYE_CLOSED_THRESHOLD}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        
        # Add alert overlay if drowsy
        if drowsy:
            cv2.putText(frame, "DROWSINESS ALERT!", (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/dashboard')
def dashboard():
    # Get user data
    user_data = db.get_current_user()
    dashboard_stats = db.get_dashboard_stats(user_data['id'] if user_data else None)
    return render_template('dashboard.html', user=dashboard_stats['user'])

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

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
    
    # Force camera cleanup
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
    
    # Save session data
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    metrics = detector.get_metrics()
    
    # Get current user
    user = db.get_current_user()
    
    session_data = {
        'session_id': session_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'duration': metrics['session_duration'],
        'alerts': metrics['total_alerts'],
        'fatigue_level': metrics['status'],
        'metrics': metrics
    }
    
    # Save to database
    if user:
        db.save_session(user['id'], session_data)
        db.update_user_stats(user['id'], metrics['session_duration'], metrics['total_alerts'])
    
    # Keep backward compatibility
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
    # Get sessions from database
    user = db.get_current_user()
    sessions = db.get_sessions(user['id'] if user else None)
    
    # Convert to expected format
    sessions_dict = {}
    for session in sessions:
        sessions_dict[session['session_id']] = {
            'date': session['date'],
            'time': session['time'],
            'duration': session['duration'],
            'alerts': session['alerts'],
            'fatigue_level': session['fatigue_level']
        }
    
    return jsonify(sessions_dict)

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

@app.route('/test_alarm')
def test_alarm():
    """Test endpoint to manually trigger alarm"""
    detector.alarm_on = True
    detector.status = "Critical"
    detector.eye_status = "Closed"
    return jsonify({
        'status': 'alarm_test_triggered',
        'alarm_on': detector.alarm_on,
        'status': detector.status,
        'eye_status': detector.eye_status
    })

@app.route('/alarm_test')
def alarm_test():
    """Serve the alarm test page"""
    with open('test_alarm_audio.html', 'r') as f:
        return f.read()

@app.route('/get_dashboard_stats')
def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    user = db.get_current_user()
    stats = db.get_dashboard_stats(user['id'] if user else None)
    return jsonify(stats)

@app.route('/get_chart_data')
def get_chart_data():
    """Get data for charts"""
    days = request.args.get('days', 7, type=int)
    user = db.get_current_user()
    chart_data = db.get_chart_data(user['id'] if user else None, days)
    return jsonify(chart_data)

@app.route('/get_user_profile')
def get_user_profile():
    """Get current user profile"""
    user = db.get_current_user()
    return jsonify(user)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update system settings"""
    data = request.get_json()
    for key, value in data.items():
        db.update_setting(key, str(value))
    return jsonify({'status': 'success', 'message': 'Settings updated'})

@app.route('/get_settings')
def get_settings():
    """Get system settings"""
    settings = {
        'eye_closed_threshold': db.get_setting('eye_closed_threshold', '3'),
        'face_detection_confidence': db.get_setting('face_detection_confidence', '0.7'),
        'alarm_volume': db.get_setting('alarm_volume', '0.8'),
        'auto_session_timeout': db.get_setting('auto_session_timeout', '3600'),
        'data_retention_days': db.get_setting('data_retention_days', '90')
    }
    return jsonify(settings)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
