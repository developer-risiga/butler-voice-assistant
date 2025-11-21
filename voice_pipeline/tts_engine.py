import os
import time
import logging
import numpy as np
import sounddevice as sd
from openai import OpenAI
from config.settings import CONFIG

class TTSEngine:
    def __init__(self):
        self.openai_client = OpenAI(api_key=CONFIG["openai_api_key"])
        self.setup_audio()
        
    def setup_audio(self):
        """Initialize audio system"""
        try:
            sd.check_output_settings()
            logging.info("Audio output system ready")
        except Exception as e:
            logging.warning(f"Audio output check failed: {e}")

    def speak(self, text, provider=None):
        """Main TTS method with automatic fallback"""
        if not text or not text.strip():
            logging.warning("Empty text provided to TTS")
            return False
            
        providers = [provider] if provider else CONFIG["tts_fallbacks"]
        providers.insert(0, CONFIG["tts_primary"])
        providers = list(dict.fromkeys(providers))
        
        logging.info(f"TTS providers chain: {providers}")
        
        for tts_provider in providers:
            try:
                logging.info(f"TTS attempt with {tts_provider}: '{text}'")
                
                if tts_provider == "openai":
                    success = self._openai_tts(text)
                elif tts_provider == "system":
                    success = self._system_tts(text)
                else:
                    continue
                    
                if success:
                    logging.info(f"TTS successful with {tts_provider}")
                    return True
                    
            except Exception as e:
                logging.warning(f"TTS failed with {tts_provider}: {str(e)}")
                continue
                
        self._ultimate_fallback(text)
        return False
        
    def _openai_tts(self, text):
        """OpenAI TTS implementation"""
        try:
            start_time = time.time()
            
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                response_format="pcm"
            )
            
            audio_data = response.content
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            sd.play(audio_array, samplerate=24000)
            sd.wait()
            
            latency = time.time() - start_time
            logging.info(f"OpenAI TTS latency: {latency:.2f}s")
            return True
            
        except Exception as e:
            logging.error(f"OpenAI TTS error: {str(e)}")
            raise
            
    def _system_tts(self, text):
        """System-level TTS as fallback"""
        try:
            import platform
            
            if platform.system() == "Windows":
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
            elif platform.system() == "Darwin":
                os.system(f'say "{text}"')
            else:
                os.system(f'espeak "{text}" 2>/dev/null')
                
            logging.info("System TTS completed")
            return True
            
        except Exception as e:
            logging.error(f"System TTS failed: {str(e)}")
            raise
            
    def _ultimate_fallback(self, text):
        """Final fallback when all TTS methods fail"""
        print(f"\n{'='*50}")
        print(f"BUTLER: {text}")
        print(f"{'='*50}\n")
        
        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            try:
                print("\a")
            except:
                pass

tts_engine = TTSEngine()

def speak(text):
    return tts_engine.speak(text)
