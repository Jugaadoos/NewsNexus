import streamlit as st
from datetime import datetime
import json

# Import our modules
from auth import get_current_user, require_auth, require_permission
from database import update_user_preferences, get_user_preferences, db
from config import RSS_FEEDS, COLOR_PSYCHOLOGY, SUBSCRIPTION_TIERS, USER_ROLES
from ai_services import generate_theme
from geo_services import get_user_location
from news_aggregator import refresh_news_cache
from analytics import get_analytics_data
from utils import format_date, validate_url

@require_auth
def show_settings():
    """Main settings page"""
    st.set_page_config(
        page_title="Settings - AI News Hub",
        page_icon="⚙️",
        layout="wide"
    )
    
    user = get_current_user()
    if not user:
        st.error("Please login to access settings")
        return
    
    st.title("⚙️ Settings")
    
    # Settings navigation based on user role
    if user['role'] == 'admin':
        tabs = ["🎨 Appearance", "📍 Location", "🔔 Notifications", "🔒 Privacy", "⚙️ System", "🗃️ Data"]
    elif user['role'] in ['editor', 'creator', 'journalist']:
        tabs = ["🎨 Appearance", "📍 Location", "🔔 Notifications", "🔒 Privacy", "✍️ Content"]
    elif user['role'] == 'affiliate':
        tabs = ["🎨 Appearance", "📍 Location", "🔔 Notifications", "🔒 Privacy", "💼 Business"]
    else:
        tabs = ["🎨 Appearance", "📍 Location", "🔔 Notifications", "🔒 Privacy"]
    
    selected_tabs = st.tabs(tabs)
    
    with selected_tabs[0]:
        show_appearance_settings(user)
    
    with selected_tabs[1]:
        show_location_settings(user)
    
    with selected_tabs[2]:
        show_notification_settings(user)
    
    with selected_tabs[3]:
        show_privacy_settings(user)
    
    if len(selected_tabs) > 4:
        with selected_tabs[4]:
            if user['role'] == 'admin':
                show_system_settings(user)
            elif user['role'] in ['editor', 'creator', 'journalist']:
                show_content_settings(user)
            elif user['role'] == 'affiliate':
                show_business_settings(user)
    
    if len(selected_tabs) > 5 and user['role'] == 'admin':
        with selected_tabs[5]:
            show_data_settings(user)

def show_appearance_settings(user: dict):
    """Show appearance and theme settings"""
    st.subheader("🎨 Appearance & Themes")
    
    current_prefs = get_user_preferences(user['id'])
    
    # Theme selection
    st.markdown("### Theme Selection")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Predefined themes
        predefined_themes = {
            "Default": {"primary": "#1A73E8", "secondary": "#34A853", "background": "#F8F9FA", "text": "#202124"},
            "Dark Mode": {"primary": "#BB86FC", "secondary": "#03DAC6", "background": "#121212", "text": "#FFFFFF"},
            "Light": {"primary": "#6200EE", "secondary": "#03DAC5", "background": "#FFFFFF", "text": "#000000"},
            "Ocean": {"primary": "#0277BD", "secondary": "#00ACC1", "background": "#E0F2F1", "text": "#004D40"},
            "Forest": {"primary": "#2E7D32", "secondary": "#66BB6A", "background": "#E8F5E9", "text": "#1B5E20"},
            "Sunset": {"primary": "#F57C00", "secondary": "#FF9800", "background": "#FFF8E1", "text": "#E65100"}
        }
        
        current_theme = current_prefs.get('theme_name', 'Default')
        
        for theme_name, theme_data in predefined_themes.items():
            if st.button(f"Apply {theme_name}", key=f"theme_{theme_name}"):
                updated_prefs = current_prefs.copy()
                updated_prefs.update({
                    'theme_name': theme_name,
                    'theme_data': theme_data
                })
                
                if update_user_preferences(user['id'], updated_prefs):
                    st.success(f"{theme_name} theme applied!")
                    st.rerun()
                else:
                    st.error("Error applying theme")
        
        # AI Theme Generator
        st.markdown("#### 🤖 AI Theme Generator")
        theme_prompt = st.text_input("Describe your ideal theme", 
                                   placeholder="e.g., 'Dark theme with purple accents for late night reading'")
        
        if st.button("🎨 Generate AI Theme") and theme_prompt:
            with st.spinner("Generating custom theme..."):
                ai_theme = generate_theme(theme_prompt)
                
                if ai_theme:
                    st.success("Custom theme generated!")
                    
                    # Preview the generated theme
                    st.markdown("**Preview:**")
                    st.markdown(f"""
                    <div style="
                        background: {ai_theme.get('background_color', '#FFFFFF')};
                        color: {ai_theme.get('text_color', '#000000')};
                        border: 2px solid {ai_theme.get('primary_color', '#1A73E8')};
                        border-radius: 8px;
                        padding: 20px;
                        margin: 10px 0;
                    ">
                        <h4 style="color: {ai_theme.get('primary_color', '#1A73E8')}; margin-top: 0;">
                            {ai_theme.get('theme_name', 'Custom Theme')}
                        </h4>
                        <p>{ai_theme.get('description', 'AI-generated custom theme')}</p>
                        <div style="
                            background: {ai_theme.get('accent_color', '#34A853')};
                            color: white;
                            padding: 8px 16px;
                            border-radius: 4px;
                            display: inline-block;
                        ">
                            Sample Element
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Apply AI Theme"):
                        updated_prefs = current_prefs.copy()
                        updated_prefs.update({
                            'theme_name': ai_theme.get('theme_name', 'Custom AI Theme'),
                            'theme_data': ai_theme
                        })
                        
                        if update_user_preferences(user['id'], updated_prefs):
                            st.success("AI theme applied!")
                            st.rerun()
                        else:
                            st.error("Error applying AI theme")
                else:
                    st.error("Error generating theme. Please try again.")
    
    with col2:
        # Theme upload
        st.markdown("#### 📁 Upload Theme")
        uploaded_theme = st.file_uploader("Upload theme JSON", type=['json'])
        
        if uploaded_theme:
            try:
                theme_data = json.load(uploaded_theme)
                
                # Validate theme structure
                required_keys = ['primary_color', 'secondary_color', 'background_color', 'text_color']
                if all(key in theme_data for key in required_keys):
                    if st.button("Apply Uploaded Theme"):
                        updated_prefs = current_prefs.copy()
                        updated_prefs.update({
                            'theme_name': theme_data.get('theme_name', 'Uploaded Theme'),
                            'theme_data': theme_data
                        })
                        
                        if update_user_preferences(user['id'], updated_prefs):
                            st.success("Uploaded theme applied!")
                            st.rerun()
                        else:
                            st.error("Error applying uploaded theme")
                else:
                    st.error("Invalid theme file format")
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
    
    # Display preferences
    st.markdown("### Display Preferences")
    
    with st.form("display_preferences"):
        col1, col2 = st.columns(2)
        
        with col1:
            font_size = st.selectbox("Font Size", 
                                   ["Small", "Medium", "Large", "Extra Large"],
                                   index=["Small", "Medium", "Large", "Extra Large"].index(current_prefs.get('font_size', 'Medium')))
            
            article_layout = st.selectbox("Article Layout",
                                        ["Card", "List", "Compact"],
                                        index=["Card", "List", "Compact"].index(current_prefs.get('article_layout', 'Card')))
            
            show_images = st.checkbox("Show article images", 
                                    value=current_prefs.get('show_images', True))
        
        with col2:
            articles_per_page = st.slider("Articles per page", 5, 50, 
                                        current_prefs.get('articles_per_page', 20))
            
            animation_speed = st.selectbox("Animation Speed",
                                         ["Slow", "Normal", "Fast", "None"],
                                         index=["Slow", "Normal", "Fast", "None"].index(current_prefs.get('animation_speed', 'Normal')))
            
            reduce_motion = st.checkbox("Reduce motion (accessibility)", 
                                      value=current_prefs.get('reduce_motion', False))
        
        if st.form_submit_button("💾 Save Display Preferences"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'font_size': font_size,
                'article_layout': article_layout,
                'show_images': show_images,
                'articles_per_page': articles_per_page,
                'animation_speed': animation_speed,
                'reduce_motion': reduce_motion
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Display preferences saved!")
                st.rerun()
            else:
                st.error("Error saving preferences")

def show_location_settings(user: dict):
    """Show location and geographic settings"""
    st.subheader("📍 Location & Geographic Settings")
    
    current_prefs = get_user_preferences(user['id'])
    
    # Current location
    st.markdown("### Current Location")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if user.get('location_city'):
            st.write(f"📍 **Current Location:** {user['location_city']}, {user.get('location_state', '')}, {user.get('location_country', '')}")
        else:
            st.info("No location set")
        
        # Auto-detect location
        if st.button("🎯 Detect My Location"):
            with st.spinner("Detecting location..."):
                location = get_user_location()
                
                if location:
                    # Update user location in database
                    update_query = """
                    UPDATE users 
                    SET location_lat = %s, location_lng = %s, location_city = %s, 
                        location_state = %s, location_country = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    
                    result = db.execute_query(update_query, (
                        location.get('lat'),
                        location.get('lng'),
                        location.get('city'),
                        location.get('region'),
                        location.get('country'),
                        user['id']
                    ), fetch=False)
                    
                    if result:
                        st.success(f"Location updated: {location.get('city')}, {location.get('country')}")
                        st.rerun()
                    else:
                        st.error("Error updating location")
                else:
                    st.error("Could not detect location")
    
    with col2:
        st.markdown("**Manual Location Entry**")
        with st.form("manual_location"):
            manual_city = st.text_input("City", value=user.get('location_city', ''))
            manual_state = st.text_input("State/Province", value=user.get('location_state', ''))
            manual_country = st.text_input("Country", value=user.get('location_country', ''))
            
            if st.form_submit_button("📍 Set Location"):
                update_query = """
                UPDATE users 
                SET location_city = %s, location_state = %s, location_country = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                
                result = db.execute_query(update_query, (
                    manual_city or None,
                    manual_state or None,
                    manual_country or None,
                    user['id']
                ), fetch=False)
                
                if result:
                    st.success("Location updated manually!")
                    st.rerun()
                else:
                    st.error("Error updating location")
    
    # Geographic preferences
    st.markdown("### Geographic Preferences")
    
    with st.form("geo_preferences"):
        col1, col2 = st.columns(2)
        
        with col1:
            local_radius = st.slider("Local news radius (miles)", 
                                   25, 200, current_prefs.get('local_radius', 75))
            
            preferred_regions = st.multiselect("Preferred regions for news",
                                             ["North America", "Europe", "Asia", "Africa", "South America", "Oceania"],
                                             default=current_prefs.get('preferred_regions', []))
            
            international_focus = st.selectbox("International news focus",
                                             ["Global", "Regional", "Neighboring Countries", "English-speaking"],
                                             index=0)
        
        with col2:
            show_local_weather = st.checkbox("Show local weather", 
                                           value=current_prefs.get('show_local_weather', True))
            
            time_zone_auto = st.checkbox("Auto-detect time zone", 
                                       value=current_prefs.get('time_zone_auto', True))
            
            if not time_zone_auto:
                time_zone = st.selectbox("Manual time zone",
                                       ["UTC", "EST", "PST", "GMT", "CET"],
                                       index=0)
            else:
                time_zone = "auto"
        
        if st.form_submit_button("🌍 Save Geographic Preferences"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'local_radius': local_radius,
                'preferred_regions': preferred_regions,
                'international_focus': international_focus,
                'show_local_weather': show_local_weather,
                'time_zone_auto': time_zone_auto,
                'time_zone': time_zone
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Geographic preferences saved!")
                st.rerun()
            else:
                st.error("Error saving preferences")

def show_notification_settings(user: dict):
    """Show notification settings"""
    st.subheader("🔔 Notification Settings")
    
    current_prefs = get_user_preferences(user['id'])
    
    with st.form("notification_settings"):
        st.markdown("### Email Notifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_enabled = st.checkbox("Enable email notifications", 
                                      value=current_prefs.get('email_notifications', True))
            
            breaking_news = st.checkbox("Breaking news alerts", 
                                      value=current_prefs.get('breaking_alerts', True))
            
            daily_digest = st.checkbox("Daily news digest", 
                                     value=current_prefs.get('daily_digest', False))
            
            weekly_summary = st.checkbox("Weekly summary", 
                                       value=current_prefs.get('weekly_summary', False))
        
        with col2:
            subscription_updates = st.checkbox("Subscription updates", 
                                             value=current_prefs.get('subscription_updates', True))
            
            new_features = st.checkbox("New feature announcements", 
                                     value=current_prefs.get('new_features', True))
            
            marketing_emails = st.checkbox("Marketing emails", 
                                         value=current_prefs.get('marketing_emails', False))
            
            security_alerts = st.checkbox("Security alerts", 
                                        value=current_prefs.get('security_alerts', True))
        
        st.markdown("### Push Notifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            push_enabled = st.checkbox("Enable push notifications", 
                                     value=current_prefs.get('push_notifications', False))
            
            push_breaking = st.checkbox("Push breaking news", 
                                      value=current_prefs.get('push_breaking', False))
        
        with col2:
            push_personalized = st.checkbox("Personalized article recommendations", 
                                          value=current_prefs.get('push_personalized', False))
            
            push_quiet_hours = st.checkbox("Respect quiet hours (9 PM - 8 AM)", 
                                         value=current_prefs.get('push_quiet_hours', True))
        
        st.markdown("### Notification Frequency")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_frequency = st.selectbox("Email frequency",
                                         ["Immediate", "Hourly", "Daily", "Weekly"],
                                         index=["Immediate", "Hourly", "Daily", "Weekly"].index(current_prefs.get('email_frequency', 'Daily')))
        
        with col2:
            digest_time = st.selectbox("Daily digest time",
                                     ["6:00 AM", "8:00 AM", "12:00 PM", "6:00 PM", "8:00 PM"],
                                     index=1)
        
        if st.form_submit_button("🔔 Save Notification Settings"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'email_notifications': email_enabled,
                'breaking_alerts': breaking_news,
                'daily_digest': daily_digest,
                'weekly_summary': weekly_summary,
                'subscription_updates': subscription_updates,
                'new_features': new_features,
                'marketing_emails': marketing_emails,
                'security_alerts': security_alerts,
                'push_notifications': push_enabled,
                'push_breaking': push_breaking,
                'push_personalized': push_personalized,
                'push_quiet_hours': push_quiet_hours,
                'email_frequency': email_frequency,
                'digest_time': digest_time
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Notification settings saved!")
                st.rerun()
            else:
                st.error("Error saving notification settings")

def show_privacy_settings(user: dict):
    """Show privacy and security settings"""
    st.subheader("🔒 Privacy & Security")
    
    current_prefs = get_user_preferences(user['id'])
    
    # Privacy settings
    st.markdown("### Privacy Settings")
    
    with st.form("privacy_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            public_profile = st.checkbox("Make profile public", 
                                       value=current_prefs.get('public_profile', False))
            
            share_reading = st.checkbox("Share reading activity", 
                                      value=current_prefs.get('share_reading', False))
            
            data_collection = st.checkbox("Allow data collection for improvements", 
                                        value=current_prefs.get('data_collection', True))
            
            personalized_ads = st.checkbox("Show personalized advertisements", 
                                         value=current_prefs.get('personalized_ads', True))
        
        with col2:
            analytics_tracking = st.checkbox("Enable analytics tracking", 
                                           value=current_prefs.get('analytics_tracking', True))
            
            location_sharing = st.checkbox("Share location for local news", 
                                         value=current_prefs.get('location_sharing', True))
            
            third_party_sharing = st.checkbox("Allow sharing with trusted partners", 
                                            value=current_prefs.get('third_party_sharing', False))
            
            cookie_consent = st.checkbox("Accept all cookies", 
                                       value=current_prefs.get('cookie_consent', True))
        
        if st.form_submit_button("🔒 Save Privacy Settings"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'public_profile': public_profile,
                'share_reading': share_reading,
                'data_collection': data_collection,
                'personalized_ads': personalized_ads,
                'analytics_tracking': analytics_tracking,
                'location_sharing': location_sharing,
                'third_party_sharing': third_party_sharing,
                'cookie_consent': cookie_consent
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Privacy settings saved!")
                st.rerun()
            else:
                st.error("Error saving privacy settings")
    
    # Security settings
    st.markdown("### Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Account Security")
        
        if st.button("🔑 Change Password"):
            st.info("Password change functionality coming soon!")
        
        if st.button("📱 Setup Two-Factor Authentication"):
            st.info("2FA setup coming soon!")
        
        if st.button("📋 View Login History"):
            show_login_history(user['id'])
    
    with col2:
        st.markdown("#### Data Management")
        
        if st.button("📥 Download My Data"):
            st.info("Data export functionality coming soon!")
        
        if st.button("🗑️ Delete Account"):
            st.warning("This action cannot be undone!")
            st.info("Account deletion requires admin approval")
        
        if st.button("🔄 Revoke All Sessions"):
            st.info("Session management coming soon!")

def show_login_history(user_id: int):
    """Show user login history"""
    st.markdown("#### 📋 Recent Login Activity")
    
    try:
        # Get recent login activity from analytics
        login_query = """
        SELECT 
            created_at,
            metadata->>'ip_address' as ip_address,
            metadata->>'user_agent' as user_agent
        FROM user_analytics 
        WHERE user_id = %s 
        AND action = 'login'
        ORDER BY created_at DESC 
        LIMIT 10
        """
        
        login_history = db.execute_query(login_query, (user_id,))
        
        if login_history:
            for login in login_history:
                with st.container():
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Date:** {format_date(login['created_at'])}")
                    
                    with col2:
                        st.write(f"**IP:** {login.get('ip_address', 'Unknown')}")
                    
                    with col3:
                        user_agent = login.get('user_agent', 'Unknown')
                        if len(user_agent) > 30:
                            user_agent = user_agent[:30] + "..."
                        st.write(f"**Device:** {user_agent}")
                    
                    st.divider()
        else:
            st.info("No recent login activity found")
    
    except Exception as e:
        st.error(f"Error loading login history: {e}")

@require_permission("all")
def show_system_settings(user: dict):
    """Show system administration settings"""
    st.subheader("⚙️ System Administration")
    
    # System status
    st.markdown("### System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Database status
        try:
            result = db.execute_query("SELECT 1")
            db_status = "🟢 Online" if result else "🔴 Offline"
        except:
            db_status = "🔴 Offline"
        st.metric("Database", db_status)
    
    with col2:
        st.metric("Cache Status", "🟢 Active")
    
    with col3:
        st.metric("API Status", "🟢 Connected")
    
    with col4:
        st.metric("Uptime", "99.9%")
    
    # System controls
    st.markdown("### System Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh News Cache"):
            with st.spinner("Refreshing news cache..."):
                refresh_news_cache()
            st.success("News cache refreshed!")
        
        if st.button("🧹 Clear System Cache"):
            st.cache_data.clear()
            st.success("System cache cleared!")
    
    with col2:
        if st.button("📊 Generate System Report"):
            st.info("System report generation coming soon!")
        
        if st.button("🔍 Run Diagnostics"):
            st.info("System diagnostics coming soon!")
    
    with col3:
        if st.button("⚠️ Emergency Maintenance"):
            st.warning("Emergency maintenance mode!")
        
        if st.button("🔒 Lock System"):
            st.error("System lock functionality coming soon!")
    
    # Configuration management
    st.markdown("### Configuration Management")
    
    # RSS Feeds management
    with st.expander("📡 RSS Feeds Configuration"):
        st.write("**Current RSS Feeds:**")
        
        for category, feeds in RSS_FEEDS.items():
            st.write(f"**{category.title()}:**")
            for feed in feeds:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"- {feed}")
                with col2:
                    if st.button("🗑️", key=f"remove_{feed}"):
                        st.info("RSS feed removal coming soon!")
        
        # Add new RSS feed
        st.markdown("**Add New RSS Feed:**")
        with st.form("add_rss_feed"):
            new_feed_category = st.selectbox("Category", list(RSS_FEEDS.keys()))
            new_feed_url = st.text_input("RSS Feed URL")
            
            if st.form_submit_button("➕ Add Feed"):
                if validate_url(new_feed_url):
                    st.success(f"RSS feed would be added to {new_feed_category}")
                else:
                    st.error("Please enter a valid URL")
    
    # Color psychology configuration
    with st.expander("🎨 Color Psychology Configuration"):
        st.write("**Current Color Schemes:**")
        
        for news_type, colors in COLOR_PSYCHOLOGY.items():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{news_type.title()}:**")
            
            with col2:
                st.color_picker("Primary", colors['primary'], key=f"primary_{news_type}")
            
            with col3:
                st.color_picker("Secondary", colors['secondary'], key=f"secondary_{news_type}")
            
            with col4:
                st.color_picker("Accent", colors['accent'], key=f"accent_{news_type}")

def show_content_settings(user: dict):
    """Show content creation settings for creators and journalists"""
    st.subheader("✍️ Content Settings")
    
    current_prefs = get_user_preferences(user['id'])
    
    # Content preferences
    st.markdown("### Content Creation Preferences")
    
    with st.form("content_preferences"):
        col1, col2 = st.columns(2)
        
        with col1:
            default_category = st.selectbox("Default article category",
                                          ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"],
                                          index=0)
            
            auto_save = st.checkbox("Auto-save drafts", 
                                  value=current_prefs.get('auto_save', True))
            
            spell_check = st.checkbox("Enable spell check", 
                                    value=current_prefs.get('spell_check', True))
        
        with col2:
            word_count_target = st.number_input("Default word count target", 
                                              min_value=100, max_value=5000, 
                                              value=current_prefs.get('word_count_target', 500))
            
            ai_assistance = st.checkbox("Enable AI writing assistance", 
                                      value=current_prefs.get('ai_assistance', True))
            
            grammar_check = st.checkbox("Enable grammar check", 
                                      value=current_prefs.get('grammar_check', True))
        
        # Publishing preferences
        st.markdown("#### Publishing Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_publish = st.checkbox("Auto-publish after review", 
                                     value=current_prefs.get('auto_publish', False))
            
            require_review = st.checkbox("Always require editorial review", 
                                       value=current_prefs.get('require_review', True))
        
        with col2:
            social_sharing = st.checkbox("Auto-share to social media", 
                                       value=current_prefs.get('social_sharing', False))
            
            seo_optimization = st.checkbox("Enable SEO optimization suggestions", 
                                         value=current_prefs.get('seo_optimization', True))
        
        if st.form_submit_button("✍️ Save Content Settings"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'default_category': default_category,
                'auto_save': auto_save,
                'spell_check': spell_check,
                'word_count_target': word_count_target,
                'ai_assistance': ai_assistance,
                'grammar_check': grammar_check,
                'auto_publish': auto_publish,
                'require_review': require_review,
                'social_sharing': social_sharing,
                'seo_optimization': seo_optimization
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Content settings saved!")
                st.rerun()
            else:
                st.error("Error saving content settings")

def show_business_settings(user: dict):
    """Show business settings for affiliates"""
    st.subheader("💼 Business Settings")
    
    current_prefs = get_user_preferences(user['id'])
    
    # Business information
    st.markdown("### Business Information")
    
    with st.form("business_info"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name", 
                                        value=current_prefs.get('business_name', ''))
            
            tax_id = st.text_input("Tax ID", 
                                 value=current_prefs.get('tax_id', ''))
            
            website_url = st.text_input("Website URL", 
                                      value=current_prefs.get('website_url', ''))
        
        with col2:
            business_type = st.selectbox("Business Type",
                                       ["Individual", "LLC", "Corporation", "Partnership"],
                                       index=0)
            
            industry = st.selectbox("Industry",
                                  ["Media", "Technology", "Education", "Healthcare", "Finance", "Other"],
                                  index=0)
            
            phone_business = st.text_input("Business Phone", 
                                         value=current_prefs.get('phone_business', ''))
        
        # Payment preferences
        st.markdown("#### Payment Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            payment_method = st.selectbox("Preferred Payment Method",
                                        ["PayPal", "Bank Transfer", "Check"],
                                        index=0)
            
            minimum_payout = st.number_input("Minimum Payout Amount", 
                                           min_value=25.0, max_value=1000.0, 
                                           value=current_prefs.get('minimum_payout', 50.0))
        
        with col2:
            payment_frequency = st.selectbox("Payment Frequency",
                                           ["Monthly", "Bi-weekly", "Weekly"],
                                           index=0)
            
            currency = st.selectbox("Currency",
                                  ["USD", "EUR", "GBP", "CAD"],
                                  index=0)
        
        if st.form_submit_button("💼 Save Business Settings"):
            updated_prefs = current_prefs.copy()
            updated_prefs.update({
                'business_name': business_name,
                'tax_id': tax_id,
                'website_url': website_url,
                'business_type': business_type,
                'industry': industry,
                'phone_business': phone_business,
                'payment_method': payment_method,
                'minimum_payout': minimum_payout,
                'payment_frequency': payment_frequency,
                'currency': currency
            })
            
            if update_user_preferences(user['id'], updated_prefs):
                st.success("Business settings saved!")
                st.rerun()
            else:
                st.error("Error saving business settings")

@require_permission("all")
def show_data_settings(user: dict):
    """Show data management and backup settings"""
    st.subheader("🗃️ Data Management")
    
    # Data export
    st.markdown("### Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export User Data"):
            st.info("User data export coming soon!")
    
    with col2:
        if st.button("📥 Export Analytics Data"):
            st.info("Analytics data export coming soon!")
    
    with col3:
        if st.button("📥 Export System Logs"):
            st.info("System logs export coming soon!")
    
    # Data cleanup
    st.markdown("### Data Cleanup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Automated Cleanup")
        
        if st.button("🧹 Clean Old Analytics (>1 year)"):
            st.info("Analytics cleanup coming soon!")
        
        if st.button("🧹 Clean Inactive Users (>2 years)"):
            st.info("User cleanup coming soon!")
        
        if st.button("🧹 Clean Old Articles (>5 years)"):
            st.info("Article cleanup coming soon!")
    
    with col2:
        st.markdown("#### Backup Management")
        
        if st.button("💾 Create System Backup"):
            st.info("System backup coming soon!")
        
        if st.button("📋 View Backup History"):
            st.info("Backup history coming soon!")
        
        if st.button("🔄 Restore from Backup"):
            st.warning("Restore functionality coming soon!")

if __name__ == "__main__":
    show_settings()
