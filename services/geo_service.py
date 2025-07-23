import requests
import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import re

class GeoService:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="news_platform")
        
        # Common location patterns for news content
        self.location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # City, State
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2,3})\b',  # City, State Code
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'   # City State
        ]
    
    def get_user_location(self) -> Optional[Dict[str, Any]]:
        """Get user location using IP geolocation"""
        try:
            # Try to get location from IP
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'lat': float(data.get('latitude', 0)),
                    'lon': float(data.get('longitude', 0)),
                    'city': data.get('city', ''),
                    'region': data.get('region', ''),
                    'country': data.get('country_name', ''),
                    'country_code': data.get('country_code', '')
                }
        except Exception as e:
            logging.error(f"Error getting user location: {str(e)}")
        
        # Fallback to default location (New York)
        return {
            'lat': 40.7128,
            'lon': -74.0060,
            'city': 'New York',
            'region': 'New York',
            'country': 'United States',
            'country_code': 'US'
        }
    
    def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """Extract location mentions from text"""
        locations = []
        
        try:
            # Use regex patterns to find potential locations
            for pattern in self.location_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        location_str = ', '.join(match)
                    else:
                        location_str = match
                    
                    # Geocode the location
                    coords = self.geocode_location(location_str)
                    if coords:
                        locations.append({
                            'name': location_str,
                            'lat': coords[0],
                            'lon': coords[1]
                        })
            
            return locations
            
        except Exception as e:
            logging.error(f"Error extracting locations: {str(e)}")
            return []
    
    def geocode_location(self, location_str: str) -> Optional[Tuple[float, float]]:
        """Geocode a location string to coordinates"""
        try:
            location = self.geocoder.geocode(location_str)
            if location:
                return (location.latitude, location.longitude)
            return None
            
        except Exception as e:
            logging.error(f"Error geocoding location {location_str}: {str(e)}")
            return None
    
    def calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations in miles"""
        try:
            point1 = (loc1['lat'], loc1['lon'])
            point2 = (loc2['lat'], loc2['lon'])
            
            distance = geodesic(point1, point2).miles
            return distance
            
        except Exception as e:
            logging.error(f"Error calculating distance: {str(e)}")
            return float('inf')
    
    def is_within_radius(self, article_location: Dict[str, Any], 
                        user_location: Dict[str, Any], radius_miles: float = 100) -> bool:
        """Check if article location is within radius of user location"""
        try:
            if not article_location or not user_location:
                return False
            
            # Check if article has location data
            article_locations = article_location.get('locations', [])
            if not article_locations:
                return False
            
            # Check if any article location is within radius
            for loc in article_locations:
                distance = self.calculate_distance(loc, user_location)
                if distance <= radius_miles:
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking radius: {str(e)}")
            return False
    
    def is_same_region(self, article_location: Dict[str, Any], 
                      user_location: Dict[str, Any]) -> bool:
        """Check if article is from same region (state/province)"""
        try:
            if not article_location or not user_location:
                return False
            
            user_region = user_location.get('region', '').lower()
            if not user_region:
                return False
            
            # Check article locations for same region
            article_locations = article_location.get('locations', [])
            for loc in article_locations:
                # Try to get region for this location
                location_info = self.get_location_info(loc['lat'], loc['lon'])
                if location_info and location_info.get('region', '').lower() == user_region:
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking region: {str(e)}")
            return False
    
    def is_same_country(self, article_location: Dict[str, Any], 
                       user_location: Dict[str, Any]) -> bool:
        """Check if article is from same country"""
        try:
            if not article_location or not user_location:
                return False
            
            user_country = user_location.get('country_code', '').lower()
            if not user_country:
                return False
            
            # Check article locations for same country
            article_locations = article_location.get('locations', [])
            for loc in article_locations:
                # Try to get country for this location
                location_info = self.get_location_info(loc['lat'], loc['lon'])
                if location_info and location_info.get('country_code', '').lower() == user_country:
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking country: {str(e)}")
            return False
    
    def get_location_info(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get location information from coordinates"""
        try:
            location = self.geocoder.reverse(f"{lat}, {lon}")
            if location:
                address = location.raw.get('address', {})
                return {
                    'city': address.get('city', address.get('town', address.get('village', ''))),
                    'region': address.get('state', address.get('province', '')),
                    'country': address.get('country', ''),
                    'country_code': address.get('country_code', '').upper()
                }
            return None
            
        except Exception as e:
            logging.error(f"Error getting location info: {str(e)}")
            return None
    
    def calculate_relevance(self, article_content: str, user_location: Dict[str, Any]) -> float:
        """Calculate geographic relevance score for article"""
        try:
            # Extract locations from article
            article_locations = self.extract_locations(article_content)
            if not article_locations:
                return 0.0
            
            max_relevance = 0.0
            
            for loc in article_locations:
                distance = self.calculate_distance(loc, user_location)
                
                # Calculate relevance based on distance
                if distance <= 50:  # Very local
                    relevance = 1.0
                elif distance <= 100:  # Local
                    relevance = 0.8
                elif distance <= 500:  # Regional
                    relevance = 0.6
                elif distance <= 1000:  # National
                    relevance = 0.4
                else:  # International
                    relevance = 0.2
                
                max_relevance = max(max_relevance, relevance)
            
            return max_relevance
            
        except Exception as e:
            logging.error(f"Error calculating relevance: {str(e)}")
            return 0.0
    
    def get_countries_by_region(self) -> Dict[str, List[str]]:
        """Get countries organized by geographic regions"""
        return {
            'North America': ['United States', 'Canada', 'Mexico'],
            'South America': ['Brazil', 'Argentina', 'Colombia', 'Chile', 'Peru'],
            'Europe': ['United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Russia'],
            'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Thailand'],
            'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Kenya', 'Morocco'],
            'Oceania': ['Australia', 'New Zealand', 'Fiji'],
            'Middle East': ['Saudi Arabia', 'UAE', 'Israel', 'Turkey', 'Iran']
        }
    
    def get_major_cities(self, country: str) -> List[Dict[str, Any]]:
        """Get major cities for a country"""
        cities_data = {
            'United States': [
                {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
                {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
                {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298},
                {'name': 'Houston', 'lat': 29.7604, 'lon': -95.3698}
            ],
            'United Kingdom': [
                {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
                {'name': 'Manchester', 'lat': 53.4808, 'lon': -2.2426},
                {'name': 'Birmingham', 'lat': 52.4862, 'lon': -1.8904}
            ],
            'Canada': [
                {'name': 'Toronto', 'lat': 43.6532, 'lon': -79.3832},
                {'name': 'Vancouver', 'lat': 49.2827, 'lon': -123.1207},
                {'name': 'Montreal', 'lat': 45.5017, 'lon': -73.5673}
            ]
        }
        
        return cities_data.get(country, [])
