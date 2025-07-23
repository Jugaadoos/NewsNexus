import requests
import json
from typing import Dict, List, Optional, Tuple
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math

class GeoLocationManager:
    """Handles geo-location services and geographic content curation"""
    
    def __init__(self):
        self.ipinfo_api_key = os.getenv('IPINFO_API_KEY', 'demo_key')
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', 'demo_key')
        self.geolocator = Nominatim(user_agent="ai-news-platform")
        
        # Geographic boundaries for news filtering
        self.geo_boundaries = {
            'local_radius_miles': 100,
            'regional_boundaries': self.load_regional_boundaries(),
            'country_boundaries': self.load_country_boundaries()
        }
    
    def load_regional_boundaries(self) -> Dict:
        """Load regional boundaries data"""
        # In production, this would load from a comprehensive database
        return {
            'US': {
                'states': {
                    'CA': {'name': 'California', 'center': [36.7783, -119.4179]},
                    'TX': {'name': 'Texas', 'center': [31.9686, -99.9018]},
                    'FL': {'name': 'Florida', 'center': [27.7663, -81.6868]},
                    'NY': {'name': 'New York', 'center': [40.7128, -74.0060]},
                    'IL': {'name': 'Illinois', 'center': [40.6331, -89.3985]},
                    'PA': {'name': 'Pennsylvania', 'center': [41.2033, -77.1945]},
                    'OH': {'name': 'Ohio', 'center': [40.3888, -82.7649]},
                    'MI': {'name': 'Michigan', 'center': [44.3467, -85.4102]},
                    'WA': {'name': 'Washington', 'center': [47.7511, -120.7401]},
                    'OR': {'name': 'Oregon', 'center': [44.9319, -123.0351]}
                }
            },
            'CA': {
                'provinces': {
                    'ON': {'name': 'Ontario', 'center': [51.2538, -85.3232]},
                    'QC': {'name': 'Quebec', 'center': [53.9333, -73.6000]},
                    'BC': {'name': 'British Columbia', 'center': [53.7267, -127.6476]},
                    'AB': {'name': 'Alberta', 'center': [53.9333, -116.5765]},
                    'SK': {'name': 'Saskatchewan', 'center': [52.9399, -106.4509]},
                    'MB': {'name': 'Manitoba', 'center': [53.7609, -98.8139]}
                }
            },
            'UK': {
                'regions': {
                    'England': {'center': [52.3555, -1.1743]},
                    'Scotland': {'center': [56.4907, -4.2026]},
                    'Wales': {'center': [52.1307, -3.7837]},
                    'Northern Ireland': {'center': [54.7877, -6.4923]}
                }
            },
            'AU': {
                'states': {
                    'NSW': {'name': 'New South Wales', 'center': [-31.2532, 146.9211]},
                    'VIC': {'name': 'Victoria', 'center': [-36.8485, 144.9631]},
                    'QLD': {'name': 'Queensland', 'center': [-20.9176, 142.7028]},
                    'WA': {'name': 'Western Australia', 'center': [-25.0424, 121.6426]},
                    'SA': {'name': 'South Australia', 'center': [-30.0002, 136.2092]},
                    'TAS': {'name': 'Tasmania', 'center': [-41.4545, 145.9707]}
                }
            }
        }
    
    def load_country_boundaries(self) -> Dict:
        """Load country boundaries data"""
        return {
            'US': {'name': 'United States', 'center': [39.8283, -98.5795], 'continent': 'North America'},
            'CA': {'name': 'Canada', 'center': [56.1304, -106.3468], 'continent': 'North America'},
            'UK': {'name': 'United Kingdom', 'center': [55.3781, -3.4360], 'continent': 'Europe'},
            'DE': {'name': 'Germany', 'center': [51.1657, 10.4515], 'continent': 'Europe'},
            'FR': {'name': 'France', 'center': [46.6034, 1.8883], 'continent': 'Europe'},
            'JP': {'name': 'Japan', 'center': [36.2048, 138.2529], 'continent': 'Asia'},
            'CN': {'name': 'China', 'center': [35.8617, 104.1954], 'continent': 'Asia'},
            'IN': {'name': 'India', 'center': [20.5937, 78.9629], 'continent': 'Asia'},
            'AU': {'name': 'Australia', 'center': [-25.2744, 133.7751], 'continent': 'Oceania'},
            'BR': {'name': 'Brazil', 'center': [-14.2350, -51.9253], 'continent': 'South America'},
            'MX': {'name': 'Mexico', 'center': [23.6345, -102.5528], 'continent': 'North America'},
            'AR': {'name': 'Argentina', 'center': [-38.4161, -63.6167], 'continent': 'South America'},
            'ZA': {'name': 'South Africa', 'center': [-30.5595, 22.9375], 'continent': 'Africa'},
            'EG': {'name': 'Egypt', 'center': [26.0975, 31.2357], 'continent': 'Africa'},
            'RU': {'name': 'Russia', 'center': [61.5240, 105.3188], 'continent': 'Europe/Asia'},
            'TR': {'name': 'Turkey', 'center': [38.9637, 35.2433], 'continent': 'Europe/Asia'},
            'SA': {'name': 'Saudi Arabia', 'center': [23.8859, 45.0792], 'continent': 'Asia'},
            'AE': {'name': 'United Arab Emirates', 'center': [23.4241, 53.8478], 'continent': 'Asia'},
            'IL': {'name': 'Israel', 'center': [31.0461, 34.8516], 'continent': 'Asia'},
            'KR': {'name': 'South Korea', 'center': [35.9078, 127.7669], 'continent': 'Asia'},
            'TH': {'name': 'Thailand', 'center': [15.8700, 100.9925], 'continent': 'Asia'},
            'VN': {'name': 'Vietnam', 'center': [14.0583, 108.2772], 'continent': 'Asia'},
            'PH': {'name': 'Philippines', 'center': [12.8797, 121.7740], 'continent': 'Asia'},
            'ID': {'name': 'Indonesia', 'center': [-0.7893, 113.9213], 'continent': 'Asia'},
            'MY': {'name': 'Malaysia', 'center': [4.2105, 101.9758], 'continent': 'Asia'},
            'SG': {'name': 'Singapore', 'center': [1.3521, 103.8198], 'continent': 'Asia'},
            'NZ': {'name': 'New Zealand', 'center': [-40.9006, 174.8860], 'continent': 'Oceania'}
        }
    
    def get_location_from_ip(self, ip_address: str) -> Optional[Dict]:
        """Get location from IP address"""
        try:
            if self.ipinfo_api_key == 'demo_key':
                # Return demo location data
                return {
                    'ip': ip_address,
                    'city': 'San Francisco',
                    'region': 'California',
                    'country': 'US',
                    'country_name': 'United States',
                    'latitude': 37.7749,
                    'longitude': -122.4194,
                    'timezone': 'America/Los_Angeles',
                    'postal_code': '94102',
                    'continent': 'North America'
                }
            
            # Use IPinfo API
            url = f"https://ipinfo.io/{ip_address}"
            headers = {'Authorization': f'Bearer {self.ipinfo_api_key}'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Parse location data
                loc = data.get('loc', '').split(',')
                latitude = float(loc[0]) if len(loc) > 0 else None
                longitude = float(loc[1]) if len(loc) > 1 else None
                
                return {
                    'ip': ip_address,
                    'city': data.get('city', ''),
                    'region': data.get('region', ''),
                    'country': data.get('country', ''),
                    'country_name': self.get_country_name(data.get('country', '')),
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': data.get('timezone', ''),
                    'postal_code': data.get('postal', ''),
                    'continent': self.get_continent(data.get('country', ''))
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting location from IP: {e}")
            return None
    
    def get_country_name(self, country_code: str) -> str:
        """Get country name from country code"""
        country_data = self.geo_boundaries['country_boundaries'].get(country_code)
        return country_data['name'] if country_data else country_code
    
    def get_continent(self, country_code: str) -> str:
        """Get continent from country code"""
        country_data = self.geo_boundaries['country_boundaries'].get(country_code)
        return country_data['continent'] if country_data else 'Unknown'
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode address to coordinates"""
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'raw': location.raw
                }
            return None
            
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Reverse geocode coordinates to address"""
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                return {
                    'address': location.address,
                    'latitude': latitude,
                    'longitude': longitude,
                    'raw': location.raw
                }
            return None
            
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            return None
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate distance between two points in miles"""
        try:
            distance = geodesic(point1, point2).miles
            return distance
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return 0.0
    
    def is_within_local_radius(self, user_location: Dict, article_location: Dict) -> bool:
        """Check if article is within local radius of user"""
        try:
            if not all(key in user_location for key in ['latitude', 'longitude']):
                return False
            
            if not all(key in article_location for key in ['latitude', 'longitude']):
                return False
            
            user_point = (user_location['latitude'], user_location['longitude'])
            article_point = (article_location['latitude'], article_location['longitude'])
            
            distance = self.calculate_distance(user_point, article_point)
            return distance <= self.geo_boundaries['local_radius_miles']
            
        except Exception as e:
            print(f"Error checking local radius: {e}")
            return False
    
    def is_same_region(self, user_location: Dict, article_location: Dict) -> bool:
        """Check if article is in same region as user"""
        try:
            if user_location.get('country') != article_location.get('country'):
                return False
            
            return user_location.get('region') == article_location.get('region')
            
        except Exception as e:
            print(f"Error checking same region: {e}")
            return False
    
    def is_same_country(self, user_location: Dict, article_location: Dict) -> bool:
        """Check if article is in same country as user"""
        try:
            return user_location.get('country') == article_location.get('country')
            
        except Exception as e:
            print(f"Error checking same country: {e}")
            return False
    
    def filter_articles_by_geo_level(self, articles: List[Dict], user_location: Dict, geo_level: str) -> List[Dict]:
        """Filter articles by geographic level"""
        filtered_articles = []
        
        for article in articles:
            article_location = {
                'latitude': article.get('latitude'),
                'longitude': article.get('longitude'),
                'city': article.get('city'),
                'region': article.get('region'),
                'country': article.get('country')
            }
            
            include_article = False
            
            if geo_level == 'Local':
                include_article = self.is_within_local_radius(user_location, article_location)
            elif geo_level == 'Regional':
                include_article = self.is_same_region(user_location, article_location)
            elif geo_level == 'National':
                include_article = self.is_same_country(user_location, article_location)
            elif geo_level == 'International':
                include_article = not self.is_same_country(user_location, article_location)
            else:
                include_article = True  # Include all if no filter
            
            if include_article:
                filtered_articles.append(article)
        
        return filtered_articles
    
    def get_nearby_cities(self, user_location: Dict, radius_miles: int = 100) -> List[Dict]:
        """Get nearby cities within radius"""
        try:
            # In production, this would query a cities database
            # For now, return some example cities
            nearby_cities = [
                {'name': 'San Francisco', 'state': 'CA', 'latitude': 37.7749, 'longitude': -122.4194},
                {'name': 'Oakland', 'state': 'CA', 'latitude': 37.8044, 'longitude': -122.2711},
                {'name': 'San Jose', 'state': 'CA', 'latitude': 37.3382, 'longitude': -121.8863},
                {'name': 'Berkeley', 'state': 'CA', 'latitude': 37.8715, 'longitude': -122.2730},
                {'name': 'Fremont', 'state': 'CA', 'latitude': 37.5485, 'longitude': -121.9886}
            ]
            
            # Filter by distance
            user_point = (user_location['latitude'], user_location['longitude'])
            filtered_cities = []
            
            for city in nearby_cities:
                city_point = (city['latitude'], city['longitude'])
                distance = self.calculate_distance(user_point, city_point)
                
                if distance <= radius_miles:
                    city['distance'] = distance
                    filtered_cities.append(city)
            
            # Sort by distance
            filtered_cities.sort(key=lambda x: x['distance'])
            return filtered_cities
            
        except Exception as e:
            print(f"Error getting nearby cities: {e}")
            return []
    
    def get_regional_hierarchy(self, location: Dict) -> Dict:
        """Get regional hierarchy for location"""
        try:
            country_code = location.get('country', '')
            region = location.get('region', '')
            
            hierarchy = {
                'country': {
                    'code': country_code,
                    'name': self.get_country_name(country_code),
                    'continent': self.get_continent(country_code)
                },
                'region': {
                    'code': region,
                    'name': region,
                    'type': self.get_region_type(country_code)
                },
                'city': location.get('city', ''),
                'coordinates': {
                    'latitude': location.get('latitude'),
                    'longitude': location.get('longitude')
                }
            }
            
            return hierarchy
            
        except Exception as e:
            print(f"Error getting regional hierarchy: {e}")
            return {}
    
    def get_region_type(self, country_code: str) -> str:
        """Get region type for country"""
        region_types = {
            'US': 'state',
            'CA': 'province',
            'UK': 'region',
            'AU': 'state',
            'DE': 'state',
            'FR': 'region',
            'IN': 'state',
            'BR': 'state',
            'MX': 'state',
            'AR': 'province',
            'ZA': 'province',
            'RU': 'region',
            'CN': 'province',
            'JP': 'prefecture'
        }
        
        return region_types.get(country_code, 'region')
    
    def get_international_news_map(self) -> Dict:
        """Get international news organized by geographic regions"""
        try:
            continents = {
                'North America': {
                    'countries': ['US', 'CA', 'MX'],
                    'center': [54.5260, -105.2551],
                    'zoom': 3
                },
                'South America': {
                    'countries': ['BR', 'AR', 'CL', 'PE', 'CO', 'VE'],
                    'center': [-8.7832, -55.4915],
                    'zoom': 3
                },
                'Europe': {
                    'countries': ['UK', 'DE', 'FR', 'ES', 'IT', 'RU', 'TR'],
                    'center': [54.5260, 15.2551],
                    'zoom': 4
                },
                'Asia': {
                    'countries': ['CN', 'IN', 'JP', 'KR', 'TH', 'VN', 'PH', 'ID', 'MY', 'SG'],
                    'center': [34.0479, 100.6197],
                    'zoom': 3
                },
                'Africa': {
                    'countries': ['ZA', 'EG', 'NG', 'KE', 'MA', 'GH'],
                    'center': [-8.7832, 34.5085],
                    'zoom': 3
                },
                'Oceania': {
                    'countries': ['AU', 'NZ'],
                    'center': [-25.2744, 133.7751],
                    'zoom': 4
                }
            }
            
            # Add country details
            for continent_name, continent_data in continents.items():
                country_details = []
                for country_code in continent_data['countries']:
                    country_info = self.geo_boundaries['country_boundaries'].get(country_code)
                    if country_info:
                        country_details.append({
                            'code': country_code,
                            'name': country_info['name'],
                            'center': country_info['center']
                        })
                continent_data['country_details'] = country_details
            
            return continents
            
        except Exception as e:
            print(f"Error getting international news map: {e}")
            return {}
    
    def get_location_insights(self, location: Dict) -> Dict:
        """Get insights about location for news curation"""
        try:
            insights = {
                'timezone': location.get('timezone', ''),
                'local_time': None,
                'region_type': self.get_region_type(location.get('country', '')),
                'continent': self.get_continent(location.get('country', '')),
                'nearby_cities': self.get_nearby_cities(location),
                'regional_hierarchy': self.get_regional_hierarchy(location),
                'country_info': self.geo_boundaries['country_boundaries'].get(location.get('country', {}))
            }
            
            return insights
            
        except Exception as e:
            print(f"Error getting location insights: {e}")
            return {}
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude coordinates"""
        try:
            return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
        except:
            return False
    
    def get_distance_display(self, distance_miles: float) -> str:
        """Get human-readable distance display"""
        if distance_miles < 1:
            return f"{distance_miles * 5280:.0f} feet"
        elif distance_miles < 100:
            return f"{distance_miles:.1f} miles"
        else:
            return f"{distance_miles:.0f} miles"
