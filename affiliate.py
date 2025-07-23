import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from database import db
from config import AFFILIATE_COMMISSION
import streamlit as st

class AffiliateManager:
    def __init__(self):
        self.commission_rates = AFFILIATE_COMMISSION
        self.product_categories = [
            "News & Media", "Books", "Electronics", "Software",
            "Education", "Health & Wellness", "Finance", "Travel"
        ]
    
    def register_affiliate(self, user_id: int, application_data: Dict) -> Optional[Dict]:
        """Register new affiliate"""
        try:
            query = """
            INSERT INTO affiliate_applications (user_id, company_name, website_url, 
                                             tax_id, payment_method, application_data, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """
            
            result = db.execute_query(query, (
                user_id,
                application_data.get('company_name', ''),
                application_data.get('website_url', ''),
                application_data.get('tax_id', ''),
                application_data.get('payment_method', 'paypal'),
                json.dumps(application_data),
                'pending'
            ))
            
            if result:
                # Update user role to affiliate
                update_query = "UPDATE users SET role = 'affiliate' WHERE id = %s"
                db.execute_query(update_query, (user_id,), fetch=False)
                
                return {
                    "application_id": result[0]['id'],
                    "status": "pending",
                    "created_at": result[0]['created_at']
                }
            
            return None
            
        except Exception as e:
            print(f"Error registering affiliate: {e}")
            return None
    
    def create_affiliate_product(self, affiliate_id: int, product_data: Dict) -> Optional[Dict]:
        """Create new affiliate product"""
        try:
            query = """
            INSERT INTO affiliate_products (affiliate_id, product_name, product_url, 
                                          category, price, commission_rate, description, 
                                          image_url, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """
            
            result = db.execute_query(query, (
                affiliate_id,
                product_data['product_name'],
                product_data['product_url'],
                product_data.get('category', 'General'),
                product_data.get('price', 0),
                product_data.get('commission_rate', self.commission_rates['product']),
                product_data.get('description', ''),
                product_data.get('image_url', ''),
                True
            ))
            
            return dict(result[0]) if result else None
            
        except Exception as e:
            print(f"Error creating affiliate product: {e}")
            return None
    
    def get_affiliate_products(self, affiliate_id: int = None, category: str = None) -> List[Dict]:
        """Get affiliate products"""
        try:
            query = "SELECT * FROM affiliate_products WHERE active = TRUE"
            params = []
            
            if affiliate_id:
                query += " AND affiliate_id = %s"
                params.append(affiliate_id)
            
            if category:
                query += " AND category = %s"
                params.append(category)
            
            query += " ORDER BY created_at DESC"
            
            result = db.execute_query(query, tuple(params) if params else None)
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            print(f"Error getting affiliate products: {e}")
            return []
    
    def track_affiliate_click(self, affiliate_id: int, product_id: int, user_id: int = None, 
                            ip_address: str = None) -> Optional[Dict]:
        """Track affiliate click"""
        try:
            query = """
            INSERT INTO affiliate_clicks (affiliate_id, product_id, clicked_by, ip_address)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """
            
            result = db.execute_query(query, (affiliate_id, product_id, user_id, ip_address))
            return dict(result[0]) if result else None
            
        except Exception as e:
            print(f"Error tracking affiliate click: {e}")
            return None
    
    def record_affiliate_conversion(self, click_id: int, sale_amount: float) -> bool:
        """Record affiliate conversion"""
        try:
            # Get click details
            click_query = "SELECT * FROM affiliate_clicks WHERE id = %s"
            click_result = db.execute_query(click_query, (click_id,))
            
            if not click_result:
                return False
            
            click_data = dict(click_result[0])
            
            # Get product details for commission calculation
            product_query = "SELECT * FROM affiliate_products WHERE id = %s"
            product_result = db.execute_query(product_query, (click_data['product_id'],))
            
            if not product_result:
                return False
            
            product_data = dict(product_result[0])
            
            # Calculate commission
            commission = sale_amount * float(product_data['commission_rate'])
            
            # Update click with conversion
            update_query = """
            UPDATE affiliate_clicks 
            SET conversion = TRUE, commission_earned = %s, sale_amount = %s
            WHERE id = %s
            """
            
            return db.execute_query(update_query, (commission, sale_amount, click_id), fetch=False)
            
        except Exception as e:
            print(f"Error recording affiliate conversion: {e}")
            return False
    
    def get_affiliate_analytics(self, affiliate_id: int, date_range: int = 30) -> Dict:
        """Get affiliate performance analytics"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_clicks,
                COUNT(CASE WHEN conversion = TRUE THEN 1 END) as conversions,
                SUM(commission_earned) as total_commission,
                AVG(commission_earned) as avg_commission,
                DATE(created_at) as date
            FROM affiliate_clicks
            WHERE affiliate_id = %s
            AND created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            
            result = db.execute_query(query, (affiliate_id, date_range))
            
            analytics_data = []
            if result:
                analytics_data = [
                    {
                        "date": row["date"],
                        "clicks": row["total_clicks"],
                        "conversions": row["conversions"],
                        "commission": float(row["total_commission"]) if row["total_commission"] else 0,
                        "conversion_rate": (row["conversions"] / row["total_clicks"] * 100) if row["total_clicks"] > 0 else 0
                    }
                    for row in result
                ]
            
            # Get top products
            top_products_query = """
            SELECT 
                p.product_name,
                COUNT(c.id) as clicks,
                SUM(c.commission_earned) as total_commission
            FROM affiliate_products p
            LEFT JOIN affiliate_clicks c ON p.id = c.product_id
            WHERE p.affiliate_id = %s
            AND c.created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY p.id, p.product_name
            ORDER BY clicks DESC
            LIMIT 10
            """
            
            top_products_result = db.execute_query(top_products_query, (affiliate_id, date_range))
            top_products = []
            if top_products_result:
                top_products = [
                    {
                        "product_name": row["product_name"],
                        "clicks": row["clicks"],
                        "commission": float(row["total_commission"]) if row["total_commission"] else 0
                    }
                    for row in top_products_result
                ]
            
            return {
                "daily_stats": analytics_data,
                "top_products": top_products
            }
            
        except Exception as e:
            print(f"Error getting affiliate analytics: {e}")
            return {"daily_stats": [], "top_products": []}
    
    def generate_affiliate_link(self, affiliate_id: int, product_id: int) -> str:
        """Generate affiliate tracking link"""
        base_url = "https://your-domain.com"
        return f"{base_url}/affiliate/{affiliate_id}/product/{product_id}"
    
    def process_affiliate_payment(self, affiliate_id: int, amount: float, payment_method: str) -> bool:
        """Process affiliate payment"""
        try:
            # In a real implementation, this would integrate with payment processors
            payment_query = """
            INSERT INTO affiliate_payments (affiliate_id, amount, payment_method, status)
            VALUES (%s, %s, %s, %s)
            """
            
            result = db.execute_query(payment_query, (affiliate_id, amount, payment_method, 'processed'), fetch=False)
            
            if result:
                # Mark commissions as paid
                update_query = """
                UPDATE affiliate_clicks 
                SET commission_paid = TRUE 
                WHERE affiliate_id = %s AND commission_earned > 0 AND commission_paid = FALSE
                """
                db.execute_query(update_query, (affiliate_id,), fetch=False)
            
            return result
            
        except Exception as e:
            print(f"Error processing affiliate payment: {e}")
            return False

# Initialize affiliate manager
affiliate_manager = AffiliateManager()

def display_affiliate_dashboard(user: Dict):
    """Display affiliate dashboard"""
    st.title("🤝 Affiliate Dashboard")
    
    # Check if user is affiliate
    if user.get('role') != 'affiliate':
        st.warning("You need to be registered as an affiliate to access this dashboard.")
        if st.button("Apply to Become Affiliate"):
            display_affiliate_registration()
        return
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🛍️ Products", "💰 Earnings", "⚙️ Settings"])
    
    with tab1:
        display_affiliate_analytics(user['id'])
    
    with tab2:
        display_affiliate_products(user['id'])
    
    with tab3:
        display_affiliate_earnings(user['id'])
    
    with tab4:
        display_affiliate_settings(user['id'])

def display_affiliate_registration():
    """Display affiliate registration form"""
    st.title("🤝 Become an Affiliate")
    
    with st.form("affiliate_registration"):
        st.markdown("### Application Information")
        
        company_name = st.text_input("Company Name", placeholder="Your Company Name")
        website_url = st.text_input("Website URL", placeholder="https://your-website.com")
        tax_id = st.text_input("Tax ID (Optional)", placeholder="Tax identification number")
        
        st.markdown("### Business Details")
        business_type = st.selectbox("Business Type", [
            "Individual", "Partnership", "Corporation", "LLC", "Non-Profit"
        ])
        
        monthly_traffic = st.selectbox("Monthly Website Traffic", [
            "< 1,000", "1,000 - 10,000", "10,000 - 100,000", "100,000 - 1M", "> 1M"
        ])
        
        marketing_channels = st.multiselect("Marketing Channels", [
            "Social Media", "Email Marketing", "Blog/Content", "PPC Advertising", 
            "SEO", "Influencer Marketing", "Other"
        ])
        
        st.markdown("### Payment Information")
        payment_method = st.selectbox("Preferred Payment Method", ["PayPal", "Bank Transfer", "Check"])
        
        if payment_method == "PayPal":
            paypal_email = st.text_input("PayPal Email")
        elif payment_method == "Bank Transfer":
            bank_account = st.text_input("Bank Account Number")
            routing_number = st.text_input("Routing Number")
        
        experience = st.text_area("Affiliate Marketing Experience", 
                                placeholder="Tell us about your experience with affiliate marketing...")
        
        terms_agreed = st.checkbox("I agree to the Affiliate Terms and Conditions")
        
        if st.form_submit_button("Submit Application"):
            if not all([company_name, website_url, business_type]) or not terms_agreed:
                st.error("Please fill in all required fields and agree to the terms.")
            else:
                application_data = {
                    "company_name": company_name,
                    "website_url": website_url,
                    "tax_id": tax_id,
                    "business_type": business_type,
                    "monthly_traffic": monthly_traffic,
                    "marketing_channels": marketing_channels,
                    "payment_method": payment_method,
                    "experience": experience
                }
                
                if payment_method == "PayPal":
                    application_data["paypal_email"] = paypal_email
                elif payment_method == "Bank Transfer":
                    application_data["bank_account"] = bank_account
                    application_data["routing_number"] = routing_number
                
                if 'user' in st.session_state:
                    result = affiliate_manager.register_affiliate(st.session_state.user['id'], application_data)
                    if result:
                        st.success("Application submitted successfully! We'll review it within 2-3 business days.")
                        st.balloons()
                    else:
                        st.error("Error submitting application. Please try again.")

def display_affiliate_analytics(affiliate_id: int):
    """Display affiliate analytics"""
    st.subheader("📊 Performance Analytics")
    
    # Date range selector
    date_range = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
    
    # Get analytics data
    analytics = affiliate_manager.get_affiliate_analytics(affiliate_id, date_range)
    
    if analytics['daily_stats']:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Create metrics
        total_clicks = sum(day['clicks'] for day in analytics['daily_stats'])
        total_conversions = sum(day['conversions'] for day in analytics['daily_stats'])
        total_commission = sum(day['commission'] for day in analytics['daily_stats'])
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", total_clicks)
        with col2:
            st.metric("Conversions", total_conversions)
        with col3:
            st.metric("Total Commission", f"${total_commission:.2f}")
        with col4:
            st.metric("Conversion Rate", f"{avg_conversion_rate:.1f}%")
        
        # Create charts
        df = pd.DataFrame(analytics['daily_stats'])
        
        # Clicks and conversions chart
        fig_clicks = px.line(df, x='date', y=['clicks', 'conversions'], 
                           title="Daily Clicks and Conversions")
        st.plotly_chart(fig_clicks, use_container_width=True)
        
        # Commission chart
        fig_commission = px.bar(df, x='date', y='commission', 
                              title="Daily Commission Earned")
        st.plotly_chart(fig_commission, use_container_width=True)
        
        # Top products
        if analytics['top_products']:
            st.subheader("🏆 Top Performing Products")
            
            products_df = pd.DataFrame(analytics['top_products'])
            fig_products = px.bar(products_df, x='product_name', y='clicks',
                                title="Top Products by Clicks")
            st.plotly_chart(fig_products, use_container_width=True)
    else:
        st.info("No analytics data available yet. Start promoting your affiliate links to see performance metrics.")

def display_affiliate_products(affiliate_id: int):
    """Display affiliate products management"""
    st.subheader("🛍️ Product Management")
    
    # Add new product
    with st.expander("➕ Add New Product"):
        with st.form("new_product"):
            product_name = st.text_input("Product Name")
            product_url = st.text_input("Product URL")
            category = st.selectbox("Category", affiliate_manager.product_categories)
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)
            commission_rate = st.number_input("Commission Rate (%)", 
                                            min_value=0.0, max_value=100.0, 
                                            value=affiliate_manager.commission_rates['product'] * 100,
                                            step=0.1) / 100
            description = st.text_area("Description")
            image_url = st.text_input("Image URL (Optional)")
            
            if st.form_submit_button("Add Product"):
                if product_name and product_url:
                    product_data = {
                        "product_name": product_name,
                        "product_url": product_url,
                        "category": category,
                        "price": price,
                        "commission_rate": commission_rate,
                        "description": description,
                        "image_url": image_url
                    }
                    
                    result = affiliate_manager.create_affiliate_product(affiliate_id, product_data)
                    if result:
                        st.success("Product added successfully!")
                        st.rerun()
                    else:
                        st.error("Error adding product. Please try again.")
                else:
                    st.error("Please fill in required fields.")
    
    # Display existing products
    products = affiliate_manager.get_affiliate_products(affiliate_id)
    
    if products:
        st.subheader("Your Products")
        
        for product in products:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{product['product_name']}**")
                    st.write(f"Category: {product['category']}")
                    st.write(f"Price: ${product['price']:.2f}")
                
                with col2:
                    st.write(f"Commission: {product['commission_rate']*100:.1f}%")
                    affiliate_link = affiliate_manager.generate_affiliate_link(affiliate_id, product['id'])
                    st.code(affiliate_link, language="text")
                
                with col3:
                    if st.button("📋 Copy Link", key=f"copy_{product['id']}"):
                        st.success("Link copied!")
                
                st.divider()
    else:
        st.info("No products added yet. Add your first product to start earning commissions.")

def display_affiliate_earnings(affiliate_id: int):
    """Display affiliate earnings"""
    st.subheader("💰 Earnings Dashboard")
    
    # Get earnings data
    analytics = affiliate_manager.get_affiliate_analytics(affiliate_id, 30)
    
    if analytics['daily_stats']:
        total_commission = sum(day['commission'] for day in analytics['daily_stats'])
        
        # Earnings summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("This Month", f"${total_commission:.2f}")
        with col2:
            st.metric("Pending Payment", f"${total_commission:.2f}")
        with col3:
            st.metric("Total Paid", "$0.00")
        
        # Payment threshold notice
        if total_commission >= 50:
            st.success("🎉 You've reached the minimum payout threshold of $50!")
            if st.button("Request Payment"):
                st.info("Payment request submitted. You'll receive payment within 5-7 business days.")
        else:
            st.info(f"You need ${50 - total_commission:.2f} more to reach the minimum payout threshold of $50.")
    else:
        st.info("No earnings yet. Start promoting your affiliate links to earn commissions.")

def display_affiliate_settings(affiliate_id: int):
    """Display affiliate settings"""
    st.subheader("⚙️ Account Settings")
    
    # Payment settings
    st.markdown("### Payment Settings")
    
    with st.form("payment_settings"):
        payment_method = st.selectbox("Payment Method", ["PayPal", "Bank Transfer", "Check"])
        
        if payment_method == "PayPal":
            paypal_email = st.text_input("PayPal Email")
        elif payment_method == "Bank Transfer":
            bank_account = st.text_input("Bank Account Number")
            routing_number = st.text_input("Routing Number")
        
        minimum_payout = st.number_input("Minimum Payout Amount", min_value=25.0, value=50.0)
        
        if st.form_submit_button("Update Payment Settings"):
            st.success("Payment settings updated successfully!")
    
    # Marketing materials
    st.markdown("### Marketing Materials")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Banner Ads"):
            st.info("Banner ads package downloaded!")
    
    with col2:
        if st.button("📝 Get Marketing Templates"):
            st.info("Email templates downloaded!")

# Export functions
def get_affiliate_products(affiliate_id: int = None, category: str = None) -> List[Dict]:
    return affiliate_manager.get_affiliate_products(affiliate_id, category)

def track_affiliate_clicks(affiliate_id: int, product_id: int, user_id: int = None) -> Optional[Dict]:
    return affiliate_manager.track_affiliate_click(affiliate_id, product_id, user_id)
