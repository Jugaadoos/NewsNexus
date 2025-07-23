import feedparser
import requests
from bs4 import BeautifulSoup
import trafilatura
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json
from database.connection import get_db_connection
from database.models import Article, User
from services.ai_service import AIService
from services.geo_service import GeoService

class NewsService:
    def __init__(self):
        self.ai_service = AIService()
        self.geo_service = GeoService()
        
        # Major news sources RSS feeds
        self.rss_feeds = {
            'World': [
                'https://feeds.bbci.co.uk/news/world/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.reuters.com/reuters/worldNews'
            ],
            'Politics': [
                'https://feeds.bbci.co.uk/news/politics/rss.xml',
                'https://rss.cnn.com/rss/cnn_politics.rss',
                'https://feeds.reuters.com/Reuters/PoliticsNews'
            ],
            'Business': [
                'https://feeds.bbci.co.uk/news/business/rss.xml',
                'https://rss.cnn.com/rss/money_news_economy.rss',
                'https://feeds.reuters.com/reuters/businessNews'
            ],
            'Technology': [
                'https://feeds.bbci.co.uk/news/technology/rss.xml',
                'https://rss.cnn.com/rss/cnn_tech.rss',
                'https://feeds.reuters.com/reuters/technologyNews'
            ],
            'Sports': [
                'https://feeds.bbci.co.uk/sport/rss.xml',
                'https://rss.cnn.com/rss/cnn_sports.rss',
                'https://feeds.reuters.com/reuters/sportsNews'
            ],
            'Entertainment': [
                'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
                'https://rss.cnn.com/rss/cnn_entertainment.rss'
            ],
            'Health': [
                'https://feeds.bbci.co.uk/news/health/rss.xml',
                'https://rss.cnn.com/rss/cnn_health.rss',
                'https://feeds.reuters.com/reuters/healthNews'
            ],
            'Science': [
                'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
                'https://rss.cnn.com/rss/cnn_science.rss'
            ]
        }
    
    def fetch_news_articles(self, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch news articles from RSS feeds"""
        articles = []
        
        try:
            feeds_to_process = self.rss_feeds.get(category, []) if category else []
            if not feeds_to_process:
                # If no specific category, get from all feeds
                for cat_feeds in self.rss_feeds.values():
                    feeds_to_process.extend(cat_feeds)
            
            for feed_url in feeds_to_process:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries:
                        article = {
                            'title': entry.title,
                            'url': entry.link,
                            'published_at': self._parse_date(entry.get('published')),
                            'source': feed.feed.get('title', 'Unknown Source'),
                            'description': entry.get('description', ''),
                            'category': category or 'World'
                        }
                        
                        # Extract full content
                        content = self._extract_content(entry.link)
                        if content:
                            article['content'] = content
                            article['summary'] = self.ai_service.summarize_article(content)
                        else:
                            article['content'] = article['description']
                            article['summary'] = article['description'][:200] + "..."
                        
                        articles.append(article)
                        
                        if len(articles) >= limit:
                            break
                            
                except Exception as e:
                    logging.error(f"Error fetching from {feed_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error fetching news articles: {str(e)}")
        
        return articles[:limit]
    
    def get_articles(self, category: str = None, geo_level: str = None, 
                    location: Dict = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get articles filtered by category and geographic level"""
        try:
            # First try to get from database
            db_articles = self._get_articles_from_db(category, geo_level, location, limit)
            
            if len(db_articles) < limit:
                # If not enough articles in DB, fetch fresh ones
                fresh_articles = self.fetch_news_articles(category, limit - len(db_articles))
                
                # Process and save fresh articles
                for article in fresh_articles:
                    processed_article = self._process_article(article, location)
                    if self._matches_geo_criteria(processed_article, geo_level, location):
                        self._save_article_to_db(processed_article)
                        db_articles.append(processed_article)
                        
                        if len(db_articles) >= limit:
                            break
            
            return db_articles[:limit]
            
        except Exception as e:
            logging.error(f"Error getting articles: {str(e)}")
            return []
    
    def _extract_content(self, url: str) -> str:
        """Extract content from URL using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text
            return None
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def _process_article(self, article: Dict[str, Any], user_location: Dict = None) -> Dict[str, Any]:
        """Process article with AI analysis and geo-tagging"""
        try:
            # AI processing
            article['sentiment'] = self.ai_service.analyze_sentiment(article['content'])
            article['category'] = self.ai_service.categorize_news(article['title'], article['content'])
            
            # Geo-tagging
            if user_location:
                article['geo_relevance'] = self.geo_service.calculate_relevance(
                    article['content'], user_location
                )
                article['location_data'] = self.geo_service.extract_locations(article['content'])
            
            # Generate ID if not present
            if 'id' not in article:
                article['id'] = hash(article['title'] + article['url'])
            
            return article
            
        except Exception as e:
            logging.error(f"Error processing article: {str(e)}")
            return article
    
    def _matches_geo_criteria(self, article: Dict[str, Any], geo_level: str, location: Dict) -> bool:
        """Check if article matches geographic criteria"""
        if not geo_level or not location:
            return True
            
        try:
            if geo_level == "Local":
                # Check if article is within 50-100 miles
                return self.geo_service.is_within_radius(
                    article.get('location_data', {}), 
                    location, 
                    radius_miles=100
                )
            elif geo_level == "Regional":
                # Check if article is within same state/province
                return self.geo_service.is_same_region(
                    article.get('location_data', {}), 
                    location
                )
            elif geo_level == "National":
                # Check if article is within same country
                return self.geo_service.is_same_country(
                    article.get('location_data', {}), 
                    location
                )
            elif geo_level == "International":
                # Check if article is from different country
                return not self.geo_service.is_same_country(
                    article.get('location_data', {}), 
                    location
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking geo criteria: {str(e)}")
            return True
    
    def _get_articles_from_db(self, category: str, geo_level: str, 
                             location: Dict, limit: int) -> List[Dict[str, Any]]:
        """Get articles from database"""
        try:
            db = get_db_connection()
            
            query = db.query(Article).filter(Article.is_approved == True)
            
            if category:
                query = query.filter(Article.category == category)
            
            # Add geo-level filtering logic here
            
            articles = query.order_by(Article.published_at.desc()).limit(limit).all()
            
            return [self._article_to_dict(article) for article in articles]
            
        except Exception as e:
            logging.error(f"Error getting articles from DB: {str(e)}")
            return []
    
    def _save_article_to_db(self, article: Dict[str, Any]):
        """Save article to database"""
        try:
            db = get_db_connection()
            
            # Check if article already exists
            existing = db.query(Article).filter(
                Article.url == article['url']
            ).first()
            
            if existing:
                return
            
            db_article = Article(
                title=article['title'],
                content=article['content'],
                summary=article['summary'],
                url=article['url'],
                source=article['source'],
                category=article['category'],
                published_at=article['published_at'],
                sentiment_score=article.get('sentiment', {}).get('score', 0),
                sentiment_label=article.get('sentiment', {}).get('label', 'neutral'),
                location_data=article.get('location_data', {}),
                is_approved=True  # Auto-approve for now
            )
            
            db.add(db_article)
            db.commit()
            
        except Exception as e:
            logging.error(f"Error saving article to DB: {str(e)}")
            db.rollback()
    
    def _article_to_dict(self, article: Article) -> Dict[str, Any]:
        """Convert Article model to dictionary"""
        return {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'summary': article.summary,
            'url': article.url,
            'source': article.source,
            'category': article.category,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'sentiment': {
                'score': article.sentiment_score,
                'label': article.sentiment_label
            },
            'location_data': article.location_data or {}
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            if date_str:
                return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
            return datetime.now()
        except:
            return datetime.now()
