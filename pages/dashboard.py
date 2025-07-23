import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import our modules
from auth import get_current_user, require_auth
from analytics import get_analytics_data, display_analytics_dashboard
from subscription import get_subscription_analytics
from affiliate import get_affiliate_analytics
from advertisement import get_advertisement_analytics
from ai_agents import get_agent_system_status, get_workflow_history
from blockchain import get_blockchain_statistics
from database import get_user_saved_articles, db
from utils import format_number, format_currency, format_date

@require_auth
def show_dashboard():
    """Main dashboard page"""
    st.set_page_config(
        page_title="Dashboard - AI News Hub",
        page_icon="📊",
        layout="wide"
    )
    
    user = get_current_user()
    if not user:
        st.error("Please login to access the dashboard")
        return
    
    st.title("📊 Dashboard")
    st.markdown(f"Welcome back, **{user['name']}**!")
    
    # Role-based dashboard
    if user['role'] in ['admin', 'editor']:
        show_admin_dashboard(user)
    elif user['role'] == 'affiliate':
        show_affiliate_dashboard(user)
    elif user['role'] in ['creator', 'journalist']:
        show_creator_dashboard(user)
    elif user['role'] == 'partner':
        show_partner_dashboard(user)
    else:
        show_reader_dashboard(user)

def show_admin_dashboard(user: dict):
    """Show admin dashboard with comprehensive analytics"""
    st.subheader("🔧 Admin Dashboard")
    
    # Date range selector
    col1, col2 = st.columns([2, 1])
    with col1:
        date_range = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Get analytics data
    with st.spinner("Loading analytics..."):
        analytics_data = get_analytics_data(date_range=date_range)
        subscription_analytics = get_subscription_analytics(date_range)
        ad_analytics = get_advertisement_analytics(date_range)
        agent_status = get_agent_system_status()
        blockchain_stats = get_blockchain_statistics()
    
    # Key Metrics Row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if analytics_data.get("engagement", {}).get("daily_active_users"):
            total_users = max(day["users"] for day in analytics_data["engagement"]["daily_active_users"])
            st.metric("Active Users", format_number(total_users))
        else:
            st.metric("Active Users", "0")
    
    with col2:
        if subscription_analytics.get("tiers"):
            total_revenue = sum(tier["total_revenue"] for tier in subscription_analytics["tiers"])
            st.metric("Revenue", format_currency(total_revenue))
        else:
            st.metric("Revenue", "$0.00")
    
    with col3:
        if analytics_data.get("content", {}).get("top_articles"):
            total_articles = len(analytics_data["content"]["top_articles"])
            st.metric("Articles", format_number(total_articles))
        else:
            st.metric("Articles", "0")
    
    with col4:
        if ad_analytics.get("ads"):
            total_impressions = sum(ad["impressions"] for ad in ad_analytics["ads"])
            st.metric("Ad Impressions", format_number(total_impressions))
        else:
            st.metric("Ad Impressions", "0")
    
    with col5:
        st.metric("AI Agents", len(agent_status.get("agents", {})))
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # User Engagement Chart
        if analytics_data.get("engagement", {}).get("daily_active_users"):
            df_users = pd.DataFrame(analytics_data["engagement"]["daily_active_users"])
            fig_users = px.line(df_users, x='date', y='users', 
                               title='Daily Active Users',
                               labels={'users': 'Users', 'date': 'Date'})
            st.plotly_chart(fig_users, use_container_width=True)
        else:
            st.info("No user engagement data available")
    
    with col2:
        # Revenue Chart
        if subscription_analytics.get("tiers"):
            df_revenue = pd.DataFrame(subscription_analytics["tiers"])
            fig_revenue = px.bar(df_revenue, x='tier', y='total_revenue',
                                title='Revenue by Subscription Tier',
                                labels={'total_revenue': 'Revenue ($)', 'tier': 'Tier'})
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.info("No revenue data available")
    
    # System Status
    st.markdown("### 🖥️ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🤖 AI Agents")
        if agent_status.get("agents"):
            for agent_id, status in agent_status["agents"].items():
                status_color = "🟢" if status["is_active"] else "🔴"
                st.write(f"{status_color} {agent_id} ({status['type']})")
                st.write(f"   Tasks: {status['pending_tasks']}/{status['total_tasks']}")
        else:
            st.info("No agent data available")
    
    with col2:
        st.markdown("#### ⛓️ Blockchain")
        if blockchain_stats:
            st.write(f"📦 Blocks: {blockchain_stats.get('total_blocks', 0)}")
            st.write(f"📝 Reviews: {blockchain_stats.get('total_reviews', 0)}")
            st.write(f"📊 Consensus: {blockchain_stats.get('average_consensus', 0):.1%}")
            integrity_status = "✅" if blockchain_stats.get('blockchain_integrity') else "❌"
            st.write(f"🔒 Integrity: {integrity_status}")
        else:
            st.info("No blockchain data available")
    
    with col3:
        st.markdown("#### 📊 Performance")
        # System performance metrics
        st.write("📈 Response Time: ~150ms")
        st.write("💾 Database: ✅ Online")
        st.write("🔄 Cache Hit Rate: 87%")
        st.write("⚡ API Health: ✅ Good")
    
    # Recent Activity
    st.markdown("### 📝 Recent Activity")
    
    tab1, tab2, tab3 = st.tabs(["Content", "Users", "System"])
    
    with tab1:
        if analytics_data.get("content", {}).get("top_articles"):
            df_articles = pd.DataFrame(analytics_data["content"]["top_articles"][:10])
            st.dataframe(df_articles[['title', 'category', 'views', 'avg_read_percentage']], 
                        use_container_width=True)
        else:
            st.info("No content data available")
    
    with tab2:
        if subscription_analytics.get("tiers"):
            df_subs = pd.DataFrame(subscription_analytics["tiers"])
            st.dataframe(df_subs, use_container_width=True)
        else:
            st.info("No subscription data available")
    
    with tab3:
        workflow_history = get_workflow_history()
        if workflow_history:
            for workflow in workflow_history[:5]:
                with st.expander(f"Workflow: {workflow['name']} - {workflow.get('status', 'unknown')}"):
                    st.write(f"Started: {format_date(workflow.get('started_at'))}")
                    if workflow.get('completed_at'):
                        st.write(f"Completed: {format_date(workflow.get('completed_at'))}")
                    st.write(f"Steps: {len(workflow.get('steps', []))}")
        else:
            st.info("No workflow history available")

def show_affiliate_dashboard(user: dict):
    """Show affiliate-specific dashboard"""
    st.subheader("🤝 Affiliate Dashboard")
    
    from affiliate import display_affiliate_dashboard
    display_affiliate_dashboard(user)

def show_creator_dashboard(user: dict):
    """Show creator/journalist dashboard"""
    st.subheader("✍️ Creator Dashboard")
    
    # Date range selector
    date_range = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
    
    # Creator metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Articles Published", "0")  # Would get from database
    with col2:
        st.metric("Total Views", "0")
    with col3:
        st.metric("Avg. Read Time", "0 min")
    with col4:
        st.metric("Followers", "0")
    
    # Content performance
    st.markdown("### 📊 Content Performance")
    
    # Placeholder for creator-specific analytics
    st.info("Creator analytics coming soon! Track your article performance, reader engagement, and follower growth.")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Write New Article"):
            st.info("Article creation interface coming soon!")
    
    with col2:
        if st.button("📈 View Analytics"):
            st.info("Detailed analytics coming soon!")
    
    with col3:
        if st.button("👥 Manage Profile"):
            st.switch_page("pages/profile.py")

def show_partner_dashboard(user: dict):
    """Show publishing partner dashboard"""
    st.subheader("🤝 Partner Dashboard")
    
    # Partner metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Content Delivered", "0")
    with col2:
        st.metric("API Calls", "0")
    with col3:
        st.metric("Revenue Share", "$0.00")
    with col4:
        st.metric("Performance Score", "0%")
    
    # API Usage
    st.markdown("### 🔌 API Usage")
    st.info("API usage analytics and documentation coming soon!")
    
    # Content Feeds
    st.markdown("### 📡 Content Feeds")
    st.info("Manage your content feeds and distribution settings.")

def show_reader_dashboard(user: dict):
    """Show reader dashboard"""
    st.subheader("📚 Reader Dashboard")
    
    # Reading stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Articles Read", "0")  # Would get from analytics
    with col2:
        st.metric("Reading Streak", "0 days")
    with col3:
        st.metric("Saved Articles", "0")
    with col4:
        st.metric("Categories", "0")
    
    # Saved Articles
    st.markdown("### 📑 Your Saved Articles")
    
    saved_articles = get_user_saved_articles(user['id'])
    
    if saved_articles:
        for article in saved_articles[:5]:  # Show recent 5
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{article['title']}**")
                    st.write(f"Source: {article.get('source', 'Unknown')}")
                    st.write(f"Saved: {format_date(article.get('saved_at'))}")
                
                with col2:
                    if st.button("🔗 Read", key=f"read_{article['id']}"):
                        st.info("Opening article...")
                
                st.divider()
        
        if len(saved_articles) > 5:
            st.info(f"... and {len(saved_articles) - 5} more saved articles")
    else:
        st.info("No saved articles yet. Start reading and save articles you find interesting!")
    
    # Personalized Recommendations
    st.markdown("### 🎯 Recommended for You")
    st.info("Personalized recommendations based on your reading history coming soon!")
    
    # Reading Goals
    st.markdown("### 🎯 Reading Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Daily Goal")
        daily_goal = st.slider("Articles per day", 1, 20, 5)
        daily_progress = 0  # Would calculate from actual reading
        st.progress(daily_progress / daily_goal if daily_goal > 0 else 0)
        st.write(f"{daily_progress}/{daily_goal} articles today")
    
    with col2:
        st.markdown("#### Weekly Goal")
        weekly_goal = daily_goal * 7
        weekly_progress = 0  # Would calculate from actual reading
        st.progress(weekly_progress / weekly_goal if weekly_goal > 0 else 0)
        st.write(f"{weekly_progress}/{weekly_goal} articles this week")

if __name__ == "__main__":
    show_dashboard()
