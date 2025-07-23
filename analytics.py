import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import db
import streamlit as st

class AnalyticsManager:
    def __init__(self):
        self.metrics = {
            "engagement": ["page_views", "article_reads", "comments", "shares", "saves"],
            "user_behavior": ["session_duration", "bounce_rate", "return_visits"],
            "content": ["articles_published", "categories_viewed", "search_queries"],
            "revenue": ["subscription_revenue", "ad_revenue", "affiliate_commission"],
            "geographic": ["location_distribution", "regional_engagement"]
        }
    
    def track_page_view(self, user_id: int, page: str, session_id: str, metadata: Dict = None):
        """Track page view"""
        self.track_event(user_id, session_id, "page_view", page, metadata)
    
    def track_article_read(self, user_id: int, article_id: int, session_id: str, 
                          read_duration: int = None, read_percentage: float = None):
        """Track article read"""
        metadata = {}
        if read_duration:
            metadata["read_duration"] = read_duration
        if read_percentage:
            metadata["read_percentage"] = read_percentage
        
        self.track_event(user_id, session_id, "article_read", f"article_{article_id}", metadata)
    
    def track_search(self, user_id: int, query: str, session_id: str, results_count: int = 0):
        """Track search query"""
        metadata = {
            "query": query,
            "results_count": results_count
        }
        self.track_event(user_id, session_id, "search", "search_query", metadata)
    
    def track_subscription(self, user_id: int, tier: str, amount: float, session_id: str):
        """Track subscription event"""
        metadata = {
            "tier": tier,
            "amount": amount
        }
        self.track_event(user_id, session_id, "subscription", "subscription_created", metadata)
    
    def track_ad_interaction(self, user_id: int, ad_id: int, interaction_type: str, 
                           session_id: str, metadata: Dict = None):
        """Track ad interaction"""
        if not metadata:
            metadata = {}
        metadata["ad_id"] = ad_id
        metadata["interaction_type"] = interaction_type
        
        self.track_event(user_id, session_id, "ad_interaction", f"ad_{ad_id}", metadata)
    
    def track_event(self, user_id: int, session_id: str, event_type: str, 
                   event_target: str, metadata: Dict = None):
        """Generic event tracking"""
        try:
            query = """
            INSERT INTO user_analytics (user_id, session_id, page_view, action, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            db.execute_query(query, (
                user_id,
                session_id,
                event_target,
                event_type,
                json.dumps(metadata or {})
            ), fetch=False)
            
        except Exception as e:
            print(f"Error tracking event: {e}")
    
    def get_user_analytics(self, user_id: int, date_range: int = 30) -> Dict:
        """Get analytics for a specific user"""
        try:
            query = """
            SELECT 
                action,
                page_view,
                COUNT(*) as count,
                DATE(created_at) as date
            FROM user_analytics
            WHERE user_id = %s
            AND created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY action, page_view, DATE(created_at)
            ORDER BY date DESC
            """
            
            result = db.execute_query(query, (user_id, date_range))
            
            if result:
                return {
                    "activities": [
                        {
                            "action": row["action"],
                            "page_view": row["page_view"],
                            "count": row["count"],
                            "date": row["date"]
                        }
                        for row in result
                    ]
                }
            
            return {"activities": []}
            
        except Exception as e:
            print(f"Error getting user analytics: {e}")
            return {"activities": []}
    
    def get_content_analytics(self, date_range: int = 30) -> Dict:
        """Get content performance analytics"""
        try:
            # Article performance
            article_query = """
            SELECT 
                a.id,
                a.title,
                a.category,
                a.published_at,
                COUNT(ua.id) as views,
                AVG(CAST(ua.metadata->>'read_percentage' AS FLOAT)) as avg_read_percentage
            FROM news_articles a
            LEFT JOIN user_analytics ua ON ua.page_view = CONCAT('article_', a.id)
            WHERE a.published_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY a.id, a.title, a.category, a.published_at
            ORDER BY views DESC
            LIMIT 50
            """
            
            article_result = db.execute_query(article_query, (date_range,))
            
            # Category performance
            category_query = """
            SELECT 
                a.category,
                COUNT(ua.id) as views,
                COUNT(DISTINCT ua.user_id) as unique_readers
            FROM news_articles a
            LEFT JOIN user_analytics ua ON ua.page_view = CONCAT('article_', a.id)
            WHERE a.published_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY a.category
            ORDER BY views DESC
            """
            
            category_result = db.execute_query(category_query, (date_range,))
            
            # Search analytics
            search_query = """
            SELECT 
                ua.metadata->>'query' as search_query,
                COUNT(*) as search_count
            FROM user_analytics ua
            WHERE ua.action = 'search'
            AND ua.created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY ua.metadata->>'query'
            ORDER BY search_count DESC
            LIMIT 20
            """
            
            search_result = db.execute_query(search_query, (date_range,))
            
            return {
                "top_articles": [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "category": row["category"],
                        "views": row["views"],
                        "avg_read_percentage": float(row["avg_read_percentage"]) if row["avg_read_percentage"] else 0
                    }
                    for row in article_result
                ] if article_result else [],
                "category_performance": [
                    {
                        "category": row["category"],
                        "views": row["views"],
                        "unique_readers": row["unique_readers"]
                    }
                    for row in category_result
                ] if category_result else [],
                "top_searches": [
                    {
                        "query": row["search_query"],
                        "count": row["search_count"]
                    }
                    for row in search_result
                ] if search_result else []
            }
            
        except Exception as e:
            print(f"Error getting content analytics: {e}")
            return {"top_articles": [], "category_performance": [], "top_searches": []}
    
    def get_user_engagement_metrics(self, date_range: int = 30) -> Dict:
        """Get user engagement metrics"""
        try:
            # Daily active users
            dau_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT user_id) as daily_active_users
            FROM user_analytics
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            
            dau_result = db.execute_query(dau_query, (date_range,))
            
            # Session metrics
            session_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT session_id) as sessions,
                AVG(session_duration) as avg_session_duration
            FROM (
                SELECT 
                    session_id,
                    DATE(created_at) as created_at,
                    MAX(created_at) - MIN(created_at) as session_duration
                FROM user_analytics
                WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY session_id, DATE(created_at)
            ) session_data
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            
            session_result = db.execute_query(session_query, (date_range,))
            
            # Engagement actions
            engagement_query = """
            SELECT 
                action,
                COUNT(*) as count
            FROM user_analytics
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            AND action IN ('article_read', 'search', 'subscription', 'ad_interaction')
            GROUP BY action
            ORDER BY count DESC
            """
            
            engagement_result = db.execute_query(engagement_query, (date_range,))
            
            return {
                "daily_active_users": [
                    {
                        "date": row["date"],
                        "users": row["daily_active_users"]
                    }
                    for row in dau_result
                ] if dau_result else [],
                "session_metrics": [
                    {
                        "date": row["date"],
                        "sessions": row["sessions"],
                        "avg_duration": float(row["avg_session_duration"].total_seconds()) if row["avg_session_duration"] else 0
                    }
                    for row in session_result
                ] if session_result else [],
                "engagement_actions": [
                    {
                        "action": row["action"],
                        "count": row["count"]
                    }
                    for row in engagement_result
                ] if engagement_result else []
            }
            
        except Exception as e:
            print(f"Error getting engagement metrics: {e}")
            return {"daily_active_users": [], "session_metrics": [], "engagement_actions": []}
    
    def get_revenue_analytics(self, date_range: int = 30) -> Dict:
        """Get revenue analytics"""
        try:
            # Subscription revenue
            subscription_query = """
            SELECT 
                DATE(subscription_date) as date,
                tier,
                SUM(amount) as revenue,
                COUNT(*) as subscriptions
            FROM subscriptions
            WHERE subscription_date >= CURRENT_DATE - INTERVAL '%s days'
            AND status = 'active'
            GROUP BY DATE(subscription_date), tier
            ORDER BY date DESC
            """
            
            subscription_result = db.execute_query(subscription_query, (date_range,))
            
            # Ad revenue (from ad analytics)
            ad_query = """
            SELECT 
                DATE(ua.created_at) as date,
                COUNT(CASE WHEN ua.action = 'ad_interaction' THEN 1 END) as ad_clicks,
                COUNT(CASE WHEN ua.action = 'ad_impression' THEN 1 END) as ad_impressions
            FROM user_analytics ua
            WHERE ua.created_at >= CURRENT_DATE - INTERVAL '%s days'
            AND ua.action IN ('ad_interaction', 'ad_impression')
            GROUP BY DATE(ua.created_at)
            ORDER BY date DESC
            """
            
            ad_result = db.execute_query(ad_query, (date_range,))
            
            # Affiliate commission
            affiliate_query = """
            SELECT 
                DATE(created_at) as date,
                SUM(commission_earned) as total_commission,
                COUNT(*) as conversions
            FROM affiliate_clicks
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            AND conversion = TRUE
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            
            affiliate_result = db.execute_query(affiliate_query, (date_range,))
            
            return {
                "subscription_revenue": [
                    {
                        "date": row["date"],
                        "tier": row["tier"],
                        "revenue": float(row["revenue"]) if row["revenue"] else 0,
                        "subscriptions": row["subscriptions"]
                    }
                    for row in subscription_result
                ] if subscription_result else [],
                "ad_metrics": [
                    {
                        "date": row["date"],
                        "clicks": row["ad_clicks"],
                        "impressions": row["ad_impressions"],
                        "ctr": (row["ad_clicks"] / row["ad_impressions"] * 100) if row["ad_impressions"] > 0 else 0
                    }
                    for row in ad_result
                ] if ad_result else [],
                "affiliate_revenue": [
                    {
                        "date": row["date"],
                        "commission": float(row["total_commission"]) if row["total_commission"] else 0,
                        "conversions": row["conversions"]
                    }
                    for row in affiliate_result
                ] if affiliate_result else []
            }
            
        except Exception as e:
            print(f"Error getting revenue analytics: {e}")
            return {"subscription_revenue": [], "ad_metrics": [], "affiliate_revenue": []}
    
    def get_geographic_analytics(self, date_range: int = 30) -> Dict:
        """Get geographic analytics"""
        try:
            # User location distribution
            location_query = """
            SELECT 
                u.location_country,
                u.location_state,
                u.location_city,
                COUNT(DISTINCT ua.user_id) as users,
                COUNT(ua.id) as total_actions
            FROM user_analytics ua
            JOIN users u ON ua.user_id = u.id
            WHERE ua.created_at >= CURRENT_DATE - INTERVAL '%s days'
            AND u.location_country IS NOT NULL
            GROUP BY u.location_country, u.location_state, u.location_city
            ORDER BY users DESC
            LIMIT 100
            """
            
            location_result = db.execute_query(location_query, (date_range,))
            
            # Regional engagement
            regional_query = """
            SELECT 
                u.location_country,
                COUNT(DISTINCT ua.user_id) as users,
                COUNT(ua.id) as total_actions,
                AVG(EXTRACT(EPOCH FROM (MAX(ua.created_at) - MIN(ua.created_at)))) as avg_session_duration
            FROM user_analytics ua
            JOIN users u ON ua.user_id = u.id
            WHERE ua.created_at >= CURRENT_DATE - INTERVAL '%s days'
            AND u.location_country IS NOT NULL
            GROUP BY u.location_country
            ORDER BY users DESC
            """
            
            regional_result = db.execute_query(regional_query, (date_range,))
            
            return {
                "location_distribution": [
                    {
                        "country": row["location_country"],
                        "state": row["location_state"],
                        "city": row["location_city"],
                        "users": row["users"],
                        "actions": row["total_actions"]
                    }
                    for row in location_result
                ] if location_result else [],
                "regional_engagement": [
                    {
                        "country": row["location_country"],
                        "users": row["users"],
                        "actions": row["total_actions"],
                        "avg_session_duration": float(row["avg_session_duration"]) if row["avg_session_duration"] else 0
                    }
                    for row in regional_result
                ] if regional_result else []
            }
            
        except Exception as e:
            print(f"Error getting geographic analytics: {e}")
            return {"location_distribution": [], "regional_engagement": []}
    
    def create_dashboard_charts(self, analytics_data: Dict) -> Dict:
        """Create dashboard charts"""
        charts = {}
        
        try:
            # User engagement chart
            if analytics_data.get("engagement", {}).get("daily_active_users"):
                dau_data = analytics_data["engagement"]["daily_active_users"]
                df_dau = pd.DataFrame(dau_data)
                
                fig_dau = px.line(df_dau, x='date', y='users', 
                                 title='Daily Active Users',
                                 labels={'users': 'Active Users', 'date': 'Date'})
                charts["daily_active_users"] = fig_dau
            
            # Content performance chart
            if analytics_data.get("content", {}).get("category_performance"):
                category_data = analytics_data["content"]["category_performance"]
                df_category = pd.DataFrame(category_data)
                
                fig_category = px.bar(df_category, x='category', y='views',
                                     title='Content Performance by Category',
                                     labels={'views': 'Views', 'category': 'Category'})
                charts["category_performance"] = fig_category
            
            # Revenue chart
            if analytics_data.get("revenue", {}).get("subscription_revenue"):
                revenue_data = analytics_data["revenue"]["subscription_revenue"]
                df_revenue = pd.DataFrame(revenue_data)
                
                fig_revenue = px.bar(df_revenue, x='date', y='revenue', color='tier',
                                   title='Subscription Revenue',
                                   labels={'revenue': 'Revenue ($)', 'date': 'Date'})
                charts["subscription_revenue"] = fig_revenue
            
            # Geographic chart
            if analytics_data.get("geographic", {}).get("regional_engagement"):
                geo_data = analytics_data["geographic"]["regional_engagement"]
                df_geo = pd.DataFrame(geo_data)
                
                fig_geo = px.bar(df_geo, x='country', y='users',
                               title='Users by Country',
                               labels={'users': 'Users', 'country': 'Country'})
                charts["geographic_distribution"] = fig_geo
            
            return charts
            
        except Exception as e:
            print(f"Error creating dashboard charts: {e}")
            return {}
    
    def generate_analytics_report(self, date_range: int = 30) -> Dict:
        """Generate comprehensive analytics report"""
        try:
            report = {
                "generated_at": datetime.now(),
                "date_range": date_range,
                "engagement": self.get_user_engagement_metrics(date_range),
                "content": self.get_content_analytics(date_range),
                "revenue": self.get_revenue_analytics(date_range),
                "geographic": self.get_geographic_analytics(date_range)
            }
            
            # Add summary metrics
            report["summary"] = self.calculate_summary_metrics(report)
            
            # Add charts
            report["charts"] = self.create_dashboard_charts(report)
            
            return report
            
        except Exception as e:
            print(f"Error generating analytics report: {e}")
            return {"error": str(e)}
    
    def calculate_summary_metrics(self, report: Dict) -> Dict:
        """Calculate summary metrics from report data"""
        try:
            summary = {}
            
            # Total users
            if report.get("engagement", {}).get("daily_active_users"):
                total_users = max(day["users"] for day in report["engagement"]["daily_active_users"])
                summary["total_active_users"] = total_users
            
            # Total revenue
            if report.get("revenue", {}).get("subscription_revenue"):
                total_revenue = sum(day["revenue"] for day in report["revenue"]["subscription_revenue"])
                summary["total_revenue"] = total_revenue
            
            # Top performing content
            if report.get("content", {}).get("top_articles"):
                top_article = report["content"]["top_articles"][0] if report["content"]["top_articles"] else None
                summary["top_article"] = top_article
            
            # Geographic reach
            if report.get("geographic", {}).get("regional_engagement"):
                countries = len(report["geographic"]["regional_engagement"])
                summary["countries_reached"] = countries
            
            return summary
            
        except Exception as e:
            print(f"Error calculating summary metrics: {e}")
            return {}

# Initialize analytics manager
analytics_manager = AnalyticsManager()

# Export functions
def track_user_activity(user_id: int, session_id: str, action: str, target: str, metadata: Dict = None):
    """Track user activity"""
    analytics_manager.track_event(user_id, session_id, action, target, metadata)

def get_analytics_data(user_id: int = None, date_range: int = 30) -> Dict:
    """Get analytics data"""
    if user_id:
        return analytics_manager.get_user_analytics(user_id, date_range)
    else:
        return analytics_manager.generate_analytics_report(date_range)

def display_analytics_dashboard():
    """Display analytics dashboard in Streamlit"""
    st.title("📊 Analytics Dashboard")
    
    # Date range selector
    date_range = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
    
    # Generate report
    with st.spinner("Generating analytics report..."):
        report = analytics_manager.generate_analytics_report(date_range)
    
    if "error" in report:
        st.error(f"Error generating report: {report['error']}")
        return
    
    # Summary metrics
    st.subheader("📈 Summary Metrics")
    
    if report.get("summary"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Users", report["summary"].get("total_active_users", 0))
        
        with col2:
            st.metric("Total Revenue", f"${report['summary'].get('total_revenue', 0):,.2f}")
        
        with col3:
            st.metric("Countries Reached", report["summary"].get("countries_reached", 0))
        
        with col4:
            if report["summary"].get("top_article"):
                st.metric("Top Article Views", report["summary"]["top_article"]["views"])
    
    # Charts
    st.subheader("📊 Performance Charts")
    
    if report.get("charts"):
        # Daily active users
        if "daily_active_users" in report["charts"]:
            st.plotly_chart(report["charts"]["daily_active_users"], use_container_width=True)
        
        # Content performance
        if "category_performance" in report["charts"]:
            st.plotly_chart(report["charts"]["category_performance"], use_container_width=True)
        
        # Revenue
        if "subscription_revenue" in report["charts"]:
            st.plotly_chart(report["charts"]["subscription_revenue"], use_container_width=True)
        
        # Geographic distribution
        if "geographic_distribution" in report["charts"]:
            st.plotly_chart(report["charts"]["geographic_distribution"], use_container_width=True)
    
    # Detailed tables
    st.subheader("📋 Detailed Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Content", "Users", "Revenue", "Geographic"])
    
    with tab1:
        if report.get("content", {}).get("top_articles"):
            st.markdown("### Top Performing Articles")
            df_articles = pd.DataFrame(report["content"]["top_articles"])
            st.dataframe(df_articles, use_container_width=True)
    
    with tab2:
        if report.get("engagement", {}).get("engagement_actions"):
            st.markdown("### User Engagement")
            df_engagement = pd.DataFrame(report["engagement"]["engagement_actions"])
            st.dataframe(df_engagement, use_container_width=True)
    
    with tab3:
        if report.get("revenue", {}).get("subscription_revenue"):
            st.markdown("### Revenue Details")
            df_revenue = pd.DataFrame(report["revenue"]["subscription_revenue"])
            st.dataframe(df_revenue, use_container_width=True)
    
    with tab4:
        if report.get("geographic", {}).get("location_distribution"):
            st.markdown("### Geographic Distribution")
            df_geo = pd.DataFrame(report["geographic"]["location_distribution"])
            st.dataframe(df_geo, use_container_width=True)
