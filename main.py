import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

from config.settings import CONFIG
from voice_pipeline.tts_engine import speak
from voice_pipeline.stt_engine import transcribe
from voice_pipeline.wake_word import wake_detector
from utils.performance_optimizer import performance_monitor
from utils.connection_manager import connection_manager
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('butler_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

client = OpenAI(api_key=CONFIG["openai_api_key"])

# Simple greeting function since we don't have Butler_greeting.py yet
def generate_greeting(client):
    return "Hello! I'm Butler, your voice assistant. How can I help you today?"

@performance_monitor.measure_latency("llm")
def reply_with_llm(user_input):
    if not user_input or not user_input.strip():
        return "I didn't catch that. Could you please repeat?"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Butler, a helpful voice assistant. Reply in 1-2 short sentences (under 15 words). Be conversational and helpful."
                },
                {"role": "user", "content": user_input}
            ],
            max_tokens=60,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        return answer if answer else "I'm here to help. What do you need?"
        
    except Exception as e:
        logging.error(f"LLM request failed: {e}")
        return "I'm having trouble processing that right now. Please try again."

def main():
    try:
        logging.info("Starting Butler Voice Assistant...")
        
        if not connection_manager.check_services_health():
            logging.warning("Some services are unhealthy, but continuing...")
        
        performance_monitor.print_performance_report()
        
        session_start = time.time()
        request_count = 0
        
        logging.info("Butler is ready and listening...")
        
        while True:
            try:
                request_count += 1
                logging.info(f"--- Request #{request_count} ---")
                
                with performance_monitor.measure_latency("wake_word"):
                    audio_file = wake_detector.listen_and_record(CONFIG["record_seconds"])
                
                try:
                    greeting = generate_greeting(client)
                    logging.info(f"Greeting: {greeting}")
                    speak(greeting)
                    time.sleep(1)
                except Exception as e:
                    logging.error(f"Greeting failed: {e}")
                    speak("Hello! How can I help you?")
                
                with performance_monitor.measure_latency("stt"):
                    user_text = transcribe(audio_file)
                
                if user_text and user_text.strip():
                    logging.info(f"User said: '{user_text}'")
                    
                    with performance_monitor.measure_latency("llm"):
                        response_text = reply_with_llm(user_text)
                    
                    with performance_monitor.measure_latency("tts"):
                        speak(response_text)
                    
                    if request_count % 3 == 0:
                        performance_monitor.print_performance_report()
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                logging.info("Shutting down by user request...")
                break
            except Exception as e:
                logging.error(f"Unexpected error in main loop: {e}")
                time.sleep(2)
                
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        if wake_detector:
            wake_detector.cleanup()
        
        session_duration = time.time() - session_start
        logging.info(f"Session summary: {request_count} requests in {session_duration:.1f}s")
        performance_monitor.print_performance_report()
        logging.info("Butler shutdown complete")

if __name__ == "__main__":
    main()
