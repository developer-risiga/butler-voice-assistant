import asyncio
import time
import hashlib
import json
from typing import Any, Dict

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    timestamp = str(time.time_ns())
    unique_str = prefix + timestamp
    return hashlib.md5(unique_str.encode()).hexdigest()[:8]

def sanitize_text(text: str) -> str:
    """Sanitize text for processing"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = text.strip()
    
    return text

def format_phone_number(phone: str) -> str:
    """Format phone number for display"""
    if not phone:
        return ""
    
    # Remove non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 10:
        return f"+91-{digits}"
    elif len(digits) == 12 and digits.startswith('91'):
        return f"+{digits[:2]}-{digits[2:]}"
    else:
        return phone

async def async_retry(operation, max_retries: int = 3, delay: float = 1.0):
    """Retry an async operation with exponential backoff"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                await asyncio.sleep(wait_time)
    
    raise last_exception

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def calculate_confidence(text: str, intent: str) -> float:
    """Calculate confidence score for intent detection"""
    # Simple confidence calculation based on keyword matching
    intent_keywords = {
        "find_service": ["find", "search", "need", "want", "look for", "get"],
        "book_service": ["book", "schedule", "appointment", "reserve"],
        "greet": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "cancel": ["cancel", "stop", "never mind"],
        "thanks": ["thank", "thanks", "appreciate"]
    }
    
    text_lower = text.lower()
    keywords = intent_keywords.get(intent, [])
    
    if not keywords:
        return 0.5  # Default confidence
    
    matches = sum(1 for keyword in keywords if keyword in text_lower)
    return min(1.0, matches * 0.3)  # Scale confidence