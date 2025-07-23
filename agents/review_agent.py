import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.ai_service import AIService
from services.blockchain_service import BlockchainService
from database.connection import get_db_connection
from database.models import Article, Review, User, AIAgent
from difflib import SequenceMatcher
import hashlib

class ReviewAgent:
    def __init__(self, agent_id: str = "review_agent"):
        self.agent_id = agent_id
        self.ai_service = AIService()
        self.blockchain_service = BlockchainService()
        self.status = "idle"
        self.last_run = None
        
    async def start(self):
        """Start the review agent"""
        logging.info(f"Starting Review Agent {self.agent_id}")
        self.status = "running"
        
        try:
            while self.status == "running":
                await self.process_pending_reviews()
                await asyncio.sleep(600)  # Run every 10 minutes
                
        except Exception as e:
            logging.error(f"Error in Review Agent: {str(e)}")
            self.status = "error"
    
    async def process_pending_reviews(self):
        """Process articles pending review"""
        try:
            logging.info("Processing pending reviews")
            
            db = get_db_connection()
            
            # Get articles needing review
            pending_articles = db.query(Article).filter(
                Article.is_approved == False,
                Article.created_at >= datetime.now() - timedelta(days=7)
            ).limit(20).all()
            
            for article in pending_articles:
                await self.review_article(article)
            
            self.last_run = datetime.now()
            self._update_agent_status()
            
        except Exception as e:
            logging.error(f"Error processing reviews: {str(e)}")
    
    async def review_article(self, article: Article):
        """Review individual article"""
        try:
            logging.info(f"Reviewing article: {article.title}")
            
            # Perform comprehensive review
            review_result = await self.comprehensive_review(article)
            
            # Create review record
            review = Review(
                article_id=article.id,
                reviewer_id=1,  # AI Agent reviewer
                status=review_result['status'],
                comments=review_result['comments']
            )
            
            db = get_db_connection()
            db.add(review)
            
            # Update article approval status
            if review_result['status'] == 'approved':
                article.is_approved = True
                
                # Record approval on blockchain
                blockchain_hash = self.blockchain_service.record_content_approval(
                    article.id,
                    1,  # AI Agent approver
                    review_result
                )
                
                if blockchain_hash:
                    review.blockchain_hash = blockchain_hash
                    article.blockchain_hash = blockchain_hash
            
            db.commit()
            
        except Exception as e:
            logging.error(f"Error reviewing article: {str(e)}")
            db.rollback()
    
    async def comprehensive_review(self, article: Article) -> Dict[str, Any]:
        """Perform comprehensive article review"""
        try:
            review_result = {
                'status': 'pending',
                'comments': [],
                'scores': {},
                'compliance_checks': {},
                'originality_score': 0.0
            }
            
            # Content quality check
            quality_score = await self.check_content_quality(article)
            review_result['scores']['quality'] = quality_score
            
            # Originality check
            originality_score = await self.check_originality(article)
            review_result['originality_score'] = originality_score
            
            # Compliance check
            compliance_result = await self.check_compliance(article)
            review_result['compliance_checks'] = compliance_result
            
            # Sentiment appropriateness
            sentiment_check = await self.check_sentiment_appropriateness(article)
            review_result['scores']['sentiment'] = sentiment_check
            
            # Factual accuracy check
            accuracy_score = await self.check_factual_accuracy(article)
            review_result['scores']['accuracy'] = accuracy_score
            
            # Determine overall status
            overall_score = self.calculate_overall_score(review_result['scores'])
            
            if overall_score >= 0.8 and originality_score >= 0.7 and compliance_result['passes_all']:
                review_result['status'] = 'approved'
                review_result['comments'].append("Article meets all quality and compliance standards.")
            elif overall_score >= 0.6:
                review_result['status'] = 'needs_revision'
                review_result['comments'].append("Article needs minor revisions before approval.")
            else:
                review_result['status'] = 'rejected'
                review_result['comments'].append("Article does not meet quality standards.")
            
            return review_result
            
        except Exception as e:
            logging.error(f"Error in comprehensive review: {str(e)}")
            return {
                'status': 'error',
                'comments': [f"Review failed: {str(e)}"],
                'scores': {},
                'compliance_checks': {},
                'originality_score': 0.0
            }
    
    async def check_content_quality(self, article: Article) -> float:
        """Check content quality using AI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content quality reviewer. Analyze the article for grammar, coherence, factual consistency, and journalistic standards. Return a JSON response with 'quality_score' (0-1), 'issues' (list), and 'suggestions' (list)."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {article.title}\n\nContent: {article.content[:2000]}..."
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            import json
            quality_data = json.loads(result)
            
            return quality_data.get('quality_score', 0.5)
            
        except Exception as e:
            logging.error(f"Error checking content quality: {str(e)}")
            return 0.5
    
    async def check_originality(self, article: Article) -> float:
        """Check article originality against existing content"""
        try:
            db = get_db_connection()
            
            # Get recent articles for comparison
            recent_articles = db.query(Article).filter(
                Article.category == article.category,
                Article.created_at >= datetime.now() - timedelta(days=30),
                Article.id != article.id
            ).limit(50).all()
            
            if not recent_articles:
                return 1.0
            
            # Compare content similarity
            max_similarity = 0.0
            
            for existing_article in recent_articles:
                similarity = SequenceMatcher(None, article.content, existing_article.content).ratio()
                max_similarity = max(max_similarity, similarity)
            
            # Convert similarity to originality score
            originality_score = 1.0 - max_similarity
            
            return max(0.0, originality_score)
            
        except Exception as e:
            logging.error(f"Error checking originality: {str(e)}")
            return 0.5
    
    async def check_compliance(self, article: Article) -> Dict[str, Any]:
        """Check article compliance with editorial standards"""
        try:
            compliance_checks = {
                'has_source': bool(article.source),
                'has_url': bool(article.url),
                'appropriate_length': len(article.content) >= 200,
                'has_summary': bool(article.summary),
                'category_appropriate': bool(article.category),
                'passes_all': False
            }
            
            # Check for inappropriate content
            inappropriate_content = await self.check_inappropriate_content(article)
            compliance_checks['content_appropriate'] = not inappropriate_content
            
            # Check for bias
            bias_check = await self.check_bias(article)
            compliance_checks['bias_acceptable'] = bias_check
            
            # Overall compliance
            compliance_checks['passes_all'] = all([
                compliance_checks['has_source'],
                compliance_checks['appropriate_length'],
                compliance_checks['has_summary'],
                compliance_checks['content_appropriate'],
                compliance_checks['bias_acceptable']
            ])
            
            return compliance_checks
            
        except Exception as e:
            logging.error(f"Error checking compliance: {str(e)}")
            return {'passes_all': False}
    
    async def check_inappropriate_content(self, article: Article) -> bool:
        """Check for inappropriate content"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content moderation expert. Check if the article contains inappropriate content, hate speech, misinformation, or violates journalistic ethics. Return JSON with 'inappropriate' (boolean) and 'reasons' (list)."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {article.title}\n\nContent: {article.content[:1500]}..."
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            import json
            moderation_data = json.loads(result)
            
            return moderation_data.get('inappropriate', False)
            
        except Exception as e:
            logging.error(f"Error checking inappropriate content: {str(e)}")
            return False
    
    async def check_bias(self, article: Article) -> bool:
        """Check for excessive bias in article"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a journalistic bias analyzer. Assess if the article maintains reasonable objectivity and balance. Return JSON with 'bias_score' (0-1, where 0 is no bias), 'bias_type' (political, commercial, etc.), and 'acceptable' (boolean)."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {article.title}\n\nContent: {article.content[:1500]}..."
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            import json
            bias_data = json.loads(result)
            
            return bias_data.get('acceptable', True)
            
        except Exception as e:
            logging.error(f"Error checking bias: {str(e)}")
            return True
    
    async def check_sentiment_appropriateness(self, article: Article) -> float:
        """Check if sentiment is appropriate for the content"""
        try:
            sentiment = self.ai_service.analyze_sentiment(article.content)
            
            # Check if sentiment matches content type
            if article.category in ['Health', 'Science'] and sentiment['label'] == 'positive':
                return 0.9
            elif article.category in ['Politics', 'World'] and sentiment['label'] == 'negative':
                return 0.8
            elif sentiment['label'] == 'neutral':
                return 0.9
            else:
                return 0.7
                
        except Exception as e:
            logging.error(f"Error checking sentiment appropriateness: {str(e)}")
            return 0.5
    
    async def check_factual_accuracy(self, article: Article) -> float:
        """Check factual accuracy of article"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.ai_service.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact-checking expert. Analyze the article for factual accuracy, verifiable claims, and credible sources. Return JSON with 'accuracy_score' (0-1), 'verifiable_claims' (number), and 'concerns' (list)."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {article.title}\n\nContent: {article.content[:1500]}..."
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            import json
            accuracy_data = json.loads(result)
            
            return accuracy_data.get('accuracy_score', 0.7)
            
        except Exception as e:
            logging.error(f"Error checking factual accuracy: {str(e)}")
            return 0.5
    
    def calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate overall review score"""
        if not scores:
            return 0.0
        
        # Weighted average of different scores
        weights = {
            'quality': 0.3,
            'sentiment': 0.2,
            'accuracy': 0.5
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for score_type, score_value in scores.items():
            weight = weights.get(score_type, 0.1)
            total_score += score_value * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def stop(self):
        """Stop the review agent"""
        logging.info(f"Stopping Review Agent {self.agent_id}")
        self.status = "stopped"
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'type': 'review_agent'
        }
    
    def _update_agent_status(self):
        """Update agent status in database"""
        try:
            db = get_db_connection()
            
            agent = db.query(AIAgent).filter(AIAgent.name == self.agent_id).first()
            
            if not agent:
                agent = AIAgent(
                    name=self.agent_id,
                    type='reviewer',
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
