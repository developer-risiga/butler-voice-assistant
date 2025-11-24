#!/usr/bin/env python3
"""
Butler Voice Assistant - Main Entry Point
Beta Version 1.0
"""
import asyncio
import signal
import sys
import logging
from datetime import datetime

from config.config import Config
from utils.logger import setup_logging
from voice.voice_engine import VoiceEngine
from nlu.nlu_engine import NLUEngine
from services.service_manager import ServiceManager
from conversation.conversation_manager import ConversationManager
from hardware.hardware_manager import HardwareManager
from database.db_manager import DatabaseManager

class ButlerAssistant:
    """Main Butler Voice Assistant class"""
    
    def __init__(self):
        self.config = Config()
        self.is_running = False
        self.components = {}
        
    async def initialize(self):
        """Initialize all components"""
        setup_logging()
        self.logger = logging.getLogger("butler")
        
        self.logger.info("🚀 Initializing Butler Voice Assistant...")
        self.logger.info(f"Version: {self.config.VERSION}")
        
        try:
            # Validate configuration
            if not self.config.validate():
                self.logger.error("Configuration validation failed!")
                return False
            
            # Initialize components in order
            self.components['database'] = DatabaseManager()
            if not await self.components['database'].initialize():
                self.logger.warning("Database initialization failed, continuing without database")
            
            self.components['hardware'] = HardwareManager()
            await self.components['hardware'].initialize()
            
            self.components['voice'] = VoiceEngine()
            if not await self.components['voice'].initialize():
                self.logger.error("Voice engine initialization failed!")
                return False
            
            self.components['nlu'] = NLUEngine()
            if not await self.components['nlu'].initialize():
                self.logger.error("NLU engine initialization failed!")
                return False
            
            self.components['services'] = ServiceManager()
            if not await self.components['services'].initialize():
                self.logger.error("Service manager initialization failed!")
                return False
            
            self.components['conversation'] = ConversationManager()
            if not await self.components['conversation'].initialize():
                self.logger.error("Conversation manager initialization failed!")
                return False
            
            # Signal that Butler is ready
            await self.components['hardware'].set_ready_status()
            
            self.logger.info("✅ Butler initialization complete!")
            self.logger.info("🎯 Butler is ready! Say 'Hey Butler' or press the button to start.")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def start(self):
        """Start the main listening loop"""
        self.is_running = True
        self.logger.info("👂 Butler is now listening...")
        
        # Main loop
        while self.is_running:
            try:
                # Check for wake word or button press
                wake_detected = await self.components['voice'].detect_wake_word()
                button_pressed = await self.components['hardware'].check_button()
                
                if wake_detected or button_pressed:
                    await self.handle_voice_interaction()
                    
                await asyncio.sleep(0.1)  # Prevent CPU overload
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
    
    async def handle_voice_interaction(self):
        """Handle a single voice interaction"""
        try:
            # Visual feedback - show we're listening
            await self.components['hardware'].set_listening_status(True)
            
            # Play activation sound
            await self.components['voice'].play_activation_sound()
            
            # Process voice command
            response = await self.process_voice_command()
            
            # Speak response
            if response:
                await self.components['voice'].text_to_speech(response)
            
        except Exception as e:
            self.logger.error(f"Error in voice interaction: {e}")
            error_msg = "I encountered an error. Please try again."
            await self.components['voice'].text_to_speech(error_msg)
        finally:
            # Reset hardware status
            await self.components['hardware'].set_listening_status(False)
    
    async def process_voice_command(self) -> str:
        """Process a voice command end-to-end"""
        # Record audio
        audio_data = await self.components['voice'].record_audio()
        if not audio_data:
            return "I didn't hear anything. Please try again."
        
        # Convert speech to text
        user_text = await self.components['voice'].speech_to_text(audio_data)
        if not user_text:
            return "I couldn't understand that. Could you please repeat?"
        
        self.logger.info(f"🗣️ User: {user_text}")
        
        # Understand intent
        nlu_result = await self.components['nlu'].parse(user_text)
        self.logger.info(f"🧠 NLU: {nlu_result}")
        
        # Execute based on intent
        if nlu_result.intent == "find_service":
            return await self.handle_service_discovery(nlu_result)
        elif nlu_result.intent == "book_service":
            return await self.handle_booking(nlu_result)
        elif nlu_result.intent == "greet":
            return "Hello! I'm Butler. I can help you find and book local services like plumbers, electricians, and more."
        elif nlu_result.intent == "cancel":
            await self.components['conversation'].clear_context()
            return "Okay, cancelling the current operation."
        elif nlu_result.intent == "thanks":
            return "You're welcome! Is there anything else I can help you with?"
        else:
            return "I can help you find local service providers. Try saying 'Find me plumbers nearby' or 'I need an electrician'."
    
    async def handle_service_discovery(self, nlu_result) -> str:
        """Handle service discovery requests"""
        service_type = nlu_result.entities.get('service_type', 'plumber')
        location = nlu_result.entities.get('location', 'current')
        
        self.logger.info(f"🔍 Finding {service_type} services in {location}")
        
        result = await self.components['services'].find_services(
            service_type=service_type,
            location=location
        )
        
        # Update conversation context
        await self.components['conversation'].update_context(
            user_input=nlu_result.text,
            system_response=result['response_text'],
            data=result
        )
        
        return result['response_text']
    
    async def handle_booking(self, nlu_result) -> str:
        """Handle service booking requests"""
        context = await self.components['conversation'].get_context()
        
        if not context or 'current_services' not in context:
            return "Please search for services first. Say 'Find me plumbers nearby'."
        
        vendor_index = nlu_result.entities.get('vendor_index', 0)
        result = await self.components['services'].book_service(
            vendor_index=vendor_index,
            context=context
        )
        
        return result['response_text']
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Shutting down Butler...")
        self.is_running = False
        
        # Shutdown components in reverse order
        for name, component in reversed(self.components.items()):
            if hasattr(component, 'shutdown'):
                try:
                    await component.shutdown()
                    self.logger.info(f"✅ {name} shut down")
                except Exception as e:
                    self.logger.error(f"❌ Error shutting down {name}: {e}")
        
        self.logger.info("Butler shutdown complete")

def signal_handler(butler, sig, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down Butler...")
    asyncio.create_task(butler.shutdown())

async def main():
    """Main entry point"""
    butler = ButlerAssistant()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(butler, s, f))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(butler, s, f))
    
    try:
        # Initialize Butler
        success = await butler.initialize()
        if not success:
            print("❌ Failed to initialize Butler. Check logs for details.")
            return 1
        
        # Start main loop
        await butler.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        logging.getLogger("butler").error(f"💥 Butler crashed: {e}")
        return 1
    finally:
        await butler.shutdown()
    
    return 0

if __name__ == "__main__":
    print("🎯 Starting Butler Voice Assistant...")
    print("Press Ctrl+C to stop\n")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)