import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import trafilatura
from bs4 import BeautifulSoup
import re
from config import RSS_FEEDS
from ai_services import summarize_article, analyze_sentiment, categorize_content
from database import save_article, get_articles_by_category

class NewsAggregator:
    def __init__(self):
        self.feeds = RSS_FEEDS
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published_at': self._parse_date(entry.get('published', '')),
                    'source': feed.feed.get('title', ''),
                    'author': entry.get('author', ''),
                    'category': entry.get('category', ''),
                    'content': ''
                }
                
                # Extract full content from the article URL
                if article['url']:
                    article['content'] = self.extract_article_content(article['url'])
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {e}")
            return []
    
    def extract_article_content(self, url: str) -> str:
        """Extract article content from URL"""
        try:
            # Use trafilatura for content extraction
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded)
                return content or ""
            return ""
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return ""
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_string:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S GMT',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S',
                '%d %b %Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return None
            return None
            
        except Exception:
            return None
    
    def process_article(self, article: Dict) -> Dict:
        """Process article with AI services"""
        try:
            # Generate AI summary if content is available
            if article['content'] and len(article['content']) > 200:
                article['summary'] = summarize_article(article['content'])
            
            # Analyze sentiment
            sentiment_data = analyze_sentiment(article['content'] or article['summary'])
            article['sentiment_score'] = sentiment_data.get('rating', 3) / 5.0  # Convert to 0-1 scale
            article['sentiment_category'] = self._get_sentiment_category(sentiment_data.get('rating', 3))
            
            # Categorize content
            if not article['category']:
                article['category'] = categorize_content(article['title'] + ' ' + article['summary'])
            
            return article
            
        except Exception as e:
            print(f"Error processing article: {e}")
            return article
    
    def _get_sentiment_category(self, rating: float) -> str:
        """Convert sentiment rating to category"""
        if rating >= 4:
            return 'positive'
        elif rating <= 2:
            return 'negative'
        else:
            return 'neutral'
    
    def fetch_news_by_category(self, category: str) -> List[Dict]:
        """Fetch news articles by category"""
        articles = []
        
        # Get RSS feeds for the category
        feeds = self.feeds.get(category.lower(), [])
        
        for feed_url in feeds:
            feed_articles = self.fetch_rss_feed(feed_url)
            for article in feed_articles:
                # Process article with AI
                processed_article = self.process_article(article)
                processed_article['category'] = category
                articles.append(processed_article)
        
        # Sort by publication date (newest first)
        articles.sort(key=lambda x: x.get('published_at') or datetime.min, reverse=True)
        
        return articles[:50]  # Return top 50 articles
    
    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """Fetch news from all categories"""
        all_news = {}
        
        for category in self.feeds.keys():
            all_news[category] = self.fetch_news_by_category(category)
        
        return all_news
    
    def search_news(self, query: str, articles: List[Dict]) -> List[Dict]:
        """Search news articles by query"""
        query_lower = query.lower()
        results = []
        
        for article in articles:
            # Search in title, summary, and content
            if (query_lower in article['title'].lower() or
                query_lower in article['summary'].lower() or
                query_lower in article['content'].lower()):
                results.append(article)
        
        return results
    
    def filter_by_date_range(self, articles: List[Dict], days: int = 7) -> List[Dict]:
        """Filter articles by date range"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_articles = []
        for article in articles:
            if article.get('published_at') and article['published_at'] >= cutoff_date:
                filtered_articles.append(article)
        
        return filtered_articles
    
    def get_trending_topics(self, articles: List[Dict]) -> List[Dict]:
        """Get trending topics based on article frequency"""
        topic_counts = {}
        
        for article in articles:
            # Extract keywords from title and summary
            text = article['title'] + ' ' + article['summary']
            words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
            
            # Common words to exclude
            stop_words = {'this', 'that', 'with', 'have', 'will', 'been', 'said', 'they', 'their', 'from', 'more', 'were', 'about', 'after', 'would', 'could', 'should', 'what', 'when', 'where', 'which', 'while'}
            
            for word in words:
                if word not in stop_words:
                    topic_counts[word] = topic_counts.get(word, 0) + 1
        
        # Sort by frequency and return top topics
        trending = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'topic': topic, 'count': count} for topic, count in trending[:10]]

# Initialize news aggregator
news_aggregator = NewsAggregator()

def get_news_feeds(category: str = None) -> List[Dict]:
    """Get news feeds by category or all news"""
    if category:
        return news_aggregator.fetch_news_by_category(category)
    else:
        return news_aggregator.fetch_all_news()

def categorize_news(articles: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize news articles"""
    categorized = {}
    
    for article in articles:
        category = article.get('category', 'general')
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(article)
    
    return categorized

def save_news_articles(articles: List[Dict]) -> List[int]:
    """Save news articles to database"""
    saved_ids = []
    
    for article in articles:
        try:
            article_id = save_article(article)
            if article_id:
                saved_ids.append(article_id)
        except Exception as e:
            print(f"Error saving article: {e}")
    
    return saved_ids

def get_cached_news(category: str, max_age_hours: int = 1) -> List[Dict]:
    """Get cached news articles from database"""
    return get_articles_by_category(category, limit=50)

def refresh_news_cache():
    """Refresh news cache by fetching latest articles"""
    all_news = news_aggregator.fetch_all_news()
    
    for category, articles in all_news.items():
        save_news_articles(articles)
