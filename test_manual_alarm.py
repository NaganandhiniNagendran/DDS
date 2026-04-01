#!/usr/bin/env python3
"""
Manually trigger alarm for testing
"""

from drowsiness_detection_simple import detector
import time

print("=== Manual Alarm Test ===")

# Force trigger alarm
detector.alarm_on = True
detector.status = "Critical"
detector.eye_status = "Closed"

print("Alarm has been manually triggered!")
print(f"Alarm on: {detector.alarm_on}")
print(f"Status: {detector.status}")
print(f"Eye status: {detector.eye_status}")

print("\nNow:")
print("1. Go to http://localhost:5000/detection")
print("2. Click 'Start Detection'")
print("3. Check browser console for alarm messages")
print("4. Listen for alarm sound")
print("5. Look for visual alerts")

print("\nThe alarm should trigger immediately since alarm_on is now True")
