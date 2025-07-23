import streamlit as st
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
from database import create_user, get_user_by_email, db

class AuthManager:
    def __init__(self):
        self.session_timeout = 24 * 60 * 60  # 24 hours in seconds
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hash_string: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hash_string.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == password_hash
        except:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?1?-?\.?\s?\(?(\d{3})\)?-?\.?\s?(\d{3})-?\.?\s?(\d{4})$'
        return re.match(pattern, phone) is not None

auth_manager = AuthManager()

def authenticate_user():
    """Handle user authentication"""
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    
    # Authentication modal
    with st.container():
        st.markdown("### Authentication")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            handle_login()
        
        with tab2:
            handle_signup()

def handle_login():
    """Handle user login"""
    with st.form("login_form"):
        st.markdown("#### Login to your account")
        
        # Login options
        login_method = st.selectbox("Login Method", ["Email", "Phone"])
        
        if login_method == "Email":
            email = st.text_input("Email Address", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("Login"):
                if email and password:
                    user = authenticate_email_password(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please fill in all fields")
        
        elif login_method == "Phone":
            phone = st.text_input("Phone Number", placeholder="+1234567890")
            
            if st.form_submit_button("Send OTP"):
                if phone and auth_manager.validate_phone(phone):
                    # In a real implementation, this would send an OTP via SMS
                    st.session_state.phone_otp = "123456"  # Demo OTP
                    st.success("OTP sent to your phone!")
                else:
                    st.error("Please enter a valid phone number")
            
            if 'phone_otp' in st.session_state:
                otp = st.text_input("Enter OTP", placeholder="123456")
                if st.form_submit_button("Verify OTP"):
                    if otp == st.session_state.phone_otp:
                        user = authenticate_phone_otp(phone, otp)
                        if user:
                            st.session_state.user = user
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Phone number not found")
                    else:
                        st.error("Invalid OTP")

def handle_signup():
    """Handle user registration"""
    with st.form("signup_form"):
        st.markdown("#### Create your account")
        
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email Address", placeholder="Enter your email")
        phone = st.text_input("Phone Number", placeholder="+1234567890")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Role selection
        role = st.selectbox("Account Type", [
            "reader", "creator", "journalist", "affiliate", "publisher"
        ])
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        if st.form_submit_button("Create Account"):
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all required fields")
            elif not auth_manager.validate_email(email):
                st.error("Please enter a valid email address")
            elif phone and not auth_manager.validate_phone(phone):
                st.error("Please enter a valid phone number")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif not terms_accepted:
                st.error("Please accept the Terms of Service and Privacy Policy")
            else:
                # Check if user already exists
                existing_user = get_user_by_email(email)
                if existing_user:
                    st.error("An account with this email already exists")
                else:
                    # Create new user
                    user_data = create_user(email, name, phone, role)
                    if user_data:
                        # Store password hash separately (in a real app, this would be in the database)
                        password_hash = auth_manager.hash_password(password)
                        store_password_hash(user_data['id'], password_hash)
                        
                        st.success("Account created successfully! Please login.")
                        st.session_state.auth_mode = 'login'
                        st.rerun()
                    else:
                        st.error("Error creating account. Please try again.")

def authenticate_email_password(email: str, password: str) -> Optional[Dict]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    
    # In a real implementation, password hash would be stored in database
    stored_hash = get_password_hash(user['id'])
    if stored_hash and auth_manager.verify_password(password, stored_hash):
        return user
    
    return None

def authenticate_phone_otp(phone: str, otp: str) -> Optional[Dict]:
    """Authenticate user with phone and OTP"""
    # In a real implementation, this would verify OTP against SMS service
    query = "SELECT * FROM users WHERE phone = %s"
    result = db.execute_query(query, (phone,))
    return dict(result[0]) if result else None

def get_current_user() -> Optional[Dict]:
    """Get current authenticated user"""
    if 'user' in st.session_state and st.session_state.user:
        # Check if session is still valid
        if 'last_activity' in st.session_state:
            last_activity = st.session_state.last_activity
            if datetime.now() - last_activity > timedelta(seconds=auth_manager.session_timeout):
                # Session expired
                st.session_state.user = None
                st.session_state.last_activity = None
                return None
        
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return st.session_state.user
    
    return None

def logout_user():
    """Logout current user"""
    st.session_state.user = None
    st.session_state.last_activity = None
    if 'phone_otp' in st.session_state:
        del st.session_state.phone_otp

def check_user_permission(permission: str) -> bool:
    """Check if current user has specific permission"""
    user = get_current_user()
    if not user:
        return False
    
    from config import USER_ROLES
    user_role = user.get('role', 'reader')
    permissions = USER_ROLES.get(user_role, {}).get('permissions', [])
    
    return permission in permissions or 'all' in permissions

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not get_current_user():
            st.warning("Please login to access this feature")
            authenticate_user()
            return None
        return func(*args, **kwargs)
    return wrapper

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_user_permission(permission):
                st.error("You don't have permission to access this feature")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Helper functions for password storage (in production, use proper database storage)
def store_password_hash(user_id: int, password_hash: str):
    """Store password hash (demo implementation)"""
    if 'password_hashes' not in st.session_state:
        st.session_state.password_hashes = {}
    st.session_state.password_hashes[user_id] = password_hash

def get_password_hash(user_id: int) -> Optional[str]:
    """Get password hash (demo implementation)"""
    if 'password_hashes' not in st.session_state:
        return None
    return st.session_state.password_hashes.get(user_id)
