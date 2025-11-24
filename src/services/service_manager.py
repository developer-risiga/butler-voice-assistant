import asyncio
import logging
import json
import time
from typing import List, Dict, Any
from config.config import Config
from config.constants import SERVICE_TYPES, RESPONSE_TEMPLATES
from .justdial_client import JustdialClient
from .booking_engine import BookingEngine

class ServiceManager:
    """Manager for service discovery and booking"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.services")
        self.justdial_client = JustdialClient()
        self.booking_engine = BookingEngine()
        self.service_cache = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize service manager"""
        self.logger.info("Initializing service manager...")
        
        try:
            await self.justdial_client.initialize()
            await self.booking_engine.initialize()
            self.is_initialized = True
            self.logger.info("✅ Service manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Service manager initialization failed: {e}")
            return False
    
    async def find_services(self, service_type: str, location: str = None) -> Dict[str, Any]:
        """Find services of specified type in location"""
        if not location or location == "current":
            location = self.config.DEFAULT_LOCATION
        
        self.logger.info(f"Finding {service_type} services in {location}")
        
        # Check cache first
        cache_key = f"{service_type}_{location}"
        if cache_key in self.service_cache:
            cached_data = self.service_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.config.CACHE_DURATION * 60:
                self.logger.info("Using cached service data")
                return cached_data['data']
        
        try:
            # Fetch from Justdial API
            vendors = await self.justdial_client.search_services(service_type, location)
            
            if not vendors:
                vendors = self._get_mock_vendors(service_type, location)
            
            # Rank vendors
            ranked_vendors = self._rank_vendors(vendors)
            
            # Format response
            response_data = self._format_service_response(ranked_vendors, service_type, location)
            
            # Cache the result
            self.service_cache[cache_key] = {
                'timestamp': time.time(),
                'data': response_data
            }
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error finding services: {e}")
            # Return mock data as fallback
            mock_vendors = self._get_mock_vendors(service_type, location)
            return self._format_service_response(mock_vendors, service_type, location)
    
    async def book_service(self, vendor_index: int, context: Dict = None) -> Dict[str, Any]:
        """Book a service with the specified vendor"""
        self.logger.info(f"Booking service with vendor index: {vendor_index}")
        
        try:
            if not context or 'current_services' not in context:
                return {
                    'success': False,
                    'response_text': "Please search for services first before booking."
                }
            
            vendors = context['current_services']
            
            if vendor_index >= len(vendors):
                return {
                    'success': False,
                    'response_text': f"Please select a vendor between 1 and {len(vendors)}"
                }
            
            vendor = vendors[vendor_index]
            booking_result = await self.booking_engine.book_vendor(vendor, context)
            
            return booking_result
            
        except Exception as e:
            self.logger.error(f"Booking error: {e}")
            return {
                'success': False,
                'response_text': "Sorry, I encountered an error while booking. Please try again."
            }
    
    def _rank_vendors(self, vendors: List[Dict]) -> List[Dict]:
        """Rank vendors by rating and other factors"""
        if not vendors:
            return []
        
        # Simple ranking by rating (descending)
        return sorted(vendors, key=lambda x: x.get('rating', 0), reverse=True)
    
    def _format_service_response(self, vendors: List[Dict], service_type: str, location: str) -> Dict[str, Any]:
        """Format vendor list into response data"""
        if not vendors:
            service_name = SERVICE_TYPES.get(service_type, service_type)
            return {
                'success': False,
                'vendors': [],
                'response_text': RESPONSE_TEMPLATES['no_services'].format(service_type=service_name),
                'service_type': service_type,
                'location': location
            }
        
        # Limit number of vendors shown
        vendors_to_show = vendors[:self.config.MAX_VENDORS_TO_SHOW]
        service_name = SERVICE_TYPES.get(service_type, service_type)
        
        # Build response text
        response_parts = [
            RESPONSE_TEMPLATES['services_found'].format(
                count=len(vendors_to_show), 
                service_type=service_name
            )
        ]
        
        for i, vendor in enumerate(vendors_to_show, 1):
            rating = vendor.get('rating', 'No rating')
            distance = vendor.get('distance', '')
            distance_text = f" - {distance}" if distance else ""
            
            response_parts.append(
                f"{i}. {vendor['name']} - Rating: {rating}★{distance_text}"
            )
        
        response_parts.append("\nYou can say 'Book the first one' or ask for more details.")
        
        return {
            'success': True,
            'vendors': vendors_to_show,
            'response_text': "\n".join(response_parts),
            'service_type': service_type,
            'location': location
        }
    
    def _get_mock_vendors(self, service_type: str, location: str) -> List[Dict]:
        """Get mock vendor data for development"""
        service_name = SERVICE_TYPES.get(service_type, service_type).title()
        
        mock_vendors = [
            {
                'name': f'ABC {service_name} Services',
                'rating': 4.5,
                'phone': '+91-9876543210',
                'address': f'123 Main Street, {location}',
                'services': [f'General {service_name}', 'Emergency Services'],
                'distance': '1.2 km',
                'experience': '5 years'
            },
            {
                'name': f'QuickFix {service_name}',
                'rating': 4.3,
                'phone': '+91-9876543211',
                'address': f'456 Market Road, {location}',
                'services': [f'Residential {service_name}', 'Commercial'],
                'distance': '2.1 km',
                'experience': '3 years'
            },
            {
                'name': f'Pro {service_name} Experts',
                'rating': 4.7,
                'phone': '+91-9876543212',
                'address': f'789 Business Park, {location}',
                'services': [f'Expert {service_name}', '24/7 Service'],
                'distance': '3.5 km',
                'experience': '8 years'
            },
            {
                'name': f'Reliable {service_name} Solutions',
                'rating': 4.2,
                'phone': '+91-9876543213',
                'address': f'321 Service Lane, {location}',
                'services': [f'All {service_name} Needs', 'Maintenance'],
                'distance': '1.8 km',
                'experience': '6 years'
            },
            {
                'name': f'Premium {service_name} Care',
                'rating': 4.6,
                'phone': '+91-9876543214',
                'address': f'654 Quality Road, {location}',
                'services': [f'Premium {service_name}', 'Guaranteed Service'],
                'distance': '2.5 km',
                'experience': '7 years'
            }
        ]
        
        return mock_vendors
    
    async def shutdown(self):
        """Cleanup resources"""
        await self.justdial_client.shutdown()
        await self.booking_engine.shutdown()
        self.logger.info("Service manager shut down")