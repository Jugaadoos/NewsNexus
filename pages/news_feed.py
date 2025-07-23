import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

def render_news_feed(user: Dict[str, Any], services: Dict[str, Any]):
    """Render the main news feed with hierarchical filtering"""
    try:
        st.title("News Feed")
        
        # Sidebar filters
        render_news_filters(services)
        
        # Main content tabs for categories
        category_tabs = st.tabs(["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"])
        
        categories = ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"]
        
        for i, tab in enumerate(category_tabs):
            with tab:
                render_category_feed(categories[i], user, services)
                
    except Exception as e:
        st.error(f"Error loading news feed: {str(e)}")
        logging.error(f"News feed error: {str(e)}")

def render_news_filters(services: Dict[str, Any]):
    """Render news filtering sidebar"""
    try:
        with st.sidebar:
            st.header("News Filters")
            
            # Geographic filtering
            st.subheader("Geographic Scope")
            geo_level = st.selectbox(
                "Select Geographic Level",
                ["Local (50-100 miles)", "Regional (State/Province)", "National (Country)", "International"],
                index=0
            )
            
            # Store in session state
            st.session_state.selected_geo_level = geo_level.split(" ")[0]
            
            # Sentiment filtering
            st.subheader("Content Filters")
            sentiment_filter = st.selectbox(
                "Sentiment",
                ["All", "Positive", "Negative", "Neutral"]
            )
            st.session_state.sentiment_filter = sentiment_filter
            
            # Date range
            st.subheader("Time Range")
            date_range = st.selectbox(
                "Time Period",
                ["Last 24 hours", "Last 3 days", "Last week", "Last month"]
            )
            st.session_state.date_range = date_range
            
            # Source filtering
            st.subheader("News Sources")
            available_sources = ["All Sources", "BBC", "CNN", "Reuters", "Associated Press"]
            selected_sources = st.multiselect(
                "Select Sources",
                available_sources,
                default=["All Sources"]
            )
            st.session_state.selected_sources = selected_sources
            
            # Language preference
            st.subheader("Language")
            language = st.selectbox(
                "Content Language",
                ["English", "Spanish", "French", "German", "Chinese", "Japanese"]
            )
            st.session_state.content_language = language
            
    except Exception as e:
        st.error(f"Error rendering news filters: {str(e)}")

def render_category_feed(category: str, user: Dict[str, Any], services: Dict[str, Any]):
    """Render news feed for a specific category with geographic sub-tabs"""
    try:
        # Geographic sub-tabs
        geo_tabs = st.tabs(["Local", "Regional", "National", "International"])
        geo_levels = ["Local", "Regional", "National", "International"]
        
        for i, geo_tab in enumerate(geo_tabs):
            with geo_tab:
                render_geographic_feed(category, geo_levels[i], user, services)
                
    except Exception as e:
        st.error(f"Error rendering category feed for {category}: {str(e)}")

def render_geographic_feed(category: str, geo_level: str, user: Dict[str, Any], services: Dict[str, Any]):
    """Render news feed for specific category and geographic level"""
    try:
        # Show location context
        if st.session_state.location:
            location = st.session_state.location
            location_text = f"📍 {location.get('city', 'Unknown')}, {location.get('region', 'Unknown')}, {location.get('country', 'Unknown')}"
            st.caption(f"Showing {geo_level.lower()} news for: {location_text}")
        
        # Get filtered articles
        articles = get_filtered_articles(category, geo_level, user, services)
        
        if not articles:
            render_empty_state(category, geo_level)
            return
        
        # Render articles
        render_article_grid(articles, user, services)
        
    except Exception as e:
        st.error(f"Error rendering geographic feed: {str(e)}")

def get_filtered_articles(category: str, geo_level: str, user: Dict[str, Any], services: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get articles with applied filters"""
    try:
        # Get base articles
        articles = services['news'].get_articles(
            category=category,
            geo_level=geo_level,
            location=st.session_state.location,
            limit=20
        )
        
        # Apply sentiment filter
        sentiment_filter = st.session_state.get('sentiment_filter', 'All')
        if sentiment_filter != 'All':
            articles = [
                article for article in articles
                if article.get('sentiment', {}).get('label', '').lower() == sentiment_filter.lower()
            ]
        
        # Apply date filter
        date_range = st.session_state.get('date_range', 'Last 24 hours')
        cutoff_date = get_date_cutoff(date_range)
        if cutoff_date:
            articles = [
                article for article in articles
                if article.get('published_at') and 
                datetime.fromisoformat(article['published_at'].replace('Z', '+00:00')) >= cutoff_date
            ]
        
        # Apply source filter
        selected_sources = st.session_state.get('selected_sources', [])
        if selected_sources and 'All Sources' not in selected_sources:
            articles = [
                article for article in articles
                if article.get('source') in selected_sources
            ]
        
        return articles
        
    except Exception as e:
        logging.error(f"Error filtering articles: {str(e)}")
        return []

def get_date_cutoff(date_range: str) -> datetime:
    """Get cutoff date based on range selection"""
    now = datetime.now()
    
    if date_range == "Last 24 hours":
        return now - timedelta(days=1)
    elif date_range == "Last 3 days":
        return now - timedelta(days=3)
    elif date_range == "Last week":
        return now - timedelta(weeks=1)
    elif date_range == "Last month":
        return now - timedelta(days=30)
    
    return None

def render_article_grid(articles: List[Dict[str, Any]], user: Dict[str, Any], services: Dict[str, Any]):
    """Render articles in a grid layout"""
    try:
        # Show ads for free users
        if st.session_state.get('subscription_tier') == 'free':
            render_banner_ad()
        
        # Render articles
        for i, article in enumerate(articles):
            # Show inline ads every 5 articles for free users
            if i > 0 and i % 5 == 0 and st.session_state.get('subscription_tier') == 'free':
                render_inline_ad()
            
            render_news_card_component(article, user, services)
        
        # Load more button
        if len(articles) >= 20:
            if st.button("Load More Articles", key="load_more_news"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Error rendering article grid: {str(e)}")

def render_news_card_component(article: Dict[str, Any], user: Dict[str, Any], services: Dict[str, Any]):
    """Render individual news card using the news card component"""
    try:
        # Import and use the news card component
        from components.news_card import NewsCard
        
        news_card = NewsCard(services)
        news_card.render(article, user)
        
    except Exception as e:
        # Fallback rendering if component fails
        render_simple_news_card(article, user, services)

def render_simple_news_card(article: Dict[str, Any], user: Dict[str, Any], services: Dict[str, Any]):
    """Simple fallback news card rendering"""
    try:
        # Get color scheme
        sentiment = article.get('sentiment', {'label': 'neutral', 'score': 0.0})
        color_scheme = services['color'].get_color_scheme(article['category'], sentiment)
        
        with st.container():
            # Article content
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(article['title'])
                st.write(article['summary'])
                
                # Article metadata
                metadata_col1, metadata_col2, metadata_col3 = st.columns(3)
                
                with metadata_col1:
                    st.caption(f"📰 {article['source']}")
                
                with metadata_col2:
                    st.caption(f"📂 {article['category']}")
                
                with metadata_col3:
                    if article.get('published_at'):
                        st.caption(f"🕒 {article['published_at'][:10]}")
            
            with col2:
                # Sentiment indicator
                sentiment_label = sentiment.get('label', 'neutral')
                sentiment_colors = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '🟡'
                }
                st.write(f"{sentiment_colors.get(sentiment_label, '🟡')} {sentiment_label.title()}")
                
                # Action buttons
                if user['role'] != 'guest':
                    col_save, col_like = st.columns(2)
                    
                    with col_save:
                        if st.button("💾", key=f"save_{article['id']}", help="Save article"):
                            save_article(article)
                    
                    with col_like:
                        if st.button("❤️", key=f"like_{article['id']}", help="Like article"):
                            like_article(article, services)
                
                # Read original button
                if st.button("📖 Read", key=f"read_{article['id']}"):
                    show_article_modal(article)
            
            st.divider()
            
    except Exception as e:
        st.error(f"Error rendering news card: {str(e)}")

def render_empty_state(category: str, geo_level: str):
    """Render empty state when no articles are found"""
    st.info(f"No {category.lower()} news found for {geo_level.lower()} area. Try adjusting your filters or check back later.")
    
    # Suggestions
    st.subheader("Suggestions:")
    st.write("• Expand your geographic scope")
    st.write("• Try different time ranges")
    st.write("• Check other news categories")
    st.write("• Remove sentiment filters")

def render_banner_ad():
    """Render banner advertisement"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1A73E8, #34A853); color: white; padding: 1rem; text-align: center; border-radius: 0.5rem; margin: 1rem 0;">
        <h3>🎯 Upgrade to Premium</h3>
        <p>Remove ads and get exclusive features!</p>
    </div>
    """, unsafe_allow_html=True)

def render_inline_ad():
    """Render inline advertisement"""
    st.markdown("""
    <div style="background: #f5f5f5; border: 1px dashed #ddd; padding: 1rem; text-align: center; margin: 1rem 0;">
        <h4>Advertisement</h4>
        <p>Sponsored content space</p>
    </div>
    """, unsafe_allow_html=True)

def save_article(article: Dict[str, Any]):
    """Save article to user's collection"""
    try:
        saved_articles = st.session_state.get('saved_articles', [])
        
        # Check if already saved
        if any(saved['id'] == article['id'] for saved in saved_articles):
            st.warning("Article already saved!")
            return
        
        # Add to saved articles
        saved_articles.append(article)
        st.session_state.saved_articles = saved_articles
        
        st.success("Article saved!")
        
    except Exception as e:
        st.error(f"Error saving article: {str(e)}")

def like_article(article: Dict[str, Any], services: Dict[str, Any]):
    """Like an article and track engagement"""
    try:
        # Track engagement
        if st.session_state.user and st.session_state.user.get('id'):
            services['analytics'].track_event(
                user_id=st.session_state.user['id'],
                event_type='like',
                event_data={'article_id': article['id']},
                article_id=article['id'],
                geo_data=st.session_state.location
            )
        
        st.success("Article liked!")
        
    except Exception as e:
        st.error(f"Error liking article: {str(e)}")

def show_article_modal(article: Dict[str, Any]):
    """Show article in an expandable section"""
    try:
        with st.expander("📖 Full Article", expanded=True):
            st.subheader(article['title'])
            st.caption(f"Source: {article['source']} | Published: {article.get('published_at', 'Unknown')}")
            
            if article.get('url'):
                st.markdown(f"**Original URL:** [{article['url']}]({article['url']})")
            
            st.markdown("---")
            
            # Article content
            content = article.get('content', article.get('summary', 'Content not available'))
            st.write(content)
            
            # Social sharing
            st.subheader("Share this article")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Email", key=f"email_{article['id']}"):
                    st.info("Email sharing feature coming soon!")
            
            with col2:
                if st.button("🐦 Twitter", key=f"twitter_{article['id']}"):
                    st.info("Twitter sharing feature coming soon!")
            
            with col3:
                if st.button("📋 Copy Link", key=f"copy_{article['id']}"):
                    st.success("Link copied to clipboard!")
                    
    except Exception as e:
        st.error(f"Error showing article: {str(e)}")

def render_trending_topics():
    """Render trending topics sidebar"""
    try:
        with st.sidebar:
            st.header("Trending Topics")
            
            # Sample trending topics - in production this would come from analytics
            trending = [
                "AI Technology",
                "Climate Change",
                "Global Economy",
                "Space Exploration",
                "Healthcare Innovation"
            ]
            
            for topic in trending:
                if st.button(f"🔥 {topic}", key=f"trending_{topic}"):
                    st.session_state.search_query = topic
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Error rendering trending topics: {str(e)}")

def render_search_interface():
    """Render search interface"""
    try:
        st.subheader("Search News")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search articles...",
                value=st.session_state.get('search_query', ''),
                placeholder="Enter keywords, topics, or phrases"
            )
        
        with col2:
            search_button = st.button("🔍 Search", key="search_news")
        
        if search_button and search_query:
            st.session_state.search_query = search_query
            perform_search(search_query)
            
    except Exception as e:
        st.error(f"Error rendering search interface: {str(e)}")

def perform_search(query: str):
    """Perform news search"""
    try:
        st.info(f"Searching for: {query}")
        # Search functionality would be implemented here
        st.write("Search results will appear here...")
        
    except Exception as e:
        st.error(f"Error performing search: {str(e)}")
