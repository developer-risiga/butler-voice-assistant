import os
import time
import logging
import numpy as np
import sounddevice as sd
from config.settings import CONFIG

try:
    import pvporcupine
except ImportError:
    logging.error("pvporcupine not installed")

class WakeWordDetector:
    def __init__(self):
        self.porcupine = None
        self.setup_wake_word()
        
    def setup_wake_word(self):
        """Initialize Porcupine wake-word detection"""
        try:
            self.porcupine = pvporcupine.create(
                access_key=CONFIG["picovoice_key"],
                keyword_paths=[CONFIG["ppn_path"]]
            )
            logging.info("Wake-word detector initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize wake-word detector: {e}")
            raise
    
    def listen_and_record(self, seconds):
        """Listen for wake word and record audio"""
        sr = self.porcupine.sample_rate
        frame_len = self.porcupine.frame_length
        total_samples = int(sr * seconds)
        
        stream_args = {
            'samplerate': sr,
            'channels': 1,
            'dtype': 'int16',
            'blocksize': frame_len,
        }
        
        if CONFIG["mic_index"] >= 0:
            stream_args['device'] = CONFIG["mic_index"]
        
        try:
            with sd.RawInputStream(**stream_args) as stream:
                logging.info("Listening for wake-word... (Press Ctrl+C to stop)")
                
                while True:
                    data, overflowed = stream.read(frame_len)
                    if overflowed:
                        logging.warning("Audio input overflow")
                    
                    frame = np.frombuffer(data, dtype=np.int16)
                    result = self.porcupine.process(frame)
                    
                    if result >= 0:
                        logging.info(f"Wake-word detected! Recording {seconds} seconds...")
                        return self._record_audio(stream, frame, total_samples, sr)
                        
        except Exception as e:
            logging.error(f"Error in wake-word detection: {e}")
            raise
    
    def _record_audio(self, stream, first_frame, total_samples, sample_rate):
        """Record audio after wake-word detection"""
        chunks = [first_frame]
        collected = first_frame.shape[0]
        
        start_time = time.time()
        
        while collected < total_samples:
            data, overflowed = stream.read(self.porcupine.frame_length)
            frame = np.frombuffer(data, dtype=np.int16)
            chunks.append(frame)
            collected += frame.shape[0]
            
            if time.time() - start_time > CONFIG["record_seconds"] + 2:
                logging.warning("Recording timeout reached")
                break
        
        audio = np.concatenate(chunks).astype(np.int16)
        filename = f"recording_{int(time.time())}.wav"
        self._save_wav(filename, audio, sample_rate)
        
        return filename
    
    def _save_wav(self, filename, audio, sample_rate):
        """Save audio to WAV file"""
        import wave
        
        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(audio.tobytes())
        
        logging.info(f"Saved recording: {filename} ({len(audio)/sample_rate:.1f}s)")
    
    def cleanup(self):
        """Clean up Porcupine resources"""
        if self.porcupine:
            self.porcupine.delete()
            logging.info("Wake-word detector cleaned up")

wake_detector = WakeWordDetector()
