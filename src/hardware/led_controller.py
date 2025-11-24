import asyncio
import logging

class LEDController:
    """Controller for LED status indicators"""
    
    def __init__(self, pin: int):
        self.pin = pin
        self.logger = logging.getLogger("butler.led")
        self.is_active = False
        
    async def start_blink(self, interval: float = 0.5):
        """Start blinking LED"""
        self.is_active = True
        while self.is_active:
            await self._set_led(True)
            await asyncio.sleep(interval)
            await self._set_led(False)
            await asyncio.sleep(interval)
    
    async def stop_blink(self):
        """Stop blinking LED"""
        self.is_active = False
        await self._set_led(False)
    
    async def _set_led(self, state: bool):
        """Set LED state"""
        try:
            import RPi.GPIO as GPIO
            GPIO.output(self.pin, GPIO.HIGH if state else GPIO.LOW)
        except Exception:
            # Simulation mode - just log
            if state:
                self.logger.debug("LED ON")
            else:
                self.logger.debug("LED OFF")