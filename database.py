import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from config import DATABASE_URL, PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': PGHOST,
            'port': PGPORT,
            'database': PGDATABASE,
            'user': PGUSER,
            'password': PGPASSWORD
        }
        if DATABASE_URL:
            self.connection_params = {'dsn': DATABASE_URL}
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute database query"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    if fetch:
                        return cur.fetchall()
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Query execution error: {e}")
            return None if fetch else False

# Initialize database manager
db = DatabaseManager()

def init_database():
    """Initialize database schema"""
    schema_queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            role VARCHAR(50) DEFAULT 'reader',
            subscription_tier VARCHAR(50) DEFAULT 'free',
            location_lat DECIMAL(10, 8),
            location_lng DECIMAL(11, 8),
            location_city VARCHAR(100),
            location_state VARCHAR(100),
            location_country VARCHAR(100),
            preferences JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            url VARCHAR(1000) UNIQUE NOT NULL,
            content TEXT,
            summary TEXT,
            category VARCHAR(100),
            source VARCHAR(200),
            author VARCHAR(200),
            published_at TIMESTAMP,
            sentiment_score DECIMAL(3, 2),
            sentiment_category VARCHAR(50),
            location_relevance JSON,
            hash_content VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_articles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            article_id INTEGER REFERENCES news_articles(id),
            action VARCHAR(50), -- 'saved', 'favorite', 'read', 'shared'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            tier VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            payment_method VARCHAR(100),
            subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date TIMESTAMP,
            amount DECIMAL(10, 2),
            currency VARCHAR(10) DEFAULT 'USD'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES news_articles(id),
            reviewer_id INTEGER REFERENCES users(id),
            review_type VARCHAR(50), -- 'accuracy', 'bias', 'quality'
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            blockchain_hash VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS affiliate_products (
            id SERIAL PRIMARY KEY,
            affiliate_id INTEGER REFERENCES users(id),
            product_name VARCHAR(255) NOT NULL,
            product_url VARCHAR(1000),
            category VARCHAR(100),
            price DECIMAL(10, 2),
            commission_rate DECIMAL(5, 4),
            description TEXT,
            image_url VARCHAR(1000),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id SERIAL PRIMARY KEY,
            affiliate_id INTEGER REFERENCES users(id),
            product_id INTEGER REFERENCES affiliate_products(id),
            clicked_by INTEGER REFERENCES users(id),
            ip_address INET,
            conversion BOOLEAN DEFAULT FALSE,
            commission_earned DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_analytics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            session_id VARCHAR(100),
            page_view VARCHAR(200),
            action VARCHAR(100),
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS advertisements (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            image_url VARCHAR(1000),
            target_url VARCHAR(1000),
            ad_type VARCHAR(50), -- 'banner', 'popup', 'native'
            placement VARCHAR(50), -- 'header', 'sidebar', 'content'
            targeting_criteria JSON,
            budget DECIMAL(10, 2),
            clicks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS publisher_partners (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            company_name VARCHAR(255),
            website_url VARCHAR(1000),
            api_key VARCHAR(255),
            revenue_share DECIMAL(5, 4),
            content_feeds JSON,
            analytics_access BOOLEAN DEFAULT TRUE,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS themes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            theme_name VARCHAR(100) NOT NULL,
            theme_data JSON,
            is_public BOOLEAN DEFAULT FALSE,
            downloads INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for query in schema_queries:
        db.execute_query(query, fetch=False)
    
    # Create indexes for better performance
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_articles_category ON news_articles(category)",
        "CREATE INDEX IF NOT EXISTS idx_articles_published ON news_articles(published_at)",
        "CREATE INDEX IF NOT EXISTS idx_user_articles_user ON user_articles(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_user ON user_analytics(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id)"
    ]
    
    for query in index_queries:
        db.execute_query(query, fetch=False)

def create_user(email: str, name: str, phone: str = None, role: str = 'reader') -> Optional[Dict]:
    """Create a new user"""
    query = """
    INSERT INTO users (email, name, phone, role, preferences)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, email, name, role, created_at
    """
    default_preferences = {
        "language": "en",
        "theme": "default",
        "notifications": True,
        "location_sharing": True
    }
    
    result = db.execute_query(query, (email, name, phone, role, json.dumps(default_preferences)))
    return dict(result[0]) if result else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    query = "SELECT * FROM users WHERE email = %s"
    result = db.execute_query(query, (email,))
    return dict(result[0]) if result else None

def get_user_preferences(user_id: int) -> Dict:
    """Get user preferences"""
    query = "SELECT preferences FROM users WHERE id = %s"
    result = db.execute_query(query, (user_id,))
    if result and result[0]['preferences']:
        return json.loads(result[0]['preferences'])
    return {}

def update_user_preferences(user_id: int, preferences: Dict) -> bool:
    """Update user preferences"""
    query = "UPDATE users SET preferences = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    return db.execute_query(query, (json.dumps(preferences), user_id), fetch=False)

def save_article(article_data: Dict) -> Optional[int]:
    """Save article to database"""
    # Generate content hash for deduplication
    content_hash = hashlib.sha256(article_data['content'].encode()).hexdigest()
    
    query = """
    INSERT INTO news_articles (title, url, content, summary, category, source, author, 
                              published_at, sentiment_score, sentiment_category, 
                              location_relevance, hash_content)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO UPDATE SET
        content = EXCLUDED.content,
        summary = EXCLUDED.summary,
        sentiment_score = EXCLUDED.sentiment_score,
        sentiment_category = EXCLUDED.sentiment_category
    RETURNING id
    """
    
    result = db.execute_query(query, (
        article_data['title'],
        article_data['url'],
        article_data['content'],
        article_data.get('summary', ''),
        article_data.get('category', ''),
        article_data.get('source', ''),
        article_data.get('author', ''),
        article_data.get('published_at'),
        article_data.get('sentiment_score', 0),
        article_data.get('sentiment_category', 'neutral'),
        json.dumps(article_data.get('location_relevance', {})),
        content_hash
    ))
    
    return result[0]['id'] if result else None

def get_articles_by_category(category: str, limit: int = 50) -> List[Dict]:
    """Get articles by category"""
    query = """
    SELECT * FROM news_articles 
    WHERE category = %s 
    ORDER BY published_at DESC 
    LIMIT %s
    """
    result = db.execute_query(query, (category, limit))
    return [dict(row) for row in result] if result else []

def get_articles_by_location(location_data: Dict, radius_miles: int = 75) -> List[Dict]:
    """Get articles by location within radius"""
    query = """
    SELECT * FROM news_articles 
    WHERE location_relevance IS NOT NULL
    AND ST_DWithin(
        ST_MakePoint(%s, %s)::geography,
        ST_MakePoint(
            (location_relevance->>'lng')::float,
            (location_relevance->>'lat')::float
        )::geography,
        %s
    )
    ORDER BY published_at DESC
    LIMIT 100
    """
    
    result = db.execute_query(query, (
        location_data['lng'],
        location_data['lat'],
        radius_miles * 1609.34  # Convert miles to meters
    ))
    return [dict(row) for row in result] if result else []

def save_user_article_action(user_id: int, article_id: int, action: str) -> bool:
    """Save user article interaction"""
    query = """
    INSERT INTO user_articles (user_id, article_id, action)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id, article_id, action) DO NOTHING
    """
    return db.execute_query(query, (user_id, article_id, action), fetch=False)

def get_user_saved_articles(user_id: int) -> List[Dict]:
    """Get user's saved articles"""
    query = """
    SELECT a.*, ua.created_at as saved_at
    FROM news_articles a
    JOIN user_articles ua ON a.id = ua.article_id
    WHERE ua.user_id = %s AND ua.action = 'saved'
    ORDER BY ua.created_at DESC
    """
    result = db.execute_query(query, (user_id,))
    return [dict(row) for row in result] if result else []

def create_subscription(user_id: int, tier: str, payment_data: Dict) -> Optional[Dict]:
    """Create subscription"""
    query = """
    INSERT INTO subscriptions (user_id, tier, payment_method, amount, currency, expiry_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING *
    """
    
    expiry_date = datetime.now() + timedelta(days=30)  # Monthly subscription
    
    result = db.execute_query(query, (
        user_id,
        tier,
        payment_data.get('method', 'card'),
        payment_data.get('amount', 0),
        payment_data.get('currency', 'USD'),
        expiry_date
    ))
    
    if result:
        # Update user subscription tier
        update_query = "UPDATE users SET subscription_tier = %s WHERE id = %s"
        db.execute_query(update_query, (tier, user_id), fetch=False)
        
    return dict(result[0]) if result else None

def get_active_subscription(user_id: int) -> Optional[Dict]:
    """Get user's active subscription"""
    query = """
    SELECT * FROM subscriptions 
    WHERE user_id = %s AND status = 'active' AND expiry_date > CURRENT_TIMESTAMP
    ORDER BY created_at DESC
    LIMIT 1
    """
    result = db.execute_query(query, (user_id,))
    return dict(result[0]) if result else None

def track_user_activity(user_id: int, session_id: str, page_view: str, action: str, metadata: Dict = None):
    """Track user activity for analytics"""
    query = """
    INSERT INTO user_analytics (user_id, session_id, page_view, action, metadata)
    VALUES (%s, %s, %s, %s, %s)
    """
    db.execute_query(query, (user_id, session_id, page_view, action, json.dumps(metadata or {})), fetch=False)

def get_analytics_data(user_id: int = None, date_range: int = 30) -> Dict:
    """Get analytics data"""
    base_query = """
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as total_actions,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as unique_sessions
    FROM user_analytics
    WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
    """
    
    if user_id:
        base_query += " AND user_id = %s"
        params = (date_range, user_id)
    else:
        params = (date_range,)
    
    base_query += " GROUP BY DATE(created_at) ORDER BY date DESC"
    
    result = db.execute_query(base_query, params)
    return [dict(row) for row in result] if result else []
