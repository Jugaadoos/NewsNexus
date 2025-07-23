import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from database.connection import get_db_connection
from database.models import Analytics, User, Article, Subscription
from sqlalchemy import func
import plotly.express as px
import plotly.graph_objects as go

class AnalyticsService:
    def __init__(self):
        self.db = get_db_connection()
    
    def track_event(self, user_id: int, event_type: str, event_data: Dict[str, Any], 
                   article_id: int = None, geo_data: Dict[str, Any] = None):
        """Track user event"""
        try:
            db = get_db_connection()
            
            analytics_record = Analytics(
                user_id=user_id,
                article_id=article_id,
                event_type=event_type,
                event_data=event_data,
                geo_data=geo_data or {}
            )
            
            db.add(analytics_record)
            db.commit()
            
        except Exception as e:
            logging.error(f"Error tracking event: {str(e)}")
            db.rollback()
    
    def get_user_engagement_metrics(self, user_id: int = None, 
                                   days: int = 30) -> Dict[str, Any]:
        """Get user engagement metrics"""
        try:
            db = get_db_connection()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = db.query(Analytics).filter(
                Analytics.timestamp >= start_date,
                Analytics.timestamp <= end_date
            )
            
            if user_id:
                query = query.filter(Analytics.user_id == user_id)
            
            events = query.all()
            
            # Calculate metrics
            total_events = len(events)
            unique_users = len(set(event.user_id for event in events))
            
            event_counts = {}
            for event in events:
                event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
            
            return {
                'total_events': total_events,
                'unique_users': unique_users,
                'event_breakdown': event_counts,
                'period_days': days
            }
            
        except Exception as e:
            logging.error(f"Error getting engagement metrics: {str(e)}")
            return {}
    
    def get_article_performance(self, article_id: int = None, 
                               days: int = 30) -> Dict[str, Any]:
        """Get article performance metrics"""
        try:
            db = get_db_connection()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = db.query(Analytics).filter(
                Analytics.timestamp >= start_date,
                Analytics.timestamp <= end_date
            )
            
            if article_id:
                query = query.filter(Analytics.article_id == article_id)
            
            events = query.all()
            
            # Group by article
            article_metrics = {}
            for event in events:
                if event.article_id:
                    aid = event.article_id
                    if aid not in article_metrics:
                        article_metrics[aid] = {
                            'views': 0,
                            'likes': 0,
                            'shares': 0,
                            'comments': 0,
                            'saves': 0
                        }
                    
                    if event.event_type in article_metrics[aid]:
                        article_metrics[aid][event.event_type] += 1
            
            return article_metrics
            
        except Exception as e:
            logging.error(f"Error getting article performance: {str(e)}")
            return {}
    
    def get_geographic_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get geographic analytics"""
        try:
            db = get_db_connection()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            events = db.query(Analytics).filter(
                Analytics.timestamp >= start_date,
                Analytics.timestamp <= end_date,
                Analytics.geo_data != None
            ).all()
            
            # Analyze by geographic regions
            geo_metrics = {
                'countries': {},
                'regions': {},
                'cities': {}
            }
            
            for event in events:
                geo_data = event.geo_data or {}
                
                country = geo_data.get('country', 'Unknown')
                region = geo_data.get('region', 'Unknown')
                city = geo_data.get('city', 'Unknown')
                
                # Count by country
                geo_metrics['countries'][country] = geo_metrics['countries'].get(country, 0) + 1
                
                # Count by region
                geo_metrics['regions'][region] = geo_metrics['regions'].get(region, 0) + 1
                
                # Count by city
                geo_metrics['cities'][city] = geo_metrics['cities'].get(city, 0) + 1
            
            return geo_metrics
            
        except Exception as e:
            logging.error(f"Error getting geographic analytics: {str(e)}")
            return {}
    
    def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics"""
        try:
            db = get_db_connection()
            
            # Get subscription counts by tier
            subscription_counts = db.query(
                Subscription.tier,
                func.count(Subscription.id).label('count')
            ).filter(
                Subscription.is_active == True
            ).group_by(Subscription.tier).all()
            
            # Get revenue metrics
            revenue_query = db.query(
                func.sum(Subscription.amount).label('total_revenue'),
                func.avg(Subscription.amount).label('avg_revenue')
            ).filter(
                Subscription.is_active == True
            ).first()
            
            # Get churn analytics
            total_subscriptions = db.query(Subscription).count()
            active_subscriptions = db.query(Subscription).filter(
                Subscription.is_active == True
            ).count()
            
            churn_rate = (total_subscriptions - active_subscriptions) / total_subscriptions if total_subscriptions > 0 else 0
            
            return {
                'subscription_counts': {tier.value: count for tier, count in subscription_counts},
                'total_revenue': float(revenue_query.total_revenue or 0),
                'average_revenue': float(revenue_query.avg_revenue or 0),
                'churn_rate': churn_rate,
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions
            }
            
        except Exception as e:
            logging.error(f"Error getting subscription analytics: {str(e)}")
            return {}
    
    def get_content_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get content analytics"""
        try:
            db = get_db_connection()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get article counts by category
            article_counts = db.query(
                Article.category,
                func.count(Article.id).label('count')
            ).filter(
                Article.created_at >= start_date,
                Article.created_at <= end_date
            ).group_by(Article.category).all()
            
            # Get sentiment distribution
            sentiment_counts = db.query(
                Article.sentiment_label,
                func.count(Article.id).label('count')
            ).filter(
                Article.created_at >= start_date,
                Article.created_at <= end_date
            ).group_by(Article.sentiment_label).all()
            
            # Get approval rates
            total_articles = db.query(Article).filter(
                Article.created_at >= start_date,
                Article.created_at <= end_date
            ).count()
            
            approved_articles = db.query(Article).filter(
                Article.created_at >= start_date,
                Article.created_at <= end_date,
                Article.is_approved == True
            ).count()
            
            approval_rate = approved_articles / total_articles if total_articles > 0 else 0
            
            return {
                'article_counts': {category: count for category, count in article_counts},
                'sentiment_distribution': {sentiment: count for sentiment, count in sentiment_counts},
                'approval_rate': approval_rate,
                'total_articles': total_articles,
                'approved_articles': approved_articles
            }
            
        except Exception as e:
            logging.error(f"Error getting content analytics: {str(e)}")
            return {}
    
    def create_engagement_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create engagement chart"""
        try:
            df = pd.DataFrame(list(data['event_breakdown'].items()), 
                            columns=['Event Type', 'Count'])
            
            fig = px.bar(df, x='Event Type', y='Count', 
                        title='User Engagement by Event Type',
                        color='Count',
                        color_continuous_scale='Blues')
            
            return fig
            
        except Exception as e:
            logging.error(f"Error creating engagement chart: {str(e)}")
            return go.Figure()
    
    def create_geographic_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create geographic distribution chart"""
        try:
            countries = data.get('countries', {})
            df = pd.DataFrame(list(countries.items()), 
                            columns=['Country', 'Count'])
            
            fig = px.choropleth(df, 
                              locations='Country',
                              color='Count',
                              locationmode='country names',
                              title='Geographic Distribution of Users',
                              color_continuous_scale='Viridis')
            
            return fig
            
        except Exception as e:
            logging.error(f"Error creating geographic chart: {str(e)}")
            return go.Figure()
    
    def create_revenue_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create revenue analytics chart"""
        try:
            subscription_counts = data.get('subscription_counts', {})
            
            fig = go.Figure(data=[
                go.Pie(labels=list(subscription_counts.keys()),
                      values=list(subscription_counts.values()),
                      hole=0.3)
            ])
            
            fig.update_layout(
                title='Revenue Distribution by Subscription Tier',
                annotations=[dict(text='Subscriptions', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            
            return fig
            
        except Exception as e:
            logging.error(f"Error creating revenue chart: {str(e)}")
            return go.Figure()
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            db = get_db_connection()
            
            # Get metrics for last hour
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            recent_events = db.query(Analytics).filter(
                Analytics.timestamp >= start_time,
                Analytics.timestamp <= end_time
            ).count()
            
            # Get active users (last 24 hours)
            active_users = db.query(Analytics.user_id).filter(
                Analytics.timestamp >= datetime.now() - timedelta(days=1)
            ).distinct().count()
            
            # Get new articles today
            new_articles = db.query(Article).filter(
                Article.created_at >= datetime.now().date()
            ).count()
            
            return {
                'recent_events': recent_events,
                'active_users_24h': active_users,
                'new_articles_today': new_articles,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting real-time metrics: {str(e)}")
            return {}
