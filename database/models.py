from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    READER = "reader"
    REVIEWER = "reviewer"
    EDITOR = "editor"
    CREATOR = "creator"
    JOURNALIST = "journalist"
    PUBLISHING_PARTNER = "publishing_partner"
    AFFILIATE = "affiliate"
    ADMIN = "admin"

class SubscriptionTier(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.READER)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    location_data = Column(JSON)
    preferences = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    articles = relationship("Article", back_populates="author")
    reviews = relationship("Review", back_populates="reviewer")
    saved_articles = relationship("SavedArticle", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    affiliate_activities = relationship("AffiliateActivity", back_populates="user")

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    url = Column(String(1000))
    source = Column(String(255))
    author_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String(100))
    geo_level = Column(String(50))
    location_data = Column(JSON)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    color_scheme = Column(JSON)
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_approved = Column(Boolean, default=False)
    blockchain_hash = Column(String(64))
    
    # Relationships
    author = relationship("User", back_populates="articles")
    reviews = relationship("Review", back_populates="article")
    saved_by = relationship("SavedArticle", back_populates="article")

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(50))  # pending, approved, rejected
    comments = Column(Text)
    blockchain_hash = Column(String(64))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

class SavedArticle(Base):
    __tablename__ = 'saved_articles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_articles")
    article = relationship("Article", back_populates="saved_by")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tier = Column(Enum(SubscriptionTier))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    payment_method = Column(String(50))
    amount = Column(Float)
    currency = Column(String(3))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class Partner(Base):
    __tablename__ = 'partners'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))  # news_source, advertiser, affiliate
    contact_info = Column(JSON)
    revenue_share = Column(Float)
    api_credentials = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    event_type = Column(String(100))  # view, like, share, click
    event_data = Column(JSON)
    geo_data = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())

class AffiliateActivity(Base):
    __tablename__ = 'affiliate_activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(String(100))
    action_type = Column(String(50))  # click, purchase, referral
    commission = Column(Float)
    currency = Column(String(3))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="affiliate_activities")

class AIAgent(Base):
    __tablename__ = 'ai_agents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))  # news_scraper, reviewer, summarizer
    config = Column(JSON)
    status = Column(String(50))
    last_run = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class BlockchainRecord(Base):
    __tablename__ = 'blockchain_records'
    
    id = Column(Integer, primary_key=True)
    record_type = Column(String(100))  # article, review, transaction
    record_id = Column(String(100))
    hash_value = Column(String(64))
    previous_hash = Column(String(64))
    timestamp = Column(DateTime, server_default=func.now())
    data = Column(JSON)
