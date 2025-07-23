import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import math
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from config import GOOGLE_MAPS_API_KEY, LOCAL_RADIUS_MILES, REGIONAL_BOUNDARIES
from database import get_articles_by_location, db

class GeoServices:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="ai_news_hub")
        self.maps_api_key = GOOGLE_MAPS_API_KEY
        self.local_radius = LOCAL_RADIUS_MILES
    
    def get_user_location_from_ip(self) -> Optional[Dict]:
        """Get user location from IP address"""
        try:
            # Using ipapi.co for IP geolocation
            response = requests.get("https://ipapi.co/json/")
            if response.status_code == 200:
                data = response.json()
                return {
                    "lat": float(data.get("latitude", 0)),
                    "lng": float(data.get("longitude", 0)),
                    "city": data.get("city", ""),
                    "region": data.get("region", ""),
                    "country": data.get("country_name", ""),
                    "country_code": data.get("country_code", "")
                }
        except Exception as e:
            print(f"Error getting location from IP: {e}")
        
        return None
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode address to coordinates"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                return {
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "address": location.address
                }
        except Exception as e:
            print(f"Error geocoding address: {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """Reverse geocode coordinates to address"""
        try:
            location = self.geocoder.reverse(f"{lat}, {lng}")
            if location:
                address_components = location.raw.get("address", {})
                return {
                    "address": location.address,
                    "city": address_components.get("city", ""),
                    "state": address_components.get("state", ""),
                    "country": address_components.get("country", ""),
                    "postal_code": address_components.get("postcode", "")
                }
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
        
        return None
    
    def calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in miles"""
        try:
            point1 = (loc1["lat"], loc1["lng"])
            point2 = (loc2["lat"], loc2["lng"])
            distance = geodesic(point1, point2).miles
            return distance
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')
    
    def get_regional_boundaries(self, country_code: str) -> List[Dict]:
        """Get regional boundaries for a country"""
        boundaries = REGIONAL_BOUNDARIES.get(country_code, [])
        
        # In a real implementation, this would query a geospatial database
        # For now, return sample regional data
        if country_code == "US":
            return [
                {"name": "California", "code": "CA", "type": "state"},
                {"name": "New York", "code": "NY", "type": "state"},
                {"name": "Texas", "code": "TX", "type": "state"},
                {"name": "Florida", "code": "FL", "type": "state"}
            ]
        elif country_code == "UK":
            return [
                {"name": "England", "code": "ENG", "type": "country"},
                {"name": "Scotland", "code": "SCO", "type": "country"},
                {"name": "Wales", "code": "WAL", "type": "country"},
                {"name": "Northern Ireland", "code": "NIR", "type": "country"}
            ]
        
        return []
    
    def filter_articles_by_location(self, articles: List[Dict], location: Dict, radius_miles: float = None) -> List[Dict]:
        """Filter articles by location and radius"""
        if not location or not articles:
            return articles
        
        radius = radius_miles or self.local_radius
        filtered_articles = []
        
        for article in articles:
            article_location = article.get("location_relevance")
            if article_location and isinstance(article_location, dict):
                distance = self.calculate_distance(location, article_location)
                if distance <= radius:
                    article["distance"] = distance
                    filtered_articles.append(article)
        
        # Sort by distance
        filtered_articles.sort(key=lambda x: x.get("distance", float('inf')))
        return filtered_articles
    
    def get_country_news_sources(self, country_code: str) -> List[Dict]:
        """Get news sources for a specific country"""
        # Country-specific news sources
        sources_by_country = {
            "US": [
                {"name": "CNN", "url": "https://rss.cnn.com/rss/edition.rss"},
                {"name": "USA Today", "url": "https://rss.usatoday.com/news/nation"},
                {"name": "AP News", "url": "https://storage.googleapis.com/afs-prod/feeds/xml/rss_2.0.xml"}
            ],
            "UK": [
                {"name": "BBC", "url": "https://feeds.bbci.co.uk/news/rss.xml"},
                {"name": "The Guardian", "url": "https://www.theguardian.com/uk/rss"},
                {"name": "Sky News", "url": "https://feeds.skynews.com/feeds/rss/uk.xml"}
            ],
            "CA": [
                {"name": "CBC", "url": "https://www.cbc.ca/cmlink/rss-canada"},
                {"name": "Globe and Mail", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/"}
            ]
        }
        
        return sources_by_country.get(country_code, [])
    
    def get_hierarchical_location_data(self, location: Dict) -> Dict:
        """Get hierarchical location data for news filtering"""
        try:
            return {
                "local": {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "radius": self.local_radius,
                    "city": location.get("city", "")
                },
                "regional": {
                    "state": location.get("region", ""),
                    "country": location.get("country", "")
                },
                "national": {
                    "country": location.get("country", ""),
                    "country_code": location.get("country_code", "")
                },
                "international": {
                    "exclude_country": location.get("country_code", "")
                }
            }
        except Exception as e:
            print(f"Error getting hierarchical location data: {e}")
            return {}
    
    def get_news_by_geo_level(self, location: Dict, geo_level: str, category: str = None) -> List[Dict]:
        """Get news articles by geographic hierarchy level"""
        try:
            hierarchy = self.get_hierarchical_location_data(location)
            
            if geo_level == "local":
                # Get local news within radius
                local_data = hierarchy.get("local", {})
                return get_articles_by_location(local_data, self.local_radius)
            
            elif geo_level == "regional":
                # Get regional news (state/province level)
                regional_data = hierarchy.get("regional", {})
                return self.get_regional_news(regional_data, category)
            
            elif geo_level == "national":
                # Get national news
                national_data = hierarchy.get("national", {})
                return self.get_national_news(national_data, category)
            
            elif geo_level == "international":
                # Get international news
                international_data = hierarchy.get("international", {})
                return self.get_international_news(international_data, category)
            
            return []
            
        except Exception as e:
            print(f"Error getting news by geo level: {e}")
            return []
    
    def get_regional_news(self, regional_data: Dict, category: str = None) -> List[Dict]:
        """Get regional news articles"""
        query = """
        SELECT * FROM news_articles 
        WHERE location_relevance->>'state' = %s
        OR location_relevance->>'country' = %s
        """
        params = [regional_data.get("state", ""), regional_data.get("country", "")]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY published_at DESC LIMIT 100"
        
        result = db.execute_query(query, tuple(params))
        return [dict(row) for row in result] if result else []
    
    def get_national_news(self, national_data: Dict, category: str = None) -> List[Dict]:
        """Get national news articles"""
        query = """
        SELECT * FROM news_articles 
        WHERE location_relevance->>'country' = %s
        """
        params = [national_data.get("country", "")]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY published_at DESC LIMIT 100"
        
        result = db.execute_query(query, tuple(params))
        return [dict(row) for row in result] if result else []
    
    def get_international_news(self, international_data: Dict, category: str = None) -> List[Dict]:
        """Get international news articles"""
        query = """
        SELECT * FROM news_articles 
        WHERE location_relevance->>'country' != %s
        OR location_relevance->>'country' IS NULL
        """
        params = [international_data.get("exclude_country", "")]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY published_at DESC LIMIT 100"
        
        result = db.execute_query(query, tuple(params))
        return [dict(row) for row in result] if result else []
    
    def get_world_map_data(self) -> Dict:
        """Get world map data for international news visualization"""
        query = """
        SELECT 
            location_relevance->>'country' as country,
            COUNT(*) as article_count,
            AVG(sentiment_score) as avg_sentiment
        FROM news_articles 
        WHERE location_relevance->>'country' IS NOT NULL
        AND published_at >= NOW() - INTERVAL '7 days'
        GROUP BY location_relevance->>'country'
        """
        
        result = db.execute_query(query)
        if result:
            return {
                "countries": [
                    {
                        "country": row["country"],
                        "article_count": row["article_count"],
                        "avg_sentiment": float(row["avg_sentiment"]) if row["avg_sentiment"] else 0.5
                    }
                    for row in result
                ]
            }
        
        return {"countries": []}

# Initialize geo services
geo_services = GeoServices()

# Export functions for easy import
def get_user_location() -> Optional[Dict]:
    return geo_services.get_user_location_from_ip()

def get_hierarchical_news(category: str, geo_level: str, location: Dict, user_preferences: Dict) -> List[Dict]:
    if not location:
        return []
    
    # Map UI labels to internal geo levels
    geo_level_map = {
        "📍 Local": "local",
        "🗺️ Regional": "regional", 
        "🏳️ National": "national",
        "🌐 International": "international"
    }
    
    # Map category labels to internal categories
    category_map = {
        "🏠 Home": "world",
        "🌍 World": "world",
        "🏛️ Politics": "politics",
        "💼 Business": "business",
        "🔬 Technology": "technology",
        "⚽ Sports": "sports",
        "🎬 Entertainment": "entertainment",
        "🏥 Health": "health",
        "🔬 Science": "science"
    }
    
    internal_geo_level = geo_level_map.get(geo_level, "local")
    internal_category = category_map.get(category, "world")
    
    return geo_services.get_news_by_geo_level(location, internal_geo_level, internal_category)

def calculate_distance(loc1: Dict, loc2: Dict) -> float:
    return geo_services.calculate_distance(loc1, loc2)

def get_world_map_data() -> Dict:
    return geo_services.get_world_map_data()
