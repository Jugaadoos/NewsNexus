import json
import os
from typing import Dict, List, Optional
from openai import OpenAI
import re
from datetime import datetime
from config import OPENAI_API_KEY

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class AIServices:
    def __init__(self):
        self.openai_client = client
    
    def summarize_article(self, content: str, max_words: int = 100) -> str:
        """Generate AI summary of article content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional news summarizer. Create a concise summary of the following news article in {max_words} words or less. Focus on the key facts, main events, and important details. Write in a clear, objective journalistic style."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return content[:200] + "..." if len(content) > 200 else content
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze the sentiment of the provided text and provide a rating from 1 to 5 (1=very negative, 2=negative, 3=neutral, 4=positive, 5=very positive) and a confidence score between 0 and 1. Also categorize the news type for color psychology purposes. Respond with JSON in this format: {'rating': number, 'confidence': number, 'news_type': 'breaking|politics|business|technology|sports|entertainment|health|science|positive|neutral'}"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "rating": max(1, min(5, round(result.get("rating", 3)))),
                "confidence": max(0, min(1, result.get("confidence", 0.5))),
                "news_type": result.get("news_type", "neutral")
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"rating": 3, "confidence": 0.5, "news_type": "neutral"}
    
    def categorize_content(self, text: str) -> str:
        """Categorize content into news categories"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news categorization expert. Categorize the following text into one of these categories: world, politics, business, technology, sports, entertainment, health, science. Respond with only the category name in lowercase."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip().lower()
            valid_categories = ['world', 'politics', 'business', 'technology', 'sports', 'entertainment', 'health', 'science']
            
            return category if category in valid_categories else 'world'
            
        except Exception as e:
            print(f"Error categorizing content: {e}")
            return 'world'
    
    def generate_theme(self, prompt: str) -> Dict:
        """Generate custom theme based on user prompt"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI/UX designer specializing in news applications. Generate a complete theme configuration based on the user's prompt. Include colors, typography, spacing, and styling preferences. Respond with JSON in this format: {'primary_color': '#hex', 'secondary_color': '#hex', 'background_color': '#hex', 'text_color': '#hex', 'accent_color': '#hex', 'card_background': '#hex', 'border_color': '#hex', 'theme_name': 'string', 'description': 'string'}"
                    },
                    {
                        "role": "user",
                        "content": f"Create a news application theme based on: {prompt}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            theme_data = json.loads(response.choices[0].message.content)
            return theme_data
            
        except Exception as e:
            print(f"Error generating theme: {e}")
            return {
                "primary_color": "#1A73E8",
                "secondary_color": "#34A853",
                "background_color": "#F8F9FA",
                "text_color": "#202124",
                "accent_color": "#EA4335",
                "card_background": "#FFFFFF",
                "border_color": "#E0E0E0",
                "theme_name": "Default",
                "description": "Clean and modern news theme"
            }
    
    def generate_article_embedding(self, text: str) -> List[float]:
        """Generate embedding for article text"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def find_similar_articles(self, query_embedding: List[float], article_embeddings: List[Dict]) -> List[Dict]:
        """Find similar articles based on embeddings"""
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            similarities = []
            query_vec = np.array(query_embedding).reshape(1, -1)
            
            for article_data in article_embeddings:
                article_vec = np.array(article_data['embedding']).reshape(1, -1)
                similarity = cosine_similarity(query_vec, article_vec)[0][0]
                similarities.append({
                    'article': article_data['article'],
                    'similarity': similarity
                })
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:10]  # Return top 10 similar articles
            
        except Exception as e:
            print(f"Error finding similar articles: {e}")
            return []
    
    def generate_opinion(self, article_content: str, perspective: str = "balanced") -> str:
        """Generate AI opinion on article content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert journalist providing {perspective} analysis. Write a thoughtful opinion piece about the following news article. Focus on implications, context, and different perspectives. Keep it under 200 words."
                    },
                    {
                        "role": "user",
                        "content": article_content
                    }
                ],
                max_tokens=300,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating opinion: {e}")
            return "Unable to generate opinion at this time."
    
    def extract_key_entities(self, text: str) -> List[Dict]:
        """Extract key entities from text"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract key entities from the text including people, organizations, locations, and events. Respond with JSON in this format: {'people': ['name1', 'name2'], 'organizations': ['org1', 'org2'], 'locations': ['loc1', 'loc2'], 'events': ['event1', 'event2']}"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            entities = json.loads(response.choices[0].message.content)
            return entities
            
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"people": [], "organizations": [], "locations": [], "events": []}
    
    def generate_headline_alternatives(self, content: str) -> List[str]:
        """Generate alternative headlines for content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate 5 alternative headlines for the following news content. Make them engaging, accurate, and appropriate for different audiences. Respond with JSON in this format: {'headlines': ['headline1', 'headline2', 'headline3', 'headline4', 'headline5']}"
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('headlines', [])
            
        except Exception as e:
            print(f"Error generating headlines: {e}")
            return []

# Initialize AI services
ai_services = AIServices()

# Export functions for easy import
def summarize_article(content: str, max_words: int = 100) -> str:
    return ai_services.summarize_article(content, max_words)

def analyze_sentiment(text: str) -> Dict:
    return ai_services.analyze_sentiment(text)

def categorize_content(text: str) -> str:
    return ai_services.categorize_content(text)

def generate_theme(prompt: str) -> Dict:
    return ai_services.generate_theme(prompt)

def generate_article_embedding(text: str) -> List[float]:
    return ai_services.generate_article_embedding(text)

def find_similar_articles(query_embedding: List[float], article_embeddings: List[Dict]) -> List[Dict]:
    return ai_services.find_similar_articles(query_embedding, article_embeddings)

def generate_opinion(article_content: str, perspective: str = "balanced") -> str:
    return ai_services.generate_opinion(article_content, perspective)

def extract_key_entities(text: str) -> List[Dict]:
    return ai_services.extract_key_entities(text)

def generate_headline_alternatives(content: str) -> List[str]:
    return ai_services.generate_headline_alternatives(content)
