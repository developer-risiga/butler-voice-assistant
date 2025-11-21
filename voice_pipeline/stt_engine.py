import os
import time
import logging
import speech_recognition as sr
from openai import OpenAI
from config.settings import CONFIG

class STTEngine:
    def __init__(self):
        self.openai_client = OpenAI(api_key=CONFIG["openai_api_key"])
        self.speech_recognizer = sr.Recognizer()
        
    def transcribe(self, audio_path, provider=None):
        """Main STT method with automatic fallback"""
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return ""
            
        providers = [provider] if provider else CONFIG["stt_fallbacks"]
        providers.insert(0, CONFIG["stt_primary"])
        providers = list(dict.fromkeys(providers))
        
        logging.info(f"STT providers chain: {providers}")
        
        for stt_provider in providers:
            try:
                logging.info(f"STT attempt with {stt_provider}")
                start_time = time.time()
                
                if stt_provider == "openai":
                    text = self._openai_transcribe(audio_path)
                elif stt_provider == "system":
                    text = self._system_transcribe(audio_path)
                else:
                    continue
                    
                if text and text.strip():
                    latency = time.time() - start_time
                    logging.info(f"STT successful with {stt_provider}, latency: {latency:.2f}s")
                    logging.info(f"Transcribed: '{text}'")
                    return text.strip()
                    
            except Exception as e:
                logging.warning(f"STT failed with {stt_provider}: {str(e)}")
                continue
                
        logging.error("All STT providers failed")
        return ""
        
    def _openai_transcribe(self, audio_path):
        """OpenAI Whisper transcription"""
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en",
                    temperature=0.0
                )
            return transcription.text
            
        except Exception as e:
            logging.error(f"OpenAI transcription error: {str(e)}")
            raise
            
    def _system_transcribe(self, audio_path):
        """System-level STT using speech_recognition"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.speech_recognizer.record(source)
                text = self.speech_recognizer.recognize_google(audio)
                return text
                
        except sr.UnknownValueError:
            logging.warning("System STT could not understand audio")
            return ""
        except sr.RequestError as e:
            logging.error(f"System STT request error: {e}")
            raise
        except Exception as e:
            logging.error(f"System STT error: {str(e)}")
            raise

stt_engine = STTEngine()

def transcribe(audio_path):
    return stt_engine.transcribe(audio_path)
