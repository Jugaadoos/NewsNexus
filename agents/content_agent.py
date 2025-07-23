import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.ai_service import AIService
from services.news_service import NewsService
from database.connection import get_db_connection
from database.models import Article, User, AIAgent
import json

class ContentAgent:
    def __init__(self, agent_id: str = "content_agent"):
        self.agent_id = agent_id
        self.ai_service = AIService()
        self.news_service = NewsService()
        self.status = "idle"
        self.last_run = None
        
    async def start(self):
        """Start the content agent"""
        logging.info(f"Starting Content Agent {self.agent_id}")
        self.status = "running"
        
        try:
            while self.status == "running":
                await self.process_content_tasks()
                await asyncio.sleep(1800)  # Run every 30 minutes
                
        except Exception as e:
            logging.error(f"Error in Content Agent: {str(e)}")
            self.status = "error"
    
    async def process_content_tasks(self):
        """Process various content-related tasks"""
        try:
            logging.info("Processing content tasks")
            
            # Update article summaries
            await self.update_article_summaries()
            
            # Generate editorial opinions
            await self.generate_editorial_opinions()
            
            # Update content recommendations
            await self.update_content_recommendations()
            
            # Analyze content trends
            await self.analyze_content_trends()
            
            self.last_run = datetime.now()
            self._update_agent_status()
            
        except Exception as e:
            logging.error(f"Error processing content tasks: {str(e)}")
    
    async def update_article_summaries(self):
        """Update or create missing article summaries"""
        try:
            db = get_db_connection()
            
            # Get articles without summaries or with old summaries
            articles_needing_summaries = db.query(Article).filter(
                Article.summary == None,
                Article.created_at >= datetime.now() - timedelta(days=1)
            ).limit(10).all()
            
            for article in articles_needing_summaries:
                if article.content:
                    summary = self.ai_service.summarize_article(article.content, max_words=100)
                    article.summary = summary
                    
                    logging.info(f"Updated summary for article: {article.title}")
            
            db.commit()
            
        except Exception as e:
            logging.error(f"Error updating article summaries: {str(e)}")
            db.rollback()
    
    async def generate_editorial_opinions(self):
        """Generate editorial opinions for trending articles"""
        try:
            db = get_db_connection()
            
            # Get trending articles from the last 24 hours
            trending_articles = db.query(Article).filter(
                Article.created_at >= datetime.now() - timedelta(days=1),
                Article.is_approved == True,
                Article.category.in_(['Politics', 'World', 'Business'])
            ).limit(5).all()
            
            for article in trending_articles:
                await self.create_editorial_opinion(article)
            
        except Exception as e:
            logging.error(f"Error generating editorial opinions: {str(e)}")
    
    async def create_editorial_opinion(self, article: Article):
        """Create editorial opinion for an article"""
        try:
            # Generate balanced editorial opinion
            opinion = self.ai_service.generate_opinion(article.content, "balanced")
            
            # Store the opinion (you might want to create an Opinion model)
            # For now, we'll store it in the article's metadata
            if not hasattr(article, 'metadata'):
                article.metadata = {}
            
            article.metadata = article.metadata or {}
            article.metadata['editorial_opinion'] = {
                'content': opinion,
                'generated_at': datetime.now().isoformat(),
                'perspective': 'balanced'
            }
            
            db = get_db_connection()
            db.commit()
            
            logging.info(f"Generated editorial opinion for: {article.title}")
            
        except Exception as e:
            logging.error(f"Error creating editorial opinion: {str(e)}")
    
    async def update_content_recommendations(self):
        """Update content recommendations for users"""
        try:
            db = get_db_connection()
            
            # Get active users
            active_users = db.query(User).filter(
                User.is_active == True
            ).limit(100).all()
            
            for user in active_users:
                await self.generate_user_recommendations(user)
            
        except Exception as e:
            logging.error(f"Error updating content recommendations: {str(e)}")
    
    async def generate_user_recommendations(self, user: User):
        """Generate personalized content recommendations for a user"""
        try:
            db = get_db_connection()
            
            # Get user preferences
            preferences = user.preferences or {}
            
            # Get user's reading history (simplified)
            # In production, you'd have a proper UserActivity model
            
            # Get articles matching user preferences
            query = db.query(Article).filter(
                Article.is_approved == True,
                Article.created_at >= datetime.now() - timedelta(days=7)
            )
            
            # Filter by preferred categories
            preferred_categories = preferences.get('categories', [])
            if preferred_categories:
                query = query.filter(Article.category.in_(preferred_categories))
            
            recommended_articles = query.limit(10).all()
            
            # Store recommendations
            user.preferences = user.preferences or {}
            user.preferences['recommendations'] = [
                {
                    'article_id': article.id,
                    'title': article.title,
                    'category': article.category,
                    'generated_at': datetime.now().isoformat()
                }
                for article in recommended_articles
            ]
            
            db.commit()
            
        except Exception as e:
            logging.error(f"Error generating user recommendations: {str(e)}")
    
    async def analyze_content_trends(self):
        """Analyze content trends and patterns"""
        try:
            db = get_db_connection()
            
            # Get recent articles
            recent_articles = db.query(Article).filter(
                Article.created_at >= datetime.now() - timedelta(days=7),
                Article.is_approved == True
            ).all()
            
            # Analyze trends
            trends = await self.extract_trends(recent_articles)
            
            # Store trends analysis
            self._store_trends_analysis(trends)
            
        except Exception as e:
            logging.error(f"Error analyzing content trends: {str(e)}")
    
    async def extract_trends(self, articles: List[Article]) -> Dict[str, Any]:
        """Extract trends from articles"""
        try:
            # Category distribution
            category_counts = {}
            sentiment_distribution = {}
            keyword_frequency = {}
            
            for article in articles:
                # Count categories
                category = article.category
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Count sentiment
                sentiment = article.sentiment_label
                sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
                
                # Extract keywords (simplified)
                keywords = await self.extract_keywords(article.content)
                for keyword in keywords:
                    keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
            
            return {
                'category_distribution': category_counts,
                'sentiment_distribution': sentiment_distribution,
                'trending_keywords': dict(sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:20]),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error extracting trends: {str(e)}")
            return {}
    
    async def extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a keyword extraction expert. Extract the most important keywords and phrases from the given text. Return a JSON array of keywords."
                    },
                    {
                        "role": "user",
                        "content": content[:1000]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            keyword_data = json.loads(result)
            
            return keyword_data.get('keywords', [])
            
        except Exception as e:
            logging.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def _store_trends_analysis(self, trends: Dict[str, Any]):
        """Store trends analysis"""
        try:
            db = get_db_connection()
            
            # Store in AIAgent config for now
            agent = db.query(AIAgent).filter(AIAgent.name == self.agent_id).first()
            
            if agent:
                agent.config = agent.config or {}
                agent.config['trends'] = trends
                db.commit()
            
        except Exception as e:
            logging.error(f"Error storing trends analysis: {str(e)}")
            db.rollback()
    
    async def enhance_article_metadata(self, article: Article) -> Dict[str, Any]:
        """Enhance article with additional metadata"""
        try:
            enhanced_metadata = {}
            
            # Extract entities
            entities = await self.extract_entities(article.content)
            enhanced_metadata['entities'] = entities
            
            # Generate tags
            tags = await self.generate_tags(article.content)
            enhanced_metadata['tags'] = tags
            
            # Estimate reading time
            reading_time = self.estimate_reading_time(article.content)
            enhanced_metadata['reading_time'] = reading_time
            
            # Content complexity score
            complexity = await self.analyze_complexity(article.content)
            enhanced_metadata['complexity'] = complexity
            
            return enhanced_metadata
            
        except Exception as e:
            logging.error(f"Error enhancing article metadata: {str(e)}")
            return {}
    
    async def extract_entities(self, content: str) -> List[Dict[str, str]]:
        """Extract named entities from content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a named entity recognition expert. Extract people, organizations, locations, and other important entities from the text. Return JSON with 'entities' array containing objects with 'text' and 'type' fields."
                    },
                    {
                        "role": "user",
                        "content": content[:1500]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            entity_data = json.loads(result)
            
            return entity_data.get('entities', [])
            
        except Exception as e:
            logging.error(f"Error extracting entities: {str(e)}")
            return []
    
    async def generate_tags(self, content: str) -> List[str]:
        """Generate tags for content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content tagging expert. Generate relevant tags for the given content. Return JSON with 'tags' array of strings."
                    },
                    {
                        "role": "user",
                        "content": content[:1000]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            tag_data = json.loads(result)
            
            return tag_data.get('tags', [])
            
        except Exception as e:
            logging.error(f"Error generating tags: {str(e)}")
            return []
    
    def estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes"""
        try:
            words = len(content.split())
            # Average reading speed: 200 words per minute
            reading_time = max(1, words // 200)
            return reading_time
            
        except Exception as e:
            logging.error(f"Error estimating reading time: {str(e)}")
            return 1
    
    async def analyze_complexity(self, content: str) -> float:
        """Analyze content complexity"""
        try:
            # Simple complexity analysis based on sentence length and vocabulary
            sentences = content.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Normalize to 0-1 scale
            complexity = min(1.0, avg_sentence_length / 30.0)
            
            return complexity
            
        except Exception as e:
            logging.error(f"Error analyzing complexity: {str(e)}")
            return 0.5
    
    def stop(self):
        """Stop the content agent"""
        logging.info(f"Stopping Content Agent {self.agent_id}")
        self.status = "stopped"
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'type': 'content_agent'
        }
    
    def _update_agent_status(self):
        """Update agent status in database"""
        try:
            db = get_db_connection()
            
            agent = db.query(AIAgent).filter(AIAgent.name == self.agent_id).first()
            
            if not agent:
                agent = AIAgent(
                    name=self.agent_id,
                    type='content_processor',
                    config={},
                    status=self.status
                )
                db.add(agent)
            else:
                agent.status = self.status
                agent.last_run = self.last_run
            
            db.commit()
            
        except Exception as e:
            logging.error(f"Error updating agent status: {str(e)}")
            db.rollback()
