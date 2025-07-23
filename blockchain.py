import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from database import db
from config import OPENAI_API_KEY
from ai_services import client as openai_client

class BlockchainReviewSystem:
    def __init__(self):
        self.chain = []
        self.pending_reviews = []
        self.review_types = ['accuracy', 'bias', 'quality', 'originality', 'compliance']
        self.consensus_threshold = 0.67  # 67% consensus required
        
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'reviews': [],
            'previous_hash': '0',
            'nonce': 0,
            'merkle_root': self.calculate_merkle_root([])
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        return genesis_block
    
    def calculate_hash(self, block: Dict) -> str:
        """Calculate SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def calculate_merkle_root(self, reviews: List[Dict]) -> str:
        """Calculate Merkle root of reviews"""
        if not reviews:
            return hashlib.sha256(b'').hexdigest()
        
        # Create leaf nodes
        leaves = [hashlib.sha256(json.dumps(review, sort_keys=True).encode()).hexdigest() 
                 for review in reviews]
        
        # Build Merkle tree
        while len(leaves) > 1:
            new_level = []
            for i in range(0, len(leaves), 2):
                left = leaves[i]
                right = leaves[i + 1] if i + 1 < len(leaves) else leaves[i]
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                new_level.append(combined)
            leaves = new_level
        
        return leaves[0]
    
    def proof_of_work(self, block: Dict, difficulty: int = 4) -> Dict:
        """Perform proof of work mining"""
        target = "0" * difficulty
        
        while block['hash'][:difficulty] != target:
            block['nonce'] += 1
            block['hash'] = self.calculate_hash(block)
        
        return block
    
    def add_review_to_blockchain(self, review_data: Dict) -> Dict:
        """Add a review to the blockchain"""
        try:
            # Validate review data
            if not self.validate_review_data(review_data):
                raise ValueError("Invalid review data")
            
            # Add timestamp and reviewer verification
            review_data['timestamp'] = time.time()
            review_data['review_hash'] = self.calculate_review_hash(review_data)
            
            # Add to pending reviews
            self.pending_reviews.append(review_data)
            
            # Mine new block if enough reviews
            if len(self.pending_reviews) >= 10:  # Batch reviews
                new_block = self.mine_block()
                self.chain.append(new_block)
                
                # Store in database
                self.store_block_in_database(new_block)
                
                # Clear pending reviews
                self.pending_reviews = []
                
                return new_block
            
            return {"status": "pending", "review_hash": review_data['review_hash']}
            
        except Exception as e:
            print(f"Error adding review to blockchain: {e}")
            return {"status": "error", "message": str(e)}
    
    def validate_review_data(self, review_data: Dict) -> bool:
        """Validate review data structure"""
        required_fields = ['article_id', 'reviewer_id', 'review_type', 'rating', 'comment']
        return all(field in review_data for field in required_fields)
    
    def calculate_review_hash(self, review_data: Dict) -> str:
        """Calculate hash for a review"""
        review_string = json.dumps(review_data, sort_keys=True)
        return hashlib.sha256(review_string.encode()).hexdigest()
    
    def mine_block(self) -> Dict:
        """Mine a new block with pending reviews"""
        previous_block = self.chain[-1] if self.chain else self.create_genesis_block()
        
        new_block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'reviews': self.pending_reviews.copy(),
            'previous_hash': previous_block['hash'],
            'nonce': 0,
            'merkle_root': self.calculate_merkle_root(self.pending_reviews)
        }
        
        # Perform proof of work
        new_block = self.proof_of_work(new_block)
        
        return new_block
    
    def verify_block_integrity(self, block: Dict) -> bool:
        """Verify the integrity of a block"""
        try:
            # Check hash
            calculated_hash = self.calculate_hash(block)
            if calculated_hash != block['hash']:
                return False
            
            # Check Merkle root
            calculated_merkle = self.calculate_merkle_root(block['reviews'])
            if calculated_merkle != block['merkle_root']:
                return False
            
            # Check previous hash
            if block['index'] > 0:
                previous_block = self.get_block_by_index(block['index'] - 1)
                if previous_block and previous_block['hash'] != block['previous_hash']:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error verifying block integrity: {e}")
            return False
    
    def get_block_by_index(self, index: int) -> Optional[Dict]:
        """Get block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_reviews_for_article(self, article_id: int) -> List[Dict]:
        """Get all reviews for a specific article"""
        reviews = []
        
        for block in self.chain:
            for review in block['reviews']:
                if review['article_id'] == article_id:
                    reviews.append(review)
        
        return reviews
    
    def calculate_consensus_score(self, article_id: int) -> Dict:
        """Calculate consensus score for an article"""
        reviews = self.get_reviews_for_article(article_id)
        
        if not reviews:
            return {"consensus_score": 0, "total_reviews": 0}
        
        # Group reviews by type
        review_groups = {}
        for review in reviews:
            review_type = review['review_type']
            if review_type not in review_groups:
                review_groups[review_type] = []
            review_groups[review_type].append(review['rating'])
        
        # Calculate consensus for each review type
        consensus_scores = {}
        for review_type, ratings in review_groups.items():
            if len(ratings) > 1:
                # Calculate variance (lower variance = higher consensus)
                mean_rating = sum(ratings) / len(ratings)
                variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
                consensus_scores[review_type] = {
                    "mean_rating": mean_rating,
                    "consensus": max(0, 1 - variance / 4)  # Normalize to 0-1
                }
        
        # Overall consensus score
        if consensus_scores:
            overall_consensus = sum(score['consensus'] for score in consensus_scores.values()) / len(consensus_scores)
        else:
            overall_consensus = 0
        
        return {
            "consensus_score": overall_consensus,
            "total_reviews": len(reviews),
            "review_breakdown": consensus_scores
        }
    
    def detect_review_fraud(self, review_data: Dict) -> Dict:
        """Detect potential review fraud using AI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fraud detection expert. Analyze the review data for potential fraud indicators such as duplicate content, unusual patterns, or suspicious reviewer behavior. Respond with JSON containing fraud_score (0-1), indicators found, and confidence level."
                    },
                    {
                        "role": "user",
                        "content": json.dumps(review_data)
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            fraud_analysis = json.loads(response.choices[0].message.content)
            return fraud_analysis
            
        except Exception as e:
            print(f"Error detecting review fraud: {e}")
            return {"fraud_score": 0, "indicators": [], "confidence": 0}
    
    def store_block_in_database(self, block: Dict):
        """Store block in database for persistence"""
        try:
            query = """
            INSERT INTO blockchain_blocks (block_index, block_hash, previous_hash, 
                                         timestamp, merkle_root, nonce, reviews_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            db.execute_query(query, (
                block['index'],
                block['hash'],
                block['previous_hash'],
                datetime.fromtimestamp(block['timestamp']),
                block['merkle_root'],
                block['nonce'],
                json.dumps(block['reviews'])
            ), fetch=False)
            
        except Exception as e:
            print(f"Error storing block in database: {e}")
    
    def load_blockchain_from_database(self):
        """Load blockchain from database"""
        try:
            query = """
            SELECT * FROM blockchain_blocks 
            ORDER BY block_index ASC
            """
            
            result = db.execute_query(query)
            
            if result:
                self.chain = []
                for row in result:
                    block = {
                        'index': row['block_index'],
                        'hash': row['block_hash'],
                        'previous_hash': row['previous_hash'],
                        'timestamp': row['timestamp'].timestamp(),
                        'merkle_root': row['merkle_root'],
                        'nonce': row['nonce'],
                        'reviews': json.loads(row['reviews_data'])
                    }
                    self.chain.append(block)
            
            # Initialize with genesis block if empty
            if not self.chain:
                self.chain = [self.create_genesis_block()]
                
        except Exception as e:
            print(f"Error loading blockchain from database: {e}")
            self.chain = [self.create_genesis_block()]
    
    def get_blockchain_stats(self) -> Dict:
        """Get blockchain statistics"""
        total_blocks = len(self.chain)
        total_reviews = sum(len(block['reviews']) for block in self.chain)
        
        # Calculate average consensus scores
        article_consensus = {}
        for block in self.chain:
            for review in block['reviews']:
                article_id = review['article_id']
                if article_id not in article_consensus:
                    article_consensus[article_id] = []
                article_consensus[article_id].append(review['rating'])
        
        avg_consensus = 0
        if article_consensus:
            consensus_scores = []
            for article_id, ratings in article_consensus.items():
                if len(ratings) > 1:
                    mean_rating = sum(ratings) / len(ratings)
                    variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
                    consensus = max(0, 1 - variance / 4)
                    consensus_scores.append(consensus)
            
            avg_consensus = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
        
        return {
            "total_blocks": total_blocks,
            "total_reviews": total_reviews,
            "average_consensus": avg_consensus,
            "blockchain_integrity": self.verify_blockchain_integrity()
        }
    
    def verify_blockchain_integrity(self) -> bool:
        """Verify entire blockchain integrity"""
        for block in self.chain:
            if not self.verify_block_integrity(block):
                return False
        return True

# Initialize blockchain system
blockchain_system = BlockchainReviewSystem()

def initialize_blockchain():
    """Initialize blockchain system"""
    # Create database tables
    create_blockchain_tables()
    
    # Load existing blockchain
    blockchain_system.load_blockchain_from_database()

def create_blockchain_tables():
    """Create blockchain-related database tables"""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS blockchain_blocks (
            id SERIAL PRIMARY KEY,
            block_index INTEGER NOT NULL,
            block_hash VARCHAR(64) NOT NULL,
            previous_hash VARCHAR(64) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            merkle_root VARCHAR(64) NOT NULL,
            nonce INTEGER NOT NULL,
            reviews_data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS review_verification (
            id SERIAL PRIMARY KEY,
            review_id INTEGER REFERENCES reviews(id),
            blockchain_hash VARCHAR(64) NOT NULL,
            block_index INTEGER NOT NULL,
            verification_status VARCHAR(50) DEFAULT 'verified',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for query in queries:
        db.execute_query(query, fetch=False)

def submit_review_to_blockchain(review_data: Dict) -> Dict:
    """Submit a review to the blockchain"""
    # Add fraud detection
    fraud_analysis = blockchain_system.detect_review_fraud(review_data)
    
    if fraud_analysis.get('fraud_score', 0) > 0.7:
        return {
            "status": "rejected",
            "reason": "High fraud probability detected",
            "fraud_indicators": fraud_analysis.get('indicators', [])
        }
    
    # Add to blockchain
    result = blockchain_system.add_review_to_blockchain(review_data)
    
    # Store review verification
    if result.get('review_hash'):
        store_review_verification(review_data.get('review_id'), result['review_hash'])
    
    return result

def store_review_verification(review_id: int, blockchain_hash: str):
    """Store review verification in database"""
    try:
        query = """
        INSERT INTO review_verification (review_id, blockchain_hash, block_index)
        VALUES (%s, %s, %s)
        """
        
        block_index = len(blockchain_system.chain) - 1
        db.execute_query(query, (review_id, blockchain_hash, block_index), fetch=False)
        
    except Exception as e:
        print(f"Error storing review verification: {e}")

def get_article_consensus(article_id: int) -> Dict:
    """Get consensus score for an article"""
    return blockchain_system.calculate_consensus_score(article_id)

def verify_review_authenticity(review_id: int) -> Dict:
    """Verify review authenticity using blockchain"""
    try:
        query = """
        SELECT * FROM review_verification 
        WHERE review_id = %s
        """
        
        result = db.execute_query(query, (review_id,))
        
        if result:
            verification_data = dict(result[0])
            
            # Verify blockchain integrity
            block_index = verification_data['block_index']
            block = blockchain_system.get_block_by_index(block_index)
            
            if block and blockchain_system.verify_block_integrity(block):
                return {
                    "verified": True,
                    "blockchain_hash": verification_data['blockchain_hash'],
                    "block_index": block_index,
                    "timestamp": verification_data['created_at']
                }
            else:
                return {
                    "verified": False,
                    "reason": "Blockchain integrity compromised"
                }
        
        return {
            "verified": False,
            "reason": "Review not found in blockchain"
        }
        
    except Exception as e:
        print(f"Error verifying review authenticity: {e}")
        return {
            "verified": False,
            "reason": "Verification error"
        }

def get_blockchain_statistics() -> Dict:
    """Get blockchain system statistics"""
    return blockchain_system.get_blockchain_stats()

# Initialize blockchain on module load
initialize_blockchain()
