import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agents.news_agent import NewsAgent
from agents.review_agent import ReviewAgent
from agents.content_agent import ContentAgent
from services.blockchain_service import BlockchainService
from database.connection import get_db_connection
from database.models import AIAgent

class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.blockchain_service = BlockchainService()
        self.running = False
        self.workflows = {}
        
    def initialize_agents(self):
        """Initialize all AI agents"""
        try:
            logging.info("Initializing AI agents")
            
            # Create agents
            self.agents['news'] = NewsAgent("news_agent_001")
            self.agents['review'] = ReviewAgent("review_agent_001")
            self.agents['content'] = ContentAgent("content_agent_001")
            
            logging.info("All agents initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing agents: {str(e)}")
            raise
    
    async def start_orchestration(self):
        """Start the orchestration system"""
        try:
            logging.info("Starting AI agent orchestration")
            
            if not self.agents:
                self.initialize_agents()
            
            self.running = True
            
            # Start all agents concurrently
            tasks = []
            for agent_name, agent in self.agents.items():
                task = asyncio.create_task(agent.start())
                tasks.append(task)
            
            # Start workflow monitoring
            workflow_task = asyncio.create_task(self.monitor_workflows())
            tasks.append(workflow_task)
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logging.error(f"Error in orchestration: {str(e)}")
            self.running = False
            raise
    

    async def run_single_cycle(self):
        """Run one orchestration cycle for local testing and health checks."""
        if not self.agents:
            self.initialize_agents()
        await self.execute_workflows()

    async def monitor_workflows(self):
        """Monitor and manage workflows"""
        try:
            while self.running:
                await self.execute_workflows()
                await asyncio.sleep(300)  # Check every 5 minutes
                
        except Exception as e:
            logging.error(f"Error monitoring workflows: {str(e)}")
    
    async def execute_workflows(self):
        """Execute defined workflows"""
        try:
            # News processing workflow
            await self.execute_news_workflow()
            
            # Review workflow
            await self.execute_review_workflow()
            
            # Content enhancement workflow
            await self.execute_content_workflow()
            
            # Blockchain recording workflow
            await self.execute_blockchain_workflow()
            
        except Exception as e:
            logging.error(f"Error executing workflows: {str(e)}")
    
    async def execute_news_workflow(self):
        """Execute news processing workflow"""
        try:
            workflow_id = "news_processing_001"
            
            # Get workflow status
            workflow_status = self.workflows.get(workflow_id, {
                'status': 'idle',
                'last_run': None,
                'steps': []
            })
            
            if workflow_status['status'] == 'running':
                return
            
            # Start workflow
            workflow_status['status'] = 'running'
            workflow_status['started_at'] = datetime.now()
            workflow_status['steps'] = []
            
            # Step 1: Check news agent status
            news_agent = self.agents.get('news')
            if news_agent and news_agent.status == 'running':
                workflow_status['steps'].append({
                    'step': 'news_fetching',
                    'status': 'active',
                    'timestamp': datetime.now()
                })
            
            # Step 2: Trigger targeted news collection
            if news_agent:
                # This would trigger location-specific news collection
                await self.trigger_geo_targeted_collection()
                
                workflow_status['steps'].append({
                    'step': 'geo_targeting',
                    'status': 'completed',
                    'timestamp': datetime.now()
                })
            
            # Complete workflow
            workflow_status['status'] = 'completed'
            workflow_status['completed_at'] = datetime.now()
            
            self.workflows[workflow_id] = workflow_status
            
        except Exception as e:
            logging.error(f"Error in news workflow: {str(e)}")
    
    async def execute_review_workflow(self):
        """Execute review workflow"""
        try:
            workflow_id = "review_process_001"
            
            workflow_status = self.workflows.get(workflow_id, {
                'status': 'idle',
                'last_run': None,
                'steps': []
            })
            
            if workflow_status['status'] == 'running':
                return
            
            # Start workflow
            workflow_status['status'] = 'running'
            workflow_status['started_at'] = datetime.now()
            workflow_status['steps'] = []
            
            # Step 1: AI Review
            review_agent = self.agents.get('review')
            if review_agent and review_agent.status == 'running':
                workflow_status['steps'].append({
                    'step': 'ai_review',
                    'status': 'active',
                    'timestamp': datetime.now()
                })
            
            # Step 2: Blockchain Recording
            await self.record_reviews_on_blockchain()
            
            workflow_status['steps'].append({
                'step': 'blockchain_recording',
                'status': 'completed',
                'timestamp': datetime.now()
            })
            
            # Step 3: Human Review Queue
            await self.queue_for_human_review()
            
            workflow_status['steps'].append({
                'step': 'human_review_queue',
                'status': 'completed',
                'timestamp': datetime.now()
            })
            
            # Complete workflow
            workflow_status['status'] = 'completed'
            workflow_status['completed_at'] = datetime.now()
            
            self.workflows[workflow_id] = workflow_status
            
        except Exception as e:
            logging.error(f"Error in review workflow: {str(e)}")
    
    async def execute_content_workflow(self):
        """Execute content enhancement workflow"""
        try:
            workflow_id = "content_enhancement_001"
            
            workflow_status = self.workflows.get(workflow_id, {
                'status': 'idle',
                'last_run': None,
                'steps': []
            })
            
            if workflow_status['status'] == 'running':
                return
            
            # Start workflow
            workflow_status['status'] = 'running'
            workflow_status['started_at'] = datetime.now()
            workflow_status['steps'] = []
            
            # Step 1: Content Analysis
            content_agent = self.agents.get('content')
            if content_agent and content_agent.status == 'running':
                workflow_status['steps'].append({
                    'step': 'content_analysis',
                    'status': 'active',
                    'timestamp': datetime.now()
                })
            
            # Step 2: Sentiment Analysis
            await self.enhance_sentiment_analysis()
            
            workflow_status['steps'].append({
                'step': 'sentiment_analysis',
                'status': 'completed',
                'timestamp': datetime.now()
            })
            
            # Step 3: Color Psychology Assignment
            await self.assign_color_psychology()
            
            workflow_status['steps'].append({
                'step': 'color_psychology',
                'status': 'completed',
                'timestamp': datetime.now()
            })
            
            # Complete workflow
            workflow_status['status'] = 'completed'
            workflow_status['completed_at'] = datetime.now()
            
            self.workflows[workflow_id] = workflow_status
            
        except Exception as e:
            logging.error(f"Error in content workflow: {str(e)}")
    
    async def execute_blockchain_workflow(self):
        """Execute blockchain recording workflow"""
        try:
            workflow_id = "blockchain_recording_001"
            
            # Mine pending blocks
            if len(self.blockchain_service.pending_transactions) >= 3:
                block = self.blockchain_service.mine_block()
                if block:
                    logging.info(f"Mined new block: {block['hash']}")
            
            # Verify chain integrity
            is_valid = self.blockchain_service.verify_chain()
            if not is_valid:
                logging.error("Blockchain integrity check failed")
            
        except Exception as e:
            logging.error(f"Error in blockchain workflow: {str(e)}")
    
    async def trigger_geo_targeted_collection(self):
        """Trigger geo-targeted news collection"""
        try:
            # Get active user locations
            db = get_db_connection()
            from database.models import User
            
            users = db.query(User).filter(
                User.is_active == True,
                User.location_data != None
            ).limit(100).all()
            
            # Collect unique locations
            locations = []
            for user in users:
                location_data = user.location_data
                if location_data:
                    locations.append(location_data)
            
            # Trigger targeted collection for each location
            news_agent = self.agents.get('news')
            if news_agent:
                for location in locations:
                    # This would trigger location-specific news collection
                    # Implementation depends on news agent capabilities
                    pass
            
        except Exception as e:
            logging.error(f"Error triggering geo-targeted collection: {str(e)}")
    
    async def record_reviews_on_blockchain(self):
        """Record reviews on blockchain"""
        try:
            db = get_db_connection()
            from database.models import Review
            
            # Get recent reviews not yet recorded
            unrecorded_reviews = db.query(Review).filter(
                Review.blockchain_hash == None,
                Review.created_at >= datetime.now() - timedelta(hours=1)
            ).limit(10).all()
            
            for review in unrecorded_reviews:
                review_data = {
                    'review_id': review.id,
                    'article_id': review.article_id,
                    'reviewer_id': review.reviewer_id,
                    'status': review.status,
                    'timestamp': review.created_at.isoformat()
                }
                
                transaction_id = self.blockchain_service.record_article_review(
                    review.article_id,
                    review.reviewer_id,
                    review_data
                )
                
                if transaction_id:
                    review.blockchain_hash = transaction_id
                    db.commit()
            
        except Exception as e:
            logging.error(f"Error recording reviews on blockchain: {str(e)}")
    
    async def queue_for_human_review(self):
        """Queue articles for human review"""
        try:
            db = get_db_connection()
            from database.models import Article
            
            # Get articles that need human review
            articles_needing_review = db.query(Article).filter(
                Article.is_approved == False,
                Article.created_at >= datetime.now() - timedelta(days=1)
            ).limit(20).all()
            
            # Create human review queue
            # This would integrate with a human review system
            for article in articles_needing_review:
                # Queue for human review
                # Implementation depends on human review system
                pass
            
        except Exception as e:
            logging.error(f"Error queuing for human review: {str(e)}")
    
    async def enhance_sentiment_analysis(self):
        """Enhance sentiment analysis for articles"""
        try:
            db = get_db_connection()
            from database.models import Article
            
            # Get articles needing sentiment analysis
            articles = db.query(Article).filter(
                Article.sentiment_label == None,
                Article.created_at >= datetime.now() - timedelta(hours=1)
            ).limit(10).all()
            
            content_agent = self.agents.get('content')
            if content_agent:
                for article in articles:
                    # Enhance with detailed sentiment analysis
                    pass
            
        except Exception as e:
            logging.error(f"Error enhancing sentiment analysis: {str(e)}")
    
    async def assign_color_psychology(self):
        """Assign color psychology to articles"""
        try:
            db = get_db_connection()
            from database.models import Article
            
            # Get articles needing color assignment
            articles = db.query(Article).filter(
                Article.color_scheme == None,
                Article.created_at >= datetime.now() - timedelta(hours=1)
            ).limit(10).all()
            
            # Assign colors based on sentiment and category
            for article in articles:
                # Implementation would use ColorPsychology service
                pass
            
        except Exception as e:
            logging.error(f"Error assigning color psychology: {str(e)}")
    
    def stop_orchestration(self):
        """Stop the orchestration system"""
        try:
            logging.info("Stopping AI agent orchestration")
            
            self.running = False
            
            # Stop all agents
            for agent_name, agent in self.agents.items():
                agent.stop()
            
            logging.info("Orchestration stopped successfully")
            
        except Exception as e:
            logging.error(f"Error stopping orchestration: {str(e)}")
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get orchestration status"""
        try:
            agent_statuses = {}
            for agent_name, agent in self.agents.items():
                agent_statuses[agent_name] = agent.get_status()
            
            return {
                'running': self.running,
                'agents': agent_statuses,
                'workflows': self.workflows,
                'blockchain_stats': self.blockchain_service.get_chain_stats()
            }
            
        except Exception as e:
            logging.error(f"Error getting orchestration status: {str(e)}")
            return {}
    
    def create_custom_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Create a custom workflow"""
        try:
            workflow_id = f"custom_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.workflows[workflow_id] = {
                'id': workflow_id,
                'config': workflow_config,
                'status': 'created',
                'created_at': datetime.now(),
                'steps': []
            }
            
            return workflow_id
            
        except Exception as e:
            logging.error(f"Error creating custom workflow: {str(e)}")
            return None
    
    async def execute_custom_workflow(self, workflow_id: str):
        """Execute a custom workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return
            
            workflow['status'] = 'running'
            workflow['started_at'] = datetime.now()
            
            # Execute workflow steps based on configuration
            steps = workflow['config'].get('steps', [])
            
            for step in steps:
                await self.execute_workflow_step(step, workflow)
            
            workflow['status'] = 'completed'
            workflow['completed_at'] = datetime.now()
            
        except Exception as e:
            logging.error(f"Error executing custom workflow: {str(e)}")
            if workflow_id in self.workflows:
                self.workflows[workflow_id]['status'] = 'error'
                self.workflows[workflow_id]['error'] = str(e)
    
    async def execute_workflow_step(self, step: Dict[str, Any], workflow: Dict[str, Any]):
        """Execute a workflow step"""
        try:
            step_type = step.get('type')
            
            if step_type == 'news_fetch':
                await self.execute_news_fetch_step(step)
            elif step_type == 'review':
                await self.execute_review_step(step)
            elif step_type == 'content_process':
                await self.execute_content_process_step(step)
            elif step_type == 'blockchain_record':
                await self.execute_blockchain_record_step(step)
            
            # Record step completion
            workflow['steps'].append({
                'step': step_type,
                'status': 'completed',
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logging.error(f"Error executing workflow step: {str(e)}")
            workflow['steps'].append({
                'step': step.get('type', 'unknown'),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now()
            })
    
    async def execute_news_fetch_step(self, step: Dict[str, Any]):
        """Execute news fetch step"""
        news_agent = self.agents.get('news')
        if news_agent:
            # Trigger news fetching with specific parameters
            pass
    
    async def execute_review_step(self, step: Dict[str, Any]):
        """Execute review step"""
        review_agent = self.agents.get('review')
        if review_agent:
            # Trigger review process
            pass
    
    async def execute_content_process_step(self, step: Dict[str, Any]):
        """Execute content processing step"""
        content_agent = self.agents.get('content')
        if content_agent:
            # Trigger content processing
            pass
    
    async def execute_blockchain_record_step(self, step: Dict[str, Any]):
        """Execute blockchain recording step"""
        # Record specific data on blockchain
        pass
