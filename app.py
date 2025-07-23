import streamlit as st
import os
from datetime import datetime
import json

# Import our modules
from config import *
from database import init_database, get_user_preferences
from auth import authenticate_user, get_current_user
from news_aggregator import get_news_feeds, categorize_news
from ai_services import summarize_article, analyze_sentiment, generate_theme
from geo_services import get_user_location, get_hierarchical_news
from color_psychology import get_color_scheme, apply_dynamic_styling
from advertisement import display_ads, check_ad_blocker
from subscription import check_subscription_status, display_paywall
from affiliate import get_affiliate_products, track_affiliate_clicks
from analytics import track_user_activity, get_analytics_data
from components.news_card import render_news_card
from components.map_interface import render_international_map
from components.theme_manager import render_theme_selector
from utils import load_css, safe_execute

# Initialize database
init_database()

# Set page config
st.set_page_config(
    page_title="AI News Hub",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
load_css()

def main():
    """Main application entry point"""
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'location' not in st.session_state:
        st.session_state.location = None
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}
    if 'theme' not in st.session_state:
        st.session_state.theme = 'default'
    
    # Check authentication
    current_user = get_current_user()
    if current_user:
        st.session_state.user = current_user
    
    # Get user location if not set
    if not st.session_state.location:
        st.session_state.location = get_user_location()
    
    # Load user preferences
    if st.session_state.user:
        st.session_state.preferences = get_user_preferences(st.session_state.user['id'])
    
    # Display header
    render_header()
    
    # Check subscription status and display ads
    subscription_status = check_subscription_status(st.session_state.user)
    if not subscription_status.get('premium', False):
        display_ads('header')
    
    # Main navigation
    render_navigation()
    
    # Main content area
    render_main_content()
    
    # Footer
    render_footer()

def render_header():
    """Render application header"""
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        st.markdown("# 📰 AI News Hub")
    
    with col2:
        # Search functionality
        search_query = st.text_input("Search news...", placeholder="Search articles, topics, or locations")
        if search_query:
            st.session_state.search_query = search_query
    
    with col3:
        # User authentication
        if st.session_state.user:
            with st.popover(f"👤 {st.session_state.user['name']}"):
                st.write(f"Role: {st.session_state.user['role']}")
                if st.button("Profile"):
                    st.switch_page("pages/profile.py")
                if st.button("Settings"):
                    st.switch_page("pages/settings.py")
                if st.button("Logout"):
                    st.session_state.user = None
                    st.rerun()
        else:
            if st.button("Login"):
                authenticate_user()

def render_navigation():
    """Render main navigation tabs"""
    tabs = ["🏠 Home", "🌍 World", "🏛️ Politics", "💼 Business", "🔬 Technology", 
            "⚽ Sports", "🎬 Entertainment", "🏥 Health", "🔬 Science"]
    
    selected_tab = st.tabs(tabs)
    
    # Geographic sub-navigation
    geo_tabs = ["📍 Local", "🗺️ Regional", "🏳️ National", "🌐 International"]
    geo_selected = st.tabs(geo_tabs)
    
    # Store selected categories in session state
    st.session_state.selected_category = tabs[0] if not hasattr(st.session_state, 'selected_category') else st.session_state.selected_category
    st.session_state.selected_geo = geo_tabs[0] if not hasattr(st.session_state, 'selected_geo') else st.session_state.selected_geo

def render_main_content():
    """Render main content area"""
    try:
        # Get news based on selected category and geography
        news_data = get_hierarchical_news(
            category=st.session_state.selected_category,
            geo_level=st.session_state.selected_geo,
            location=st.session_state.location,
            user_preferences=st.session_state.preferences
        )
        
        # Apply color psychology
        color_scheme = get_color_scheme(news_data)
        apply_dynamic_styling(color_scheme)
        
        # Render news cards
        if news_data:
            cols = st.columns(3)
            for idx, article in enumerate(news_data):
                with cols[idx % 3]:
                    render_news_card(article, color_scheme)
                    
                    # Display ads between articles for non-premium users
                    subscription_status = check_subscription_status(st.session_state.user)
                    if not subscription_status.get('premium', False) and idx % 6 == 5:
                        display_ads('content')
        else:
            st.info("No news articles available for your current selection.")
            
        # International map view
        if st.session_state.selected_geo == "🌐 International":
            render_international_map(news_data)
            
    except Exception as e:
        st.error(f"Error loading news content: {str(e)}")
        st.info("Please try refreshing the page or check your internet connection.")

def render_footer():
    """Render application footer"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Quick Links")
        st.markdown("- About Us")
        st.markdown("- Contact")
        st.markdown("- Privacy Policy")
        st.markdown("- Terms of Service")
    
    with col2:
        st.markdown("### For Publishers")
        st.markdown("- Partner Portal")
        st.markdown("- Content Guidelines")
        st.markdown("- API Documentation")
        st.markdown("- Revenue Sharing")
    
    with col3:
        st.markdown("### For Affiliates")
        st.markdown("- Affiliate Program")
        st.markdown("- Commission Structure")
        st.markdown("- Marketing Materials")
        st.markdown("- Performance Dashboard")
    
    with col4:
        st.markdown("### Follow Us")
        st.markdown("- Twitter")
        st.markdown("- LinkedIn")
        st.markdown("- Facebook")
        st.markdown("- RSS Feeds")
    
    # Copyright
    st.markdown(f"© {datetime.now().year} AI News Hub. All rights reserved.")

if __name__ == "__main__":
    main()
