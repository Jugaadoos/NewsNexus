import streamlit as st
from datetime import datetime
from typing import Dict, Optional
import base64
from io import BytesIO

# Import our modules
from auth import get_current_user, require_auth
from database import update_user_preferences, get_user_preferences, get_user_saved_articles, db
from subscription import check_subscription_status, display_subscription_plans
from analytics import get_user_analytics
from utils import format_date, generate_avatar, validate_email, validate_phone, format_phone

@require_auth
def show_profile():
    """Show user profile page"""
    st.set_page_config(
        page_title="Profile - AI News Hub",
        page_icon="👤",
        layout="wide"
    )
    
    user = get_current_user()
    if not user:
        st.error("Please login to view your profile")
        return
    
    st.title("👤 Your Profile")
    
    # Profile navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Basic Info", "⚙️ Preferences", "📊 Activity", "💳 Subscription", "🎨 Appearance"
    ])
    
    with tab1:
        show_basic_info(user)
    
    with tab2:
        show_preferences(user)
    
    with tab3:
        show_activity(user)
    
    with tab4:
        show_subscription_info(user)
    
    with tab5:
        show_appearance_settings(user)

def show_basic_info(user: Dict):
    """Show and edit basic user information"""
    st.subheader("📝 Basic Information")
    
    # Profile header
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Profile avatar
        avatar_url = generate_avatar(user['name'])
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="{avatar_url}" style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #1A73E8;">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📷 Change Avatar"):
            st.info("Avatar upload functionality coming soon!")
    
    with col2:
        st.markdown(f"### {user['name']}")
        st.markdown(f"**Role:** {user['role'].title()}")
        st.markdown(f"**Member since:** {format_date(user['created_at'], 'long')}")
        st.markdown(f"**Email:** {user['email']}")
        if user.get('phone'):
            st.markdown(f"**Phone:** {format_phone(user['phone'])}")
    
    st.divider()
    
    # Edit profile form
    with st.form("edit_profile"):
        st.markdown("#### Edit Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Full Name", value=user['name'])
            new_email = st.text_input("Email Address", value=user['email'])
            new_phone = st.text_input("Phone Number", value=user.get('phone', ''))
        
        with col2:
            # Location information
            new_city = st.text_input("City", value=user.get('location_city', ''))
            new_state = st.text_input("State/Province", value=user.get('location_state', ''))
            new_country = st.text_input("Country", value=user.get('location_country', ''))
        
        # Bio/Description for creators and journalists
        if user['role'] in ['creator', 'journalist', 'editor']:
            bio = st.text_area("Bio/Description", 
                             placeholder="Tell others about yourself and your expertise...",
                             height=100)
        
        if st.form_submit_button("💾 Save Changes"):
            # Validate inputs
            if not new_name.strip():
                st.error("Name cannot be empty")
            elif not validate_email(new_email):
                st.error("Please enter a valid email address")
            elif new_phone and not validate_phone(new_phone):
                st.error("Please enter a valid phone number")
            else:
                # Update user information
                try:
                    update_query = """
                    UPDATE users 
                    SET name = %s, email = %s, phone = %s, 
                        location_city = %s, location_state = %s, location_country = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    
                    db.execute_query(update_query, (
                        new_name, new_email, new_phone or None,
                        new_city or None, new_state or None, new_country or None,
                        user['id']
                    ), fetch=False)
                    
                    # Update session state
                    st.session_state.user.update({
                        'name': new_name,
                        'email': new_email,
                        'phone': new_phone,
                        'location_city': new_city,
                        'location_state': new_state,
                        'location_country': new_country
                    })
                    
                    st.success("Profile updated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
    
    # Account actions
    st.markdown("#### Account Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Change Email"):
            st.info("Email change functionality coming soon!")
    
    with col2:
        if st.button("🔒 Change Password"):
            st.info("Password change functionality coming soon!")
    
    with col3:
        if st.button("❌ Delete Account"):
            show_delete_account_confirmation()

def show_delete_account_confirmation():
    """Show account deletion confirmation"""
    st.warning("⚠️ Account Deletion")
    st.markdown("""
    **This action cannot be undone.** Deleting your account will:
    - Remove all your personal information
    - Delete your saved articles and preferences
    - Cancel any active subscriptions
    - Remove your comment history
    """)
    
    if st.checkbox("I understand that this action cannot be undone"):
        confirmation_text = st.text_input("Type 'DELETE' to confirm")
        
        if confirmation_text == "DELETE":
            if st.button("🗑️ Permanently Delete Account", type="primary"):
                st.error("Account deletion functionality would be implemented here")
        else:
            st.info("Please type 'DELETE' to confirm account deletion")

def show_preferences(user: Dict):
    """Show and edit user preferences"""
    st.subheader("⚙️ Preferences")
    
    # Get current preferences
    current_prefs = get_user_preferences(user['id'])
    
    with st.form("preferences_form"):
        st.markdown("#### Content Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Language preference
            language = st.selectbox("Preferred Language", 
                                  ["English", "Spanish", "French", "German", "Chinese"],
                                  index=0 if current_prefs.get('language') == 'en' else 0)
            
            # News categories
            st.markdown("**Favorite Categories:**")
            categories = ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"]
            selected_categories = st.multiselect("Select your interests", categories,
                                               default=current_prefs.get('favorite_categories', []))
            
            # Reading preferences
            reading_speed = st.selectbox("Reading Speed", 
                                       ["Slow (150 wpm)", "Normal (200 wpm)", "Fast (250 wpm)"],
                                       index=1)
        
        with col2:
            # Location preferences
            auto_location = st.checkbox("Automatically detect my location", 
                                      value=current_prefs.get('auto_location', True))
            
            local_radius = st.slider("Local news radius (miles)", 25, 200, 
                                   current_prefs.get('local_radius', 75))
            
            # Content filtering
            st.markdown("**Content Filtering:**")
            show_breaking = st.checkbox("Show breaking news alerts", 
                                      value=current_prefs.get('show_breaking', True))
            
            filter_negative = st.checkbox("Filter out highly negative content", 
                                        value=current_prefs.get('filter_negative', False))
            
            show_opinions = st.checkbox("Show editorial opinions", 
                                      value=current_prefs.get('show_opinions', True))
        
        st.markdown("#### Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_notifications = st.checkbox("Email notifications", 
                                            value=current_prefs.get('email_notifications', True))
            
            breaking_alerts = st.checkbox("Breaking news alerts", 
                                        value=current_prefs.get('breaking_alerts', True))
            
            daily_digest = st.checkbox("Daily news digest", 
                                     value=current_prefs.get('daily_digest', False))
        
        with col2:
            weekly_summary = st.checkbox("Weekly summary", 
                                       value=current_prefs.get('weekly_summary', False))
            
            subscription_updates = st.checkbox("Subscription and billing updates", 
                                             value=current_prefs.get('subscription_updates', True))
            
            marketing_emails = st.checkbox("Marketing and promotional emails", 
                                         value=current_prefs.get('marketing_emails', False))
        
        st.markdown("#### Privacy Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            public_profile = st.checkbox("Make my profile public", 
                                       value=current_prefs.get('public_profile', False))
            
            share_reading_activity = st.checkbox("Share my reading activity", 
                                               value=current_prefs.get('share_activity', False))
        
        with col2:
            analytics_tracking = st.checkbox("Allow analytics tracking", 
                                           value=current_prefs.get('analytics_tracking', True))
            
            personalized_ads = st.checkbox("Show personalized advertisements", 
                                         value=current_prefs.get('personalized_ads', True))
        
        if st.form_submit_button("💾 Save Preferences"):
            # Create preferences object
            new_preferences = {
                'language': 'en' if language == 'English' else language.lower()[:2],
                'favorite_categories': selected_categories,
                'reading_speed': reading_speed,
                'auto_location': auto_location,
                'local_radius': local_radius,
                'show_breaking': show_breaking,
                'filter_negative': filter_negative,
                'show_opinions': show_opinions,
                'email_notifications': email_notifications,
                'breaking_alerts': breaking_alerts,
                'daily_digest': daily_digest,
                'weekly_summary': weekly_summary,
                'subscription_updates': subscription_updates,
                'marketing_emails': marketing_emails,
                'public_profile': public_profile,
                'share_activity': share_reading_activity,
                'analytics_tracking': analytics_tracking,
                'personalized_ads': personalized_ads
            }
            
            # Update preferences
            if update_user_preferences(user['id'], new_preferences):
                st.success("Preferences updated successfully!")
                st.session_state.preferences = new_preferences
                st.rerun()
            else:
                st.error("Error updating preferences. Please try again.")

def show_activity(user: Dict):
    """Show user activity and statistics"""
    st.subheader("📊 Your Activity")
    
    # Get user analytics
    user_analytics = get_user_analytics(user['id'], 30)
    
    # Activity summary
    st.markdown("#### Activity Summary (Last 30 Days)")
    
    if user_analytics and user_analytics.get('activities'):
        activities = user_analytics['activities']
        
        # Calculate metrics
        total_actions = sum(activity['count'] for activity in activities)
        article_reads = sum(activity['count'] for activity in activities if activity['action'] == 'article_read')
        searches = sum(activity['count'] for activity in activities if activity['action'] == 'search')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Actions", total_actions)
        
        with col2:
            st.metric("Articles Read", article_reads)
        
        with col3:
            st.metric("Searches", searches)
        
        with col4:
            st.metric("Active Days", len(set(activity['date'] for activity in activities)))
        
        # Activity chart
        if activities:
            import pandas as pd
            import plotly.express as px
            
            df_activity = pd.DataFrame(activities)
            
            # Group by date
            daily_activity = df_activity.groupby('date')['count'].sum().reset_index()
            
            fig = px.line(daily_activity, x='date', y='count',
                         title='Daily Activity',
                         labels={'count': 'Actions', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity details
        st.markdown("#### Recent Activity")
        
        for activity in activities[:10]:  # Show last 10 activities
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    action_icon = {
                        'article_read': '📖',
                        'search': '🔍',
                        'page_view': '👁️',
                        'subscription': '💳',
                        'ad_interaction': '📺'
                    }.get(activity['action'], '📝')
                    
                    st.write(f"{action_icon} {activity['action'].replace('_', ' ').title()}")
                    st.write(f"Target: {activity['page_view']}")
                
                with col2:
                    st.write(f"**Count:** {activity['count']}")
                
                with col3:
                    st.write(f"**Date:** {format_date(activity['date'])}")
                
                st.divider()
    else:
        st.info("No activity data available yet. Start reading to see your activity here!")
    
    # Saved articles
    st.markdown("#### 📑 Your Saved Articles")
    
    saved_articles = get_user_saved_articles(user['id'])
    
    if saved_articles:
        st.write(f"You have **{len(saved_articles)}** saved articles")
        
        # Show recent saved articles
        for article in saved_articles[:5]:
            with st.expander(f"📰 {article['title'][:80]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Source:** {article.get('source', 'Unknown')}")
                    st.write(f"**Category:** {article.get('category', 'General')}")
                    if article.get('summary'):
                        st.write(f"**Summary:** {article['summary'][:200]}...")
                
                with col2:
                    st.write(f"**Saved:** {format_date(article.get('saved_at'))}")
                    
                    if st.button("🔗 Read", key=f"read_saved_{article['id']}"):
                        st.info("Opening article...")
                    
                    if st.button("🗑️ Remove", key=f"remove_saved_{article['id']}"):
                        # Remove from saved articles
                        try:
                            delete_query = """
                            DELETE FROM user_articles 
                            WHERE user_id = %s AND article_id = %s AND action = 'saved'
                            """
                            db.execute_query(delete_query, (user['id'], article['id']), fetch=False)
                            st.success("Article removed from saved list!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error removing article: {e}")
        
        if len(saved_articles) > 5:
            st.info(f"... and {len(saved_articles) - 5} more saved articles")
    else:
        st.info("No saved articles yet. Save articles while reading to see them here!")

def show_subscription_info(user: Dict):
    """Show subscription information and management"""
    st.subheader("💳 Subscription")
    
    # Get subscription status
    subscription_status = check_subscription_status(user)
    
    # Current subscription info
    st.markdown("#### Current Subscription")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tier = subscription_status.get('tier', 'free').title()
        st.metric("Current Plan", tier)
    
    with col2:
        if subscription_status.get('expires_at'):
            expires = format_date(subscription_status['expires_at'])
            st.metric("Expires", expires)
        else:
            st.metric("Status", "No expiration")
    
    with col3:
        features_count = len(subscription_status.get('features', []))
        st.metric("Features", features_count)
    
    # Subscription features
    if subscription_status.get('features'):
        st.markdown("#### Your Plan Features")
        
        for feature in subscription_status['features']:
            st.write(f"✅ {feature}")
    
    # Subscription management
    if subscription_status.get('premium'):
        st.markdown("#### Manage Subscription")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 View Billing History"):
                show_billing_history(user['id'])
        
        with col2:
            if st.button("💳 Update Payment Method"):
                st.info("Payment method update coming soon!")
        
        with col3:
            if st.button("❌ Cancel Subscription"):
                show_cancel_subscription_form(user['id'])
    else:
        st.markdown("#### Upgrade Your Plan")
        st.info("Upgrade to a premium plan to unlock additional features and remove ads.")
        
        if st.button("🚀 View Plans"):
            display_subscription_plans()

def show_billing_history(user_id: int):
    """Show billing history"""
    st.markdown("#### 📄 Billing History")
    
    try:
        billing_query = """
        SELECT * FROM subscriptions 
        WHERE user_id = %s 
        ORDER BY subscription_date DESC
        """
        
        billing_history = db.execute_query(billing_query, (user_id,))
        
        if billing_history:
            for bill in billing_history:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**Plan:** {bill['tier'].title()}")
                    
                    with col2:
                        st.write(f"**Amount:** ${bill['amount']:.2f}")
                    
                    with col3:
                        st.write(f"**Date:** {format_date(bill['subscription_date'])}")
                    
                    with col4:
                        status_color = {"active": "🟢", "cancelled": "🔴", "expired": "🟡"}.get(bill['status'], "⚫")
                        st.write(f"**Status:** {status_color} {bill['status'].title()}")
                    
                    st.divider()
        else:
            st.info("No billing history found")
    
    except Exception as e:
        st.error(f"Error loading billing history: {e}")

def show_cancel_subscription_form(user_id: int):
    """Show subscription cancellation form"""
    st.warning("⚠️ Cancel Subscription")
    
    st.markdown("""
    **Are you sure you want to cancel your subscription?**
    
    If you cancel:
    - You'll lose access to premium features at the end of your billing period
    - Your saved preferences will be retained
    - You can resubscribe at any time
    """)
    
    reason = st.selectbox("Reason for cancelling (optional)", [
        "Too expensive",
        "Not using it enough", 
        "Found a better alternative",
        "Technical issues",
        "Other"
    ])
    
    feedback = st.text_area("Additional feedback (optional)", 
                           placeholder="Help us improve by sharing your feedback...")
    
    if st.checkbox("I understand that I'll lose premium features"):
        if st.button("❌ Cancel Subscription", type="primary"):
            try:
                from subscription import subscription_manager
                result = subscription_manager.cancel_subscription(user_id)
                
                if result:
                    st.success("Subscription cancelled successfully. You'll retain access until the end of your billing period.")
                    st.rerun()
                else:
                    st.error("Error cancelling subscription. Please contact support.")
            
            except Exception as e:
                st.error(f"Error cancelling subscription: {e}")

def show_appearance_settings(user: Dict):
    """Show appearance and theme settings"""
    st.subheader("🎨 Appearance")
    
    # Get current preferences
    current_prefs = get_user_preferences(user['id'])
    
    with st.form("appearance_form"):
        st.markdown("#### Theme Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Theme selection
            theme_options = ["Default", "Dark", "Light", "Blue", "Green", "Purple"]
            current_theme = current_prefs.get('theme', 'Default')
            selected_theme = st.selectbox("Theme", theme_options, 
                                        index=theme_options.index(current_theme) if current_theme in theme_options else 0)
            
            # Font size
            font_sizes = ["Small", "Medium", "Large", "Extra Large"]
            current_font = current_prefs.get('font_size', 'Medium')
            selected_font = st.selectbox("Font Size", font_sizes,
                                       index=font_sizes.index(current_font) if current_font in font_sizes else 1)
        
        with col2:
            # Display preferences
            compact_view = st.checkbox("Compact article view", 
                                     value=current_prefs.get('compact_view', False))
            
            show_images = st.checkbox("Show article images", 
                                    value=current_prefs.get('show_images', True))
            
            auto_play_audio = st.checkbox("Auto-play text-to-speech", 
                                        value=current_prefs.get('auto_play_audio', False))
        
        st.markdown("#### Layout Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sidebar_position = st.selectbox("Sidebar Position", ["Left", "Right"],
                                          index=0 if current_prefs.get('sidebar_position') == 'left' else 1)
            
            articles_per_page = st.slider("Articles per page", 5, 50, 
                                        current_prefs.get('articles_per_page', 20))
        
        with col2:
            show_categories = st.checkbox("Show category filters", 
                                        value=current_prefs.get('show_categories', True))
            
            show_timestamps = st.checkbox("Show article timestamps", 
                                        value=current_prefs.get('show_timestamps', True))
        
        if st.form_submit_button("🎨 Apply Theme"):
            # Update appearance preferences
            appearance_prefs = current_prefs.copy()
            appearance_prefs.update({
                'theme': selected_theme,
                'font_size': selected_font,
                'compact_view': compact_view,
                'show_images': show_images,
                'auto_play_audio': auto_play_audio,
                'sidebar_position': sidebar_position.lower(),
                'articles_per_page': articles_per_page,
                'show_categories': show_categories,
                'show_timestamps': show_timestamps
            })
            
            if update_user_preferences(user['id'], appearance_prefs):
                st.success("Appearance settings updated!")
                st.session_state.preferences = appearance_prefs
                st.rerun()
            else:
                st.error("Error updating appearance settings.")
    
    # Theme preview
    st.markdown("#### 🎭 Theme Preview")
    
    # Create a preview of the selected theme
    preview_theme = st.session_state.get('preview_theme', current_prefs.get('theme', 'Default'))
    
    theme_colors = {
        "Default": {"primary": "#1A73E8", "secondary": "#34A853", "background": "#F8F9FA"},
        "Dark": {"primary": "#BB86FC", "secondary": "#03DAC6", "background": "#121212"},
        "Light": {"primary": "#6200EE", "secondary": "#03DAC5", "background": "#FFFFFF"},
        "Blue": {"primary": "#2196F3", "secondary": "#21CBF3", "background": "#E3F2FD"},
        "Green": {"primary": "#4CAF50", "secondary": "#8BC34A", "background": "#E8F5E9"},
        "Purple": {"primary": "#9C27B0", "secondary": "#E91E63", "background": "#F3E5F5"}
    }
    
    colors = theme_colors.get(preview_theme, theme_colors["Default"])
    
    st.markdown(f"""
    <div style="
        background: {colors['background']};
        border: 2px solid {colors['primary']};
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    ">
        <h4 style="color: {colors['primary']}; margin-top: 0;">Sample News Article</h4>
        <p style="color: #666; margin-bottom: 10px;">
            This is how articles will look with the {preview_theme} theme. 
            The colors and styling will be applied throughout the application.
        </p>
        <div style="
            background: {colors['secondary']};
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            display: inline-block;
            font-size: 14px;
        ">
            Sample Category
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_profile()
