import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import db, get_active_subscription
from subscription import check_subscription_status
import streamlit as st

class AdvertisementManager:
    def __init__(self):
        self.ad_types = {
            "banner": {"width": "100%", "height": "90px"},
            "popup": {"width": "400px", "height": "300px"},
            "native": {"width": "100%", "height": "auto"},
            "sidebar": {"width": "300px", "height": "250px"}
        }
        
        self.ad_placements = {
            "header": {"frequency": 1, "type": "banner"},
            "content": {"frequency": 3, "type": "native"},
            "sidebar": {"frequency": 1, "type": "sidebar"},
            "popup": {"frequency": 1, "type": "popup"}
        }
    
    def should_show_ads(self, user: Dict = None) -> bool:
        """Check if ads should be shown to user"""
        if not user:
            return True
        
        subscription = check_subscription_status(user)
        if subscription.get('premium', False):
            return False
        
        # Check ad-free periods or special conditions
        return True
    
    def get_targeted_ads(self, user: Dict = None, context: Dict = None) -> List[Dict]:
        """Get targeted ads based on user profile and context"""
        try:
            query = """
            SELECT * FROM advertisements 
            WHERE active = TRUE
            AND (budget > 0 OR budget IS NULL)
            ORDER BY RANDOM()
            LIMIT 10
            """
            
            result = db.execute_query(query)
            ads = [dict(row) for row in result] if result else []
            
            # Apply targeting logic
            if user and context:
                ads = self.apply_targeting_filters(ads, user, context)
            
            return ads
            
        except Exception as e:
            print(f"Error getting targeted ads: {e}")
            return self.get_fallback_ads()
    
    def apply_targeting_filters(self, ads: List[Dict], user: Dict, context: Dict) -> List[Dict]:
        """Apply targeting filters to ads"""
        filtered_ads = []
        
        for ad in ads:
            targeting = ad.get('targeting_criteria', {})
            if isinstance(targeting, str):
                try:
                    import json
                    targeting = json.loads(targeting)
                except:
                    targeting = {}
            
            # Geographic targeting
            if 'geo' in targeting:
                user_location = context.get('location', {})
                if not self.matches_geo_targeting(targeting['geo'], user_location):
                    continue
            
            # Category targeting
            if 'category' in targeting:
                article_category = context.get('category', '')
                if article_category not in targeting['category']:
                    continue
            
            # Demographic targeting
            if 'demographics' in targeting:
                if not self.matches_demographic_targeting(targeting['demographics'], user):
                    continue
            
            filtered_ads.append(ad)
        
        return filtered_ads
    
    def matches_geo_targeting(self, geo_targeting: Dict, user_location: Dict) -> bool:
        """Check if user location matches ad geo targeting"""
        if not user_location:
            return True
        
        # Check country targeting
        if 'countries' in geo_targeting:
            user_country = user_location.get('country_code', '')
            if user_country not in geo_targeting['countries']:
                return False
        
        # Check city targeting
        if 'cities' in geo_targeting:
            user_city = user_location.get('city', '').lower()
            if user_city not in [city.lower() for city in geo_targeting['cities']]:
                return False
        
        return True
    
    def matches_demographic_targeting(self, demo_targeting: Dict, user: Dict) -> bool:
        """Check if user demographics match ad targeting"""
        # In a real implementation, this would check user profile data
        return True
    
    def get_fallback_ads(self) -> List[Dict]:
        """Get fallback ads when targeting fails"""
        return [
            {
                "id": 1,
                "title": "Premium News Experience",
                "content": "Upgrade to Premium for ad-free reading",
                "image_url": "",
                "target_url": "/subscription",
                "ad_type": "native"
            },
            {
                "id": 2,
                "title": "Stay Informed",
                "content": "Get breaking news alerts on your phone",
                "image_url": "",
                "target_url": "/settings",
                "ad_type": "banner"
            }
        ]
    
    def create_ad_html(self, ad: Dict, placement: str) -> str:
        """Create HTML for ad display"""
        ad_type = ad.get('ad_type', 'native')
        dimensions = self.ad_types.get(ad_type, self.ad_types['native'])
        
        # Google AdSense integration
        if ad.get('ad_provider') == 'adsense':
            return self.create_adsense_ad(ad, dimensions)
        
        # Native ad HTML
        html = f"""
        <div class="advertisement-container" style="
            width: {dimensions['width']};
            height: {dimensions['height']};
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            background: #f8f9fa;
            position: relative;
        ">
            <div class="ad-label" style="
                position: absolute;
                top: 4px;
                right: 4px;
                font-size: 10px;
                color: #666;
                background: #fff;
                padding: 2px 4px;
                border-radius: 2px;
            ">AD</div>
            
            <div class="ad-content" onclick="window.open('{ad.get('target_url', '#')}', '_blank')">
                <h4 style="margin: 0 0 8px 0; font-size: 16px; color: #333;">
                    {ad.get('title', 'Advertisement')}
                </h4>
                <p style="margin: 0; font-size: 14px; color: #666; line-height: 1.4;">
                    {ad.get('content', 'Click to learn more')}
                </p>
            </div>
        </div>
        """
        
        return html
    
    def create_adsense_ad(self, ad: Dict, dimensions: Dict) -> str:
        """Create Google AdSense ad HTML"""
        return f"""
        <div class="adsense-container" style="
            width: {dimensions['width']};
            height: {dimensions['height']};
            margin: 16px 0;
        ">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-{ad.get('adsense_id', 'XXXXXXXXX')}"
                 data-ad-slot="{ad.get('ad_slot', 'XXXXXXXXX')}"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
        </div>
        """
    
    def create_popup_ad(self, ad: Dict) -> str:
        """Create popup ad HTML"""
        return f"""
        <div id="popup-ad" style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            height: 300px;
            background: white;
            border: 2px solid #333;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            display: none;
        ">
            <div class="popup-header" style="
                padding: 16px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <h3 style="margin: 0; font-size: 18px;">{ad.get('title', 'Advertisement')}</h3>
                <button onclick="closePopupAd()" style="
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                ">×</button>
            </div>
            
            <div class="popup-content" style="padding: 16px;">
                <p style="margin: 0 0 16px 0; line-height: 1.6;">
                    {ad.get('content', 'Advertisement content here')}
                </p>
                <a href="{ad.get('target_url', '#')}" target="_blank" style="
                    display: inline-block;
                    background: #1A73E8;
                    color: white;
                    padding: 8px 16px;
                    text-decoration: none;
                    border-radius: 4px;
                ">Learn More</a>
            </div>
        </div>
        
        <div id="popup-overlay" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 9999;
            display: none;
        " onclick="closePopupAd()"></div>
        
        <script>
            function showPopupAd() {{
                document.getElementById('popup-ad').style.display = 'block';
                document.getElementById('popup-overlay').style.display = 'block';
            }}
            
            function closePopupAd() {{
                document.getElementById('popup-ad').style.display = 'none';
                document.getElementById('popup-overlay').style.display = 'none';
            }}
            
            // Show popup after 5 seconds
            setTimeout(showPopupAd, 5000);
        </script>
        """
    
    def track_ad_impression(self, ad_id: int, user_id: int = None):
        """Track ad impression"""
        try:
            query = """
            UPDATE advertisements 
            SET impressions = impressions + 1 
            WHERE id = %s
            """
            db.execute_query(query, (ad_id,), fetch=False)
            
            # Log impression for analytics
            if user_id:
                from analytics import track_user_activity
                track_user_activity(user_id, "", "ad_impression", "", {"ad_id": ad_id})
                
        except Exception as e:
            print(f"Error tracking ad impression: {e}")
    
    def track_ad_click(self, ad_id: int, user_id: int = None):
        """Track ad click"""
        try:
            query = """
            UPDATE advertisements 
            SET clicks = clicks + 1 
            WHERE id = %s
            """
            db.execute_query(query, (ad_id,), fetch=False)
            
            # Log click for analytics
            if user_id:
                from analytics import track_user_activity
                track_user_activity(user_id, "", "ad_click", "", {"ad_id": ad_id})
                
        except Exception as e:
            print(f"Error tracking ad click: {e}")

# Initialize advertisement manager
ad_manager = AdvertisementManager()

def display_ads(placement: str, user: Dict = None, context: Dict = None):
    """Display ads in specified placement"""
    if not ad_manager.should_show_ads(user):
        return
    
    # Get targeted ads
    ads = ad_manager.get_targeted_ads(user, context)
    
    if not ads:
        return
    
    # Select appropriate ad for placement
    placement_config = ad_manager.ad_placements.get(placement, {})
    ad_type = placement_config.get('type', 'native')
    
    # Filter ads by type
    suitable_ads = [ad for ad in ads if ad.get('ad_type') == ad_type]
    if not suitable_ads:
        suitable_ads = ads
    
    # Select random ad
    selected_ad = random.choice(suitable_ads)
    
    # Create and display ad HTML
    if placement == "popup":
        ad_html = ad_manager.create_popup_ad(selected_ad)
    else:
        ad_html = ad_manager.create_ad_html(selected_ad, placement)
    
    # Display ad
    st.markdown(ad_html, unsafe_allow_html=True)
    
    # Track impression
    ad_manager.track_ad_impression(selected_ad['id'], user.get('id') if user else None)

def check_ad_blocker() -> bool:
    """Check if user has ad blocker enabled"""
    # This would typically use JavaScript to detect ad blockers
    # For now, return False (no ad blocker detected)
    return False

def create_ad_blocker_message() -> str:
    """Create message for ad blocker users"""
    return """
    <div style="
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        text-align: center;
    ">
        <h4 style="margin: 0 0 8px 0; color: #856404;">Ad Blocker Detected</h4>
        <p style="margin: 0; color: #856404;">
            We notice you're using an ad blocker. Please consider disabling it to support our journalism, 
            or <a href="/subscription" style="color: #1A73E8;">upgrade to Premium</a> for an ad-free experience.
        </p>
    </div>
    """

def get_advertisement_analytics(date_range: int = 30) -> Dict:
    """Get advertisement performance analytics"""
    try:
        query = """
        SELECT 
            id,
            title,
            ad_type,
            impressions,
            clicks,
            CASE 
                WHEN impressions > 0 THEN (clicks::float / impressions::float) * 100
                ELSE 0 
            END as ctr,
            created_at
        FROM advertisements
        WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY impressions DESC
        """
        
        result = db.execute_query(query, (date_range,))
        
        if result:
            return {
                "ads": [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "ad_type": row["ad_type"],
                        "impressions": row["impressions"],
                        "clicks": row["clicks"],
                        "ctr": float(row["ctr"]) if row["ctr"] else 0,
                        "created_at": row["created_at"]
                    }
                    for row in result
                ]
            }
        
        return {"ads": []}
        
    except Exception as e:
        print(f"Error getting ad analytics: {e}")
        return {"ads": []}
