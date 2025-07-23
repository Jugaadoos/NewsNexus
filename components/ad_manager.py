import streamlit as st
import random
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

class AdManager:
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.analytics_service = services.get('analytics')
        
        # Ad configuration
        self.ad_config = {
            'free_user_frequency': 5,  # Show ad every 5 articles
            'popup_frequency': 300,    # Show popup every 5 minutes
            'banner_positions': ['top', 'middle', 'bottom'],
            'sidebar_positions': ['top', 'middle', 'bottom'],
        }
        
        # Sample ad content (in production, this would come from ad networks)
        self.sample_ads = {
            'banner': [
                {
                    'id': 'banner_001',
                    'type': 'banner',
                    'title': 'Upgrade to Premium',
                    'description': 'Get ad-free news experience with exclusive features',
                    'cta': 'Upgrade Now',
                    'image_url': None,
                    'link': '/upgrade',
                    'advertiser': 'Platform Internal'
                },
                {
                    'id': 'banner_002',
                    'type': 'banner',
                    'title': 'Professional News Analysis',
                    'description': 'Advanced analytics and insights for business professionals',
                    'cta': 'Learn More',
                    'image_url': None,
                    'link': '/business-suite',
                    'advertiser': 'Platform Internal'
                }
            ],
            'sidebar': [
                {
                    'id': 'sidebar_001',
                    'type': 'sidebar',
                    'title': 'News API Access',
                    'description': 'Integrate our news data into your applications',
                    'cta': 'Get API Key',
                    'image_url': None,
                    'link': '/api',
                    'advertiser': 'Platform Internal'
                },
                {
                    'id': 'sidebar_002',
                    'type': 'sidebar',
                    'title': 'Publishing Partnership',
                    'description': 'Become a content partner and earn revenue',
                    'cta': 'Join Now',
                    'image_url': None,
                    'link': '/partner',
                    'advertiser': 'Platform Internal'
                }
            ],
            'popup': [
                {
                    'id': 'popup_001',
                    'type': 'popup',
                    'title': 'Special Offer: 50% Off Premium',
                    'description': 'Limited time offer for new subscribers. Get ad-free experience, exclusive content, and advanced features.',
                    'cta': 'Claim Offer',
                    'image_url': None,
                    'link': '/upgrade?promo=SAVE50',
                    'advertiser': 'Platform Internal'
                }
            ],
            'inline': [
                {
                    'id': 'inline_001',
                    'type': 'inline',
                    'title': 'Affiliate Program',
                    'description': 'Earn money by promoting our platform. Join thousands of successful affiliates.',
                    'cta': 'Start Earning',
                    'image_url': None,
                    'link': '/affiliate',
                    'advertiser': 'Platform Internal'
                }
            ]
        }
    
    def should_show_ad(self, user: Dict[str, Any], ad_type: str) -> bool:
        """Determine if an ad should be shown to the user"""
        try:
            # No ads for premium users
            subscription_tier = st.session_state.get('subscription_tier', 'free')
            if subscription_tier != 'free':
                return False
            
            # No ads for guests (optional policy)
            if user.get('role') == 'guest':
                return True  # Can show ads to guests
            
            # Check ad frequency for different types
            if ad_type == 'popup':
                return self._should_show_popup()
            elif ad_type == 'inline':
                return self._should_show_inline_ad()
            elif ad_type in ['banner', 'sidebar']:
                return True  # Always show these for free users
            
            return False
            
        except Exception as e:
            logging.error(f"Error determining ad display: {str(e)}")
            return False
    
    def render_banner_ad(self, position: str = 'top', user: Dict[str, Any] = None):
        """Render banner advertisement"""
        try:
            if not user:
                user = st.session_state.get('user', {})
            
            if not self.should_show_ad(user, 'banner'):
                return
            
            ad = self._get_ad('banner')
            if not ad:
                return
            
            # Render banner ad
            self._render_banner_style(ad, position)
            
            # Track ad impression
            self._track_ad_event(ad, 'impression', user)
            
        except Exception as e:
            logging.error(f"Error rendering banner ad: {str(e)}")
    
    def render_sidebar_ad(self, position: str = 'top', user: Dict[str, Any] = None):
        """Render sidebar advertisement"""
        try:
            if not user:
                user = st.session_state.get('user', {})
            
            if not self.should_show_ad(user, 'sidebar'):
                return
            
            ad = self._get_ad('sidebar')
            if not ad:
                return
            
            # Render sidebar ad
            self._render_sidebar_style(ad, position)
            
            # Track ad impression
            self._track_ad_event(ad, 'impression', user)
            
        except Exception as e:
            logging.error(f"Error rendering sidebar ad: {str(e)}")
    
    def render_inline_ad(self, user: Dict[str, Any] = None):
        """Render inline advertisement between content"""
        try:
            if not user:
                user = st.session_state.get('user', {})
            
            if not self.should_show_ad(user, 'inline'):
                return
            
            ad = self._get_ad('inline')
            if not ad:
                return
            
            # Render inline ad
            self._render_inline_style(ad)
            
            # Track ad impression
            self._track_ad_event(ad, 'impression', user)
            
        except Exception as e:
            logging.error(f"Error rendering inline ad: {str(e)}")
    
    def render_popup_ad(self, user: Dict[str, Any] = None):
        """Render popup advertisement"""
        try:
            if not user:
                user = st.session_state.get('user', {})
            
            if not self.should_show_ad(user, 'popup'):
                return
            
            ad = self._get_ad('popup')
            if not ad:
                return
            
            # Check if popup was recently shown
            if self._was_popup_recently_shown():
                return
            
            # Render popup ad
            self._render_popup_style(ad)
            
            # Mark popup as shown
            st.session_state.last_popup_time = datetime.now()
            
            # Track ad impression
            self._track_ad_event(ad, 'impression', user)
            
        except Exception as e:
            logging.error(f"Error rendering popup ad: {str(e)}")
    
    def render_adsense_placeholder(self, ad_format: str = 'auto', width: str = '100%', height: str = '250px'):
        """Render Google AdSense placeholder"""
        try:
            # AdSense integration placeholder
            adsense_html = f"""
            <div style="width: {width}; height: {height}; background: #f5f5f5; border: 1px dashed #ddd; display: flex; align-items: center; justify-content: center; margin: 1rem 0;">
                <div style="text-align: center; color: #666;">
                    <div style="font-size: 18px; margin-bottom: 8px;">📢</div>
                    <div>Google AdSense</div>
                    <div style="font-size: 12px;">Advertisement Space</div>
                </div>
            </div>
            
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-xxxxxxxxxxxxxxxx"
                 data-ad-slot="xxxxxxxxx"
                 data-ad-format="{ad_format}"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
            """
            
            st.markdown(adsense_html, unsafe_allow_html=True)
            
        except Exception as e:
            logging.error(f"Error rendering AdSense placeholder: {str(e)}")
    
    def _render_banner_style(self, ad: Dict[str, Any], position: str):
        """Render banner ad with specific styling"""
        try:
            banner_html = f"""
            <div style="
                background: linear-gradient(135deg, #1A73E8, #34A853);
                color: white;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            ">
                <div style="position: relative; z-index: 2;">
                    <h3 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 600;">{ad['title']}</h3>
                    <p style="margin: 0 0 12px 0; opacity: 0.95;">{ad['description']}</p>
                    <button onclick="window.open('{ad['link']}', '_blank')" style="
                        background: white;
                        color: #1A73E8;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        {ad['cta']}
                    </button>
                </div>
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 100%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
                    transform: rotate(45deg);
                "></div>
            </div>
            """
            
            st.markdown(banner_html, unsafe_allow_html=True)
            
            # Track click if button is clicked (would need JavaScript in production)
            if st.button("Track Click", key=f"track_{ad['id']}", help="Hidden tracking button"):
                self._track_ad_event(ad, 'click', st.session_state.get('user', {}))
            
        except Exception as e:
            logging.error(f"Error rendering banner style: {str(e)}")
    
    def _render_sidebar_style(self, ad: Dict[str, Any], position: str):
        """Render sidebar ad with specific styling"""
        try:
            sidebar_html = f"""
            <div style="
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                margin: 16px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1A73E8; font-size: 16px;">{ad['title']}</h4>
                <p style="margin: 0 0 12px 0; font-size: 14px; color: #666; line-height: 1.4;">{ad['description']}</p>
                <button onclick="window.open('{ad['link']}', '_blank')" style="
                    background: #1A73E8;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                    cursor: pointer;
                    width: 100%;
                " onmouseover="this.style.background='#1557b0'" onmouseout="this.style.background='#1A73E8'">
                    {ad['cta']}
                </button>
                <div style="font-size: 10px; color: #999; margin-top: 8px;">Advertisement</div>
            </div>
            """
            
            st.markdown(sidebar_html, unsafe_allow_html=True)
            
        except Exception as e:
            logging.error(f"Error rendering sidebar style: {str(e)}")
    
    def _render_inline_style(self, ad: Dict[str, Any]):
        """Render inline ad with specific styling"""
        try:
            inline_html = f"""
            <div style="
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin: 24px 0;
                text-align: center;
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    font-size: 10px;
                    color: #999;
                    background: white;
                    padding: 2px 6px;
                    border-radius: 3px;
                ">SPONSORED</div>
                
                <h4 style="margin: 0 0 8px 0; color: #495057;">{ad['title']}</h4>
                <p style="margin: 0 0 16px 0; color: #6c757d;">{ad['description']}</p>
                <button onclick="window.open('{ad['link']}', '_blank')" style="
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: 600;
                    cursor: pointer;
                " onmouseover="this.style.background='#218838'" onmouseout="this.style.background='#28a745'">
                    {ad['cta']}
                </button>
            </div>
            """
            
            st.markdown(inline_html, unsafe_allow_html=True)
            
        except Exception as e:
            logging.error(f"Error rendering inline style: {str(e)}")
    
    def _render_popup_style(self, ad: Dict[str, Any]):
        """Render popup ad with specific styling"""
        try:
            # Use Streamlit's modal-like behavior with expander
            with st.expander("🎯 Special Offer!", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {ad['title']}")
                    st.write(ad['description'])
                    
                    if st.button(ad['cta'], key=f"popup_cta_{ad['id']}", type="primary"):
                        # Track click
                        self._track_ad_event(ad, 'click', st.session_state.get('user', {}))
                        # Would open link in production
                        st.success("Redirecting...")
                
                with col2:
                    if st.button("❌ Close", key=f"popup_close_{ad['id']}"):
                        st.session_state.popup_closed = True
                        st.rerun()
            
        except Exception as e:
            logging.error(f"Error rendering popup style: {str(e)}")
    
    def _get_ad(self, ad_type: str) -> Optional[Dict[str, Any]]:
        """Get an appropriate ad for the given type"""
        try:
            ads = self.sample_ads.get(ad_type, [])
            if not ads:
                return None
            
            # Simple random selection (in production, this would be more sophisticated)
            return random.choice(ads)
            
        except Exception as e:
            logging.error(f"Error getting ad: {str(e)}")
            return None
    
    def _should_show_popup(self) -> bool:
        """Check if popup should be shown"""
        try:
            if st.session_state.get('popup_closed'):
                return False
            
            last_popup = st.session_state.get('last_popup_time')
            if not last_popup:
                return True
            
            # Check if enough time has passed
            time_diff = (datetime.now() - last_popup).total_seconds()
            return time_diff > self.ad_config['popup_frequency']
            
        except Exception as e:
            logging.error(f"Error checking popup timing: {str(e)}")
            return False
    
    def _should_show_inline_ad(self) -> bool:
        """Check if inline ad should be shown"""
        try:
            # Simple frequency check based on article count
            article_count = st.session_state.get('articles_viewed', 0)
            return article_count % self.ad_config['free_user_frequency'] == 0
            
        except Exception as e:
            logging.error(f"Error checking inline ad timing: {str(e)}")
            return False
    
    def _was_popup_recently_shown(self) -> bool:
        """Check if popup was recently shown"""
        try:
            last_popup = st.session_state.get('last_popup_time')
            if not last_popup:
                return False
            
            time_diff = (datetime.now() - last_popup).total_seconds()
            return time_diff < 60  # Don't show popup again within 1 minute
            
        except Exception as e:
            logging.error(f"Error checking recent popup: {str(e)}")
            return False
    
    def _track_ad_event(self, ad: Dict[str, Any], event_type: str, user: Dict[str, Any]):
        """Track ad events for analytics"""
        try:
            if not self.analytics_service or not user.get('id'):
                return
            
            self.analytics_service.track_event(
                user_id=user['id'],
                event_type=f'ad_{event_type}',
                event_data={
                    'ad_id': ad['id'],
                    'ad_type': ad['type'],
                    'advertiser': ad['advertiser'],
                    'placement': ad.get('placement', 'unknown')
                },
                geo_data=st.session_state.get('location')
            )
            
        except Exception as e:
            logging.error(f"Error tracking ad event: {str(e)}")
    
    def get_ad_performance_stats(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Get ad performance statistics"""
        try:
            # Sample performance data
            return {
                'impressions': 1245,
                'clicks': 89,
                'ctr': 7.1,  # Click-through rate
                'revenue': 23.45,
                'top_performing_ads': [
                    {'id': 'banner_001', 'ctr': 8.5, 'revenue': 12.34},
                    {'id': 'sidebar_001', 'ctr': 6.8, 'revenue': 8.90}
                ]
            }
            
        except Exception as e:
            logging.error(f"Error getting ad performance stats: {str(e)}")
            return {}
    
    def configure_ad_settings(self, settings: Dict[str, Any]):
        """Configure ad display settings"""
        try:
            self.ad_config.update(settings)
            logging.info(f"Ad settings updated: {settings}")
            
        except Exception as e:
            logging.error(f"Error configuring ad settings: {str(e)}")
    
    def render_ad_blocker_detection(self):
        """Detect and handle ad blockers"""
        try:
            # Ad blocker detection placeholder
            st.markdown("""
            <script>
            // Ad blocker detection would go here
            // This is a simplified placeholder
            if (typeof adsbygoogle === 'undefined') {
                // Ad blocker detected
                console.log('Ad blocker detected');
            }
            </script>
            """, unsafe_allow_html=True)
            
            # Show message to users with ad blockers
            if st.session_state.get('subscription_tier') == 'free':
                st.info("📢 Consider upgrading to Premium for an ad-free experience!")
            
        except Exception as e:
            logging.error(f"Error in ad blocker detection: {str(e)}")

# Utility functions for easy usage
def render_banner_ad(services: Dict[str, Any], position: str = 'top', user: Dict[str, Any] = None):
    """Utility function to render banner ad"""
    try:
        ad_manager = AdManager(services)
        ad_manager.render_banner_ad(position, user)
    except Exception as e:
        logging.error(f"Error in banner ad utility: {str(e)}")

def render_sidebar_ad(services: Dict[str, Any], position: str = 'top', user: Dict[str, Any] = None):
    """Utility function to render sidebar ad"""
    try:
        ad_manager = AdManager(services)
        ad_manager.render_sidebar_ad(position, user)
    except Exception as e:
        logging.error(f"Error in sidebar ad utility: {str(e)}")

def render_inline_ad(services: Dict[str, Any], user: Dict[str, Any] = None):
    """Utility function to render inline ad"""
    try:
        ad_manager = AdManager(services)
        ad_manager.render_inline_ad(user)
    except Exception as e:
        logging.error(f"Error in inline ad utility: {str(e)}")

def render_popup_ad(services: Dict[str, Any], user: Dict[str, Any] = None):
    """Utility function to render popup ad"""
    try:
        ad_manager = AdManager(services)
        ad_manager.render_popup_ad(user)
    except Exception as e:
        logging.error(f"Error in popup ad utility: {str(e)}")
