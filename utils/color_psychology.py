from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime

class ColorPsychology:
    def __init__(self):
        # Color schemes based on psychology and news content
        self.color_schemes = {
            'breaking_urgent': {
                'primary': '#EA4335',  # Red
                'secondary': '#FBBC04',  # Amber
                'background': '#FFF3E0',  # Light orange
                'text': '#BF360C',  # Dark red
                'border': '#FF5722',  # Deep orange
                'psychology': 'urgency, attention, alertness'
            },
            'politics_conflict': {
                'primary': '#FF9800',  # Orange
                'secondary': '#FF7043',  # Deep orange
                'background': '#FFF8E1',  # Light yellow
                'text': '#E65100',  # Dark orange
                'border': '#FF6F00',  # Amber
                'psychology': 'debate, tension, importance'
            },
            'business_economy': {
                'primary': '#1976D2',  # Blue
                'secondary': '#42A5F5',  # Light blue
                'background': '#E3F2FD',  # Very light blue
                'text': '#0D47A1',  # Dark blue
                'border': '#1565C0',  # Medium blue
                'psychology': 'trust, stability, professionalism'
            },
            'technology_innovation': {
                'primary': '#4CAF50',  # Green
                'secondary': '#66BB6A',  # Light green
                'background': '#E8F5E8',  # Very light green
                'text': '#2E7D32',  # Dark green
                'border': '#388E3C',  # Medium green
                'psychology': 'growth, innovation, progress'
            },
            'sports_entertainment': {
                'primary': '#FFC107',  # Yellow
                'secondary': '#FFD54F',  # Light yellow
                'background': '#FFFDE7',  # Very light yellow
                'text': '#F57F17',  # Dark yellow
                'border': '#FFA000',  # Amber
                'psychology': 'energy, excitement, joy'
            },
            'health_medical': {
                'primary': '#9C27B0',  # Purple
                'secondary': '#BA68C8',  # Light purple
                'background': '#F3E5F5',  # Very light purple
                'text': '#6A1B9A',  # Dark purple
                'border': '#8E24AA',  # Medium purple
                'psychology': 'care, healing, wisdom'
            },
            'environment_climate': {
                'primary': '#009688',  # Teal
                'secondary': '#4DB6AC',  # Light teal
                'background': '#E0F2F1',  # Very light teal
                'text': '#00695C',  # Dark teal
                'border': '#00796B',  # Medium teal
                'psychology': 'nature, balance, sustainability'
            },
            'positive_uplifting': {
                'primary': '#8BC34A',  # Light green
                'secondary': '#AED581',  # Lighter green
                'background': '#F1F8E9',  # Very light green
                'text': '#689F38',  # Dark green
                'border': '#7CB342',  # Medium green
                'psychology': 'hope, positivity, harmony'
            },
            'neutral_general': {
                'primary': '#757575',  # Gray
                'secondary': '#9E9E9E',  # Light gray
                'background': '#FAFAFA',  # Very light gray
                'text': '#424242',  # Dark gray
                'border': '#616161',  # Medium gray
                'psychology': 'neutrality, balance, information'
            },
            'science_research': {
                'primary': '#3F51B5',  # Indigo
                'secondary': '#7986CB',  # Light indigo
                'background': '#E8EAF6',  # Very light indigo
                'text': '#283593',  # Dark indigo
                'border': '#303F9F',  # Medium indigo
                'psychology': 'knowledge, depth, discovery'
            }
        }
        
        # Sentiment to color mapping
        self.sentiment_colors = {
            'positive': ['positive_uplifting', 'technology_innovation'],
            'negative': ['breaking_urgent', 'politics_conflict'],
            'neutral': ['neutral_general', 'business_economy']
        }
        
        # Category to color mapping
        self.category_colors = {
            'World': ['breaking_urgent', 'politics_conflict'],
            'Politics': ['politics_conflict', 'breaking_urgent'],
            'Business': ['business_economy', 'neutral_general'],
            'Technology': ['technology_innovation', 'science_research'],
            'Sports': ['sports_entertainment', 'positive_uplifting'],
            'Entertainment': ['sports_entertainment', 'positive_uplifting'],
            'Health': ['health_medical', 'positive_uplifting'],
            'Science': ['science_research', 'technology_innovation']
        }
    
    def get_color_scheme(self, category: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Get color scheme based on category and sentiment"""
        try:
            sentiment_label = sentiment.get('label', 'neutral').lower()
            sentiment_score = sentiment.get('score', 0.0)
            
            # Get potential color schemes
            category_schemes = self.category_colors.get(category, ['neutral_general'])
            sentiment_schemes = self.sentiment_colors.get(sentiment_label, ['neutral_general'])
            
            # Find best matching scheme
            best_scheme = self._find_best_scheme(category_schemes, sentiment_schemes, sentiment_score)
            
            # Get the color scheme
            color_scheme = self.color_schemes.get(best_scheme, self.color_schemes['neutral_general'])
            
            # Add dynamic adjustments based on sentiment intensity
            adjusted_scheme = self._adjust_for_intensity(color_scheme, sentiment_score)
            
            return {
                'scheme_name': best_scheme,
                'colors': adjusted_scheme,
                'category': category,
                'sentiment': sentiment_label,
                'intensity': abs(sentiment_score)
            }
            
        except Exception as e:
            logging.error(f"Error getting color scheme: {str(e)}")
            return {
                'scheme_name': 'neutral_general',
                'colors': self.color_schemes['neutral_general'],
                'category': category,
                'sentiment': 'neutral',
                'intensity': 0.0
            }
    
    def _find_best_scheme(self, category_schemes: List[str], sentiment_schemes: List[str], 
                         sentiment_score: float) -> str:
        """Find the best matching color scheme"""
        try:
            # Find intersection of category and sentiment schemes
            common_schemes = list(set(category_schemes) & set(sentiment_schemes))
            
            if common_schemes:
                # If there's a common scheme, use it
                return common_schemes[0]
            
            # If no common scheme, prioritize based on sentiment intensity
            if abs(sentiment_score) > 0.7:
                # High intensity sentiment, prioritize sentiment-based colors
                return sentiment_schemes[0]
            else:
                # Low intensity sentiment, prioritize category-based colors
                return category_schemes[0]
                
        except Exception as e:
            logging.error(f"Error finding best scheme: {str(e)}")
            return 'neutral_general'
    
    def _adjust_for_intensity(self, color_scheme: Dict[str, str], sentiment_score: float) -> Dict[str, str]:
        """Adjust color scheme based on sentiment intensity"""
        try:
            adjusted_scheme = color_scheme.copy()
            
            # Adjust opacity/intensity based on sentiment score
            intensity = abs(sentiment_score)
            
            if intensity > 0.8:
                # High intensity - make colors more vibrant
                adjusted_scheme['intensity'] = 'high'
                adjusted_scheme['opacity'] = '1.0'
            elif intensity > 0.5:
                # Medium intensity - standard colors
                adjusted_scheme['intensity'] = 'medium'
                adjusted_scheme['opacity'] = '0.9'
            else:
                # Low intensity - softer colors
                adjusted_scheme['intensity'] = 'low'
                adjusted_scheme['opacity'] = '0.8'
            
            return adjusted_scheme
            
        except Exception as e:
            logging.error(f"Error adjusting for intensity: {str(e)}")
            return color_scheme
    
    def get_dynamic_gradient(self, sentiment_score: float, category: str) -> Dict[str, str]:
        """Get dynamic gradient based on sentiment and category"""
        try:
            # Base gradients for different sentiment ranges
            if sentiment_score > 0.3:
                # Positive sentiment
                return {
                    'start': '#4CAF50',
                    'end': '#81C784',
                    'direction': 'to right'
                }
            elif sentiment_score < -0.3:
                # Negative sentiment
                return {
                    'start': '#F44336',
                    'end': '#EF5350',
                    'direction': 'to right'
                }
            else:
                # Neutral sentiment
                return {
                    'start': '#9E9E9E',
                    'end': '#BDBDBD',
                    'direction': 'to right'
                }
                
        except Exception as e:
            logging.error(f"Error getting dynamic gradient: {str(e)}")
            return {
                'start': '#9E9E9E',
                'end': '#BDBDBD',
                'direction': 'to right'
            }
    
    def get_accessibility_colors(self, base_scheme: Dict[str, str]) -> Dict[str, str]:
        """Get accessibility-compliant colors"""
        try:
            # Ensure sufficient contrast for accessibility
            accessibility_scheme = base_scheme.copy()
            
            # High contrast alternatives
            accessibility_scheme['high_contrast_text'] = '#000000'
            accessibility_scheme['high_contrast_background'] = '#FFFFFF'
            
            # Focus indicators
            accessibility_scheme['focus_color'] = '#FF6F00'
            accessibility_scheme['focus_outline'] = '2px solid #FF6F00'
            
            return accessibility_scheme
            
        except Exception as e:
            logging.error(f"Error getting accessibility colors: {str(e)}")
            return base_scheme
    
    def generate_theme_css(self, color_scheme: Dict[str, Any]) -> str:
        """Generate CSS for the color theme"""
        try:
            colors = color_scheme['colors']
            scheme_name = color_scheme['scheme_name']
            
            css = f"""
            .theme-{scheme_name} {{
                --primary-color: {colors['primary']};
                --secondary-color: {colors['secondary']};
                --background-color: {colors['background']};
                --text-color: {colors['text']};
                --border-color: {colors['border']};
                --opacity: {colors.get('opacity', '1.0')};
            }}
            
            .news-card.theme-{scheme_name} {{
                background-color: var(--background-color);
                color: var(--text-color);
                border-left: 4px solid var(--primary-color);
                opacity: var(--opacity);
            }}
            
            .news-card.theme-{scheme_name}:hover {{
                background-color: var(--secondary-color);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            
            .category-badge.theme-{scheme_name} {{
                background-color: var(--primary-color);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
            }}
            
            .sentiment-indicator.theme-{scheme_name} {{
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 0.5rem;
            }}
            """
            
            return css
            
        except Exception as e:
            logging.error(f"Error generating theme CSS: {str(e)}")
            return ""
    
    def get_color_meaning(self, color_scheme_name: str) -> Dict[str, str]:
        """Get the psychological meaning of a color scheme"""
        try:
            scheme = self.color_schemes.get(color_scheme_name, {})
            
            return {
                'scheme_name': color_scheme_name,
                'psychology': scheme.get('psychology', ''),
                'usage': self._get_usage_recommendations(color_scheme_name),
                'emotions': self._get_emotional_impact(color_scheme_name)
            }
            
        except Exception as e:
            logging.error(f"Error getting color meaning: {str(e)}")
            return {}
    
    def _get_usage_recommendations(self, scheme_name: str) -> str:
        """Get usage recommendations for a color scheme"""
        recommendations = {
            'breaking_urgent': 'Use for breaking news, urgent alerts, and time-sensitive information',
            'politics_conflict': 'Use for political news, debates, and controversial topics',
            'business_economy': 'Use for business news, financial reports, and economic updates',
            'technology_innovation': 'Use for tech news, innovations, and scientific breakthroughs',
            'sports_entertainment': 'Use for sports, entertainment, and lifestyle content',
            'health_medical': 'Use for health news, medical research, and wellness content',
            'environment_climate': 'Use for environmental news, climate change, and sustainability',
            'positive_uplifting': 'Use for positive news, success stories, and uplifting content',
            'neutral_general': 'Use for general news, neutral reporting, and balanced content'
        }
        
        return recommendations.get(scheme_name, 'General purpose color scheme')
    
    def _get_emotional_impact(self, scheme_name: str) -> str:
        """Get emotional impact of a color scheme"""
        impacts = {
            'breaking_urgent': 'Creates urgency, demands attention, conveys importance',
            'politics_conflict': 'Suggests debate, tension, and significant issues',
            'business_economy': 'Conveys trust, stability, and professionalism',
            'technology_innovation': 'Suggests growth, progress, and innovation',
            'sports_entertainment': 'Creates excitement, energy, and joy',
            'health_medical': 'Conveys care, healing, and medical authority',
            'environment_climate': 'Suggests nature, balance, and environmental consciousness',
            'positive_uplifting': 'Creates optimism, hope, and positive feelings',
            'neutral_general': 'Maintains objectivity and balanced perspective'
        }
        
        return impacts.get(scheme_name, 'Neutral emotional impact')
    
    def analyze_color_effectiveness(self, color_scheme: Dict[str, Any], 
                                  engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the effectiveness of a color scheme"""
        try:
            # This would analyze user engagement with different color schemes
            effectiveness = {
                'scheme_name': color_scheme['scheme_name'],
                'engagement_score': engagement_data.get('clicks', 0) / max(engagement_data.get('views', 1), 1),
                'time_spent': engagement_data.get('time_spent', 0),
                'user_feedback': engagement_data.get('feedback', 'neutral'),
                'conversion_rate': engagement_data.get('conversions', 0) / max(engagement_data.get('clicks', 1), 1),
                'accessibility_score': self._calculate_accessibility_score(color_scheme)
            }
            
            return effectiveness
            
        except Exception as e:
            logging.error(f"Error analyzing color effectiveness: {str(e)}")
            return {}
    
    def _calculate_accessibility_score(self, color_scheme: Dict[str, Any]) -> float:
        """Calculate accessibility score for a color scheme"""
        try:
            # Simplified accessibility scoring
            # In production, this would use proper contrast ratio calculations
            colors = color_scheme['colors']
            
            # Basic checks
            has_sufficient_contrast = True  # Would calculate actual contrast ratios
            has_focus_indicators = 'focus_color' in colors
            has_high_contrast_option = 'high_contrast_text' in colors
            
            score = 0.0
            if has_sufficient_contrast:
                score += 0.5
            if has_focus_indicators:
                score += 0.3
            if has_high_contrast_option:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logging.error(f"Error calculating accessibility score: {str(e)}")
            return 0.5
