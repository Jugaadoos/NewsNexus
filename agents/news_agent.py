import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from services.news_service import NewsService
from services.ai_service import AIService
from services.geo_service import GeoService
from database.connection import get_db_connection
from database.models import Article, AIAgent

class NewsAgent:
    def __init__(self, agent_id: str = "news_agent"):
        self.agent_id = agent_id
        self.news_service = NewsService()
        self.ai_service = AIService()
        self.geo_service = GeoService()
        self.status = "idle"
        self.last_run = None
        
    async def start(self):
        """Start the news agent"""
        logging.info(f"Starting News Agent {self.agent_id}")
        self.status = "running"
        
        try:
            while self.status == "running":
                await self.fetch_and_process_news()
                await asyncio.sleep(3600)  # Run every hour
                
        except Exception as e:
            logging.error(f"Error in News Agent: {str(e)}")
            self.status = "error"
    
    async def fetch_and_process_news(self):
        """Fetch and process news articles"""
        try:
            logging.info("Fetching and processing news articles")
            
            # Get news for each category
            categories = ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"]
            
            for category in categories:
                articles = self.news_service.fetch_news_articles(category, limit=10)
                
                for article in articles:
                    await self.process_article(article)
            
            self.last_run = datetime.now()
            self._update_agent_status()
            
        except Exception as e:
            logging.error(f"Error fetching news: {str(e)}")
    
    async def process_article(self, article: Dict[str, Any]):
        """Process individual article"""
        try:
            # Check if article already exists
            db = get_db_connection()
            existing = db.query(Article).filter(Article.url == article['url']).first()
            
            if existing:
                return
            
            # Enhance article with AI processing
            enhanced_article = await self.enhance_article(article)
            
            # Save to database
            await self.save_article(enhanced_article)
            
        except Exception as e:
            logging.error(f"Error processing article: {str(e)}")
    
    async def enhance_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance article with AI analysis"""
        try:
            # Generate summary
            if not article.get('summary'):
                article['summary'] = self.ai_service.summarize_article(article['content'])
            
            # Analyze sentiment
            sentiment = self.ai_service.analyze_sentiment(article['content'])
            article['sentiment'] = sentiment
            
            # Categorize if not already categorized
            if not article.get('category'):
                article['category'] = self.ai_service.categorize_news(article['title'], article['content'])
            
            # Extract locations
            locations = self.geo_service.extract_locations(article['content'])
            article['location_data'] = {'locations': locations}
            
            # Check originality
            # In production, this would check against existing articles
            article['originality_score'] = 0.95  # Placeholder
            
            return article
            
        except Exception as e:
            logging.error(f"Error enhancing article: {str(e)}")
            return article
    
    async def save_article(self, article: Dict[str, Any]):
        """Save article to database"""
        try:
            db = get_db_connection()
            
            db_article = Article(
                title=article['title'],
                content=article['content'],
                summary=article['summary'],
                url=article['url'],
                source=article['source'],
                category=article['category'],
                published_at=article.get('published_at'),
                sentiment_score=article.get('sentiment', {}).get('score', 0),
                sentiment_label=article.get('sentiment', {}).get('label', 'neutral'),
                location_data=article.get('location_data', {}),
                is_approved=False  # Needs review
            )
            
            db.add(db_article)
            db.commit()
            
            logging.info(f"Saved article: {article['title']}")
            
        except Exception as e:
            logging.error(f"Error saving article: {str(e)}")
            db.rollback()
    
    async def get_targeted_news(self, location: Dict[str, Any], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get news targeted to specific location and preferences"""
        try:
            # Get local news sources based on location
            local_sources = self._get_local_sources(location)
            
            # Fetch news from local sources
            local_articles = []
            for source in local_sources:
                articles = await self._fetch_from_source(source)
                local_articles.extend(articles)
            
            # Filter by preferences
            filtered_articles = self._filter_by_preferences(local_articles, preferences)
            
            return filtered_articles
            
        except Exception as e:
            logging.error(f"Error getting targeted news: {str(e)}")
            return []
    
    def _get_local_sources(self, location: Dict[str, Any]) -> List[str]:
        """Get local news sources based on location"""
        # This would be expanded with actual local news sources
        local_sources = []
        
        country = location.get('country', '')
        region = location.get('region', '')
        city = location.get('city', '')
        
        # Add local RSS feeds based on location
        if country == 'United States':
            if region == 'New York':
                local_sources.append('https://www.ny1.com/nyc/all-boroughs/news.rss')
            elif region == 'California':
                local_sources.append('https://www.abc10.com/feeds/syndication/rss/news')
        
        return local_sources
    
    async def _fetch_from_source(self, source_url: str) -> List[Dict[str, Any]]:
        """Fetch articles from a specific source"""
        try:
            # Use the news service to fetch from RSS
            articles = []
            # Implementation would go here
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching from source {source_url}: {str(e)}")
            return []
    
    def _filter_by_preferences(self, articles: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter articles by user preferences"""
        filtered = []
        
        preferred_categories = preferences.get('categories', [])
        preferred_sentiment = preferences.get('sentiment', 'all')
        
        for article in articles:
            # Filter by category
            if preferred_categories and article.get('category') not in preferred_categories:
                continue
            
            # Filter by sentiment
            if preferred_sentiment != 'all':
                article_sentiment = article.get('sentiment', {}).get('label', 'neutral')
                if article_sentiment != preferred_sentiment:
                    continue
            
            filtered.append(article)
        
        return filtered
    
    def stop(self):
        """Stop the news agent"""
        logging.info(f"Stopping News Agent {self.agent_id}")
        self.status = "stopped"
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'type': 'news_agent'
        }
    
    def _update_agent_status(self):
        """Update agent status in database"""
        try:
            db = get_db_connection()
            
            agent = db.query(AIAgent).filter(AIAgent.name == self.agent_id).first()
            
            if not agent:
                agent = AIAgent(
                    name=self.agent_id,
                    type='news_scraper',
                    config={},
                    status=self.status
                )
                db.add(agent)
            else:
                agent.status = self.status
                agent.last_run = self.last_run
            
            db.commit()
            
        except Exception as e:
            logging.error(f"Error updating agent status: {str(e)}")
            db.rollback()
