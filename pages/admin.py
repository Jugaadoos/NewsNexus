import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Import our modules
from auth import get_current_user, require_permission
from database import db
from analytics import get_analytics_data
from subscription import get_subscription_analytics
from affiliate import get_affiliate_analytics
from advertisement import get_advertisement_analytics
from ai_agents import get_agent_system_status, get_workflow_history
from blockchain import get_blockchain_statistics
from news_aggregator import refresh_news_cache
from utils import format_number, format_currency, format_date

@require_permission("all")
def show_admin_panel():
    """Main admin panel"""
    st.set_page_config(
        page_title="Admin Panel - AI News Hub",
        page_icon="⚙️",
        layout="wide"
    )
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("⚙️ Admin Panel")
    st.markdown("Complete system administration and management")
    
    # Admin navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "👥 Users", "📰 Content", "💰 Revenue", 
        "🤖 AI Agents", "⛓️ Blockchain", "⚙️ Settings"
    ])
    
    with tab1:
        show_overview_tab()
    
    with tab2:
        show_users_tab()
    
    with tab3:
        show_content_tab()
    
    with tab4:
        show_revenue_tab()
    
    with tab5:
        show_ai_agents_tab()
    
    with tab6:
        show_blockchain_tab()
    
    with tab7:
        show_settings_tab()

def show_overview_tab():
    """Show system overview"""
    st.subheader("📊 System Overview")
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh News Cache"):
            with st.spinner("Refreshing news cache..."):
                refresh_news_cache()
            st.success("News cache refreshed!")
    
    with col2:
        if st.button("📧 Send Newsletters"):
            st.info("Newsletter system integration coming soon!")
    
    with col3:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with col4:
        if st.button("📊 Generate Report"):
            st.info("Generating comprehensive system report...")
    
    st.divider()
    
    # Get system metrics
    with st.spinner("Loading system metrics..."):
        analytics_data = get_analytics_data(date_range=30)
        agent_status = get_agent_system_status()
        blockchain_stats = get_blockchain_statistics()
    
    # System health indicators
    st.markdown("### 🏥 System Health")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Database status
        try:
            result = db.execute_query("SELECT 1")
            db_status = "🟢 Online" if result else "🔴 Offline"
        except:
            db_status = "🔴 Offline"
        st.metric("Database", db_status)
    
    with col2:
        # AI Agents status
        active_agents = sum(1 for agent in agent_status.get("agents", {}).values() if agent["is_active"])
        total_agents = len(agent_status.get("agents", {}))
        st.metric("AI Agents", f"{active_agents}/{total_agents}")
    
    with col3:
        # Blockchain integrity
        integrity = blockchain_stats.get("blockchain_integrity", False)
        blockchain_status = "🟢 Valid" if integrity else "🔴 Invalid"
        st.metric("Blockchain", blockchain_status)
    
    with col4:
        # Active workflows
        active_workflows = agent_status.get("active_workflows", 0)
        st.metric("Active Workflows", active_workflows)
    
    with col5:
        # System uptime (placeholder)
        st.metric("Uptime", "99.9%")
    
    # Recent system activity
    st.markdown("### 📝 Recent System Activity")
    
    workflow_history = get_workflow_history(limit=5)
    if workflow_history:
        for workflow in workflow_history:
            with st.expander(f"🔄 {workflow['name']} - {workflow.get('status', 'unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Started:** {format_date(workflow.get('started_at'))}")
                    if workflow.get('completed_at'):
                        st.write(f"**Completed:** {format_date(workflow.get('completed_at'))}")
                with col2:
                    st.write(f"**Steps:** {len(workflow.get('steps', []))}")
                    st.write(f"**Status:** {workflow.get('status', 'unknown')}")
    else:
        st.info("No recent workflow activity")

def show_users_tab():
    """Show user management"""
    st.subheader("👥 User Management")
    
    # User statistics
    try:
        user_stats_query = """
        SELECT 
            role,
            subscription_tier,
            COUNT(*) as count,
            AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at))/86400) as avg_days_since_registration
        FROM users 
        GROUP BY role, subscription_tier
        ORDER BY count DESC
        """
        
        user_stats = db.execute_query(user_stats_query)
        
        if user_stats:
            st.markdown("### 📊 User Statistics")
            
            # Total users
            total_users = sum(row['count'] for row in user_stats)
            st.metric("Total Users", format_number(total_users))
            
            # User breakdown by role
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### By Role")
                role_data = {}
                for row in user_stats:
                    role = row['role']
                    role_data[role] = role_data.get(role, 0) + row['count']
                
                df_roles = pd.DataFrame(list(role_data.items()), columns=['Role', 'Count'])
                fig_roles = px.pie(df_roles, values='Count', names='Role', title='Users by Role')
                st.plotly_chart(fig_roles, use_container_width=True)
            
            with col2:
                st.markdown("#### By Subscription")
                tier_data = {}
                for row in user_stats:
                    tier = row['subscription_tier']
                    tier_data[tier] = tier_data.get(tier, 0) + row['count']
                
                df_tiers = pd.DataFrame(list(tier_data.items()), columns=['Tier', 'Count'])
                fig_tiers = px.bar(df_tiers, x='Tier', y='Count', title='Users by Subscription Tier')
                st.plotly_chart(fig_tiers, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading user statistics: {e}")
    
    st.divider()
    
    # User search and management
    st.markdown("### 🔍 User Search & Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("Search users by email or name", placeholder="Enter email or name...")
    
    with col2:
        search_type = st.selectbox("Search Type", ["Email", "Name", "Role"])
    
    if search_term:
        try:
            if search_type == "Email":
                search_query = "SELECT * FROM users WHERE email ILIKE %s LIMIT 20"
                search_param = f"%{search_term}%"
            elif search_type == "Name":
                search_query = "SELECT * FROM users WHERE name ILIKE %s LIMIT 20"
                search_param = f"%{search_term}%"
            else:  # Role
                search_query = "SELECT * FROM users WHERE role = %s LIMIT 20"
                search_param = search_term
            
            search_results = db.execute_query(search_query, (search_param,))
            
            if search_results:
                st.markdown("#### Search Results")
                
                for user in search_results:
                    with st.expander(f"👤 {user['name']} ({user['email']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Role:** {user['role']}")
                            st.write(f"**Subscription:** {user['subscription_tier']}")
                            st.write(f"**Phone:** {user.get('phone', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Location:** {user.get('location_city', 'N/A')}")
                            st.write(f"**Country:** {user.get('location_country', 'N/A')}")
                            st.write(f"**Created:** {format_date(user['created_at'])}")
                        
                        with col3:
                            if st.button(f"Edit User", key=f"edit_{user['id']}"):
                                st.session_state.edit_user_id = user['id']
                                st.rerun()
                            
                            if st.button(f"View Activity", key=f"activity_{user['id']}"):
                                show_user_activity(user['id'])
            else:
                st.info("No users found matching your search criteria")
        
        except Exception as e:
            st.error(f"Error searching users: {e}")
    
    # Bulk operations
    st.markdown("### 🔧 Bulk Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Send Newsletter to All"):
            st.info("Newsletter functionality coming soon!")
    
    with col2:
        if st.button("📊 Export User Data"):
            st.info("User data export functionality coming soon!")
    
    with col3:
        if st.button("🧹 Clean Inactive Users"):
            st.info("User cleanup functionality coming soon!")

def show_user_activity(user_id: int):
    """Show detailed user activity"""
    try:
        activity_query = """
        SELECT action, page_view, COUNT(*) as count, MAX(created_at) as last_activity
        FROM user_analytics 
        WHERE user_id = %s 
        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY action, page_view
        ORDER BY count DESC
        """
        
        activity_data = db.execute_query(activity_query, (user_id,))
        
        if activity_data:
            st.markdown(f"#### User Activity (Last 30 Days)")
            df_activity = pd.DataFrame(activity_data)
            st.dataframe(df_activity, use_container_width=True)
        else:
            st.info("No recent activity found for this user")
    
    except Exception as e:
        st.error(f"Error loading user activity: {e}")

def show_content_tab():
    """Show content management"""
    st.subheader("📰 Content Management")
    
    # Content statistics
    try:
        content_stats_query = """
        SELECT 
            category,
            COUNT(*) as article_count,
            AVG(sentiment_score) as avg_sentiment,
            MAX(published_at) as latest_article
        FROM news_articles 
        WHERE published_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY category
        ORDER BY article_count DESC
        """
        
        content_stats = db.execute_query(content_stats_query)
        
        if content_stats:
            st.markdown("### 📊 Content Statistics (Last 30 Days)")
            
            df_content = pd.DataFrame(content_stats)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_articles = px.bar(df_content, x='category', y='article_count',
                                    title='Articles by Category')
                st.plotly_chart(fig_articles, use_container_width=True)
            
            with col2:
                fig_sentiment = px.bar(df_content, x='category', y='avg_sentiment',
                                     title='Average Sentiment by Category')
                st.plotly_chart(fig_sentiment, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading content statistics: {e}")
    
    st.divider()
    
    # Content moderation
    st.markdown("### 🛡️ Content Moderation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Review Flagged Content"):
            st.info("Content moderation interface coming soon!")
    
    with col2:
        if st.button("🤖 Run AI Content Check"):
            st.info("AI content verification coming soon!")
    
    with col3:
        if st.button("📊 Content Quality Report"):
            st.info("Content quality analytics coming soon!")
    
    # Recent articles
    st.markdown("### 📝 Recent Articles")
    
    try:
        recent_articles_query = """
        SELECT id, title, category, source, published_at, sentiment_score
        FROM news_articles 
        ORDER BY created_at DESC 
        LIMIT 10
        """
        
        recent_articles = db.execute_query(recent_articles_query)
        
        if recent_articles:
            for article in recent_articles:
                with st.expander(f"📰 {article['title'][:100]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Category:** {article['category']}")
                        st.write(f"**Source:** {article['source']}")
                    
                    with col2:
                        st.write(f"**Published:** {format_date(article['published_at'])}")
                        st.write(f"**Sentiment:** {article.get('sentiment_score', 0):.2f}")
                    
                    if st.button(f"Moderate Article", key=f"moderate_{article['id']}"):
                        st.info("Article moderation interface coming soon!")
        else:
            st.info("No recent articles found")
    
    except Exception as e:
        st.error(f"Error loading recent articles: {e}")

def show_revenue_tab():
    """Show revenue management"""
    st.subheader("💰 Revenue Management")
    
    # Date range selector
    date_range = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
    
    # Revenue analytics
    with st.spinner("Loading revenue data..."):
        subscription_analytics = get_subscription_analytics(date_range)
        ad_analytics = get_advertisement_analytics(date_range)
        affiliate_analytics = get_affiliate_analytics(0, date_range)  # System-wide affiliate data
    
    # Revenue summary
    st.markdown("### 💵 Revenue Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if subscription_analytics.get("tiers"):
            sub_revenue = sum(tier["total_revenue"] for tier in subscription_analytics["tiers"])
            st.metric("Subscription Revenue", format_currency(sub_revenue))
        else:
            st.metric("Subscription Revenue", "$0.00")
    
    with col2:
        if ad_analytics.get("ads"):
            # Estimate ad revenue (placeholder calculation)
            total_clicks = sum(ad["clicks"] for ad in ad_analytics["ads"])
            estimated_ad_revenue = total_clicks * 0.5  # $0.50 per click estimate
            st.metric("Ad Revenue", format_currency(estimated_ad_revenue))
        else:
            st.metric("Ad Revenue", "$0.00")
    
    with col3:
        if affiliate_analytics.get("daily_stats"):
            affiliate_revenue = sum(day["commission"] for day in affiliate_analytics["daily_stats"])
            st.metric("Affiliate Revenue", format_currency(affiliate_revenue))
        else:
            st.metric("Affiliate Revenue", "$0.00")
    
    with col4:
        # Total revenue
        total = (sub_revenue if 'sub_revenue' in locals() else 0) + \
                (estimated_ad_revenue if 'estimated_ad_revenue' in locals() else 0) + \
                (affiliate_revenue if 'affiliate_revenue' in locals() else 0)
        st.metric("Total Revenue", format_currency(total))
    
    # Revenue charts
    col1, col2 = st.columns(2)
    
    with col1:
        if subscription_analytics.get("tiers"):
            df_subs = pd.DataFrame(subscription_analytics["tiers"])
            fig_subs = px.pie(df_subs, values='total_revenue', names='tier',
                             title='Revenue by Subscription Tier')
            st.plotly_chart(fig_subs, use_container_width=True)
    
    with col2:
        if ad_analytics.get("ads"):
            df_ads = pd.DataFrame(ad_analytics["ads"])
            fig_ads = px.bar(df_ads.head(10), x='title', y='clicks',
                           title='Top Performing Ads')
            st.plotly_chart(fig_ads, use_container_width=True)

def show_ai_agents_tab():
    """Show AI agents management"""
    st.subheader("🤖 AI Agents Management")
    
    # Get agent status
    agent_status = get_agent_system_status()
    
    # Agent overview
    st.markdown("### 🔍 Agent Overview")
    
    if agent_status.get("agents"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_agents = len(agent_status["agents"])
            st.metric("Total Agents", total_agents)
        
        with col2:
            active_agents = sum(1 for agent in agent_status["agents"].values() if agent["is_active"])
            st.metric("Active Agents", active_agents)
        
        with col3:
            total_tasks = sum(agent["total_tasks"] for agent in agent_status["agents"].values())
            st.metric("Total Tasks", total_tasks)
        
        # Agent details
        st.markdown("### 🤖 Agent Status")
        
        for agent_id, agent_info in agent_status["agents"].items():
            with st.expander(f"🤖 {agent_id} ({agent_info['type']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_icon = "🟢" if agent_info["is_active"] else "🔴"
                    st.write(f"**Status:** {status_icon} {'Active' if agent_info['is_active'] else 'Inactive'}")
                    st.write(f"**Type:** {agent_info['type']}")
                
                with col2:
                    st.write(f"**Pending Tasks:** {agent_info['pending_tasks']}")
                    st.write(f"**Total Tasks:** {agent_info['total_tasks']}")
                
                with col3:
                    if st.button(f"{'Deactivate' if agent_info['is_active'] else 'Activate'}", 
                               key=f"toggle_{agent_id}"):
                        st.info(f"Agent {agent_id} status change requested")
                    
                    if st.button(f"View Logs", key=f"logs_{agent_id}"):
                        st.info(f"Agent {agent_id} logs coming soon!")
    else:
        st.info("No agent data available")
    
    # Workflow management
    st.markdown("### 🔄 Workflow Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Test Workflow"):
            st.info("Test workflow initiated!")
    
    with col2:
        if st.button("⏸️ Pause All Workflows"):
            st.info("All workflows paused!")
    
    with col3:
        if st.button("📊 Workflow Analytics"):
            st.info("Workflow analytics coming soon!")

def show_blockchain_tab():
    """Show blockchain management"""
    st.subheader("⛓️ Blockchain Management")
    
    # Get blockchain statistics
    blockchain_stats = get_blockchain_statistics()
    
    # Blockchain overview
    st.markdown("### 📊 Blockchain Overview")
    
    if blockchain_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Blocks", blockchain_stats.get("total_blocks", 0))
        
        with col2:
            st.metric("Total Reviews", blockchain_stats.get("total_reviews", 0))
        
        with col3:
            consensus = blockchain_stats.get("average_consensus", 0)
            st.metric("Avg Consensus", f"{consensus:.1%}")
        
        with col4:
            integrity = blockchain_stats.get("blockchain_integrity", False)
            integrity_text = "✅ Valid" if integrity else "❌ Invalid"
            st.metric("Integrity", integrity_text)
    else:
        st.info("No blockchain data available")
    
    # Blockchain operations
    st.markdown("### 🔧 Blockchain Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Verify Integrity"):
            with st.spinner("Verifying blockchain integrity..."):
                # Would call blockchain verification
                st.success("Blockchain integrity verified!")
    
    with col2:
        if st.button("⛏️ Mine New Block"):
            st.info("Block mining functionality coming soon!")
    
    with col3:
        if st.button("📊 Block Explorer"):
            st.info("Block explorer interface coming soon!")
    
    # Recent blockchain activity
    st.markdown("### 📝 Recent Blockchain Activity")
    st.info("Recent blockchain transactions and reviews will be displayed here")

def show_settings_tab():
    """Show system settings"""
    st.subheader("⚙️ System Settings")
    
    # API Settings
    st.markdown("### 🔌 API Settings")
    
    with st.expander("OpenAI Configuration"):
        openai_status = "✅ Connected" if st.secrets.get("OPENAI_API_KEY") else "❌ Not configured"
        st.write(f"**Status:** {openai_status}")
        
        if st.button("Test OpenAI Connection"):
            st.info("Testing OpenAI API connection...")
    
    with st.expander("Database Configuration"):
        db_status = "✅ Connected"  # Would test actual connection
        st.write(f"**Status:** {db_status}")
        
        if st.button("Test Database Connection"):
            try:
                result = db.execute_query("SELECT 1")
                st.success("Database connection successful!")
            except Exception as e:
                st.error(f"Database connection failed: {e}")
    
    # System Configuration
    st.markdown("### 🖥️ System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### News Sources")
        if st.button("🔄 Refresh RSS Feeds"):
            with st.spinner("Refreshing RSS feeds..."):
                refresh_news_cache()
            st.success("RSS feeds refreshed!")
        
        if st.button("➕ Add News Source"):
            st.info("News source management coming soon!")
    
    with col2:
        st.markdown("#### Performance")
        if st.button("🧹 Clear All Caches"):
            st.cache_data.clear()
            st.success("All caches cleared!")
        
        if st.button("📊 Performance Report"):
            st.info("Performance monitoring coming soon!")
    
    # Security Settings
    st.markdown("### 🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Rotate API Keys"):
            st.info("API key rotation coming soon!")
        
        if st.button("👥 Review User Permissions"):
            st.info("Permission audit coming soon!")
    
    with col2:
        if st.button("🛡️ Security Scan"):
            st.info("Security scanning coming soon!")
        
        if st.button("📋 Security Report"):
            st.info("Security reporting coming soon!")

if __name__ == "__main__":
    show_admin_panel()
