import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

def render_affiliate_dashboard(user: Dict[str, Any], services: Dict[str, Any]):
    """Render the affiliate dashboard"""
    try:
        # Check if user is an affiliate
        if user['role'] != 'affiliate':
            st.error("Access denied. This dashboard is only available to affiliate users.")
            return
        
        st.title("Affiliate Dashboard")
        st.caption(f"Welcome, {user.get('name', 'Affiliate')}")
        
        # Main navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview",
            "Product Catalog",
            "Link Management",
            "Analytics",
            "Payments"
        ])
        
        with tab1:
            render_affiliate_overview(user, services)
        
        with tab2:
            render_product_catalog(user, services)
        
        with tab3:
            render_link_management(user, services)
        
        with tab4:
            render_affiliate_analytics(user, services)
        
        with tab5:
            render_affiliate_payments(user, services)
            
    except Exception as e:
        st.error(f"Error loading affiliate dashboard: {str(e)}")
        logging.error(f"Affiliate dashboard error: {str(e)}")

def render_affiliate_overview(user: Dict[str, Any], services: Dict[str, Any]):
    """Render affiliate overview dashboard"""
    try:
        st.subheader("Performance Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Clicks",
                "2,456",
                delta="+234 this week"
            )
        
        with col2:
            st.metric(
                "Conversions",
                "89",
                delta="+12 this week"
            )
        
        with col3:
            st.metric(
                "Conversion Rate",
                "3.6%",
                delta="+0.4%"
            )
        
        with col4:
            st.metric(
                "Total Earnings",
                "$1,234.56",
                delta="+$156.78"
            )
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔗 Generate Link", key="quick_generate_link"):
                st.session_state.show_link_generator = True
        
        with col2:
            if st.button("📊 View Analytics", key="quick_analytics"):
                st.session_state.active_tab = "Analytics"
        
        with col3:
            if st.button("💰 Payment Info", key="quick_payments"):
                st.session_state.active_tab = "Payments"
        
        with col4:
            if st.button("📧 Support", key="quick_support"):
                st.info("Support contact: affiliate@platform.com")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            render_clicks_trend_chart()
        
        with col2:
            render_earnings_trend_chart()
        
        # Recent activity
        render_recent_affiliate_activity(user, services)
        
        # Top performing products
        render_top_performing_products(user, services)
        
    except Exception as e:
        st.error(f"Error rendering affiliate overview: {str(e)}")

def render_product_catalog(user: Dict[str, Any], services: Dict[str, Any]):
    """Render product catalog for affiliates"""
    try:
        st.subheader("Product Catalog")
        
        # Search and filters
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("Search products...", placeholder="Enter product name or category")
        
        with col2:
            category_filter = st.selectbox("Category", ["All", "Subscriptions", "Digital Products", "Courses", "Tools"])
        
        with col3:
            commission_filter = st.selectbox("Commission Rate", ["All", "10%+", "20%+", "30%+"])
        
        # Product grid
        products = get_affiliate_products(search_query, category_filter, commission_filter)
        
        for product in products:
            render_product_card(product, user, services)
        
        # Load more button
        if len(products) >= 20:
            if st.button("Load More Products", key="load_more_products"):
                st.rerun()
        
    except Exception as e:
        st.error(f"Error rendering product catalog: {str(e)}")

def render_product_card(product: Dict[str, Any], user: Dict[str, Any], services: Dict[str, Any]):
    """Render individual product card"""
    try:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{product['name']}**")
                st.write(product['description'])
                st.caption(f"Category: {product['category']}")
                
                # Product features
                if product.get('features'):
                    with st.expander("Features"):
                        for feature in product['features']:
                            st.write(f"• {feature}")
            
            with col2:
                st.write(f"**Price:** {product['price']}")
                st.write(f"**Commission:** {product['commission_rate']}")
                
                # Commission amount
                commission_amount = calculate_commission(product['price'], product['commission_rate'])
                st.write(f"**You earn:** {commission_amount}")
            
            with col3:
                # Performance metrics
                st.metric("Conversion Rate", f"{product.get('conversion_rate', 0):.1f}%")
                st.metric("Avg. Earnings", f"${product.get('avg_earnings', 0):.2f}")
            
            with col4:
                # Action buttons
                if st.button("🔗 Get Link", key=f"get_link_{product['id']}"):
                    generate_affiliate_link(product, user)
                
                if st.button("📊 Stats", key=f"stats_{product['id']}"):
                    show_product_statistics(product)
                
                if st.button("❤️ Save", key=f"save_{product['id']}"):
                    save_product_to_favorites(product, user)
            
            st.divider()
        
    except Exception as e:
        st.error(f"Error rendering product card: {str(e)}")

def render_link_management(user: Dict[str, Any], services: Dict[str, Any]):
    """Render link management interface"""
    try:
        st.subheader("Link Management")
        
        # Link generator
        with st.expander("🔗 Generate New Link", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.selectbox("Select Product", get_product_options())
                campaign_name = st.text_input("Campaign Name", placeholder="e.g., Newsletter December")
            
            with col2:
                utm_source = st.text_input("UTM Source", placeholder="newsletter")
                utm_medium = st.text_input("UTM Medium", placeholder="email")
            
            if st.button("Generate Link", key="generate_affiliate_link"):
                if product_id and campaign_name:
                    link = create_affiliate_link(product_id, user['id'], campaign_name, utm_source, utm_medium)
                    st.success(f"Link generated: {link}")
                    st.code(link)
                else:
                    st.error("Please fill in required fields")
        
        # Existing links
        st.subheader("Your Affiliate Links")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Status", ["All", "Active", "Paused", "Expired"])
        
        with col2:
            product_filter = st.selectbox("Product", ["All"] + get_product_names())
        
        with col3:
            date_filter = st.selectbox("Created", ["All Time", "Last 7 days", "Last 30 days"])
        
        # Links table
        links = get_affiliate_links(user, status_filter, product_filter, date_filter)
        
        if links:
            for link in links:
                render_link_row(link, user, services)
        else:
            st.info("No affiliate links found. Create your first link above!")
        
    except Exception as e:
        st.error(f"Error rendering link management: {str(e)}")

def render_link_row(link: Dict[str, Any], user: Dict[str, Any], services: Dict[str, Any]):
    """Render individual affiliate link row"""
    try:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{link['campaign_name']}**")
                st.caption(f"Product: {link['product_name']}")
                st.caption(f"Created: {link['created_at']}")
                
                # Link preview
                with st.expander("View Link"):
                    st.code(link['url'])
            
            with col2:
                st.metric("Clicks", link.get('clicks', 0))
            
            with col3:
                st.metric("Conversions", link.get('conversions', 0))
            
            with col4:
                conversion_rate = (link.get('conversions', 0) / max(link.get('clicks', 1), 1)) * 100
                st.metric("CVR", f"{conversion_rate:.1f}%")
            
            with col5:
                # Action buttons
                if st.button("📋", key=f"copy_{link['id']}", help="Copy link"):
                    st.success("Link copied!")
                
                if st.button("📊", key=f"analytics_{link['id']}", help="View analytics"):
                    show_link_analytics(link)
                
                if st.button("⏸️", key=f"pause_{link['id']}", help="Pause/Resume link"):
                    toggle_link_status(link)
            
            st.divider()
        
    except Exception as e:
        st.error(f"Error rendering link row: {str(e)}")

def render_affiliate_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render affiliate analytics dashboard"""
    try:
        st.subheader("Affiliate Analytics")
        
        # Time range selector
        col1, col2 = st.columns([1, 3])
        
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
            )
        
        # Analytics metrics
        analytics_data = get_affiliate_analytics(user, time_range)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clicks", f"{analytics_data.get('total_clicks', 0):,}")
        
        with col2:
            st.metric("Total Conversions", f"{analytics_data.get('total_conversions', 0):,}")
        
        with col3:
            st.metric("Total Earnings", f"${analytics_data.get('total_earnings', 0):,.2f}")
        
        with col4:
            st.metric("Avg. Commission", f"${analytics_data.get('avg_commission', 0):.2f}")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            render_performance_over_time_chart(analytics_data, time_range)
        
        with col2:
            render_product_performance_chart(analytics_data)
        
        # Detailed analytics table
        st.subheader("Detailed Performance")
        render_detailed_performance_table(analytics_data)
        
        # Geographic analytics
        st.subheader("Geographic Performance")
        render_geographic_performance(analytics_data)
        
    except Exception as e:
        st.error(f"Error rendering affiliate analytics: {str(e)}")

def render_affiliate_payments(user: Dict[str, Any], services: Dict[str, Any]):
    """Render affiliate payments interface"""
    try:
        st.subheader("Payment Dashboard")
        
        # Payment overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Available Balance", "$567.89", delta="+$78.45")
        
        with col2:
            st.metric("Pending Earnings", "$123.45", delta="Processing")
        
        with col3:
            st.metric("Total Paid", "$3,456.78", delta="Lifetime")
        
        with col4:
            st.metric("Next Payment", "Dec 15", delta="5 days")
        
        # Payment settings
        with st.expander("💳 Payment Settings", expanded=False):
            payment_method = st.selectbox(
                "Payment Method",
                ["PayPal", "Bank Transfer", "Stripe", "Wire Transfer"]
            )
            
            if payment_method == "PayPal":
                paypal_email = st.text_input("PayPal Email", placeholder="your-email@paypal.com")
            elif payment_method == "Bank Transfer":
                col1, col2 = st.columns(2)
                with col1:
                    bank_name = st.text_input("Bank Name")
                    account_number = st.text_input("Account Number", type="password")
                with col2:
                    routing_number = st.text_input("Routing Number")
                    account_holder = st.text_input("Account Holder Name")
            
            minimum_payout = st.number_input("Minimum Payout Amount", min_value=50, value=100, step=10)
            
            if st.button("Save Payment Settings"):
                save_payment_settings(user, {
                    'method': payment_method,
                    'minimum_payout': minimum_payout
                })
                st.success("Payment settings saved!")
        
        # Payment history
        st.subheader("Payment History")
        render_payment_history_table(user, services)
        
        # Request payout
        st.subheader("Request Payout")
        available_balance = 567.89  # This would come from the database
        
        if available_balance >= 100:  # Minimum payout threshold
            if st.button("💸 Request Payout", type="primary"):
                if request_payout(user, available_balance):
                    st.success(f"Payout request submitted for ${available_balance:.2f}")
                else:
                    st.error("Failed to submit payout request")
        else:
            st.info(f"Minimum payout amount is $100. Current balance: ${available_balance:.2f}")
        
        # Earnings forecast
        st.subheader("Earnings Forecast")
        render_earnings_forecast(user, services)
        
    except Exception as e:
        st.error(f"Error rendering affiliate payments: {str(e)}")

def get_affiliate_products(search_query: str = "", category_filter: str = "All", 
                          commission_filter: str = "All") -> List[Dict[str, Any]]:
    """Get available affiliate products"""
    try:
        # Sample products - in production, this would query the database
        products = [
            {
                'id': 1,
                'name': 'Premium News Subscription',
                'description': 'Ad-free news experience with exclusive content',
                'category': 'Subscriptions',
                'price': '$9.99/month',
                'commission_rate': '20%',
                'conversion_rate': 3.2,
                'avg_earnings': 15.67,
                'features': ['Ad-free browsing', 'Exclusive articles', 'Early access']
            },
            {
                'id': 2,
                'name': 'Business Analytics Course',
                'description': 'Comprehensive course on business data analysis',
                'category': 'Courses',
                'price': '$199.99',
                'commission_rate': '30%',
                'conversion_rate': 2.8,
                'avg_earnings': 45.99,
                'features': ['Video lessons', 'Practical exercises', 'Certificate']
            },
            {
                'id': 3,
                'name': 'News API Access',
                'description': 'Developer API for news data integration',
                'category': 'Tools',
                'price': '$29.99/month',
                'commission_rate': '25%',
                'conversion_rate': 1.9,
                'avg_earnings': 22.45,
                'features': ['Real-time data', 'Multiple formats', 'High availability']
            }
        ]
        
        # Apply filters
        filtered_products = products
        
        if search_query:
            filtered_products = [
                p for p in filtered_products 
                if search_query.lower() in p['name'].lower() or search_query.lower() in p['description'].lower()
            ]
        
        if category_filter != "All":
            filtered_products = [p for p in filtered_products if p['category'] == category_filter]
        
        if commission_filter != "All":
            min_commission = int(commission_filter.replace('%+', ''))
            filtered_products = [
                p for p in filtered_products 
                if int(p['commission_rate'].replace('%', '')) >= min_commission
            ]
        
        return filtered_products
        
    except Exception as e:
        logging.error(f"Error getting affiliate products: {str(e)}")
        return []

def calculate_commission(price: str, commission_rate: str) -> str:
    """Calculate commission amount"""
    try:
        # Extract numeric values
        price_value = float(price.replace('$', '').replace('/month', ''))
        commission_percent = float(commission_rate.replace('%', '')) / 100
        
        commission_amount = price_value * commission_percent
        return f"${commission_amount:.2f}"
        
    except Exception as e:
        logging.error(f"Error calculating commission: {str(e)}")
        return "$0.00"

def generate_affiliate_link(product: Dict[str, Any], user: Dict[str, Any]):
    """Generate affiliate link for product"""
    try:
        # Generate unique affiliate link
        affiliate_code = f"aff_{user['id']}_{product['id']}"
        link = f"https://platform.com/product/{product['id']}?ref={affiliate_code}"
        
        st.success("Affiliate link generated!")
        st.code(link)
        
        # Track link generation
        track_affiliate_activity(user['id'], 'link_generated', {'product_id': product['id']})
        
    except Exception as e:
        st.error(f"Error generating affiliate link: {str(e)}")

def show_product_statistics(product: Dict[str, Any]):
    """Show detailed product statistics"""
    try:
        with st.expander(f"Statistics for: {product['name']}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sales", "1,234")
            
            with col2:
                st.metric("Avg. Rating", "4.7/5")
            
            with col3:
                st.metric("Conversion Rate", f"{product['conversion_rate']:.1f}%")
            
            with col4:
                st.metric("Top Performer", "Yes" if product['conversion_rate'] > 3.0 else "No")
            
            # Performance trend chart
            render_product_trend_chart(product)
        
    except Exception as e:
        st.error(f"Error showing product statistics: {str(e)}")

def save_product_to_favorites(product: Dict[str, Any], user: Dict[str, Any]):
    """Save product to user's favorites"""
    try:
        # In production, this would update the database
        st.success(f"Added '{product['name']}' to favorites!")
        
        # Track activity
        track_affiliate_activity(user['id'], 'product_favorited', {'product_id': product['id']})
        
    except Exception as e:
        st.error(f"Error saving product to favorites: {str(e)}")

def get_product_options() -> List[str]:
    """Get product options for dropdown"""
    products = get_affiliate_products()
    return [f"{p['id']} - {p['name']}" for p in products]

def get_product_names() -> List[str]:
    """Get product names for filtering"""
    products = get_affiliate_products()
    return [p['name'] for p in products]

def create_affiliate_link(product_id: str, user_id: int, campaign_name: str, 
                         utm_source: str, utm_medium: str) -> str:
    """Create new affiliate link"""
    try:
        # Generate tracking parameters
        affiliate_code = f"aff_{user_id}_{product_id.split('-')[0]}"
        utm_params = f"utm_source={utm_source}&utm_medium={utm_medium}&utm_campaign={campaign_name}"
        
        link = f"https://platform.com/product/{product_id.split('-')[0]}?ref={affiliate_code}&{utm_params}"
        
        # Save link to database (in production)
        save_affiliate_link({
            'user_id': user_id,
            'product_id': product_id.split('-')[0],
            'campaign_name': campaign_name,
            'url': link,
            'created_at': datetime.now().isoformat()
        })
        
        return link
        
    except Exception as e:
        logging.error(f"Error creating affiliate link: {str(e)}")
        return ""

def get_affiliate_links(user: Dict[str, Any], status_filter: str, 
                       product_filter: str, date_filter: str) -> List[Dict[str, Any]]:
    """Get user's affiliate links"""
    try:
        # Sample links - in production, this would query the database
        links = [
            {
                'id': 1,
                'campaign_name': 'Newsletter December',
                'product_name': 'Premium News Subscription',
                'url': 'https://platform.com/product/1?ref=aff_123_1&utm_source=newsletter',
                'created_at': '2024-01-15',
                'status': 'active',
                'clicks': 156,
                'conversions': 8
            },
            {
                'id': 2,
                'campaign_name': 'Social Media Promo',
                'product_name': 'Business Analytics Course',
                'url': 'https://platform.com/product/2?ref=aff_123_2&utm_source=social',
                'created_at': '2024-01-10',
                'status': 'active',
                'clicks': 89,
                'conversions': 3
            }
        ]
        
        # Apply filters
        filtered_links = links
        
        if status_filter != "All":
            filtered_links = [l for l in filtered_links if l['status'] == status_filter.lower()]
        
        if product_filter != "All":
            filtered_links = [l for l in filtered_links if l['product_name'] == product_filter]
        
        return filtered_links
        
    except Exception as e:
        logging.error(f"Error getting affiliate links: {str(e)}")
        return []

def show_link_analytics(link: Dict[str, Any]):
    """Show detailed analytics for a link"""
    try:
        with st.expander(f"Analytics for: {link['campaign_name']}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Clicks", f"{link.get('clicks', 0):,}")
            
            with col2:
                st.metric("Conversions", f"{link.get('conversions', 0):,}")
            
            with col3:
                conversion_rate = (link.get('conversions', 0) / max(link.get('clicks', 1), 1)) * 100
                st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
            
            with col4:
                earnings = link.get('conversions', 0) * 15.67  # Sample earnings calculation
                st.metric("Earnings", f"${earnings:.2f}")
            
            # Performance chart would go here
            st.info("Detailed performance charts coming soon!")
        
    except Exception as e:
        st.error(f"Error showing link analytics: {str(e)}")

def toggle_link_status(link: Dict[str, Any]):
    """Toggle link active/paused status"""
    try:
        new_status = "paused" if link['status'] == 'active' else "active"
        # Update in database (in production)
        st.success(f"Link {new_status}!")
        
    except Exception as e:
        st.error(f"Error toggling link status: {str(e)}")

def get_affiliate_analytics(user: Dict[str, Any], time_range: str) -> Dict[str, Any]:
    """Get affiliate analytics data"""
    try:
        # Sample analytics data - in production, this would query the database
        return {
            'total_clicks': 2456,
            'total_conversions': 89,
            'total_earnings': 1234.56,
            'avg_commission': 15.67,
            'performance_data': {
                'dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'clicks': [45, 67, 89],
                'conversions': [2, 3, 4],
                'earnings': [23.45, 34.56, 45.67]
            },
            'product_performance': {
                'Premium Subscription': 567.89,
                'Analytics Course': 345.67,
                'API Access': 234.56
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting affiliate analytics: {str(e)}")
        return {}

def render_clicks_trend_chart():
    """Render clicks trend chart"""
    try:
        # Sample data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        clicks = [20 + i * 2 + (i % 7) * 10 for i in range(30)]
        
        df = pd.DataFrame({'Date': dates, 'Clicks': clicks})
        fig = px.line(df, x='Date', y='Clicks', title='Daily Clicks Trend')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering clicks trend chart: {str(e)}")

def render_earnings_trend_chart():
    """Render earnings trend chart"""
    try:
        # Sample data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        earnings = [5 + i * 0.5 + (i % 7) * 2 for i in range(30)]
        
        df = pd.DataFrame({'Date': dates, 'Earnings': earnings})
        fig = px.line(df, x='Date', y='Earnings', title='Daily Earnings Trend')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering earnings trend chart: {str(e)}")

def render_recent_affiliate_activity(user: Dict[str, Any], services: Dict[str, Any]):
    """Render recent affiliate activity"""
    try:
        st.subheader("Recent Activity")
        
        activities = [
            {"type": "conversion", "product": "Premium Subscription", "amount": "$15.67", "time": "2 hours ago"},
            {"type": "click", "campaign": "Newsletter December", "count": "23 clicks", "time": "4 hours ago"},
            {"type": "link_created", "campaign": "Social Media Promo", "product": "Analytics Course", "time": "1 day ago"},
        ]
        
        for activity in activities:
            if activity['type'] == 'conversion':
                st.success(f"💰 Conversion: {activity['product']} - {activity['amount']} - {activity['time']}")
            elif activity['type'] == 'click':
                st.info(f"🔗 {activity['campaign']}: {activity['count']} - {activity['time']}")
            elif activity['type'] == 'link_created':
                st.warning(f"📝 Link created: {activity['campaign']} for {activity['product']} - {activity['time']}")
        
    except Exception as e:
        st.error(f"Error rendering recent activity: {str(e)}")

def render_top_performing_products(user: Dict[str, Any], services: Dict[str, Any]):
    """Render top performing products"""
    try:
        st.subheader("Top Performing Products")
        
        products = [
            {"name": "Premium Subscription", "earnings": 567.89, "conversions": 34},
            {"name": "Analytics Course", "earnings": 345.67, "conversions": 12},
            {"name": "API Access", "earnings": 234.56, "conversions": 8}
        ]
        
        for product in products:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{product['name']}**")
            
            with col2:
                st.write(f"${product['earnings']:.2f}")
            
            with col3:
                st.write(f"{product['conversions']} sales")
        
    except Exception as e:
        st.error(f"Error rendering top performing products: {str(e)}")

def render_performance_over_time_chart(analytics_data: Dict[str, Any], time_range: str):
    """Render performance over time chart"""
    try:
        performance_data = analytics_data.get('performance_data', {})
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            fig = px.line(df, x='dates', y=['clicks', 'conversions'], 
                         title=f'Performance Trend - {time_range}')
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering performance chart: {str(e)}")

def render_product_performance_chart(analytics_data: Dict[str, Any]):
    """Render product performance chart"""
    try:
        product_data = analytics_data.get('product_performance', {})
        
        if product_data:
            fig = px.bar(x=list(product_data.keys()), y=list(product_data.values()),
                        title='Earnings by Product')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering product performance chart: {str(e)}")

def render_detailed_performance_table(analytics_data: Dict[str, Any]):
    """Render detailed performance table"""
    try:
        # Sample detailed performance data
        data = {
            'Campaign': ['Newsletter Dec', 'Social Media', 'Blog Post', 'Email Series'],
            'Clicks': [156, 89, 67, 45],
            'Conversions': [8, 3, 2, 1],
            'CVR': ['5.1%', '3.4%', '3.0%', '2.2%'],
            'Earnings': ['$125.36', '$47.01', '$31.34', '$15.67']
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering detailed performance table: {str(e)}")

def render_geographic_performance(analytics_data: Dict[str, Any]):
    """Render geographic performance analysis"""
    try:
        # Sample geographic data
        geo_data = {
            'Country': ['United States', 'Canada', 'United Kingdom', 'Australia'],
            'Clicks': [1234, 567, 345, 234],
            'Conversions': [45, 23, 12, 8],
            'Earnings': ['$567.89', '$234.56', '$123.45', '$89.01']
        }
        
        df = pd.DataFrame(geo_data)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering geographic performance: {str(e)}")

def render_payment_history_table(user: Dict[str, Any], services: Dict[str, Any]):
    """Render payment history table"""
    try:
        # Sample payment history
        payments = {
            'Date': ['2024-01-15', '2023-12-15', '2023-11-15', '2023-10-15'],
            'Amount': ['$234.56', '$189.45', '$156.78', '$145.23'],
            'Method': ['PayPal', 'PayPal', 'Bank Transfer', 'PayPal'],
            'Status': ['Completed', 'Completed', 'Completed', 'Completed']
        }
        
        df = pd.DataFrame(payments)
        st.dataframe(df, use_container_width=True)
        
        # Download payment report
        if st.button("📄 Download Payment Report"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"affiliate_payments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"Error rendering payment history: {str(e)}")

def render_earnings_forecast(user: Dict[str, Any], services: Dict[str, Any]):
    """Render earnings forecast"""
    try:
        # Sample forecast data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        projected_earnings = [567, 623, 689, 756, 834, 918]
        
        df = pd.DataFrame({'Month': months, 'Projected Earnings': projected_earnings})
        fig = px.bar(df, x='Month', y='Projected Earnings', title='6-Month Earnings Forecast')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering earnings forecast: {str(e)}")

def render_product_trend_chart(product: Dict[str, Any]):
    """Render product performance trend chart"""
    try:
        # Sample trend data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        sales = [1 + (i % 10) for i in range(30)]
        
        df = pd.DataFrame({'Date': dates, 'Sales': sales})
        fig = px.line(df, x='Date', y='Sales', title=f'Sales Trend - {product["name"]}')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering product trend chart: {str(e)}")

def save_affiliate_link(link_data: Dict[str, Any]):
    """Save affiliate link to database"""
    try:
        # In production, this would save to the database
        logging.info(f"Saving affiliate link: {link_data}")
        
    except Exception as e:
        logging.error(f"Error saving affiliate link: {str(e)}")

def track_affiliate_activity(user_id: int, activity_type: str, data: Dict[str, Any]):
    """Track affiliate activity"""
    try:
        # In production, this would track to analytics system
        logging.info(f"Tracking affiliate activity: {user_id}, {activity_type}, {data}")
        
    except Exception as e:
        logging.error(f"Error tracking affiliate activity: {str(e)}")

def save_payment_settings(user: Dict[str, Any], settings: Dict[str, Any]):
    """Save payment settings"""
    try:
        # In production, this would update the database
        logging.info(f"Saving payment settings for user {user['id']}: {settings}")
        
    except Exception as e:
        logging.error(f"Error saving payment settings: {str(e)}")

def request_payout(user: Dict[str, Any], amount: float) -> bool:
    """Request payout"""
    try:
        # In production, this would create a payout request
        logging.info(f"Payout requested by user {user['id']}: ${amount:.2f}")
        return True
        
    except Exception as e:
        logging.error(f"Error requesting payout: {str(e)}")
        return False
