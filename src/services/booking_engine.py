import asyncio
import logging
import time
from typing import Dict, Any
from config.config import Config
from config.constants import RESPONSE_TEMPLATES

class BookingEngine:
    """Engine for handling service bookings"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.booking")
        self.bookings = {}  # In-memory storage for demo
        
    async def initialize(self):
        """Initialize booking engine"""
        self.logger.info("Booking engine initialized")
        return True
    
    async def book_vendor(self, vendor: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Book a service with a vendor"""
        self.logger.info(f"Booking vendor: {vendor.get('name', 'Unknown')}")
        
        try:
            # Generate booking ID
            booking_id = f"BK{int(time.time())}"
            
            # Create booking record
            booking = {
                'id': booking_id,
                'vendor_name': vendor.get('name', 'Unknown Vendor'),
                'vendor_phone': vendor.get('phone', ''),
                'service_type': context.get('service_type', 'unknown') if context else 'unknown',
                'timestamp': time.time(),
                'status': 'confirmed'
            }
            
            # Store booking
            self.bookings[booking_id] = booking
            
            # In a real implementation, this would:
            # 1. Call vendor's booking API
            # 2. Send confirmation SMS/email
            # 3. Update database
            
            response_text = RESPONSE_TEMPLATES['booking_confirmed'].format(
                vendor_name=vendor.get('name', 'the vendor')
            )
            
            response_text += f" Your booking ID is {booking_id}. "
            response_text += f"They will contact you at your registered number within 30 minutes."
            
            return {
                'success': True,
                'booking_id': booking_id,
                'vendor_name': vendor.get('name'),
                'response_text': response_text,
                'booking_details': booking
            }
            
        except Exception as e:
            self.logger.error(f"Booking error: {e}")
            return {
                'success': False,
                'response_text': "Sorry, I encountered an error while processing your booking. Please try again."
            }
    
    async def get_booking_status(self, booking_id: str) -> Dict[str, Any]:
        """Get status of a booking"""
        booking = self.bookings.get(booking_id)
        if booking:
            return {
                'success': True,
                'booking': booking
            }
        else:
            return {
                'success': False,
                'error': 'Booking not found'
            }
    
    async def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Booking engine shut down")