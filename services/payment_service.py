import stripe
import paypal
import os
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from database.connection import get_db_connection
from database.models import User, Subscription, SubscriptionTier

class PaymentService:
    def __init__(self):
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Initialize PayPal (placeholder - would need proper setup)
        self.paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.paypal_client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        
        # Subscription pricing
        self.subscription_prices = {
            'basic': {'monthly': 9.99, 'yearly': 99.99},
            'premium': {'monthly': 19.99, 'yearly': 199.99},
            'enterprise': {'monthly': 49.99, 'yearly': 499.99}
        }
    
    def create_subscription(self, user_id: int, tier: str, billing_cycle: str = 'monthly') -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            db = get_db_connection()
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get price
            price = self.subscription_prices.get(tier, {}).get(billing_cycle)
            if not price:
                return {'success': False, 'error': 'Invalid subscription tier or billing cycle'}
            
            # Create Stripe subscription
            stripe_subscription = self._create_stripe_subscription(user, tier, billing_cycle, price)
            
            if stripe_subscription:
                # Save subscription to database
                subscription = Subscription(
                    user_id=user_id,
                    tier=SubscriptionTier(tier.upper()),
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
                    payment_method='stripe',
                    amount=price,
                    currency='USD',
                    is_active=True
                )
                
                db.add(subscription)
                
                # Update user subscription tier
                user.subscription_tier = SubscriptionTier(tier.upper())
                
                db.commit()
                
                return {
                    'success': True,
                    'subscription_id': subscription.id,
                    'stripe_subscription_id': stripe_subscription.id
                }
            
            return {'success': False, 'error': 'Failed to create Stripe subscription'}
            
        except Exception as e:
            logging.error(f"Error creating subscription: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_stripe_subscription(self, user: User, tier: str, billing_cycle: str, amount: float) -> Optional[Any]:
        """Create Stripe subscription"""
        try:
            # Create customer if not exists
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={'user_id': user.id}
            )
            
            # Create price
            price = stripe.Price.create(
                unit_amount=int(amount * 100),  # Convert to cents
                currency='usd',
                recurring={
                    'interval': 'month' if billing_cycle == 'monthly' else 'year'
                },
                product_data={
                    'name': f'{tier.title()} Subscription'
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price.id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            
            return subscription
            
        except Exception as e:
            logging.error(f"Error creating Stripe subscription: {str(e)}")
            return None
    
    def cancel_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            db = get_db_connection()
            subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            
            if not subscription:
                return {'success': False, 'error': 'Subscription not found'}
            
            # Cancel on Stripe
            if subscription.payment_method == 'stripe':
                # Would need to store Stripe subscription ID
                pass
            
            # Update subscription status
            subscription.is_active = False
            subscription.end_date = datetime.now()
            
            # Update user tier
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_tier = SubscriptionTier.FREE
            
            db.commit()
            
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error canceling subscription: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process one-time payment"""
        try:
            amount = payment_data.get('amount')
            currency = payment_data.get('currency', 'usd')
            payment_method = payment_data.get('payment_method')
            
            if payment_method == 'stripe':
                return self._process_stripe_payment(payment_data)
            elif payment_method == 'paypal':
                return self._process_paypal_payment(payment_data)
            else:
                return {'success': False, 'error': 'Unsupported payment method'}
                
        except Exception as e:
            logging.error(f"Error processing payment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_stripe_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Stripe payment"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment_data['amount'] * 100),  # Convert to cents
                currency=payment_data.get('currency', 'usd'),
                payment_method_types=['card'],
                metadata=payment_data.get('metadata', {})
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
            
        except Exception as e:
            logging.error(f"Error processing Stripe payment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_paypal_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayPal payment"""
        try:
            # PayPal payment processing would go here
            # This is a placeholder implementation
            return {
                'success': True,
                'paypal_order_id': 'PAYPAL_ORDER_ID_PLACEHOLDER'
            }
            
        except Exception as e:
            logging.error(f"Error processing PayPal payment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """Get user's subscription status"""
        try:
            db = get_db_connection()
            
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).first()
            
            if subscription:
                return {
                    'has_subscription': True,
                    'tier': subscription.tier.value,
                    'start_date': subscription.start_date.isoformat(),
                    'end_date': subscription.end_date.isoformat(),
                    'is_active': subscription.is_active
                }
            
            return {'has_subscription': False}
            
        except Exception as e:
            logging.error(f"Error getting subscription status: {str(e)}")
            return {'has_subscription': False, 'error': str(e)}
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get subscription pricing information"""
        return {
            'tiers': self.subscription_prices,
            'currency': 'USD',
            'features': {
                'basic': [
                    'Ad-free browsing',
                    'Save articles',
                    'Basic analytics'
                ],
                'premium': [
                    'All Basic features',
                    'Advanced analytics',
                    'Priority support',
                    'Custom themes'
                ],
                'enterprise': [
                    'All Premium features',
                    'API access',
                    'White-label options',
                    'Dedicated support'
                ]
            }
        }
    
    def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """Handle payment webhook"""
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
            
            # Handle different event types
            if event['type'] == 'payment_intent.succeeded':
                self._handle_payment_success(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                self._handle_payment_failure(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                self._handle_subscription_cancellation(event['data']['object'])
            
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error handling webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_success(self, payment_intent: Dict[str, Any]):
        """Handle successful payment"""
        try:
            # Update subscription or payment record
            logging.info(f"Payment succeeded: {payment_intent['id']}")
            
        except Exception as e:
            logging.error(f"Error handling payment success: {str(e)}")
    
    def _handle_payment_failure(self, invoice: Dict[str, Any]):
        """Handle failed payment"""
        try:
            # Handle subscription payment failure
            logging.warning(f"Payment failed: {invoice['id']}")
            
        except Exception as e:
            logging.error(f"Error handling payment failure: {str(e)}")
    
    def _handle_subscription_cancellation(self, subscription: Dict[str, Any]):
        """Handle subscription cancellation"""
        try:
            # Update subscription status
            logging.info(f"Subscription cancelled: {subscription['id']}")
            
        except Exception as e:
            logging.error(f"Error handling subscription cancellation: {str(e)}")
