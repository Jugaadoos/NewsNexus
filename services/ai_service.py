import json
import os
import re
import openai
from typing import Dict, List, Any
import logging
from datetime import datetime

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.offline_mode = not bool(self.api_key)
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None

        if self.offline_mode:
            logging.warning(
                "OPENAI_API_KEY not set. AIService is running in offline fallback mode."
            )
        
    def summarize_article(self, content: str, max_words: int = 100) -> str:
        """Generate AI summary of article content"""
        try:
            if self.offline_mode:
                return self._offline_summary(content, max_words=max_words)

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional news summarizer. Create a concise summary of the following news article in under {max_words} words. Focus on the key facts, main points, and important details."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Article summarization failed: {str(e)}")
            return "Summary unavailable"
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text content"""
        try:
            if self.offline_mode:
                return self._offline_sentiment(text)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and provide a JSON response with 'label' (positive/negative/neutral), 'confidence' (0-1), and 'score' (-1 to 1)."
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
                "label": result.get("label", "neutral"),
                "confidence": float(result.get("confidence", 0.5)),
                "score": float(result.get("score", 0.0))
            }
            
        except Exception as e:
            logging.error(f"Sentiment analysis failed: {str(e)}")
            return {"label": "neutral", "confidence": 0.0, "score": 0.0}
    
    def categorize_news(self, title: str, content: str) -> str:
        """Categorize news article into appropriate category"""
        try:
            if self.offline_mode:
                return self._offline_category(title, content)

            categories = [
                "World", "Politics", "Business", "Technology", 
                "Sports", "Entertainment", "Health", "Science"
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a news categorization expert. Categorize the following article into one of these categories: {', '.join(categories)}. Respond with only the category name."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title}\n\nContent: {content[:500]}..."
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip()
            return category if category in categories else "World"
            
        except Exception as e:
            logging.error(f"News categorization failed: {str(e)}")
            return "World"
    
    def generate_theme(self, prompt: str) -> Dict[str, Any]:
        """Generate custom theme based on user prompt"""
        try:
            if self.offline_mode:
                return self._get_default_theme()

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI/UX designer. Create a theme configuration based on the user's prompt. Return JSON with 'colors' (primary, secondary, background, text), 'fonts', and 'spacing' properties."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Theme generation failed: {str(e)}")
            return self._get_default_theme()
    
    def check_originality(self, content: str, existing_articles: List[str]) -> Dict[str, Any]:
        """Check content originality against existing articles"""
        try:
            if self.offline_mode:
                return {"is_original": True, "similarity_score": 0.0, "similar_articles": []}

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a plagiarism detection expert. Compare the given content with existing articles and determine originality. Return JSON with 'is_original' (boolean), 'similarity_score' (0-1), and 'similar_articles' (list of indices)."
                    },
                    {
                        "role": "user",
                        "content": f"Content to check: {content}\n\nExisting articles: {existing_articles[:5]}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Originality check failed: {str(e)}")
            return {"is_original": True, "similarity_score": 0.0, "similar_articles": []}
    
    def generate_opinion(self, article_content: str, perspective: str) -> str:
        """Generate editorial opinion on article"""
        try:
            if self.offline_mode:
                return "Opinion unavailable in offline mode"

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an editorial writer with a {perspective} perspective. Write a balanced opinion piece about the given article, presenting thoughtful analysis and commentary."
                    },
                    {
                        "role": "user",
                        "content": article_content
                    }
                ],
                max_tokens=500,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Opinion generation failed: {str(e)}")
            return "Opinion unavailable"
    
    def create_embeddings(self, text: str) -> List[float]:
        """Create embeddings for text similarity"""
        try:
            if self.offline_mode:
                return []

            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logging.error(f"Embedding creation failed: {str(e)}")
            return []
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Get default theme configuration"""
        return {
            "colors": {
                "primary": "#1A73E8",
                "secondary": "#34A853",
                "background": "#F8F9FA",
                "text": "#202124"
            },
            "fonts": {
                "primary": "Inter, sans-serif",
                "secondary": "Roboto, sans-serif"
            },
            "spacing": {
                "base": "16px",
                "large": "24px",
                "small": "8px"
            }
        }

    def _offline_summary(self, content: str, max_words: int = 100) -> str:
        words = (content or "").split()
        if not words:
            return "Summary unavailable"
        return " ".join(words[:max_words])

    def _offline_sentiment(self, text: str) -> Dict[str, Any]:
        lowered = (text or "").lower()
        positive_words = {"gain", "growth", "rise", "bull", "profit", "surge", "improve"}
        negative_words = {"loss", "drop", "fall", "bear", "decline", "risk", "crash"}

        tokens = re.findall(r"\b[a-z]+\b", lowered)
        pos = sum(1 for t in tokens if t in positive_words)
        neg = sum(1 for t in tokens if t in negative_words)

        score = 0.0
        if pos or neg:
            score = (pos - neg) / max(pos + neg, 1)

        if score > 0.15:
            label = "positive"
        elif score < -0.15:
            label = "negative"
        else:
            label = "neutral"

        return {"label": label, "confidence": min(1.0, abs(score)), "score": score}

    def _offline_category(self, title: str, content: str) -> str:
        text = f"{title} {content}".lower()
        mapping = {
            "Politics": ["election", "government", "senate", "president", "minister"],
            "Business": ["market", "stock", "economy", "company", "trade"],
            "Technology": ["tech", "ai", "software", "chip", "startup"],
            "Sports": ["match", "league", "tournament", "player", "coach"],
            "Entertainment": ["movie", "music", "celebrity", "show", "festival"],
            "Health": ["health", "disease", "hospital", "medicine", "vaccine"],
            "Science": ["research", "study", "scientist", "space", "climate"],
        }
        for category, keywords in mapping.items():
            if any(keyword in text for keyword in keywords):
                return category
        return "World"
