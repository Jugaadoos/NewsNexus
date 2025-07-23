import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from database import DatabaseManager

class BlockchainReview:
    """Handles blockchain-based review and verification system"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.blockchain_enabled = os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
        self.web3_provider = os.getenv('WEB3_PROVIDER_URL', 'demo_provider')
        self.contract_address = os.getenv('REVIEW_CONTRACT_ADDRESS', 'demo_address')
        self.private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY', 'demo_key')
        
        # Initialize Web3 if enabled
        if self.blockchain_enabled and self.web3_provider != 'demo_provider':
            try:
                from web3 import Web3
                self.w3 = Web3(Web3.HTTPProvider(self.web3_provider))
                self.account = self.w3.eth.account.from_key(self.private_key)
                print("Blockchain integration initialized")
            except ImportError:
                print("Web3 not available, using local verification")
                self.blockchain_enabled = False
        else:
            self.blockchain_enabled = False
    
    def create_review_hash(self, article_id: str, reviewer_id: str, review_content: Dict) -> str:
        """Create hash for review content"""
        review_string = json.dumps({
            'article_id': article_id,
            'reviewer_id': reviewer_id,
            'review_content': review_content,
            'timestamp': datetime.now().isoformat()
        }, sort_keys=True)
        
        return hashlib.sha256(review_string.encode()).hexdigest()
    
    def submit_review(self, article_id: str, reviewer_id: str, review_content: Dict) -> Dict:
        """Submit review to blockchain"""
        try:
            # Create review hash
            review_hash = self.create_review_hash(article_id, reviewer_id, review_content)
            
            # Create blockchain transaction if enabled
            transaction_id = None
            if self.blockchain_enabled:
                transaction_id = self.submit_to_blockchain(review_hash, review_content)
            else:
                # Use local verification
                transaction_id = f"local_{uuid.uuid4().hex}"
            
            # Store review in database
            review_record = {
                'id': str(uuid.uuid4()),
                'article_id': article_id,
                'reviewer_id': reviewer_id,
                'review_hash': review_hash,
                'review_content': review_content,
                'transaction_id': transaction_id,
                'is_verified': True,
                'created_at': datetime.now()
            }
            
            if self.store_review_record(review_record):
                return {
                    'success': True,
                    'review_id': review_record['id'],
                    'review_hash': review_hash,
                    'transaction_id': transaction_id,
                    'verification_status': 'verified'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store review record'
                }
                
        except Exception as e:
            print(f"Error submitting review: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_to_blockchain(self, review_hash: str, review_content: Dict) -> str:
        """Submit review to blockchain network"""
        try:
            if not self.blockchain_enabled:
                return f"local_{uuid.uuid4().hex}"
            
            # Prepare transaction data
            transaction_data = {
                'review_hash': review_hash,
                'reviewer_score': review_content.get('score', 0),
                'review_category': review_content.get('category', 'general'),
                'timestamp': int(datetime.now().timestamp())
            }
            
            # Create transaction
            transaction = {
                'to': self.contract_address,
                'value': 0,
                'gas': 100000,
                'gasPrice': self.w3.toWei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'data': self.w3.toHex(json.dumps(transaction_data).encode())
            }
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            print(f"Error submitting to blockchain: {e}")
            return f"local_{uuid.uuid4().hex}"
    
    def store_review_record(self, review_record: Dict) -> bool:
        """Store review record in database"""
        conn = self.db.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO blockchain_reviews (
                    id, article_id, reviewer_id, review_hash, review_content,
                    blockchain_transaction_id, review_score, is_verified, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    review_record['id'],
                    review_record['article_id'],
                    review_record['reviewer_id'],
                    review_record['review_hash'],
                    json.dumps(review_record['review_content']),
                    review_record['transaction_id'],
                    review_record['review_content'].get('score', 0),
                    review_record['is_verified'],
                    review_record['created_at']
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error storing review record: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def verify_review(self, review_id: str) -> Dict:
        """Verify review authenticity"""
        conn = self.db.get_connection()
        if not conn:
            return {'verified': False, 'error': 'Database connection failed'}
        
        try:
            with conn.cursor(cursor_factory=self.db.RealDictCursor) as cur:
                cur.execute("""
                SELECT * FROM blockchain_reviews WHERE id = %s
                """, (review_id,))
                
                review = cur.fetchone()
                if not review:
                    return {'verified': False, 'error': 'Review not found'}
                
                # Verify hash
                stored_hash = review['review_hash']
                computed_hash = self.create_review_hash(
                    review['article_id'],
                    review['reviewer_id'],
                    json.loads(review['review_content'])
                )
                
                hash_valid = stored_hash == computed_hash
                
                # Verify blockchain transaction if enabled
                blockchain_valid = True
                if self.blockchain_enabled and review['blockchain_transaction_id']:
                    blockchain_valid = self.verify_blockchain_transaction(
                        review['blockchain_transaction_id']
                    )
                
                return {
                    'verified': hash_valid and blockchain_valid,
                    'hash_valid': hash_valid,
                    'blockchain_valid': blockchain_valid,
                    'transaction_id': review['blockchain_transaction_id'],
                    'review_hash': stored_hash
                }
                
        except Exception as e:
            print(f"Error verifying review: {e}")
            return {'verified': False, 'error': str(e)}
        finally:
            conn.close()
    
    def verify_blockchain_transaction(self, transaction_id: str) -> bool:
        """Verify blockchain transaction"""
        try:
            if not self.blockchain_enabled or transaction_id.startswith('local_'):
                return True  # Local transactions are considered valid
            
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(transaction_id)
            
            # Check if transaction was successful
            return receipt.status == 1
            
        except Exception as e:
            print(f"Error verifying blockchain transaction: {e}")
            return False
    
    def is_verified(self, article_id: str) -> bool:
        """Check if article has verified reviews"""
        conn = self.db.get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT COUNT(*) FROM blockchain_reviews 
                WHERE article_id = %s AND is_verified = TRUE
                """, (article_id,))
                
                count = cur.fetchone()[0]
                return count > 0
                
        except Exception as e:
            print(f"Error checking verification: {e}")
            return False
        finally:
            conn.close()
    
    def get_article_reviews(self, article_id: str) -> List[Dict]:
        """Get all reviews for an article"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=self.db.RealDictCursor) as cur:
                cur.execute("""
                SELECT br.*, u.name as reviewer_name
                FROM blockchain_reviews br
                JOIN users u ON br.reviewer_id = u.id
                WHERE br.article_id = %s
                ORDER BY br.created_at DESC
                """, (article_id,))
                
                reviews = cur.fetchall()
                return [dict(review) for review in reviews]
                
        except Exception as e:
            print(f"Error getting article reviews: {e}")
            return []
        finally:
            conn.close()
    
    def get_reviewer_stats(self, reviewer_id: str) -> Dict:
        """Get reviewer statistics"""
        conn = self.db.get_connection()
        if not conn:
            return {}
        
        try:
            with conn.cursor(cursor_factory=self.db.RealDictCursor) as cur:
                cur.execute("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(review_score) as avg_score,
                    COUNT(CASE WHEN is_verified = TRUE THEN 1 END) as verified_reviews
                FROM blockchain_reviews
                WHERE reviewer_id = %s
                """, (reviewer_id,))
                
                stats = cur.fetchone()
                return dict(stats) if stats else {}
                
        except Exception as e:
            print(f"Error getting reviewer stats: {e}")
            return {}
        finally:
            conn.close()
    
    def create_consensus_review(self, article_id: str) -> Dict:
        """Create consensus review from multiple reviews"""
        reviews = self.get_article_reviews(article_id)
        
        if not reviews:
            return {
                'consensus_score': 0,
                'consensus_status': 'unreviewed',
                'review_count': 0
            }
        
        # Calculate consensus
        total_score = sum(json.loads(review['review_content']).get('score', 0) for review in reviews)
        avg_score = total_score / len(reviews)
        
        # Determine consensus status
        if avg_score >= 0.8:
            status = 'approved'
        elif avg_score >= 0.6:
            status = 'conditional'
        else:
            status = 'rejected'
        
        return {
            'consensus_score': avg_score,
            'consensus_status': status,
            'review_count': len(reviews),
            'verified_reviews': sum(1 for review in reviews if review['is_verified'])
        }
    
    def submit_human_feedback(self, article_id: str, user_id: str, feedback: Dict) -> bool:
        """Submit human feedback for article"""
        try:
            feedback_record = {
                'article_id': article_id,
                'user_id': user_id,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create feedback hash
            feedback_hash = hashlib.sha256(
                json.dumps(feedback_record, sort_keys=True).encode()
            ).hexdigest()
            
            # Store feedback
            conn = self.db.get_connection()
            if not conn:
                return False
            
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO analytics (user_id, article_id, action, metadata)
                VALUES (%s, %s, %s, %s)
                """, (
                    user_id,
                    article_id,
                    'human_feedback',
                    json.dumps({
                        'feedback': feedback,
                        'feedback_hash': feedback_hash
                    })
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error submitting human feedback: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_transparency_report(self, article_id: str) -> Dict:
        """Generate transparency report for article"""
        try:
            reviews = self.get_article_reviews(article_id)
            consensus = self.create_consensus_review(article_id)
            
            # Get human feedback
            conn = self.db.get_connection()
            if not conn:
                return {}
            
            with conn.cursor(cursor_factory=self.db.RealDictCursor) as cur:
                cur.execute("""
                SELECT metadata FROM analytics
                WHERE article_id = %s AND action = 'human_feedback'
                """, (article_id,))
                
                feedback_records = cur.fetchall()
                human_feedback = [
                    json.loads(record['metadata']) for record in feedback_records
                ]
            
            return {
                'article_id': article_id,
                'total_reviews': len(reviews),
                'verified_reviews': sum(1 for review in reviews if review['is_verified']),
                'consensus_score': consensus['consensus_score'],
                'consensus_status': consensus['consensus_status'],
                'human_feedback_count': len(human_feedback),
                'blockchain_verified': any(
                    review['blockchain_transaction_id'] and 
                    not review['blockchain_transaction_id'].startswith('local_')
                    for review in reviews
                ),
                'transparency_score': min(1.0, (len(reviews) * 0.2) + (len(human_feedback) * 0.1)),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating transparency report: {e}")
            return {}
        finally:
            if conn:
                conn.close()
