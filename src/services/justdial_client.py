import aiohttp
import logging
import json
from typing import List, Dict, Any
from config.config import Config

class JustdialClient:
    """Client for Justdial API integration"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.justdial")
        self.session = None
        self.base_url = "https://apis.justdial.com/api/"
        
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        self.logger.info("Justdial client initialized")
    
    async def search_services(self, service_type: str, location: str) -> List[Dict[str, Any]]:
        """Search for services using Justdial API"""
        if not self.config.JUSTDIAL_API_KEY:
            self.logger.warning("No Justdial API key configured, using mock data")
            return []
        
        self.logger.info(f"Searching Justdial for {service_type} in {location}")
        
        try:
            params = {
                'q': service_type,
                'city': location,
                'api_key': self.config.JUSTDIAL_API_KEY,
                'format': 'json',
                'page': 1,
                'results_per_page': 10
            }
            
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    self.logger.error(f"Justdial API error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Justdial search error: {e}")
            return []
    
    def _parse_response(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Justdial API response"""
        vendors = []
        
        try:
            # Extract vendor information from API response
            # This structure might need adjustment based on actual API response
            results = data.get('results', [])
            
            for item in results[:10]:  # Limit to 10 results
                vendor = {
                    'name': item.get('company_name', 'Unknown Vendor'),
                    'rating': float(item.get('rating', 0)),
                    'phone': item.get('contact_number', ''),
                    'address': item.get('address', ''),
                    'services': item.get('services', []),
                    'distance': item.get('distance', ''),
                    'experience': item.get('experience', ''),
                    'reviews': item.get('reviews_count', 0)
                }
                
                # Clean up data
                if vendor['rating'] == 0:
                    vendor['rating'] = 4.0  # Default rating
                
                vendors.append(vendor)
                
        except Exception as e:
            self.logger.error(f"Error parsing Justdial response: {e}")
        
        return vendors
    
    async def shutdown(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
        self.logger.info("Justdial client shut down")