import hashlib
import json
import time
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from database.connection import get_db_connection
from database.models import BlockchainRecord

class BlockchainService:
    def __init__(self):
        # Initialize with local blockchain simulation
        # In production, this would connect to a real blockchain network
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'transactions': [],
            'previous_hash': '0',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
    
    def calculate_hash(self, block: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def add_transaction(self, transaction: Dict[str, Any]) -> str:
        """Add a transaction to the pending transactions"""
        transaction_id = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()
        
        transaction['id'] = transaction_id
        transaction['timestamp'] = time.time()
        
        self.pending_transactions.append(transaction)
        return transaction_id
    
    def mine_block(self, mining_reward_address: str = None) -> Dict[str, Any]:
        """Mine a new block with pending transactions"""
        if not self.pending_transactions:
            return None
        
        # Add mining reward if address provided
        if mining_reward_address:
            reward_transaction = {
                'from': 'system',
                'to': mining_reward_address,
                'type': 'mining_reward',
                'amount': 10,
                'timestamp': time.time()
            }
            self.pending_transactions.append(reward_transaction)
        
        # Create new block
        new_block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': self.pending_transactions.copy(),
            'previous_hash': self.chain[-1]['hash'],
            'nonce': 0
        }
        
        # Simple proof of work (find hash starting with zeros)
        new_block['hash'] = self.mine_block_hash(new_block)
        
        # Add block to chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        # Save to database
        self._save_block_to_db(new_block)
        
        return new_block
    
    def mine_block_hash(self, block: Dict[str, Any], difficulty: int = 2) -> str:
        """Mine block hash with proof of work"""
        target = "0" * difficulty
        
        while True:
            hash_attempt = self.calculate_hash(block)
            
            if hash_attempt.startswith(target):
                return hash_attempt
            
            block['nonce'] += 1
    
    def record_article_review(self, article_id: int, reviewer_id: int, 
                             review_data: Dict[str, Any]) -> str:
        """Record article review on blockchain"""
        try:
            transaction = {
                'type': 'article_review',
                'article_id': article_id,
                'reviewer_id': reviewer_id,
                'review_data': review_data,
                'timestamp': time.time()
            }
            
            transaction_id = self.add_transaction(transaction)
            
            # Mine block if we have enough pending transactions
            if len(self.pending_transactions) >= 5:
                self.mine_block()
            
            return transaction_id
            
        except Exception as e:
            logging.error(f"Error recording article review: {str(e)}")
            return None
    
    def record_content_approval(self, content_id: int, approver_id: int, 
                               approval_data: Dict[str, Any]) -> str:
        """Record content approval on blockchain"""
        try:
            transaction = {
                'type': 'content_approval',
                'content_id': content_id,
                'approver_id': approver_id,
                'approval_data': approval_data,
                'timestamp': time.time()
            }
            
            transaction_id = self.add_transaction(transaction)
            
            # Mine block if we have enough pending transactions
            if len(self.pending_transactions) >= 5:
                self.mine_block()
            
            return transaction_id
            
        except Exception as e:
            logging.error(f"Error recording content approval: {str(e)}")
            return None
    
    def record_human_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Record human feedback on blockchain"""
        try:
            transaction = {
                'type': 'human_feedback',
                'feedback_data': feedback_data,
                'timestamp': time.time()
            }
            
            transaction_id = self.add_transaction(transaction)
            
            # Mine block if we have enough pending transactions
            if len(self.pending_transactions) >= 5:
                self.mine_block()
            
            return transaction_id
            
        except Exception as e:
            logging.error(f"Error recording human feedback: {str(e)}")
            return None
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        try:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # Check if current block's hash is valid
                if current_block['hash'] != self.calculate_hash(current_block):
                    return False
                
                # Check if current block's previous hash matches
                if current_block['previous_hash'] != previous_block['hash']:
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error verifying blockchain: {str(e)}")
            return False
    
    def get_transaction_history(self, record_type: str = None, 
                               record_id: int = None) -> List[Dict[str, Any]]:
        """Get transaction history from blockchain"""
        try:
            transactions = []
            
            for block in self.chain:
                for transaction in block.get('transactions', []):
                    if record_type and transaction.get('type') != record_type:
                        continue
                    
                    if record_id and transaction.get('article_id') != record_id:
                        continue
                    
                    transaction['block_index'] = block['index']
                    transaction['block_hash'] = block['hash']
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logging.error(f"Error getting transaction history: {str(e)}")
            return []
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Dict[str, Any]]:
        """Get block by hash"""
        try:
            for block in self.chain:
                if block['hash'] == block_hash:
                    return block
            return None
            
        except Exception as e:
            logging.error(f"Error getting block by hash: {str(e)}")
            return None
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        try:
            total_blocks = len(self.chain)
            total_transactions = sum(len(block.get('transactions', [])) for block in self.chain)
            
            return {
                'total_blocks': total_blocks,
                'total_transactions': total_transactions,
                'chain_valid': self.verify_chain(),
                'pending_transactions': len(self.pending_transactions),
                'latest_block_hash': self.chain[-1]['hash'] if self.chain else None
            }
            
        except Exception as e:
            logging.error(f"Error getting chain stats: {str(e)}")
            return {}
    
    def _save_block_to_db(self, block: Dict[str, Any]):
        """Save block to database"""
        try:
            db = get_db_connection()
            
            record = BlockchainRecord(
                record_type='block',
                record_id=str(block['index']),
                hash_value=block['hash'],
                previous_hash=block['previous_hash'],
                data=block
            )
            
            db.add(record)
            db.commit()
            
        except Exception as e:
            logging.error(f"Error saving block to database: {str(e)}")
            db.rollback()
