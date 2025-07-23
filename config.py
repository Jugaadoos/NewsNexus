import os

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
PGHOST = os.environ.get("PGHOST", "")
PGPORT = os.environ.get("PGPORT", "5432")
PGDATABASE = os.environ.get("PGDATABASE", "")
PGUSER = os.environ.get("PGUSER", "")
PGPASSWORD = os.environ.get("PGPASSWORD", "")

# Application Settings
APP_NAME = "AI News Hub"
APP_VERSION = "1.0.0"
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# News Sources Configuration
RSS_FEEDS = {
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://www.aljazeera.com/xml/rss/all.xml"
    ],
    "politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://rss.cnn.com/rss/cnn_allpolitics.rss",
        "https://feeds.reuters.com/Reuters/PoliticsNews"
    ],
    "business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://rss.cnn.com/rss/money_latest.rss",
        "https://feeds.reuters.com/reuters/businessNews"
    ],
    "technology": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://rss.cnn.com/rss/cnn_tech.rss",
        "https://feeds.reuters.com/reuters/technologyNews"
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://rss.cnn.com/rss/si_topstories.rss",
        "https://feeds.reuters.com/reuters/sportsNews"
    ],
    "entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://rss.cnn.com/rss/cnn_showbiz.rss"
    ],
    "health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.cnn.com/rss/cnn_health.rss",
        "https://feeds.reuters.com/reuters/healthNews"
    ],
    "science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://rss.cnn.com/rss/cnn_space.rss"
    ]
}

# Geographic Boundaries
LOCAL_RADIUS_MILES = 75
REGIONAL_BOUNDARIES = {
    "US": "states",
    "UK": "counties",
    "CA": "provinces",
    "AU": "states",
    "DE": "lander"
}

# Color Psychology Configuration
COLOR_PSYCHOLOGY = {
    "breaking": {"primary": "#EA4335", "secondary": "#FFF3F3", "accent": "#D32F2F"},
    "politics": {"primary": "#FF9800", "secondary": "#FFF8E1", "accent": "#F57C00"},
    "business": {"primary": "#1A73E8", "secondary": "#E8F0FE", "accent": "#1565C0"},
    "technology": {"primary": "#34A853", "secondary": "#E8F5E8", "accent": "#2E7D32"},
    "sports": {"primary": "#FBBC04", "secondary": "#FFFBF0", "accent": "#F9A825"},
    "entertainment": {"primary": "#FF6D01", "secondary": "#FFF4E6", "accent": "#EF6C00"},
    "health": {"primary": "#9C27B0", "secondary": "#F3E5F5", "accent": "#7B1FA2"},
    "science": {"primary": "#00BCD4", "secondary": "#E0F2F1", "accent": "#0097A7"},
    "positive": {"primary": "#4CAF50", "secondary": "#E8F5E8", "accent": "#388E3C"},
    "neutral": {"primary": "#757575", "secondary": "#F5F5F5", "accent": "#616161"}
}

# Subscription Tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "features": ["Basic news access", "Limited summaries", "Ads displayed"],
        "ad_frequency": "high"
    },
    "basic": {
        "name": "Basic",
        "price": 9.99,
        "features": ["Ad-free experience", "Unlimited summaries", "Basic analytics"],
        "ad_frequency": "none"
    },
    "premium": {
        "name": "Premium",
        "price": 19.99,
        "features": ["Everything in Basic", "AI theme generation", "Advanced analytics", "Priority support"],
        "ad_frequency": "none"
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "features": ["Everything in Premium", "API access", "Custom integration", "Dedicated support"],
        "ad_frequency": "none"
    }
}

# User Roles
USER_ROLES = {
    "reader": {"permissions": ["read_news", "save_articles", "comment"]},
    "reviewer": {"permissions": ["read_news", "save_articles", "comment", "review_articles"]},
    "editor": {"permissions": ["read_news", "save_articles", "comment", "review_articles", "edit_content"]},
    "creator": {"permissions": ["read_news", "save_articles", "comment", "create_content", "manage_profile"]},
    "journalist": {"permissions": ["read_news", "save_articles", "comment", "create_content", "manage_profile", "verified_badge"]},
    "partner": {"permissions": ["read_news", "save_articles", "comment", "create_content", "manage_profile", "analytics_access"]},
    "affiliate": {"permissions": ["read_news", "save_articles", "comment", "manage_products", "track_commissions"]},
    "admin": {"permissions": ["all"]}
}

# Affiliate Commission Structure
AFFILIATE_COMMISSION = {
    "subscription": 0.30,  # 30% commission on subscriptions
    "product": 0.15,       # 15% commission on product sales
    "referral": 5.00       # $5 per referral
}
