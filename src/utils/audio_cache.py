import os
import hashlib
import logging
from config.config import Config

class AudioCache:
    """Cache for audio files to avoid re-generating TTS"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.audio_cache")
        self.cache_dir = os.path.join(self.config.CACHE_DIR, "audio")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cache_path(self, text: str) -> str:
        """Get cache file path for text"""
        # Create hash of text for filename
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.mp3")
    
    def exists(self, text: str) -> bool:
        """Check if audio is cached"""
        cache_path = self.get_cache_path(text)
        return os.path.exists(cache_path)
    
    def save(self, text: str, audio_data: bytes):
        """Save audio data to cache"""
        try:
            cache_path = self.get_cache_path(text)
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            self.logger.debug(f"Audio cached: {text[:50]}...")
        except Exception as e:
            self.logger.error(f"Error saving audio cache: {e}")
    
    def load(self, text: str) -> bytes:
        """Load audio data from cache"""
        try:
            cache_path = self.get_cache_path(text)
            with open(cache_path, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error loading audio cache: {e}")
            raise
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old cache files"""
        try:
            current_time = os.path.getctime
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    if file_age > max_age_hours * 3600:
                        os.remove(filepath)
                        self.logger.debug(f"Removed old cache file: {filename}")
        except Exception as e:
            self.logger.error(f"Error cleaning audio cache: {e}")