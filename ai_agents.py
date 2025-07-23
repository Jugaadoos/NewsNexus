import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
from openai import OpenAI
from config import OPENAI_API_KEY
from database import save_article, db
from news_aggregator import news_aggregator
from ai_services import analyze_sentiment, categorize_content
from blockchain import submit_review_to_blockchain
import difflib

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class AgentType(Enum):
    SOURCING = "sourcing"
    REVIEW = "review"
    SUMMARY = "summary"
    OPINION = "opinion"
    COMPLIANCE = "compliance"
    DISTRIBUTION = "distribution"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentTask:
    id: str
    agent_type: AgentType
    task_data: Dict
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class BaseAgent:
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.tasks = []
        self.is_active = True
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute a task - to be implemented by subclasses"""
        raise NotImplementedError
    
    def add_task(self, task: AgentTask):
        """Add a task to the agent's queue"""
        self.tasks.append(task)
    
    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

class SourcingAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.SOURCING)
        self.source_priorities = {
            "breaking": 1,
            "local": 2,
            "trending": 3,
            "general": 4
        }
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Source news articles based on criteria"""
        try:
            criteria = task.task_data
            location = criteria.get('location', {})
            category = criteria.get('category', 'world')
            urgency = criteria.get('urgency', 'general')
            
            # Determine sources based on criteria
            if urgency == "breaking":
                sources = self.get_breaking_news_sources()
            elif location:
                sources = self.get_local_news_sources(location)
            else:
                sources = self.get_general_news_sources(category)
            
            # Fetch articles from sources
            articles = []
            for source in sources:
                try:
                    source_articles = await self.fetch_from_source(source)
                    articles.extend(source_articles)
                except Exception as e:
                    print(f"Error fetching from source {source}: {e}")
            
            # Filter and rank articles
            filtered_articles = self.filter_articles(articles, criteria)
            ranked_articles = self.rank_articles(filtered_articles, urgency)
            
            return {
                "status": "success",
                "articles": ranked_articles[:20],  # Top 20 articles
                "sources_checked": len(sources),
                "total_found": len(articles)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_breaking_news_sources(self) -> List[Dict]:
        """Get breaking news sources"""
        return [
            {"name": "Reuters Breaking", "url": "https://feeds.reuters.com/reuters/breakingviews"},
            {"name": "AP Breaking", "url": "https://storage.googleapis.com/afs-prod/feeds/xml/rss_2.0.xml"},
            {"name": "BBC Breaking", "url": "https://feeds.bbci.co.uk/news/rss.xml"}
        ]
    
    def get_local_news_sources(self, location: Dict) -> List[Dict]:
        """Get local news sources based on location"""
        # In a real implementation, this would query a database of local news sources
        country = location.get('country_code', 'US')
        
        local_sources = {
            "US": [
                {"name": "Local News Network", "url": "https://example.com/local-rss"},
                {"name": "City News", "url": "https://example.com/city-rss"}
            ],
            "UK": [
                {"name": "Local UK News", "url": "https://example.com/uk-local-rss"}
            ]
        }
        
        return local_sources.get(country, [])
    
    def get_general_news_sources(self, category: str) -> List[Dict]:
        """Get general news sources for category"""
        from config import RSS_FEEDS
        
        sources = []
        for url in RSS_FEEDS.get(category, []):
            sources.append({"name": f"{category.title()} News", "url": url})
        
        return sources
    
    async def fetch_from_source(self, source: Dict) -> List[Dict]:
        """Fetch articles from a news source"""
        try:
            articles = news_aggregator.fetch_rss_feed(source['url'])
            for article in articles:
                article['source_name'] = source['name']
            return articles
        except Exception as e:
            print(f"Error fetching from {source['name']}: {e}")
            return []
    
    def filter_articles(self, articles: List[Dict], criteria: Dict) -> List[Dict]:
        """Filter articles based on criteria"""
        filtered = []
        
        for article in articles:
            # Apply filters
            if criteria.get('keywords'):
                if not any(keyword.lower() in article.get('title', '').lower() 
                          for keyword in criteria['keywords']):
                    continue
            
            if criteria.get('exclude_keywords'):
                if any(keyword.lower() in article.get('title', '').lower() 
                      for keyword in criteria['exclude_keywords']):
                    continue
            
            if criteria.get('min_word_count'):
                if len(article.get('content', '').split()) < criteria['min_word_count']:
                    continue
            
            filtered.append(article)
        
        return filtered
    
    def rank_articles(self, articles: List[Dict], urgency: str) -> List[Dict]:
        """Rank articles by relevance and urgency"""
        for article in articles:
            score = 0
            
            # Urgency scoring
            if urgency == "breaking":
                breaking_keywords = ['breaking', 'urgent', 'alert', 'developing']
                if any(keyword in article.get('title', '').lower() for keyword in breaking_keywords):
                    score += 10
            
            # Recency scoring
            if article.get('published_at'):
                hours_old = (datetime.now() - article['published_at']).total_seconds() / 3600
                score += max(0, 24 - hours_old)  # Prefer recent articles
            
            # Content quality scoring
            if article.get('content'):
                score += min(5, len(article['content']) / 500)  # Longer content gets higher score
            
            article['relevance_score'] = score
        
        # Sort by relevance score
        return sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)

class ReviewAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.REVIEW)
        self.review_criteria = {
            "accuracy": "Check factual accuracy and source credibility",
            "bias": "Identify potential bias and balanced reporting",
            "quality": "Assess writing quality and journalism standards",
            "originality": "Check for plagiarism and originality",
            "compliance": "Verify compliance with editorial guidelines"
        }
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Review an article for accuracy, bias, and quality"""
        try:
            article_data = task.task_data
            article_id = article_data['id']
            
            # Perform different types of reviews
            reviews = {}
            
            # Accuracy review
            reviews['accuracy'] = await self.review_accuracy(article_data)
            
            # Bias review
            reviews['bias'] = await self.review_bias(article_data)
            
            # Quality review
            reviews['quality'] = await self.review_quality(article_data)
            
            # Originality review
            reviews['originality'] = await self.review_originality(article_data)
            
            # Compliance review
            reviews['compliance'] = await self.review_compliance(article_data)
            
            # Calculate overall score
            overall_score = sum(review['score'] for review in reviews.values()) / len(reviews)
            
            # Submit to blockchain
            blockchain_result = submit_review_to_blockchain({
                'article_id': article_id,
                'reviewer_id': self.agent_id,
                'review_type': 'comprehensive',
                'rating': int(overall_score),
                'comment': f"AI Agent Review: {json.dumps(reviews)}",
                'reviews': reviews
            })
            
            return {
                "status": "success",
                "overall_score": overall_score,
                "detailed_reviews": reviews,
                "blockchain_hash": blockchain_result.get('review_hash')
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def review_accuracy(self, article_data: Dict) -> Dict:
        """Review article for factual accuracy"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact-checking expert. Review the article for factual accuracy, source credibility, and verifiable claims. Rate from 1-5 (5 being most accurate) and provide specific feedback. Respond with JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Article: {article_data.get('title', '')} - {article_data.get('content', '')}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "score": result.get('rating', 3),
                "feedback": result.get('feedback', ''),
                "issues": result.get('issues', [])
            }
            
        except Exception as e:
            return {"score": 3, "feedback": "Error in accuracy review", "issues": []}
    
    async def review_bias(self, article_data: Dict) -> Dict:
        """Review article for bias and balanced reporting"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a media bias expert. Analyze the article for political bias, balanced reporting, and fair representation of different viewpoints. Rate from 1-5 (5 being most balanced) and provide specific feedback. Respond with JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Article: {article_data.get('title', '')} - {article_data.get('content', '')}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "score": result.get('rating', 3),
                "feedback": result.get('feedback', ''),
                "bias_indicators": result.get('bias_indicators', [])
            }
            
        except Exception as e:
            return {"score": 3, "feedback": "Error in bias review", "bias_indicators": []}
    
    async def review_quality(self, article_data: Dict) -> Dict:
        """Review article for writing quality and journalism standards"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a journalism quality expert. Evaluate the article for writing quality, structure, clarity, and adherence to journalism standards. Rate from 1-5 (5 being highest quality) and provide specific feedback. Respond with JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Article: {article_data.get('title', '')} - {article_data.get('content', '')}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "score": result.get('rating', 3),
                "feedback": result.get('feedback', ''),
                "quality_metrics": result.get('quality_metrics', {})
            }
            
        except Exception as e:
            return {"score": 3, "feedback": "Error in quality review", "quality_metrics": {}}
    
    async def review_originality(self, article_data: Dict) -> Dict:
        """Review article for originality and plagiarism"""
        try:
            content = article_data.get('content', '')
            
            # Check against database for similar content
            similar_articles = self.find_similar_articles(content)
            
            originality_score = 5
            issues = []
            
            if similar_articles:
                # Calculate similarity scores
                for similar_article in similar_articles:
                    similarity = difflib.SequenceMatcher(None, content, similar_article['content']).ratio()
                    
                    if similarity > 0.8:
                        originality_score = 1
                        issues.append(f"High similarity ({similarity:.2%}) with article: {similar_article['title']}")
                    elif similarity > 0.6:
                        originality_score = min(originality_score, 2)
                        issues.append(f"Moderate similarity ({similarity:.2%}) with article: {similar_article['title']}")
                    elif similarity > 0.4:
                        originality_score = min(originality_score, 3)
                        issues.append(f"Some similarity ({similarity:.2%}) with article: {similar_article['title']}")
            
            return {
                "score": originality_score,
                "feedback": "Originality check completed",
                "issues": issues,
                "similar_articles": len(similar_articles)
            }
            
        except Exception as e:
            return {"score": 3, "feedback": "Error in originality review", "issues": []}
    
    async def review_compliance(self, article_data: Dict) -> Dict:
        """Review article for compliance with editorial guidelines"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compliance expert. Review the article for adherence to editorial guidelines, legal compliance, and ethical standards. Check for potential legal issues, ethical concerns, and guideline violations. Rate from 1-5 (5 being fully compliant) and provide specific feedback. Respond with JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Article: {article_data.get('title', '')} - {article_data.get('content', '')}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "score": result.get('rating', 3),
                "feedback": result.get('feedback', ''),
                "compliance_issues": result.get('compliance_issues', [])
            }
            
        except Exception as e:
            return {"score": 3, "feedback": "Error in compliance review", "compliance_issues": []}
    
    def find_similar_articles(self, content: str) -> List[Dict]:
        """Find similar articles in the database"""
        try:
            # Simple similarity check - in production, use proper text similarity
            query = """
            SELECT id, title, content FROM news_articles 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            LIMIT 100
            """
            
            result = db.execute_query(query)
            similar_articles = []
            
            if result:
                for row in result:
                    similarity = difflib.SequenceMatcher(None, content, row['content']).ratio()
                    if similarity > 0.3:  # Threshold for consideration
                        similar_articles.append({
                            'id': row['id'],
                            'title': row['title'],
                            'content': row['content'],
                            'similarity': similarity
                        })
            
            return sorted(similar_articles, key=lambda x: x['similarity'], reverse=True)[:5]
            
        except Exception as e:
            print(f"Error finding similar articles: {e}")
            return []

class SummaryAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.SUMMARY)
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Generate AI summary for an article"""
        try:
            article_data = task.task_data
            content = article_data.get('content', '')
            
            if not content:
                return {
                    "status": "error",
                    "error": "No content provided for summarization"
                }
            
            # Generate summary
            from ai_services import summarize_article
            summary = summarize_article(content)
            
            # Generate multiple summary variants
            variants = await self.generate_summary_variants(content)
            
            return {
                "status": "success",
                "summary": summary,
                "variants": variants,
                "word_count": len(summary.split())
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_summary_variants(self, content: str) -> List[Dict]:
        """Generate different summary variants"""
        try:
            variants = []
            
            # Different summary styles
            styles = [
                {"name": "Brief", "prompt": "Create a brief 50-word summary"},
                {"name": "Detailed", "prompt": "Create a detailed 150-word summary"},
                {"name": "Bullet Points", "prompt": "Create a bullet-point summary"},
                {"name": "Question Format", "prompt": "Create a summary in Q&A format"}
            ]
            
            for style in styles:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a professional news summarizer. {style['prompt']} of the following article."
                        },
                        {
                            "role": "user",
                            "content": content
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                variants.append({
                    "style": style["name"],
                    "summary": response.choices[0].message.content.strip()
                })
            
            return variants
            
        except Exception as e:
            print(f"Error generating summary variants: {e}")
            return []

class OpinionAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.OPINION)
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Generate opinion pieces on articles"""
        try:
            article_data = task.task_data
            content = article_data.get('content', '')
            perspective = task.task_data.get('perspective', 'balanced')
            
            if not content:
                return {
                    "status": "error",
                    "error": "No content provided for opinion generation"
                }
            
            # Generate opinion
            from ai_services import generate_opinion
            opinion = generate_opinion(content, perspective)
            
            # Generate multiple perspective opinions
            perspectives = await self.generate_multiple_perspectives(content)
            
            return {
                "status": "success",
                "primary_opinion": opinion,
                "perspectives": perspectives
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_multiple_perspectives(self, content: str) -> List[Dict]:
        """Generate opinions from multiple perspectives"""
        try:
            perspectives = []
            
            viewpoints = [
                {"name": "Conservative", "prompt": "Provide a conservative perspective"},
                {"name": "Liberal", "prompt": "Provide a liberal perspective"},
                {"name": "Neutral", "prompt": "Provide a neutral, balanced perspective"},
                {"name": "Economic", "prompt": "Focus on economic implications"},
                {"name": "Social", "prompt": "Focus on social implications"}
            ]
            
            for viewpoint in viewpoints:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a thoughtful analyst. {viewpoint['prompt']} on the following article. Keep it under 150 words."
                        },
                        {
                            "role": "user",
                            "content": content
                        }
                    ],
                    max_tokens=200,
                    temperature=0.6
                )
                
                perspectives.append({
                    "viewpoint": viewpoint["name"],
                    "opinion": response.choices[0].message.content.strip()
                })
            
            return perspectives
            
        except Exception as e:
            print(f"Error generating multiple perspectives: {e}")
            return []

class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.workflow_templates = {}
        self.active_workflows = {}
        
        # Initialize agents
        self.initialize_agents()
        self.setup_workflow_templates()
    
    def initialize_agents(self):
        """Initialize all agents"""
        # Create sourcing agents
        self.agents['sourcing_1'] = SourcingAgent('sourcing_1')
        self.agents['sourcing_2'] = SourcingAgent('sourcing_2')
        
        # Create review agents
        self.agents['review_1'] = ReviewAgent('review_1')
        self.agents['review_2'] = ReviewAgent('review_2')
        
        # Create summary agents
        self.agents['summary_1'] = SummaryAgent('summary_1')
        
        # Create opinion agents
        self.agents['opinion_1'] = OpinionAgent('opinion_1')
    
    def setup_workflow_templates(self):
        """Setup workflow templates"""
        self.workflow_templates = {
            "full_article_processing": {
                "steps": [
                    {"agent_type": AgentType.SOURCING, "parallel": True},
                    {"agent_type": AgentType.REVIEW, "parallel": True},
                    {"agent_type": AgentType.SUMMARY, "parallel": False},
                    {"agent_type": AgentType.OPINION, "parallel": False}
                ]
            },
            "breaking_news": {
                "steps": [
                    {"agent_type": AgentType.SOURCING, "parallel": True, "urgency": "breaking"},
                    {"agent_type": AgentType.SUMMARY, "parallel": False, "speed": "fast"},
                    {"agent_type": AgentType.REVIEW, "parallel": True, "priority": "high"}
                ]
            },
            "content_verification": {
                "steps": [
                    {"agent_type": AgentType.REVIEW, "parallel": True, "focus": "accuracy"},
                    {"agent_type": AgentType.REVIEW, "parallel": True, "focus": "originality"}
                ]
            }
        }
    
    async def execute_workflow(self, workflow_name: str, input_data: Dict) -> Dict:
        """Execute a complete workflow"""
        try:
            if workflow_name not in self.workflow_templates:
                return {
                    "status": "error",
                    "error": f"Unknown workflow: {workflow_name}"
                }
            
            workflow_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            workflow = self.workflow_templates[workflow_name]
            
            # Track workflow execution
            self.active_workflows[workflow_id] = {
                "name": workflow_name,
                "started_at": datetime.now(),
                "steps": [],
                "status": "running"
            }
            
            workflow_result = {
                "workflow_id": workflow_id,
                "steps": [],
                "final_result": {}
            }
            
            # Execute workflow steps
            for step_index, step in enumerate(workflow['steps']):
                step_result = await self.execute_workflow_step(step, input_data, workflow_id)
                workflow_result["steps"].append(step_result)
                
                # Use step result as input for next step
                if step_result.get("status") == "success":
                    input_data.update(step_result.get("result", {}))
                
                # Update workflow tracking
                self.active_workflows[workflow_id]["steps"].append({
                    "step_index": step_index,
                    "agent_type": step["agent_type"].value,
                    "status": step_result.get("status"),
                    "completed_at": datetime.now()
                })
            
            # Complete workflow
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
            
            workflow_result["final_result"] = input_data
            
            return {
                "status": "success",
                "workflow_result": workflow_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_workflow_step(self, step: Dict, input_data: Dict, workflow_id: str) -> Dict:
        """Execute a single workflow step"""
        try:
            agent_type = step["agent_type"]
            parallel = step.get("parallel", False)
            
            # Get available agents of the required type
            available_agents = [agent for agent in self.agents.values() 
                              if agent.agent_type == agent_type and agent.is_active]
            
            if not available_agents:
                return {
                    "status": "error",
                    "error": f"No available agents of type {agent_type.value}"
                }
            
            # Create tasks
            tasks = []
            for agent in available_agents:
                task = AgentTask(
                    id=f"{workflow_id}_{agent.agent_id}_{datetime.now().strftime('%H%M%S')}",
                    agent_type=agent_type,
                    task_data=input_data.copy(),
                    status=TaskStatus.PENDING,
                    created_at=datetime.now()
                )
                tasks.append((agent, task))
            
            # Execute tasks
            if parallel and len(tasks) > 1:
                # Execute in parallel
                results = await self.execute_parallel_tasks(tasks)
            else:
                # Execute sequentially
                results = await self.execute_sequential_tasks(tasks)
            
            # Combine results
            combined_result = self.combine_step_results(results)
            
            return {
                "status": "success",
                "agent_type": agent_type.value,
                "result": combined_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_parallel_tasks(self, tasks: List[tuple]) -> List[Dict]:
        """Execute tasks in parallel"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = []
            
            for agent, task in tasks:
                future = executor.submit(asyncio.run, agent.execute_task(task))
                futures.append((agent, task, future))
            
            for agent, task, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results.append({
                        "agent_id": agent.agent_id,
                        "task_id": task.id,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "agent_id": agent.agent_id,
                        "task_id": task.id,
                        "result": {"status": "error", "error": str(e)}
                    })
        
        return results
    
    async def execute_sequential_tasks(self, tasks: List[tuple]) -> List[Dict]:
        """Execute tasks sequentially"""
        results = []
        
        for agent, task in tasks:
            try:
                result = await agent.execute_task(task)
                results.append({
                    "agent_id": agent.agent_id,
                    "task_id": task.id,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "agent_id": agent.agent_id,
                    "task_id": task.id,
                    "result": {"status": "error", "error": str(e)}
                })
        
        return results
    
    def combine_step_results(self, results: List[Dict]) -> Dict:
        """Combine results from multiple agents"""
        combined = {
            "agent_results": results,
            "success_count": sum(1 for r in results if r["result"].get("status") == "success"),
            "total_count": len(results)
        }
        
        # Extract common data
        successful_results = [r for r in results if r["result"].get("status") == "success"]
        
        if successful_results:
            # Combine specific result types
            if "articles" in successful_results[0]["result"]:
                # Combine articles from sourcing agents
                all_articles = []
                for result in successful_results:
                    all_articles.extend(result["result"]["articles"])
                combined["articles"] = all_articles
            
            if "overall_score" in successful_results[0]["result"]:
                # Average review scores
                scores = [r["result"]["overall_score"] for r in successful_results]
                combined["average_score"] = sum(scores) / len(scores)
            
            if "summary" in successful_results[0]["result"]:
                # Use first successful summary
                combined["summary"] = successful_results[0]["result"]["summary"]
        
        return combined
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of a workflow"""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found"}
        
        return self.active_workflows[workflow_id]
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        agent_status = {}
        
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "type": agent.agent_type.value,
                "is_active": agent.is_active,
                "pending_tasks": len(agent.get_pending_tasks()),
                "total_tasks": len(agent.tasks)
            }
        
        return agent_status

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Export functions
async def process_article_with_agents(article_data: Dict, workflow: str = "full_article_processing") -> Dict:
    """Process an article using AI agents"""
    return await orchestrator.execute_workflow(workflow, article_data)

async def source_breaking_news(location: Dict, keywords: List[str]) -> Dict:
    """Source breaking news using AI agents"""
    return await orchestrator.execute_workflow("breaking_news", {
        "location": location,
        "keywords": keywords,
        "urgency": "breaking"
    })

async def verify_article_content(article_data: Dict) -> Dict:
    """Verify article content using AI agents"""
    return await orchestrator.execute_workflow("content_verification", article_data)

def get_agent_system_status() -> Dict:
    """Get overall system status"""
    return {
        "agents": orchestrator.get_agent_status(),
        "active_workflows": len(orchestrator.active_workflows),
        "workflow_templates": list(orchestrator.workflow_templates.keys())
    }

def get_workflow_history(limit: int = 10) -> List[Dict]:
    """Get workflow execution history"""
    workflows = list(orchestrator.active_workflows.values())
    workflows.sort(key=lambda x: x.get("started_at", datetime.min), reverse=True)
    return workflows[:limit]
