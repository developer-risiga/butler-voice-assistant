import logging
from typing import Dict, Any
from config.constants import RESPONSE_TEMPLATES, SERVICE_TYPES

class ResponseBuilder:
    """Builds natural language responses"""
    
    def __init__(self):
        self.logger = logging.getLogger("butler.response")
    
    async def build_response(self, intent: str, entities: Dict, context: Dict) -> str:
        """Build response based on intent and context"""
        
        if intent == "greet":
            return RESPONSE_TEMPLATES['welcome']
        
        elif intent == "find_service":
            service_type = entities.get('service_type', 'plumber')
            service_name = SERVICE_TYPES.get(service_type, service_type)
            return f"Let me find the best {service_name} services for you..."
        
        elif intent == "book_service":
            return "I'll help you book that service..."
        
        elif intent == "thanks":
            return RESPONSE_TEMPLATES['thanks']
        
        elif intent == "cancel":
            return "Okay, cancelling the current operation."
        
        else:
            return RESPONSE_TEMPLATES['not_understood']
    
    def build_service_list_response(self, vendors: list, service_type: str) -> str:
        """Build response for service list"""
        if not vendors:
            service_name = SERVICE_TYPES.get(service_type, service_type)
            return RESPONSE_TEMPLATES['no_services'].format(service_type=service_name)
        
        response_parts = [
            f"I found {len(vendors)} {SERVICE_TYPES.get(service_type, service_type)} services:"
        ]
        
        for i, vendor in enumerate(vendors, 1):
            rating = vendor.get('rating', 'No rating')
            response_parts.append(f"{i}. {vendor['name']} - Rating: {rating}★")
        
        response_parts.append("\nYou can say 'Book the first one' to make a booking.")
        
        return "\n".join(response_parts)
    
    def build_booking_confirmation(self, vendor: Dict, booking_id: str) -> str:
        """Build booking confirmation response"""
        vendor_name = vendor.get('name', 'the vendor')
        
        response = RESPONSE_TEMPLATES['booking_confirmed'].format(vendor_name=vendor_name)
        response += f" Your booking ID is {booking_id}. "
        response += "They will contact you shortly."
        
        return response