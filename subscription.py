import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from config import STRIPE_SECRET_KEY, SUBSCRIPTION_TIERS
from database import create_subscription, get_active_subscription, db
import streamlit as st

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

class SubscriptionManager:
    def __init__(self):
        self.tiers = SUBSCRIPTION_TIERS
        self.stripe_products = {}
        self.init_stripe_products()
    
    def init_stripe_products(self):
        """Initialize Stripe products for subscription tiers"""
        try:
            # In a real implementation, these would be created in Stripe dashboard
            self.stripe_products = {
                "basic": {
                    "price_id": "price_basic_monthly",
                    "product_id": "prod_basic"
                },
                "premium": {
                    "price_id": "price_premium_monthly",
                    "product_id": "prod_premium"
                },
                "enterprise": {
                    "price_id": "price_enterprise_monthly",
                    "product_id": "prod_enterprise"
                }
            }
        except Exception as e:
            print(f"Error initializing Stripe products: {e}")
    
    def get_subscription_tiers(self) -> Dict:
        """Get available subscription tiers"""
        return self.tiers
    
    def create_payment_intent(self, amount: float, currency: str = "usd") -> Optional[Dict]:
        """Create Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id
            }
        except Exception as e:
            print(f"Error creating payment intent: {e}")
            return None
    
    def create_subscription_checkout(self, user_id: int, tier: str) -> Optional[str]:
        """Create Stripe checkout session for subscription"""
        try:
            tier_data = self.tiers.get(tier)
            if not tier_data:
                return None
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{tier_data["name"]} Subscription',
                            'description': ', '.join(tier_data["features"]),
                        },
                        'unit_amount': int(tier_data["price"] * 100),
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://your-domain.com/subscription/success',
                cancel_url='https://your-domain.com/subscription/cancel',
                metadata={
                    'user_id': str(user_id),
                    'tier': tier
                }
            )
            
            return checkout_session.url
            
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None
    
    def process_subscription_payment(self, user_id: int, tier: str, payment_data: Dict) -> Optional[Dict]:
        """Process subscription payment"""
        try:
            tier_data = self.tiers.get(tier)
            if not tier_data:
                return None
            
            # Create subscription in database
            subscription = create_subscription(user_id, tier, {
                "method": "stripe",
                "amount": tier_data["price"],
                "currency": "USD",
                "payment_intent_id": payment_data.get("payment_intent_id")
            })
            
            return subscription
            
        except Exception as e:
            print(f"Error processing subscription payment: {e}")
            return None
    
    def cancel_subscription(self, user_id: int) -> bool:
        """Cancel user subscription"""
        try:
            query = """
            UPDATE subscriptions 
            SET status = 'cancelled', expiry_date = CURRENT_TIMESTAMP
            WHERE user_id = %s AND status = 'active'
            """
            
            result = db.execute_query(query, (user_id,), fetch=False)
            
            if result:
                # Update user tier
                update_user_query = "UPDATE users SET subscription_tier = 'free' WHERE id = %s"
                db.execute_query(update_user_query, (user_id,), fetch=False)
                
            return result
            
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            return False
    
    def get_subscription_status(self, user_id: int) -> Dict:
        """Get user subscription status"""
        try:
            subscription = get_active_subscription(user_id)
            
            if subscription:
                return {
                    "active": True,
                    "tier": subscription["tier"],
                    "expires_at": subscription["expiry_date"],
                    "premium": subscription["tier"] != "free",
                    "features": self.tiers.get(subscription["tier"], {}).get("features", [])
                }
            
            return {
                "active": False,
                "tier": "free",
                "expires_at": None,
                "premium": False,
                "features": self.tiers.get("free", {}).get("features", [])
            }
            
        except Exception as e:
            print(f"Error getting subscription status: {e}")
            return {"active": False, "tier": "free", "premium": False, "features": []}
    
    def get_subscription_analytics(self, date_range: int = 30) -> Dict:
        """Get subscription analytics"""
        try:
            query = """
            SELECT 
                tier,
                COUNT(*) as subscriber_count,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_revenue_per_user
            FROM subscriptions
            WHERE subscription_date >= CURRENT_DATE - INTERVAL '%s days'
            AND status = 'active'
            GROUP BY tier
            ORDER BY subscriber_count DESC
            """
            
            result = db.execute_query(query, (date_range,))
            
            if result:
                return {
                    "tiers": [
                        {
                            "tier": row["tier"],
                            "subscriber_count": row["subscriber_count"],
                            "total_revenue": float(row["total_revenue"]) if row["total_revenue"] else 0,
                            "avg_revenue_per_user": float(row["avg_revenue_per_user"]) if row["avg_revenue_per_user"] else 0
                        }
                        for row in result
                    ]
                }
            
            return {"tiers": []}
            
        except Exception as e:
            print(f"Error getting subscription analytics: {e}")
            return {"tiers": []}

# Initialize subscription manager
subscription_manager = SubscriptionManager()

def display_subscription_plans():
    """Display subscription plans in Streamlit"""
    st.markdown("## Choose Your Plan")
    
    tiers = subscription_manager.get_subscription_tiers()
    
    cols = st.columns(len(tiers))
    
    for idx, (tier_key, tier_data) in enumerate(tiers.items()):
        with cols[idx]:
            # Plan card
            st.markdown(f"""
            <div style="
                border: 2px solid {'#1A73E8' if tier_key == 'premium' else '#e0e0e0'};
                border-radius: 12px;
                padding: 24px;
                margin: 16px 0;
                background: {'#f8f9ff' if tier_key == 'premium' else '#ffffff'};
                text-align: center;
                position: relative;
            ">
                {'<div style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: #1A73E8; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">POPULAR</div>' if tier_key == 'premium' else ''}
                
                <h3 style="margin: 0 0 16px 0; color: #333;">
                    {tier_data["name"]}
                </h3>
                
                <div style="margin: 16px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #1A73E8;">
                        ${tier_data["price"]}
                    </span>
                    <span style="color: #666; font-size: 14px;">
                        /month
                    </span>
                </div>
                
                <ul style="text-align: left; margin: 24px 0; padding-left: 0; list-style: none;">
                    {''.join([f'<li style="margin: 8px 0; padding-left: 20px; position: relative;">✓ {feature}</li>' for feature in tier_data["features"]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Subscribe button
            if tier_key != "free":
                if st.button(f"Subscribe to {tier_data['name']}", key=f"subscribe_{tier_key}"):
                    if 'user' in st.session_state and st.session_state.user:
                        process_subscription_purchase(st.session_state.user['id'], tier_key, tier_data)
                    else:
                        st.warning("Please login to subscribe")

def process_subscription_purchase(user_id: int, tier: str, tier_data: Dict):
    """Process subscription purchase"""
    st.markdown("### Complete Your Purchase")
    
    # Display order summary
    st.markdown(f"""
    **Order Summary:**
    - Plan: {tier_data['name']}
    - Price: ${tier_data['price']}/month
    - Billing: Monthly
    """)
    
    # Payment form
    with st.form("payment_form"):
        st.markdown("#### Payment Information")
        
        # Demo payment form (in production, use Stripe Elements)
        card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
        col1, col2 = st.columns(2)
        
        with col1:
            expiry = st.text_input("Expiry Date", placeholder="MM/YY")
        
        with col2:
            cvv = st.text_input("CVV", placeholder="123")
        
        billing_address = st.text_input("Billing Address")
        
        if st.form_submit_button("Complete Purchase"):
            # In production, this would use Stripe's secure payment processing
            if card_number and expiry and cvv:
                # Create subscription
                subscription = subscription_manager.process_subscription_payment(
                    user_id, 
                    tier, 
                    {
                        "payment_method": "card",
                        "card_number": card_number[-4:],  # Store only last 4 digits
                        "payment_intent_id": f"pi_demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    }
                )
                
                if subscription:
                    st.success("Subscription activated successfully!")
                    st.balloons()
                    
                    # Update session state
                    if 'user' in st.session_state:
                        st.session_state.user['subscription_tier'] = tier
                    
                    st.rerun()
                else:
                    st.error("Payment failed. Please try again.")
            else:
                st.error("Please fill in all payment fields")

def display_paywall(content_type: str = "article"):
    """Display paywall for premium content"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1A73E8, #34A853);
        color: white;
        padding: 32px;
        border-radius: 12px;
        text-align: center;
        margin: 24px 0;
    ">
        <h3 style="margin: 0 0 16px 0;">Premium Content</h3>
        <p style="margin: 0 0 24px 0; font-size: 18px;">
            Unlock unlimited access to premium {content_type}s and exclusive content
        </p>
        <div style="margin: 16px 0;">
            <span style="font-size: 24px; font-weight: bold;">
                Start from $9.99/month
            </span>
        </div>
        <p style="margin: 16px 0; font-size: 14px; opacity: 0.9;">
            Cancel anytime • No long-term contracts • Premium support
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("View Subscription Plans", key="paywall_cta"):
        display_subscription_plans()

def check_subscription_status(user: Dict = None) -> Dict:
    """Check user subscription status"""
    if not user:
        return {"active": False, "tier": "free", "premium": False, "features": []}
    
    return subscription_manager.get_subscription_status(user['id'])

def get_subscription_analytics(date_range: int = 30) -> Dict:
    """Get subscription analytics"""
    return subscription_manager.get_subscription_analytics(date_range)
