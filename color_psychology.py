import colorsys
from typing import Dict, List, Optional
from config import COLOR_PSYCHOLOGY
from ai_services import analyze_sentiment

class ColorPsychology:
    def __init__(self):
        self.color_schemes = COLOR_PSYCHOLOGY
        self.sentiment_thresholds = {
            "very_negative": 0.2,
            "negative": 0.4,
            "neutral": 0.6,
            "positive": 0.8,
            "very_positive": 1.0
        }
    
    def determine_news_type(self, article: Dict) -> str:
        """Determine news type based on content analysis"""
        # Check for breaking news indicators
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        breaking_keywords = ['breaking', 'urgent', 'alert', 'emergency', 'developing']
        if any(keyword in title or keyword in content for keyword in breaking_keywords):
            return 'breaking'
        
        # Check category-based news types
        category = article.get('category', '').lower()
        category_mapping = {
            'politics': 'politics',
            'business': 'business',
            'technology': 'technology',
            'sports': 'sports',
            'entertainment': 'entertainment',
            'health': 'health',
            'science': 'science'
        }
        
        if category in category_mapping:
            return category_mapping[category]
        
        # Check sentiment for positive/neutral classification
        sentiment_score = article.get('sentiment_score', 0.5)
        if sentiment_score >= 0.7:
            return 'positive'
        
        return 'neutral'
    
    def get_color_for_news_type(self, news_type: str) -> Dict:
        """Get color scheme for news type"""
        return self.color_schemes.get(news_type, self.color_schemes['neutral'])
    
    def get_sentiment_color(self, sentiment_score: float) -> str:
        """Get color based on sentiment score"""
        if sentiment_score <= self.sentiment_thresholds["very_negative"]:
            return "#D32F2F"  # Dark red
        elif sentiment_score <= self.sentiment_thresholds["negative"]:
            return "#F57C00"  # Orange
        elif sentiment_score <= self.sentiment_thresholds["neutral"]:
            return "#616161"  # Gray
        elif sentiment_score <= self.sentiment_thresholds["positive"]:
            return "#388E3C"  # Green
        else:
            return "#2E7D32"  # Dark green
    
    def generate_gradient_colors(self, base_color: str, intensity: float = 0.5) -> Dict:
        """Generate gradient colors based on base color"""
        # Convert hex to RGB
        base_rgb = self.hex_to_rgb(base_color)
        
        # Create lighter and darker variants
        lighter = self.lighten_color(base_rgb, intensity)
        darker = self.darken_color(base_rgb, intensity)
        
        return {
            "base": base_color,
            "lighter": self.rgb_to_hex(lighter),
            "darker": self.rgb_to_hex(darker),
            "gradient": f"linear-gradient(135deg, {self.rgb_to_hex(lighter)}, {base_color}, {self.rgb_to_hex(darker)})"
        }
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def lighten_color(self, rgb: tuple, factor: float = 0.3) -> tuple:
        """Lighten RGB color by factor"""
        return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
    
    def darken_color(self, rgb: tuple, factor: float = 0.3) -> tuple:
        """Darken RGB color by factor"""
        return tuple(max(0, int(c * (1 - factor))) for c in rgb)
    
    def get_complementary_color(self, hex_color: str) -> str:
        """Get complementary color"""
        rgb = self.hex_to_rgb(hex_color)
        # Convert to HSV
        hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        # Add 180 degrees to hue for complementary
        comp_hue = (hsv[0] + 0.5) % 1.0
        comp_rgb = colorsys.hsv_to_rgb(comp_hue, hsv[1], hsv[2])
        # Convert back to 0-255 range
        comp_rgb = tuple(int(c * 255) for c in comp_rgb)
        return self.rgb_to_hex(comp_rgb)
    
    def get_accessible_text_color(self, background_color: str) -> str:
        """Get accessible text color based on background"""
        rgb = self.hex_to_rgb(background_color)
        # Calculate luminance
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        # Return white text for dark backgrounds, black for light
        return "#FFFFFF" if luminance < 0.5 else "#000000"
    
    def generate_article_colors(self, article: Dict) -> Dict:
        """Generate complete color scheme for article"""
        news_type = self.determine_news_type(article)
        base_colors = self.get_color_for_news_type(news_type)
        
        sentiment_score = article.get('sentiment_score', 0.5)
        sentiment_color = self.get_sentiment_color(sentiment_score)
        
        # Generate gradient colors
        gradient_colors = self.generate_gradient_colors(base_colors['primary'])
        
        return {
            'news_type': news_type,
            'primary': base_colors['primary'],
            'secondary': base_colors['secondary'],
            'accent': base_colors['accent'],
            'sentiment_color': sentiment_color,
            'gradient': gradient_colors['gradient'],
            'border_color': gradient_colors['darker'],
            'hover_color': gradient_colors['lighter'],
            'text_color': self.get_accessible_text_color(base_colors['secondary'])
        }
    
    def apply_urgency_styling(self, article: Dict, colors: Dict) -> Dict:
        """Apply urgency-based styling modifications"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Check for urgency indicators
        high_urgency_keywords = ['breaking', 'urgent', 'alert', 'emergency', 'crisis']
        medium_urgency_keywords = ['developing', 'update', 'latest', 'now']
        
        urgency_level = 'low'
        if any(keyword in title for keyword in high_urgency_keywords):
            urgency_level = 'high'
        elif any(keyword in title for keyword in medium_urgency_keywords):
            urgency_level = 'medium'
        
        # Modify colors based on urgency
        if urgency_level == 'high':
            colors['border_color'] = '#FF0000'
            colors['accent'] = '#FF4444'
            colors['animation'] = 'pulse 2s infinite'
        elif urgency_level == 'medium':
            colors['border_color'] = '#FF6600'
            colors['accent'] = '#FF8844'
            colors['animation'] = 'glow 3s ease-in-out infinite'
        
        colors['urgency_level'] = urgency_level
        return colors
    
    def get_theme_colors(self, articles: List[Dict]) -> Dict:
        """Get overall theme colors based on article collection"""
        if not articles:
            return self.color_schemes['neutral']
        
        # Analyze overall sentiment and news types
        sentiment_scores = [article.get('sentiment_score', 0.5) for article in articles]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Count news types
        news_types = [self.determine_news_type(article) for article in articles]
        most_common_type = max(set(news_types), key=news_types.count)
        
        # Get base colors for most common type
        base_colors = self.get_color_for_news_type(most_common_type)
        
        # Adjust based on average sentiment
        if avg_sentiment < 0.3:
            base_colors['primary'] = self.color_schemes['breaking']['primary']
        elif avg_sentiment > 0.7:
            base_colors['primary'] = self.color_schemes['positive']['primary']
        
        return base_colors

# Initialize color psychology
color_psychology = ColorPsychology()

# Export functions for easy import
def get_color_scheme(articles: List[Dict]) -> Dict:
    """Get color scheme for articles"""
    return color_psychology.get_theme_colors(articles)

def get_article_colors(article: Dict) -> Dict:
    """Get colors for a specific article"""
    colors = color_psychology.generate_article_colors(article)
    return color_psychology.apply_urgency_styling(article, colors)

def apply_dynamic_styling(color_scheme: Dict) -> str:
    """Apply dynamic styling to the page"""
    # This would typically inject CSS into the page
    css_styles = f"""
    <style>
    .news-card {{
        background: {color_scheme.get('secondary', '#FFFFFF')};
        border-left: 4px solid {color_scheme.get('primary', '#1A73E8')};
        transition: all 0.3s ease;
    }}
    
    .news-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    .urgency-high {{
        animation: pulse 2s infinite;
        border-color: #FF0000 !important;
    }}
    
    .urgency-medium {{
        animation: glow 3s ease-in-out infinite;
        border-color: #FF6600 !important;
    }}
    
    @keyframes pulse {{
        0% {{ border-color: #FF0000; }}
        50% {{ border-color: #FF4444; }}
        100% {{ border-color: #FF0000; }}
    }}
    
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(255, 102, 0, 0.5); }}
        50% {{ box-shadow: 0 0 20px rgba(255, 102, 0, 0.8); }}
    }}
    </style>
    """
    return css_styles
