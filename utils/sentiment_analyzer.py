import re
import logging
from typing import Dict, Any, List, Tuple
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Enhanced sentiment keywords
        self.positive_keywords = {
            'strong': ['excellent', 'outstanding', 'remarkable', 'exceptional', 'brilliant', 'magnificent'],
            'moderate': ['good', 'positive', 'great', 'wonderful', 'nice', 'pleased', 'happy'],
            'mild': ['okay', 'fine', 'decent', 'acceptable', 'satisfactory']
        }
        
        self.negative_keywords = {
            'strong': ['terrible', 'awful', 'horrible', 'devastating', 'catastrophic', 'disastrous'],
            'moderate': ['bad', 'negative', 'poor', 'disappointing', 'concerning', 'troubling'],
            'mild': ['mediocre', 'lacking', 'insufficient', 'questionable']
        }
        
        # News-specific sentiment indicators
        self.news_sentiment_indicators = {
            'crisis': -0.8,
            'emergency': -0.7,
            'breakthrough': 0.8,
            'success': 0.7,
            'failure': -0.6,
            'victory': 0.6,
            'defeat': -0.5,
            'improvement': 0.5,
            'decline': -0.4,
            'growth': 0.4
        }
    
    def analyze_comprehensive_sentiment(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis"""
        try:
            # Multiple sentiment analysis approaches
            textblob_result = self._analyze_with_textblob(text)
            vader_result = self._analyze_with_vader(text)
            keyword_result = self._analyze_with_keywords(text)
            news_result = self._analyze_news_sentiment(text)
            
            # Combine results
            combined_result = self._combine_sentiment_results([
                textblob_result,
                vader_result,
                keyword_result,
                news_result
            ])
            
            # Add confidence and additional metrics
            combined_result['confidence'] = self._calculate_confidence(combined_result)
            combined_result['emotional_intensity'] = self._calculate_emotional_intensity(text)
            combined_result['subjectivity'] = textblob_result.get('subjectivity', 0.5)
            
            return combined_result
            
        except Exception as e:
            logging.error(f"Error in comprehensive sentiment analysis: {str(e)}")
            return {
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'emotional_intensity': 0.0,
                'subjectivity': 0.5
            }
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Convert polarity to label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': polarity,
                'label': label,
                'subjectivity': subjectivity,
                'method': 'textblob'
            }
            
        except Exception as e:
            logging.error(f"Error with TextBlob analysis: {str(e)}")
            return {'score': 0.0, 'label': 'neutral', 'subjectivity': 0.5, 'method': 'textblob'}
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            # Convert compound score to label
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': compound,
                'label': label,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'method': 'vader'
            }
            
        except Exception as e:
            logging.error(f"Error with VADER analysis: {str(e)}")
            return {'score': 0.0, 'label': 'neutral', 'method': 'vader'}
    
    def _analyze_with_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using keyword matching"""
        try:
            text_lower = text.lower()
            
            positive_score = 0.0
            negative_score = 0.0
            
            # Check positive keywords
            for strength, keywords in self.positive_keywords.items():
                for keyword in keywords:
                    count = text_lower.count(keyword)
                    if count > 0:
                        if strength == 'strong':
                            positive_score += count * 0.8
                        elif strength == 'moderate':
                            positive_score += count * 0.5
                        else:
                            positive_score += count * 0.3
            
            # Check negative keywords
            for strength, keywords in self.negative_keywords.items():
                for keyword in keywords:
                    count = text_lower.count(keyword)
                    if count > 0:
                        if strength == 'strong':
                            negative_score += count * 0.8
                        elif strength == 'moderate':
                            negative_score += count * 0.5
                        else:
                            negative_score += count * 0.3
            
            # Calculate final score
            net_score = positive_score - negative_score
            
            # Normalize score
            if net_score > 0:
                normalized_score = min(1.0, net_score / 5.0)
                label = 'positive'
            elif net_score < 0:
                normalized_score = max(-1.0, net_score / 5.0)
                label = 'negative'
            else:
                normalized_score = 0.0
                label = 'neutral'
            
            return {
                'score': normalized_score,
                'label': label,
                'positive_keywords': positive_score,
                'negative_keywords': negative_score,
                'method': 'keywords'
            }
            
        except Exception as e:
            logging.error(f"Error with keyword analysis: {str(e)}")
            return {'score': 0.0, 'label': 'neutral', 'method': 'keywords'}
    
    def _analyze_news_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment specific to news content"""
        try:
            text_lower = text.lower()
            
            total_score = 0.0
            indicator_count = 0
            
            for indicator, score in self.news_sentiment_indicators.items():
                if indicator in text_lower:
                    total_score += score
                    indicator_count += 1
            
            if indicator_count > 0:
                average_score = total_score / indicator_count
                
                if average_score > 0.1:
                    label = 'positive'
                elif average_score < -0.1:
                    label = 'negative'
                else:
                    label = 'neutral'
            else:
                average_score = 0.0
                label = 'neutral'
            
            return {
                'score': average_score,
                'label': label,
                'indicators_found': indicator_count,
                'method': 'news_specific'
            }
            
        except Exception as e:
            logging.error(f"Error with news sentiment analysis: {str(e)}")
            return {'score': 0.0, 'label': 'neutral', 'method': 'news_specific'}
    
    def _combine_sentiment_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple sentiment analysis results"""
        try:
            # Weight different methods
            weights = {
                'textblob': 0.3,
                'vader': 0.4,
                'keywords': 0.2,
                'news_specific': 0.1
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            for result in results:
                method = result.get('method', 'unknown')
                score = result.get('score', 0.0)
                weight = weights.get(method, 0.1)
                
                total_score += score * weight
                total_weight += weight
            
            # Calculate weighted average
            if total_weight > 0:
                final_score = total_score / total_weight
            else:
                final_score = 0.0
            
            # Determine final label
            if final_score > 0.1:
                final_label = 'positive'
            elif final_score < -0.1:
                final_label = 'negative'
            else:
                final_label = 'neutral'
            
            return {
                'score': final_score,
                'label': final_label,
                'individual_results': results,
                'method': 'combined'
            }
            
        except Exception as e:
            logging.error(f"Error combining sentiment results: {str(e)}")
            return {'score': 0.0, 'label': 'neutral', 'method': 'combined'}
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence in sentiment analysis"""
        try:
            score = abs(result.get('score', 0.0))
            
            # Higher absolute score = higher confidence
            confidence = min(1.0, score * 2.0)
            
            # Adjust based on consistency across methods
            individual_results = result.get('individual_results', [])
            if len(individual_results) > 1:
                labels = [r.get('label', 'neutral') for r in individual_results]
                label_consistency = labels.count(result['label']) / len(labels)
                confidence *= label_consistency
            
            return confidence
            
        except Exception as e:
            logging.error(f"Error calculating confidence: {str(e)}")
            return 0.5
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity of text"""
        try:
            # Count emotional indicators
            emotional_words = [
                'amazing', 'terrible', 'incredible', 'awful', 'fantastic', 'horrible',
                'outstanding', 'devastating', 'brilliant', 'disastrous', 'wonderful',
                'catastrophic', 'excellent', 'tragic', 'marvelous', 'dreadful'
            ]
            
            text_lower = text.lower()
            emotion_count = 0
            
            for word in emotional_words:
                emotion_count += text_lower.count(word)
            
            # Calculate intensity based on emotional word density
            word_count = len(text.split())
            if word_count > 0:
                intensity = min(1.0, emotion_count / word_count * 10)
            else:
                intensity = 0.0
            
            return intensity
            
        except Exception as e:
            logging.error(f"Error calculating emotional intensity: {str(e)}")
            return 0.0
    
    def analyze_sentiment_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze sentiment trends across multiple texts"""
        try:
            results = []
            
            for text in texts:
                result = self.analyze_comprehensive_sentiment(text)
                results.append(result)
            
            if not results:
                return {}
            
            # Calculate trends
            scores = [r['score'] for r in results]
            labels = [r['label'] for r in results]
            
            trends = {
                'average_score': np.mean(scores),
                'score_trend': np.polyfit(range(len(scores)), scores, 1)[0],  # Linear trend
                'sentiment_distribution': {
                    'positive': labels.count('positive'),
                    'negative': labels.count('negative'),
                    'neutral': labels.count('neutral')
                },
                'volatility': np.std(scores),
                'total_articles': len(texts)
            }
            
            return trends
            
        except Exception as e:
            logging.error(f"Error analyzing sentiment trends: {str(e)}")
            return {}
    
    def get_sentiment_recommendations(self, sentiment_data: Dict[str, Any]) -> List[str]:
        """Get recommendations based on sentiment analysis"""
        try:
            recommendations = []
            
            score = sentiment_data.get('score', 0.0)
            label = sentiment_data.get('label', 'neutral')
            confidence = sentiment_data.get('confidence', 0.0)
            
            # Recommendations based on sentiment
            if label == 'negative' and confidence > 0.7:
                recommendations.append("Consider content warning for sensitive readers")
                recommendations.append("Use supportive color scheme")
                recommendations.append("Include constructive context or solutions")
            
            elif label == 'positive' and confidence > 0.7:
                recommendations.append("Highlight as uplifting content")
                recommendations.append("Use bright, energetic color scheme")
                recommendations.append("Consider featuring prominently")
            
            elif confidence < 0.3:
                recommendations.append("Consider human review for sentiment clarity")
                recommendations.append("Use neutral presentation")
            
            # Recommendations based on emotional intensity
            intensity = sentiment_data.get('emotional_intensity', 0.0)
            if intensity > 0.7:
                recommendations.append("High emotional content - consider content warning")
                recommendations.append("Use careful placement in news feed")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error getting sentiment recommendations: {str(e)}")
            return []
    
    def export_sentiment_analysis(self, text: str, detailed: bool = False) -> Dict[str, Any]:
        """Export detailed sentiment analysis for external use"""
        try:
            result = self.analyze_comprehensive_sentiment(text)
            
            export_data = {
                'text_preview': text[:100] + "..." if len(text) > 100 else text,
                'sentiment_score': result['score'],
                'sentiment_label': result['label'],
                'confidence': result['confidence'],
                'emotional_intensity': result['emotional_intensity'],
                'analysis_timestamp': logging.datetime.now().isoformat()
            }
            
            if detailed:
                export_data.update({
                    'subjectivity': result.get('subjectivity', 0.5),
                    'individual_methods': result.get('individual_results', []),
                    'recommendations': self.get_sentiment_recommendations(result)
                })
            
            return export_data
            
        except Exception as e:
            logging.error(f"Error exporting sentiment analysis: {str(e)}")
            return {}
