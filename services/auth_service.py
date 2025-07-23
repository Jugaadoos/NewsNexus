import hashlib
import secrets
import re
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from database.connection import get_db_connection
from database.models import User, UserRole
import requests

class AuthService:
    def __init__(self):
        self.otp_storage = {}  # In production, use Redis or database
        self.session_storage = {}  # In production, use proper session management
    
    def register_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Register a new user"""
        try:
            db = get_db_connection()
            
            # Validate required fields
            required_fields = ['email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not user_data.get(field):
                    return None
            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if existing_user:
                return None
            
            # Validate email format
            if not self._is_valid_email(user_data['email']):
                return None
            
            # Hash password
            password_hash = self._hash_password(user_data['password'])
            
            # Create user
            user = User(
                email=user_data['email'],
                phone=user_data.get('phone'),
                password_hash=password_hash,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=UserRole(user_data.get('role', 'READER').upper())
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return self._user_to_dict(user)
            
        except Exception as e:
            logging.error(f"Error registering user: {str(e)}")
            db.rollback()
            return None
    
    def login_email(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Login with email and password"""
        try:
            db = get_db_connection()
            
            user = db.query(User).filter(
                User.email == email,
                User.is_active == True
            ).first()
            
            if not user:
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                return None
            
            # Create session
            session_id = self._create_session(user)
            
            user_dict = self._user_to_dict(user)
            user_dict['session_id'] = session_id
            
            return user_dict
            
        except Exception as e:
            logging.error(f"Error logging in user: {str(e)}")
            return None
    
    def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number"""
        try:
            # Generate OTP
            otp = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
            
            # Store OTP with expiration
            self.otp_storage[phone] = {
                'otp': otp,
                'expires_at': datetime.now() + timedelta(minutes=5)
            }
            
            # In production, integrate with SMS service (Twilio, etc.)
            # For now, log the OTP
            logging.info(f"OTP for {phone}: {otp}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error sending OTP: {str(e)}")
            return False
    
    def verify_otp(self, phone: str, otp: str) -> Optional[Dict[str, Any]]:
        """Verify OTP and login/register user"""
        try:
            stored_otp = self.otp_storage.get(phone)
            
            if not stored_otp:
                return None
            
            if datetime.now() > stored_otp['expires_at']:
                del self.otp_storage[phone]
                return None
            
            if stored_otp['otp'] != otp:
                return None
            
            # OTP verified, clean up
            del self.otp_storage[phone]
            
            # Find or create user
            db = get_db_connection()
            user = db.query(User).filter(User.phone == phone).first()
            
            if not user:
                # Create new user
                user = User(
                    phone=phone,
                    first_name='User',
                    last_name=phone[-4:],  # Use last 4 digits
                    role=UserRole.READER
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create session
            session_id = self._create_session(user)
            
            user_dict = self._user_to_dict(user)
            user_dict['session_id'] = session_id
            
            return user_dict
            
        except Exception as e:
            logging.error(f"Error verifying OTP: {str(e)}")
            return None
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify user session"""
        try:
            session = self.session_storage.get(session_id)
            
            if not session:
                return None
            
            if datetime.now() > session['expires_at']:
                del self.session_storage[session_id]
                return None
            
            # Refresh session
            session['expires_at'] = datetime.now() + timedelta(hours=24)
            
            return session['user']
            
        except Exception as e:
            logging.error(f"Error verifying session: {str(e)}")
            return None
    
    def logout(self, session_id: str) -> bool:
        """Logout user"""
        try:
            if session_id in self.session_storage:
                del self.session_storage[session_id]
            return True
            
        except Exception as e:
            logging.error(f"Error logging out: {str(e)}")
            return False
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            db = get_db_connection()
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone', 'preferences', 'location_data']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            db.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error updating profile: {str(e)}")
            db.rollback()
            return False
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            db = get_db_connection()
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                return False
            
            # Set new password
            user.password_hash = self._hash_password(new_password)
            db.commit()
            
            return True
            
        except Exception as e:
            logging.error(f"Error changing password: {str(e)}")
            db.rollback()
            return False
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            db = get_db_connection()
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token (in production, use database)
            self.session_storage[f"reset_{reset_token}"] = {
                'user_id': user.id,
                'expires_at': datetime.now() + timedelta(hours=1)
            }
            
            # In production, send email with reset link
            logging.info(f"Password reset token for {email}: {reset_token}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error resetting password: {str(e)}")
            return False
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions based on role"""
        try:
            db = get_db_connection()
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            role_permissions = {
                UserRole.READER: ['read_articles', 'save_articles', 'comment'],
                UserRole.REVIEWER: ['read_articles', 'save_articles', 'comment', 'review_articles'],
                UserRole.EDITOR: ['read_articles', 'save_articles', 'comment', 'review_articles', 'edit_articles', 'publish_articles'],
                UserRole.CREATOR: ['read_articles', 'save_articles', 'comment', 'create_articles', 'edit_own_articles'],
                UserRole.JOURNALIST: ['read_articles', 'save_articles', 'comment', 'create_articles', 'edit_own_articles', 'publish_articles'],
                UserRole.PUBLISHING_PARTNER: ['read_articles', 'save_articles', 'comment', 'create_articles', 'edit_own_articles', 'publish_articles', 'manage_partnership'],
                UserRole.AFFILIATE: ['read_articles', 'save_articles', 'comment', 'manage_affiliate_products', 'view_affiliate_analytics'],
                UserRole.ADMIN: ['all_permissions']
            }
            
            return role_permissions.get(user.role, [])
            
        except Exception as e:
            logging.error(f"Error getting permissions: {str(e)}")
            return []
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except:
            return False
    
    def _create_session(self, user: User) -> str:
        """Create user session"""
        session_id = secrets.token_urlsafe(32)
        
        self.session_storage[session_id] = {
            'user': self._user_to_dict(user),
            'expires_at': datetime.now() + timedelta(hours=24)
        }
        
        return session_id
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User model to dictionary"""
        return {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'name': f"{user.first_name} {user.last_name}",
            'role': user.role.value,
            'subscription_tier': user.subscription_tier.value,
            'preferences': user.preferences or {},
            'location_data': user.location_data or {},
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
