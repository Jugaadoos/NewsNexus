import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

def render_analytics_page(user: Dict[str, Any], services: Dict[str, Any]):
    """Render comprehensive analytics page"""
    try:
        st.title("Analytics Dashboard")
        
        # Check permissions
        if user['role'] not in ['admin', 'editor', 'journalist', 'publishing_partner']:
            st.error("You don't have permission to access analytics.")
            return
        
        # Time range selector
        render_time_range_selector()
        
        # Main analytics sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", 
            "Content Analytics", 
            "User Engagement", 
            "Geographic Analytics", 
            "Revenue Analytics"
        ])
        
        with tab1:
            render_overview_analytics(user, services)
        
        with tab2:
            render_content_analytics(user, services)
        
        with tab3:
            render_engagement_analytics(user, services)
        
        with tab4:
            render_geographic_analytics(user, services)
        
        with tab5:
            render_revenue_analytics(user, services)
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        logging.error(f"Analytics page error: {str(e)}")

def render_time_range_selector():
    """Render time range selection controls"""
    try:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            time_period = st.selectbox(
                "Time Period",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "Custom"],
                index=1
            )
            st.session_state.analytics_time_period = time_period
        
        with col2:
            if time_period == "Custom":
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
                end_date = st.date_input("End Date", value=datetime.now())
                st.session_state.analytics_start_date = start_date
                st.session_state.analytics_end_date = end_date
        
        with col3:
            if st.button("🔄 Refresh Data", key="refresh_analytics"):
                st.rerun()
        
    except Exception as e:
        st.error(f"Error rendering time range selector: {str(e)}")

def render_overview_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render overview analytics dashboard"""
    try:
        st.subheader("Platform Overview")
        
        # Get analytics data
        analytics_service = services['analytics']
        days = get_days_from_period()
        
        # Key metrics
        engagement_metrics = analytics_service.get_user_engagement_metrics(days=days)
        content_metrics = analytics_service.get_content_analytics(days=days)
        subscription_metrics = analytics_service.get_subscription_analytics()
        real_time_metrics = analytics_service.get_real_time_metrics()
        
        # Top-level KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Users",
                f"{engagement_metrics.get('unique_users', 0):,}",
                delta=f"+{real_time_metrics.get('active_users_24h', 0)} (24h)"
            )
        
        with col2:
            st.metric(
                "Total Articles",
                f"{content_metrics.get('total_articles', 0):,}",
                delta=f"{content_metrics.get('approval_rate', 0):.1%} approved"
            )
        
        with col3:
            st.metric(
                "Engagement Events",
                f"{engagement_metrics.get('total_events', 0):,}",
                delta=f"+{real_time_metrics.get('recent_events', 0)} (1h)"
            )
        
        with col4:
            st.metric(
                "Revenue",
                f"${subscription_metrics.get('total_revenue', 0):,.2f}",
                delta=f"{subscription_metrics.get('active_subscriptions', 0)} subs"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Engagement trend chart
            if engagement_metrics.get('event_breakdown'):
                fig = analytics_service.create_engagement_chart(engagement_metrics)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue distribution
            if subscription_metrics:
                fig = analytics_service.create_revenue_chart(subscription_metrics)
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        render_recent_activity(analytics_service, days)
        
    except Exception as e:
        st.error(f"Error rendering overview analytics: {str(e)}")

def render_content_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render content-specific analytics"""
    try:
        st.subheader("Content Performance")
        
        analytics_service = services['analytics']
        days = get_days_from_period()
        
        # Get content metrics
        content_metrics = analytics_service.get_content_analytics(days=days)
        
        # Content metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Articles Published",
                content_metrics.get('total_articles', 0),
                delta=f"{content_metrics.get('approved_articles', 0)} approved"
            )
        
        with col2:
            approval_rate = content_metrics.get('approval_rate', 0)
            st.metric(
                "Approval Rate",
                f"{approval_rate:.1%}",
                delta="Quality metric"
            )
        
        with col3:
            sentiment_dist = content_metrics.get('sentiment_distribution', {})
            positive_pct = sentiment_dist.get('positive', 0) / max(sum(sentiment_dist.values()), 1)
            st.metric(
                "Positive Content",
                f"{positive_pct:.1%}",
                delta="Sentiment analysis"
            )
        
        # Category distribution
        st.subheader("Content by Category")
        article_counts = content_metrics.get('article_counts', {})
        
        if article_counts:
            fig = px.bar(
                x=list(article_counts.keys()),
                y=list(article_counts.values()),
                title="Articles by Category",
                labels={'x': 'Category', 'y': 'Number of Articles'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment analysis
        st.subheader("Content Sentiment Distribution")
        sentiment_dist = content_metrics.get('sentiment_distribution', {})
        
        if sentiment_dist:
            fig = px.pie(
                values=list(sentiment_dist.values()),
                names=list(sentiment_dist.keys()),
                title="Sentiment Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performing articles
        render_top_articles(analytics_service, days)
        
    except Exception as e:
        st.error(f"Error rendering content analytics: {str(e)}")

def render_engagement_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render user engagement analytics"""
    try:
        st.subheader("User Engagement")
        
        analytics_service = services['analytics']
        days = get_days_from_period()
        
        # Get engagement data
        engagement_metrics = analytics_service.get_user_engagement_metrics(days=days)
        
        # Engagement metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Events",
                f"{engagement_metrics.get('total_events', 0):,}"
            )
        
        with col2:
            st.metric(
                "Unique Users",
                f"{engagement_metrics.get('unique_users', 0):,}"
            )
        
        with col3:
            events_per_user = engagement_metrics.get('total_events', 0) / max(engagement_metrics.get('unique_users', 1), 1)
            st.metric(
                "Events per User",
                f"{events_per_user:.1f}"
            )
        
        with col4:
            st.metric(
                "Period",
                f"{days} days"
            )
        
        # Event breakdown
        event_breakdown = engagement_metrics.get('event_breakdown', {})
        
        if event_breakdown:
            col1, col2 = st.columns(2)
            
            with col1:
                # Event type distribution
                fig = px.bar(
                    x=list(event_breakdown.keys()),
                    y=list(event_breakdown.values()),
                    title="Events by Type"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Event type pie chart
                fig = px.pie(
                    values=list(event_breakdown.values()),
                    names=list(event_breakdown.keys()),
                    title="Event Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # User activity heatmap
        render_activity_heatmap(analytics_service, days)
        
    except Exception as e:
        st.error(f"Error rendering engagement analytics: {str(e)}")

def render_geographic_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render geographic analytics"""
    try:
        st.subheader("Geographic Distribution")
        
        analytics_service = services['analytics']
        days = get_days_from_period()
        
        # Get geographic data
        geo_data = analytics_service.get_geographic_analytics(days=days)
        
        if not geo_data:
            st.info("No geographic data available for the selected period.")
            return
        
        # Geographic metrics
        countries = geo_data.get('countries', {})
        regions = geo_data.get('regions', {})
        cities = geo_data.get('cities', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Countries", len(countries))
        
        with col2:
            st.metric("Regions", len(regions))
        
        with col3:
            st.metric("Cities", len(cities))
        
        # Geographic charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top countries
            if countries:
                top_countries = dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10])
                fig = px.bar(
                    x=list(top_countries.values()),
                    y=list(top_countries.keys()),
                    orientation='h',
                    title="Top Countries by Activity"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top regions
            if regions:
                top_regions = dict(sorted(regions.items(), key=lambda x: x[1], reverse=True)[:10])
                fig = px.bar(
                    x=list(top_regions.values()),
                    y=list(top_regions.keys()),
                    orientation='h',
                    title="Top Regions by Activity"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # World map visualization
        if countries:
            fig = analytics_service.create_geographic_chart(geo_data)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering geographic analytics: {str(e)}")

def render_revenue_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render revenue and subscription analytics"""
    try:
        st.subheader("Revenue Analytics")
        
        # Check permissions
        if user['role'] not in ['admin', 'publishing_partner']:
            st.warning("Revenue analytics are only available to administrators and publishing partners.")
            return
        
        analytics_service = services['analytics']
        
        # Get revenue data
        subscription_metrics = analytics_service.get_subscription_analytics()
        
        # Revenue metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${subscription_metrics.get('total_revenue', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                "Average Revenue",
                f"${subscription_metrics.get('average_revenue', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                "Active Subscriptions",
                f"{subscription_metrics.get('active_subscriptions', 0):,}"
            )
        
        with col4:
            churn_rate = subscription_metrics.get('churn_rate', 0)
            st.metric(
                "Churn Rate",
                f"{churn_rate:.1%}",
                delta=f"{'↑' if churn_rate > 0.1 else '↓'}"
            )
        
        # Subscription distribution
        subscription_counts = subscription_metrics.get('subscription_counts', {})
        
        if subscription_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                # Subscription tier distribution
                fig = px.pie(
                    values=list(subscription_counts.values()),
                    names=list(subscription_counts.keys()),
                    title="Subscriptions by Tier"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue by tier (estimated)
                revenue_by_tier = calculate_revenue_by_tier(subscription_counts)
                fig = px.bar(
                    x=list(revenue_by_tier.keys()),
                    y=list(revenue_by_tier.values()),
                    title="Estimated Revenue by Tier"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Revenue trends
        render_revenue_trends(analytics_service)
        
    except Exception as e:
        st.error(f"Error rendering revenue analytics: {str(e)}")

def render_recent_activity(analytics_service, days: int):
    """Render recent activity feed"""
    try:
        st.subheader("Recent Activity")
        
        # This would typically show recent user activities, article publications, etc.
        st.info("Recent activity feed coming soon!")
        
    except Exception as e:
        st.error(f"Error rendering recent activity: {str(e)}")

def render_top_articles(analytics_service, days: int):
    """Render top performing articles"""
    try:
        st.subheader("Top Performing Articles")
        
        # Get article performance data
        article_performance = analytics_service.get_article_performance(days=days)
        
        if article_performance:
            # Convert to DataFrame for display
            articles_data = []
            for article_id, metrics in article_performance.items():
                articles_data.append({
                    'Article ID': article_id,
                    'Views': metrics.get('views', 0),
                    'Likes': metrics.get('likes', 0),
                    'Shares': metrics.get('shares', 0),
                    'Saves': metrics.get('saves', 0),
                    'Total Engagement': sum(metrics.values())
                })
            
            if articles_data:
                df = pd.DataFrame(articles_data)
                df = df.sort_values('Total Engagement', ascending=False).head(10)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No article performance data available.")
        
    except Exception as e:
        st.error(f"Error rendering top articles: {str(e)}")

def render_activity_heatmap(analytics_service, days: int):
    """Render user activity heatmap"""
    try:
        st.subheader("Activity Heatmap")
        
        # This would show activity patterns by time of day and day of week
        st.info("Activity heatmap visualization coming soon!")
        
    except Exception as e:
        st.error(f"Error rendering activity heatmap: {str(e)}")

def render_revenue_trends(analytics_service):
    """Render revenue trend analysis"""
    try:
        st.subheader("Revenue Trends")
        
        # Sample revenue trend data
        # In production, this would come from actual payment data
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        revenue = [100 + i * 5 + (i % 7) * 20 for i in range(len(dates))]
        
        df = pd.DataFrame({
            'Date': dates,
            'Revenue': revenue
        })
        
        fig = px.line(df, x='Date', y='Revenue', title="Daily Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering revenue trends: {str(e)}")

def calculate_revenue_by_tier(subscription_counts: Dict[str, int]) -> Dict[str, float]:
    """Calculate estimated revenue by subscription tier"""
    # Estimated pricing per tier
    tier_prices = {
        'basic': 9.99,
        'premium': 19.99,
        'enterprise': 49.99
    }
    
    revenue_by_tier = {}
    for tier, count in subscription_counts.items():
        price = tier_prices.get(tier.lower(), 0)
        revenue_by_tier[tier] = count * price
    
    return revenue_by_tier

def get_days_from_period() -> int:
    """Get number of days from selected time period"""
    period = st.session_state.get('analytics_time_period', 'Last 30 days')
    
    if period == "Last 7 days":
        return 7
    elif period == "Last 30 days":
        return 30
    elif period == "Last 90 days":
        return 90
    elif period == "Last year":
        return 365
    elif period == "Custom":
        start_date = st.session_state.get('analytics_start_date', datetime.now() - timedelta(days=30))
        end_date = st.session_state.get('analytics_end_date', datetime.now())
        return (end_date - start_date).days
    
    return 30

def export_analytics_data(analytics_service, format_type: str = 'csv'):
    """Export analytics data"""
    try:
        if st.button("📊 Export Data", key="export_analytics"):
            days = get_days_from_period()
            
            # Get all analytics data
            engagement_data = analytics_service.get_user_engagement_metrics(days=days)
            content_data = analytics_service.get_content_analytics(days=days)
            geo_data = analytics_service.get_geographic_analytics(days=days)
            
            # Create export package
            export_data = {
                'engagement': engagement_data,
                'content': content_data,
                'geographic': geo_data,
                'exported_at': datetime.now().isoformat(),
                'period_days': days
            }
            
            if format_type == 'csv':
                # Convert to CSV format
                st.download_button(
                    label="Download CSV",
                    data=pd.DataFrame([export_data]).to_csv(index=False),
                    file_name=f"analytics_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            st.success("Analytics data exported successfully!")
        
    except Exception as e:
        st.error(f"Error exporting analytics data: {str(e)}")
