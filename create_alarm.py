import numpy as np
import wave
import struct

def create_alarm_sound(filename='alarm.wav', duration=2, sample_rate=44100):
    """Create a simple alarm sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a beeping sound pattern
    frequency1 = 800  # Hz
    frequency2 = 600  # Hz
    
    # Alternating beeps
    beep_pattern = []
    for i in range(0, len(t), int(sample_rate * 0.2)):  # 0.2 second intervals
        if (i // int(sample_rate * 0.2)) % 2 == 0:
            # High pitch beep
            beep = np.sin(2 * np.pi * frequency1 * t[i:i+int(sample_rate * 0.2)])
        else:
            # Low pitch beep
            beep = np.sin(2 * np.pi * frequency2 * t[i:i+int(sample_rate * 0.2)])
        
        # Apply envelope to avoid clicks
        envelope = np.exp(-3 * np.linspace(0, 1, len(beep)))
        beep = beep * envelope
        
        beep_pattern.extend(beep)
    
    # Convert to 16-bit PCM
    beep_pattern = np.array(beep_pattern, dtype=np.float32)
    beep_pattern = np.int16(beep_pattern * 32767)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(beep_pattern.tobytes())
    
    print(f"Alarm sound created: {filename}")

if __name__ == "__main__":
    create_alarm_sound()
