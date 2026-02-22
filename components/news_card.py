import streamlit as st
from datetime import datetime
from typing import Dict, Optional
import html
import json

from color_psychology import get_article_colors
from ai_services import generate_opinion
from utils import format_date, get_time_ago, truncate_text, calculate_reading_time

def render_news_card(article: Dict, color_scheme: Dict = None, show_full: bool = False):
    """Render a news article card with dynamic styling"""
    
    # Get dynamic colors for this article
    article_colors = get_article_colors(article)
    
    # Determine urgency level for animations
    urgency_class = ""
    if article_colors.get('urgency_level') == 'high':
        urgency_class = "urgency-high"
    elif article_colors.get('urgency_level') == 'medium':
        urgency_class = "urgency-medium"
    
    # Get news type for styling
    news_type = article_colors.get('news_type', 'neutral')
    
    # Create the card HTML with dynamic styling
    card_id = f"card_{article.get('id', hash(article.get('url', '')))}"
    
    safe_url_js = json.dumps(article.get('url', ''))

    # Card content
    title = html.escape(article.get('title', 'No Title'))
    summary = html.escape(article.get('summary', 'No summary available'))
    source = html.escape(article.get('source', 'Unknown Source'))
    
    # Time formatting
    published_at = article.get('published_at')
    if published_at:
        if isinstance(published_at, str):
            time_display = published_at
        else:
            time_display = get_time_ago(published_at)
    else:
        time_display = "Unknown time"
    
    # Reading time calculation
    content_length = len(article.get('content', ''))
    reading_time = calculate_reading_time(article.get('content', ''))
    
    # Sentiment indicator
    sentiment_score = article.get('sentiment_score', 0.5)
    sentiment_emoji = "😊" if sentiment_score > 0.7 else "😐" if sentiment_score > 0.3 else "😟"
    
    # Create card HTML
    card_html = f"""
    <div class="news-card {news_type} {urgency_class}" id="{card_id}" style="
        border-left-color: {article_colors.get('primary', '#1A73E8')};
        background: {article_colors.get('hover_color', '#FFFFFF')};
        transition: all 0.3s ease;
    ">
        <div class="news-card-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div class="news-card-category" style="
                background: {article_colors.get('primary', '#1A73E8')};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
            ">
                {article.get('category', 'General')}
            </div>
            <div class="news-card-sentiment" style="font-size: 16px;">
                {sentiment_emoji}
            </div>
        </div>
        
        <h3 class="news-card-title" style="
            color: {article_colors.get('text_color', '#202124')};
            margin-bottom: 12px;
            line-height: 1.4;
            font-size: 18px;
            font-weight: 600;
        ">
            {title}
        </h3>
        
        <p class="news-card-summary" style="
            color: #5f6368;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 16px;
        ">
            {truncate_text(summary, 150)}
        </p>
        
        <div class="news-card-meta" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #80868b;
            margin-bottom: 12px;
        ">
            <div class="news-card-source" style="font-weight: 500;">
                📰 {source}
            </div>
            <div class="news-card-time">
                🕒 {time_display}
            </div>
            <div class="news-card-reading-time">
                📖 {reading_time} min read
            </div>
        </div>
        
        <div class="news-card-actions" style="
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        ">
            <button class="card-action-btn" onclick="openArticle({safe_url_js})" style="
                background: {article_colors.get('primary', '#1A73E8')};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s ease;
            ">
                🔗 Read Full Article
            </button>
            
            <button class="card-action-btn" onclick="saveArticle({article.get('id', 0)})" style="
                background: {article_colors.get('secondary', '#34A853')};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s ease;
            ">
                💾 Save
            </button>
            
            <button class="card-action-btn" onclick="shareArticle('{article.get('url', '')}')" style="
                background: #666;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s ease;
            ">
                📤 Share
            </button>
        </div>
    </div>
    
    <script>
        function openArticle(url) {{
            if (url) {{
                window.open(url, '_blank');
            }}
        }}
        
        function saveArticle(articleId) {{
            // This would integrate with Streamlit's session state
            alert('Article saved! (Integration with backend needed)');
        }}
        
        function shareArticle(url) {{
            if (navigator.share) {{
                navigator.share({{
                    title: '{title}',
                    url: url
                }});
            }} else {{
                navigator.clipboard.writeText(url);
                alert('Article URL copied to clipboard!');
            }}
        }}
    </script>
    """
    
    # Display the card
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Add interactive elements using Streamlit
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("📖 Read Article", key=f"read_{card_id}"):
            render_article_modal(article)
    
    with col2:
        if st.button("💾 Save", key=f"save_{card_id}"):
            save_article_to_user(article)
    
    with col3:
        if st.button("💬 Comment", key=f"comment_{card_id}"):
            render_comment_section(article)
    
    with col4:
        if st.button("🤖 AI Opinion", key=f"opinion_{card_id}"):
            render_ai_opinion(article)

def render_article_modal(article: Dict):
    """Render article in a modal-like expandable section"""
    with st.expander("📖 Full Article", expanded=True):
        st.markdown(f"# {article.get('title', 'No Title')}")
        
        # Article metadata
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Source:** {article.get('source', 'Unknown')}")
        
        with col2:
            if article.get('author'):
                st.write(f"**Author:** {article.get('author')}")
        
        with col3:
            if article.get('published_at'):
                st.write(f"**Published:** {format_date(article['published_at'])}")
        
        st.divider()
        
        # Article content
        content = article.get('content', article.get('summary', 'No content available'))
        st.markdown(content)
        
        # Article actions
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔗 View Original", key=f"original_{article.get('id')}"):
                if article.get('url'):
                    st.markdown(f"[Open Original Article]({article['url']})")
                else:
                    st.error("No original URL available")
        
        with col2:
            if st.button("🎧 Listen", key=f"listen_{article.get('id')}"):
                render_text_to_speech(article)
        
        with col3:
            if st.button("📊 Analytics", key=f"analytics_{article.get('id')}"):
                render_article_analytics(article)
        
        with col4:
            if st.button("🏷️ Similar", key=f"similar_{article.get('id')}"):
                render_similar_articles(article)

def render_text_to_speech(article: Dict):
    """Render text-to-speech functionality"""
    st.markdown("### 🎧 Text-to-Speech")
    
    content_to_read = article.get('content') or article.get('summary', '')
    
    if content_to_read:
        # Create audio element with text-to-speech
        audio_html = f"""
        <div style="margin: 16px 0;">
            <button onclick="speakText()" style="
                background: #1A73E8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 8px;
            ">
                🔊 Play
            </button>
            
            <button onclick="stopSpeaking()" style="
                background: #EA4335;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 8px;
            ">
                ⏹️ Stop
            </button>
            
            <button onclick="pauseSpeaking()" style="
                background: #FBBC04;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
            ">
                ⏸️ Pause
            </button>
        </div>
        
        <script>
            let utterance = null;
            
            function speakText() {{
                if ('speechSynthesis' in window) {{
                    utterance = new SpeechSynthesisUtterance(`{content_to_read[:1000]}`);
                    utterance.rate = 1;
                    utterance.pitch = 1;
                    utterance.volume = 1;
                    speechSynthesis.speak(utterance);
                }} else {{
                    alert('Text-to-speech not supported in this browser');
                }}
            }}
            
            function stopSpeaking() {{
                if (speechSynthesis.speaking) {{
                    speechSynthesis.cancel();
                }}
            }}
            
            function pauseSpeaking() {{
                if (speechSynthesis.speaking) {{
                    speechSynthesis.pause();
                }}
            }}
        </script>
        """
        
        st.markdown(audio_html, unsafe_allow_html=True)
        
        # Voice settings
        col1, col2, col3 = st.columns(3)
        
        with col1:
            speed = st.slider("Reading Speed", 0.5, 2.0, 1.0, 0.1)
        
        with col2:
            pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
        
        with col3:
            volume = st.slider("Volume", 0.0, 1.0, 1.0, 0.1)
    else:
        st.error("No content available for text-to-speech")

def render_comment_section(article: Dict):
    """Render comment section for article"""
    st.markdown("### 💬 Comments")
    
    # Add comment form
    with st.form(f"comment_form_{article.get('id')}"):
        comment_text = st.text_area("Add a comment", placeholder="Share your thoughts on this article...")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.form_submit_button("💬 Post Comment"):
                if comment_text.strip():
                    # Would save comment to database
                    st.success("Comment posted! (Database integration needed)")
                else:
                    st.error("Please enter a comment")
    
    # Display existing comments (placeholder)
    st.markdown("#### Recent Comments")
    
    # Mock comments for demonstration
    mock_comments = [
        {
            "user": "John Doe",
            "comment": "Great article! Very informative.",
            "timestamp": datetime.now(),
            "likes": 5
        },
        {
            "user": "Jane Smith", 
            "comment": "I disagree with some points, but well written.",
            "timestamp": datetime.now(),
            "likes": 2
        }
    ]
    
    for comment in mock_comments:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{comment['user']}**")
                st.write(comment['comment'])
            
            with col2:
                st.write(f"*{get_time_ago(comment['timestamp'])}*")
            
            with col3:
                st.write(f"👍 {comment['likes']}")
            
            st.divider()

def render_ai_opinion(article: Dict):
    """Render AI-generated opinion on article"""
    st.markdown("### 🤖 AI Opinion")
    
    with st.spinner("Generating AI opinion..."):
        try:
            opinion = generate_opinion(article.get('content', ''), 'balanced')
            
            st.markdown("#### AI Analysis")
            st.write(opinion)
            
            # Opinion perspectives
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔵 Conservative View", key=f"conservative_{article.get('id')}"):
                    conservative_opinion = generate_opinion(article.get('content', ''), 'conservative')
                    st.write("**Conservative Perspective:**")
                    st.write(conservative_opinion)
            
            with col2:
                if st.button("🔴 Liberal View", key=f"liberal_{article.get('id')}"):
                    liberal_opinion = generate_opinion(article.get('content', ''), 'liberal')
                    st.write("**Liberal Perspective:**")
                    st.write(liberal_opinion)
            
        except Exception as e:
            st.error(f"Error generating AI opinion: {e}")

def render_article_analytics(article: Dict):
    """Render article analytics and metrics"""
    st.markdown("### 📊 Article Analytics")
    
    # Article metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sentiment Score", f"{article.get('sentiment_score', 0.5):.2f}")
    
    with col2:
        reading_time = calculate_reading_time(article.get('content', ''))
        st.metric("Reading Time", f"{reading_time} min")
    
    with col3:
        word_count = len(article.get('content', '').split())
        st.metric("Word Count", word_count)
    
    with col4:
        # Would get from database
        st.metric("Views", "0")
    
    # Content analysis
    st.markdown("#### Content Analysis")
    
    try:
        from ai_services import extract_key_entities
        entities = extract_key_entities(article.get('content', ''))
        
        if entities:
            col1, col2 = st.columns(2)
            
            with col1:
                if entities.get('people'):
                    st.write("**People Mentioned:**")
                    for person in entities['people'][:5]:
                        st.write(f"- {person}")
                
                if entities.get('organizations'):
                    st.write("**Organizations:**")
                    for org in entities['organizations'][:5]:
                        st.write(f"- {org}")
            
            with col2:
                if entities.get('locations'):
                    st.write("**Locations:**")
                    for location in entities['locations'][:5]:
                        st.write(f"- {location}")
                
                if entities.get('events'):
                    st.write("**Events:**")
                    for event in entities['events'][:5]:
                        st.write(f"- {event}")
        
    except Exception as e:
        st.info("Content analysis not available")

def render_similar_articles(article: Dict):
    """Render similar articles recommendations"""
    st.markdown("### 🏷️ Similar Articles")
    
    # This would use the similarity system from ai_services
    try:
        from ai_services import generate_article_embedding, find_similar_articles
        
        # Generate embedding for current article
        content = article.get('content', '') or article.get('summary', '')
        if content:
            st.info("Similar articles feature would use AI embeddings to find related content")
            
            # Mock similar articles for demonstration
            mock_similar = [
                {
                    "title": "Related Article 1",
                    "summary": "This is a related article summary...",
                    "similarity": 0.85
                },
                {
                    "title": "Related Article 2", 
                    "summary": "Another related article summary...",
                    "similarity": 0.78
                }
            ]
            
            for similar in mock_similar:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{similar['title']}**")
                        st.write(similar['summary'])
                    
                    with col2:
                        st.write(f"**Similarity:** {similar['similarity']:.0%}")
                        if st.button("Read", key=f"similar_{similar['title']}"):
                            st.info("Would open similar article")
                    
                    st.divider()
        else:
            st.error("No content available for similarity analysis")
            
    except Exception as e:
        st.error(f"Error finding similar articles: {e}")

def save_article_to_user(article: Dict):
    """Save article to user's saved list"""
    try:
        from auth import get_current_user
        from database import save_user_article_action
        
        user = get_current_user()
        if user and article.get('id'):
            result = save_user_article_action(user['id'], article['id'], 'saved')
            if result:
                st.success("Article saved!")
            else:
                st.error("Error saving article")
        else:
            st.warning("Please login to save articles")
    
    except Exception as e:
        st.error(f"Error saving article: {e}")

def render_compact_news_card(article: Dict):
    """Render a compact version of the news card"""
    article_colors = get_article_colors(article)
    
    # Compact card HTML
    compact_html = f"""
    <div style="
        border-left: 4px solid {article_colors.get('primary', '#1A73E8')};
        background: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; font-size: 16px; line-height: 1.3;">
                    {html.escape(article.get('title', 'No Title'))}
                </h4>
                <div style="font-size: 12px; color: #666; display: flex; gap: 16px;">
                    <span>📰 {html.escape(article.get('source', 'Unknown'))}</span>
                    <span>🕒 {get_time_ago(article.get('published_at', datetime.now()))}</span>
                    <span style="
                        background: {article_colors.get('primary', '#1A73E8')};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 2px;
                        text-transform: uppercase;
                    ">
                        {article.get('category', 'General')}
                    </span>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(compact_html, unsafe_allow_html=True)
