#!/usr/bin/env python3
"""
Test script to verify alarm functionality
"""

import numpy as np
import wave
import os

def create_alarm_sound():
    """Create a simple alarm sound file"""
    sample_rate = 44100
    duration = 1.0  # 1 second
    frequency = 800  # 800 Hz
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = np.sin(frequency * t * 2 * np.pi)
    
    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Write to WAV file
    with wave.open('static/alarm.wav', 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print("Created new alarm.wav file")

def test_detection_logic():
    """Test the detection logic with simulated data"""
    from drowsiness_detection_simple import detector
    
    print("Testing detection logic...")
    print(f"Current threshold: {detector.EYE_CLOSED_THRESHOLD}")
    print(f"Current counter: {detector.counter}")
    print(f"Current alarm status: {detector.alarm_on}")
    print(f"Current status: {detector.status}")
    
    # Simulate eye closure
    print("\nSimulating eye closure...")
    for i in range(detector.EYE_CLOSED_THRESHOLD + 1):
        detector.counter += 1
        print(f"Counter: {detector.counter}/{detector.EYE_CLOSED_THRESHOLD}")
        
        if detector.counter >= detector.EYE_CLOSED_THRESHOLD:
            detector.alarm_on = True
            detector.status = "Critical"
            print("ALARM SHOULD TRIGGER!")
            break

if __name__ == "__main__":
    print("=== Alarm System Test ===")
    
    # Create new alarm sound
    create_alarm_sound()
    
    # Test detection logic
    test_detection_logic()
    
    print("\n=== Test Complete ===")
    print("Run the app and check browser console for debug messages")
