import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from typing import Dict, List, Optional
import json

from geo_services import get_world_map_data
from color_psychology import get_article_colors
from utils import format_number

def render_international_map(news_data: List[Dict]):
    """Render interactive world map with international news"""
    st.markdown("### 🌐 International News Map")
    
    # Create world map
    world_map = folium.Map(
        location=[20, 0],  # Center on equator
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # Get world map data
    map_data = get_world_map_data()
    
    # Country coordinates (major countries for demonstration)
    country_coords = {
        "United States": [39.8283, -98.5795],
        "United Kingdom": [55.3781, -3.4360],
        "Germany": [51.1657, 10.4515],
        "France": [46.2276, 2.2137],
        "Japan": [36.2048, 138.2529],
        "China": [35.8617, 104.1954],
        "Russia": [61.5240, 105.3188],
        "Brazil": [-14.2350, -51.9253],
        "Australia": [-25.2744, 133.7751],
        "India": [20.5937, 78.9629],
        "Canada": [56.1304, -106.3468],
        "Mexico": [23.6345, -102.5528],
        "South Africa": [-30.5595, 22.9375],
        "Egypt": [26.0975, 30.0444],
        "Argentina": [-38.4161, -63.6167]
    }
    
    # Color scheme for different news categories
    category_colors = {
        "breaking": "#EA4335",
        "politics": "#FF9800", 
        "business": "#1A73E8",
        "technology": "#34A853",
        "sports": "#FBBC04",
        "entertainment": "#FF6D01",
        "health": "#9C27B0",
        "science": "#00BCD4",
        "world": "#757575"
    }
    
    # Add markers for countries with news
    if map_data.get('countries'):
        for country_data in map_data['countries']:
            country_name = country_data['country']
            article_count = country_data['article_count']
            avg_sentiment = country_data['avg_sentiment']
            
            if country_name in country_coords:
                lat, lng = country_coords[country_name]
                
                # Determine marker color based on sentiment
                if avg_sentiment > 0.7:
                    color = 'green'
                elif avg_sentiment > 0.3:
                    color = 'orange' 
                else:
                    color = 'red'
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>{country_name}</h4>
                    <p><strong>Articles:</strong> {article_count}</p>
                    <p><strong>Avg Sentiment:</strong> {avg_sentiment:.2f}</p>
                    <p><strong>Mood:</strong> {'😊' if avg_sentiment > 0.7 else '😐' if avg_sentiment > 0.3 else '😟'}</p>
                </div>
                """
                
                # Add marker
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=min(20, max(5, article_count)),
                    popup=folium.Popup(popup_content, max_width=300),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                    weight=2
                ).add_to(world_map)
    
    # Add news articles to map if they have location data
    for article in news_data[:50]:  # Limit to 50 articles for performance
        location_relevance = article.get('location_relevance')
        if location_relevance and isinstance(location_relevance, dict):
            lat = location_relevance.get('lat')
            lng = location_relevance.get('lng')
            
            if lat and lng:
                article_colors = get_article_colors(article)
                category = article.get('category', 'world').lower()
                marker_color = category_colors.get(category, '#757575')
                
                # Create article popup
                popup_html = create_article_popup(article)
                
                folium.Marker(
                    location=[float(lat), float(lng)],
                    popup=folium.Popup(popup_html, max_width=400),
                    icon=folium.Icon(
                        color='blue' if category in ['business', 'technology'] else 
                              'red' if category in ['breaking', 'politics'] else
                              'green' if category in ['health', 'science'] else
                              'orange',
                        icon='info-sign'
                    )
                ).add_to(world_map)
    
    # Display the map
    map_data = st_folium(world_map, width=700, height=500)
    
    # Display map controls and information
    render_map_controls(news_data)
    
    # Show clicked location info
    if map_data['last_object_clicked_popup']:
        st.write("**Last clicked:**", map_data['last_object_clicked_popup'])

def create_article_popup(article: Dict) -> str:
    """Create HTML popup content for article marker"""
    title = article.get('title', 'No Title')[:100]
    summary = article.get('summary', 'No summary')[:200]
    source = article.get('source', 'Unknown')
    category = article.get('category', 'General')
    
    popup_html = f"""
    <div style="width: 300px; font-family: Arial, sans-serif;">
        <div style="
            background: linear-gradient(135deg, #1A73E8, #34A853);
            color: white;
            padding: 8px 12px;
            margin: -8px -12px 8px -12px;
            border-radius: 4px 4px 0 0;
        ">
            <strong>{category.upper()}</strong>
        </div>
        
        <h4 style="margin: 0 0 8px 0; font-size: 14px; line-height: 1.3;">
            {title}
        </h4>
        
        <p style="margin: 0 0 8px 0; font-size: 12px; color: #666; line-height: 1.4;">
            {summary}...
        </p>
        
        <div style="font-size: 11px; color: #888; border-top: 1px solid #eee; padding-top: 6px;">
            <div>📰 {source}</div>
            <div style="margin-top: 4px;">
                <a href="{article.get('url', '#')}" target="_blank" style="
                    background: #1A73E8;
                    color: white;
                    padding: 4px 8px;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 11px;
                ">
                    🔗 Read Full Article
                </a>
            </div>
        </div>
    </div>
    """
    return popup_html

def render_map_controls(news_data: List[Dict]):
    """Render map filtering and control interface"""
    st.markdown("#### 🎛️ Map Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Category filter
        categories = list(set(article.get('category', 'General') for article in news_data))
        selected_categories = st.multiselect(
            "Filter by Category",
            categories,
            default=categories[:3] if len(categories) > 3 else categories
        )
    
    with col2:
        # Sentiment filter
        sentiment_filter = st.selectbox(
            "Sentiment Filter",
            ["All", "Positive (>0.7)", "Neutral (0.3-0.7)", "Negative (<0.3)"]
        )
    
    with col3:
        # Time filter
        time_filter = st.selectbox(
            "Time Range",
            ["Last 24 hours", "Last 3 days", "Last week", "Last month"]
        )
    
    with col4:
        # Map style
        map_style = st.selectbox(
            "Map Style",
            ["OpenStreetMap", "Satellite", "Terrain", "Dark"]
        )
    
    # Map statistics
    st.markdown("#### 📊 Map Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_articles = len(news_data)
        st.metric("Total Articles", format_number(total_articles))
    
    with col2:
        countries_with_news = len(set(
            article.get('location_relevance', {}).get('country', 'Unknown')
            for article in news_data
            if article.get('location_relevance')
        ))
        st.metric("Countries Covered", countries_with_news)
    
    with col3:
        avg_sentiment = sum(
            article.get('sentiment_score', 0.5) for article in news_data
        ) / len(news_data) if news_data else 0
        st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
    
    with col4:
        breaking_news = len([
            article for article in news_data
            if 'breaking' in article.get('title', '').lower()
        ])
        st.metric("Breaking News", breaking_news)

def render_regional_map(region: str, news_data: List[Dict]):
    """Render focused map for specific region"""
    st.markdown(f"### 🗺️ {region} Regional News")
    
    # Regional coordinates
    regional_coords = {
        "North America": [45.0, -100.0],
        "Europe": [54.0, 15.0],
        "Asia": [30.0, 100.0],
        "Africa": [0.0, 20.0],
        "South America": [-15.0, -60.0],
        "Oceania": [-25.0, 140.0]
    }
    
    center = regional_coords.get(region, [0, 0])
    
    # Create regional map
    regional_map = folium.Map(
        location=center,
        zoom_start=3 if region == "Asia" else 4,
        tiles='OpenStreetMap'
    )
    
    # Filter news for region
    regional_news = filter_news_by_region(news_data, region)
    
    # Add regional markers
    for article in regional_news[:30]:  # Limit for performance
        location_relevance = article.get('location_relevance')
        if location_relevance:
            lat = location_relevance.get('lat')
            lng = location_relevance.get('lng')
            
            if lat and lng:
                popup_html = create_article_popup(article)
                
                folium.Marker(
                    location=[float(lat), float(lng)],
                    popup=folium.Popup(popup_html, max_width=400),
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(regional_map)
    
    # Display regional map
    st_folium(regional_map, width=700, height=400)
    
    # Regional statistics
    st.markdown("#### Regional Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Regional Articles", len(regional_news))
    
    with col2:
        if regional_news:
            avg_sentiment = sum(
                article.get('sentiment_score', 0.5) for article in regional_news
            ) / len(regional_news)
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
    
    with col3:
        categories = len(set(article.get('category') for article in regional_news))
        st.metric("Categories", categories)

def filter_news_by_region(news_data: List[Dict], region: str) -> List[Dict]:
    """Filter news articles by geographic region"""
    # Regional country mappings
    regional_countries = {
        "North America": ["United States", "Canada", "Mexico"],
        "Europe": ["United Kingdom", "Germany", "France", "Italy", "Spain", "Netherlands"],
        "Asia": ["China", "Japan", "India", "South Korea", "Thailand", "Singapore"],
        "Africa": ["South Africa", "Nigeria", "Egypt", "Kenya", "Morocco"],
        "South America": ["Brazil", "Argentina", "Chile", "Colombia", "Peru"],
        "Oceania": ["Australia", "New Zealand", "Fiji"]
    }
    
    target_countries = regional_countries.get(region, [])
    
    filtered_news = []
    for article in news_data:
        location_relevance = article.get('location_relevance', {})
        if isinstance(location_relevance, dict):
            country = location_relevance.get('country', '')
            if country in target_countries:
                filtered_news.append(article)
    
    return filtered_news

def render_heatmap(news_data: List[Dict]):
    """Render news density heatmap"""
    st.markdown("### 🔥 News Density Heatmap")
    
    # Extract coordinates for heatmap
    heatmap_data = []
    
    for article in news_data:
        location_relevance = article.get('location_relevance')
        if location_relevance and isinstance(location_relevance, dict):
            lat = location_relevance.get('lat')
            lng = location_relevance.get('lng')
            
            if lat and lng:
                # Weight by sentiment and recency
                weight = 1.0
                sentiment = article.get('sentiment_score', 0.5)
                if sentiment > 0.7:
                    weight *= 1.5
                elif sentiment < 0.3:
                    weight *= 2.0  # Negative news gets higher weight
                
                heatmap_data.append([float(lat), float(lng), weight])
    
    if heatmap_data:
        # Create heatmap
        heatmap_map = folium.Map(location=[20, 0], zoom_start=2)
        
        # Add heatmap layer
        from folium.plugins import HeatMap
        HeatMap(heatmap_data).add_to(heatmap_map)
        
        # Display heatmap
        st_folium(heatmap_map, width=700, height=500)
        
        st.info(f"Showing news density from {len(heatmap_data)} geolocated articles")
    else:
        st.warning("No geographic data available for heatmap")

def render_news_timeline_map(news_data: List[Dict]):
    """Render temporal map showing news evolution"""
    st.markdown("### ⏰ News Timeline Map")
    
    # Time-based filtering
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 6 hours", "Last 24 hours", "Last 3 days", "Last week"]
    )
    
    # Create timeline map
    timeline_map = folium.Map(location=[20, 0], zoom_start=2)
    
    # Color articles by age
    for article in news_data[:50]:
        location_relevance = article.get('location_relevance')
        if location_relevance:
            lat = location_relevance.get('lat')
            lng = location_relevance.get('lng')
            
            if lat and lng:
                # Determine color by article age
                published_at = article.get('published_at')
                if published_at:
                    # Calculate age-based color
                    color = 'red'  # Recent
                    if hasattr(published_at, 'timestamp'):
                        import time
                        age_hours = (time.time() - published_at.timestamp()) / 3600
                        if age_hours > 24:
                            color = 'orange'
                        if age_hours > 72:
                            color = 'yellow'
                        if age_hours > 168:  # 1 week
                            color = 'green'
                else:
                    color = 'gray'
                
                popup_html = create_article_popup(article)
                
                folium.CircleMarker(
                    location=[float(lat), float(lng)],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=400),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(timeline_map)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 150px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Article Age</h4>
    <p><span style="color:red;">●</span> Last 24 hours</p>
    <p><span style="color:orange;">●</span> 1-3 days</p>
    <p><span style="color:yellow;">●</span> 3-7 days</p>
    <p><span style="color:green;">●</span> Older than 1 week</p>
    </div>
    """
    timeline_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Display timeline map
    st_folium(timeline_map, width=700, height=500)

def render_category_map_layers(news_data: List[Dict]):
    """Render map with category-based layers"""
    st.markdown("### 🏷️ Category Map Layers")
    
    # Create base map
    category_map = folium.Map(location=[20, 0], zoom_start=2)
    
    # Group articles by category
    categories = {}
    for article in news_data:
        category = article.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    # Create feature groups for each category
    feature_groups = {}
    category_colors = {
        "Politics": "red",
        "Business": "blue", 
        "Technology": "green",
        "Sports": "orange",
        "Entertainment": "purple",
        "Health": "pink",
        "Science": "lightblue",
        "World": "gray"
    }
    
    for category, articles in categories.items():
        if articles:
            fg = folium.FeatureGroup(name=category)
            color = category_colors.get(category, "gray")
            
            for article in articles[:20]:  # Limit per category
                location_relevance = article.get('location_relevance')
                if location_relevance:
                    lat = location_relevance.get('lat')
                    lng = location_relevance.get('lng')
                    
                    if lat and lng:
                        popup_html = create_article_popup(article)
                        
                        folium.CircleMarker(
                            location=[float(lat), float(lng)],
                            radius=6,
                            popup=folium.Popup(popup_html, max_width=400),
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.6
                        ).add_to(fg)
            
            feature_groups[category] = fg
            fg.add_to(category_map)
    
    # Add layer control
    folium.LayerControl().add_to(category_map)
    
    # Display category map
    st_folium(category_map, width=700, height=500)
    
    # Category statistics
    st.markdown("#### Category Distribution")
    
    category_stats = []
    for category, articles in categories.items():
        category_stats.append({
            "Category": category,
            "Articles": len(articles),
            "Avg Sentiment": sum(a.get('sentiment_score', 0.5) for a in articles) / len(articles) if articles else 0
        })
    
    if category_stats:
        df_stats = pd.DataFrame(category_stats)
        st.dataframe(df_stats, use_container_width=True)
