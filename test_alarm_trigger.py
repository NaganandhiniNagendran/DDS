#!/usr/bin/env python3
"""
Force trigger alarm for testing
"""

from drowsiness_detection_simple import detector
import time

print("=== Force Triggering Alarm ===")

# Reset detector
detector.reset_session()

print(f"Initial state:")
print(f"  Alarm on: {detector.alarm_on}")
print(f"  Status: {detector.status}")
print(f"  Counter: {detector.counter}")

# Force trigger alarm
print("\nForce triggering alarm...")
detector.alarm_on = True
detector.status = "Critical"
detector.eye_status = "Closed"
detector.total_alerts += 1

print(f"After trigger:")
print(f"  Alarm on: {detector.alarm_on}")
print(f"  Status: {detector.status}")
print(f"  Eye status: {detector.eye_status}")
print(f"  Total alerts: {detector.total_alerts}")

print("\nNow run the app and check:")
print("1. Browser console for alarm messages")
print("2. Audio should play")
print("3. Visual alerts should appear")
