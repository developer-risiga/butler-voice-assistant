import asyncio
import logging
from config.config import Config

class HardwareManager:
    """Hardware management for Raspberry Pi"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.hardware")
        self.led_controller = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize hardware components"""
        self.logger.info("Initializing hardware manager...")
        
        try:
            # Try to initialize GPIO (only works on Raspberry Pi)
            await self._initialize_gpio()
            
            self.is_initialized = True
            self.logger.info("✅ Hardware manager initialized")
            return True
            
        except Exception as e:
            self.logger.warning(f"Hardware initialization failed (normal on non-RPi systems): {e}")
            # Continue without hardware features
            self.is_initialized = True
            return True
    
    async def _initialize_gpio(self):
        """Initialize GPIO pins"""
        try:
            import RPi.GPIO as GPIO
            
            # Use Broadcom pin numbering
            GPIO.setmode(GPIO.BCM)
            
            # Setup LED pin
            GPIO.setup(self.config.LED_PIN, GPIO.OUT)
            
            # Setup button pin
            GPIO.setup(self.config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            self.logger.info("GPIO initialized successfully")
            
        except ImportError:
            self.logger.warning("RPi.GPIO not available - running in simulation mode")
        except Exception as e:
            self.logger.warning(f"GPIO initialization failed: {e}")
    
    async def set_ready_status(self):
        """Set hardware to ready status"""
        await self._set_led_pattern("ready")
        self.logger.info("Hardware set to ready status")
    
    async def set_listening_status(self, listening: bool):
        """Set listening status indicator"""
        if listening:
            await self._set_led_pattern("listening")
        else:
            await self._set_led_pattern("ready")
    
    async def _set_led_pattern(self, pattern: str):
        """Set LED pattern"""
        try:
            import RPi.GPIO as GPIO
            
            if pattern == "ready":
                # Slow blink
                GPIO.output(self.config.LED_PIN, GPIO.HIGH)
                await asyncio.sleep(0.5)
                GPIO.output(self.config.LED_PIN, GPIO.LOW)
                
            elif pattern == "listening":
                # Solid on
                GPIO.output(self.config.LED_PIN, GPIO.HIGH)
                
            elif pattern == "processing":
                # Fast blink
                GPIO.output(self.config.LED_PIN, GPIO.HIGH)
                await asyncio.sleep(0.1)
                GPIO.output(self.config.LED_PIN, GPIO.LOW)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            # Ignore errors in simulation mode
            pass
    
    async def check_button(self) -> bool:
        """Check if manual activation button is pressed"""
        try:
            import RPi.GPIO as GPIO
            return GPIO.input(self.config.BUTTON_PIN) == GPIO.LOW
        except Exception:
            return False
    
    async def shutdown(self):
        """Cleanup hardware resources"""
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            self.logger.info("GPIO cleanup completed")
        except Exception:
            pass
        
        self.logger.info("Hardware manager shut down")