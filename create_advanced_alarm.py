import numpy as np
import wave
import struct

def create_advanced_alarm(filename='alarm.wav', duration=3, sample_rate=44100):
    """Create an advanced alarm sound with multiple tones"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Multiple frequencies for attention-grabbing sound
    frequencies = [1000, 800, 1200, 600]  # Hz
    
    # Create complex alarm pattern
    alarm_signal = np.zeros_like(t)
    
    # Pattern: rapid beeps getting faster
    beep_duration = 0.15  # seconds
    gap_duration = 0.05   # seconds
    
    current_time = 0
    freq_index = 0
    
    while current_time < duration:
        # Calculate current beep start and end
        start_sample = int(current_time * sample_rate)
        end_sample = min(int((current_time + beep_duration) * sample_rate), len(t))
        
        if start_sample < len(t):
            # Create beep with current frequency
            freq = frequencies[freq_index % len(frequencies)]
            beep_t = t[start_sample:end_sample] - (current_time * sample_rate) / sample_rate
            
            # Add harmonics for richer sound
            beep = (np.sin(2 * np.pi * freq * beep_t) * 0.6 +
                    np.sin(2 * np.pi * freq * 2 * beep_t) * 0.3 +
                    np.sin(2 * np.pi * freq * 3 * beep_t) * 0.1)
            
            # Apply envelope
            envelope = np.ones_like(beep)
            fade_samples = int(0.01 * sample_rate)  # 10ms fade
            if len(beep) > 2 * fade_samples:
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            alarm_signal[start_sample:end_sample] = beep * envelope
        
        # Move to next beep
        current_time += beep_duration + gap_duration
        freq_index += 1
        
        # Make beeps faster as time progresses
        if current_time > duration * 0.6:
            gap_duration = 0.03
        if current_time > duration * 0.8:
            gap_duration = 0.02
    
    # Normalize and convert to 16-bit PCM
    alarm_signal = alarm_signal / np.max(np.abs(alarm_signal)) * 0.8
    alarm_signal = np.array(alarm_signal, dtype=np.float32)
    alarm_signal = np.int16(alarm_signal * 32767)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(alarm_signal.tobytes())
    
    print(f"Advanced alarm sound created: {filename}")

def create_gentle_alert(filename='gentle_alert.wav', duration=1.5, sample_rate=44100):
    """Create a gentle alert sound for warnings"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Gentle ascending tone
    start_freq = 400
    end_freq = 600
    
    # Frequency sweep
    freq_sweep = np.linspace(start_freq, end_freq, len(t))
    signal = np.sin(2 * np.pi * freq_sweep * t)
    
    # Add soft harmonics
    signal += 0.3 * np.sin(2 * np.pi * freq_sweep * 2 * t)
    signal += 0.1 * np.sin(2 * np.pi * freq_sweep * 3 * t)
    
    # Apply smooth envelope
    envelope = np.exp(-2 * t / duration)  # Exponential decay
    signal = signal * envelope
    
    # Normalize and convert
    signal = signal / np.max(np.abs(signal)) * 0.6
    signal = np.array(signal, dtype=np.float32)
    signal = np.int16(signal * 32767)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal.tobytes())
    
    print(f"Gentle alert sound created: {filename}")

if __name__ == "__main__":
    create_advanced_alarm()
    create_gentle_alert()
