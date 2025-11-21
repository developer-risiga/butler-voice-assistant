import os
from dotenv import load_dotenv

load_dotenv()

# Voice Pipeline Configuration
CONFIG = {
    # TTS Settings
    "tts_primary": "openai",
    "tts_fallbacks": ["system"],
    "stt_primary": "openai", 
    "stt_fallbacks": ["system"],
    "max_retries": 3,
    "timeout": 10,
    
    # Audio Settings
    "sample_rate": 16000,
    "channels": 1,
    "frames_per_buffer": 512,
    "record_seconds": 4,
    
    # Performance
    "target_latency": 3.0,
    "enable_monitoring": True,
    
    # API Keys
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "picovoice_key": os.getenv("PICOVOICE_ACCESS_KEY"),
    "ppn_path": os.getenv("PPN_PATH"),
    "mic_index": int(os.getenv("MIC_DEVICE_INDEX", "-1"))
}

# Demo Settings for reliability
DEMO_MODE = True
DEMO_RESPONSES = {
    "greeting": "Hello! I'm Butler, your voice assistant. How can I help you today?",
    "help": "I can help you find local services like electricians, plumbers, or restaurants.",
    "fallback": "I'm here to assist you. What service are you looking for?"
}
