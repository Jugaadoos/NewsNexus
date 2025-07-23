import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

def render_partner_portal(user: Dict[str, Any], services: Dict[str, Any]):
    """Render the publishing partner portal"""
    try:
        # Check if user is a publishing partner
        if user['role'] != 'publishing_partner':
            st.error("Access denied. This portal is only available to publishing partners.")
            return
        
        st.title("Publishing Partner Portal")
        st.caption(f"Welcome, {user.get('name', 'Partner')}")
        
        # Main navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "Content Management", 
            "Analytics",
            "Revenue Sharing",
            "Settings"
        ])
        
        with tab1:
            render_partner_dashboard(user, services)
        
        with tab2:
            render_content_management(user, services)
        
        with tab3:
            render_partner_analytics(user, services)
        
        with tab4:
            render_revenue_sharing(user, services)
        
        with tab5:
            render_partner_settings(user, services)
            
    except Exception as e:
        st.error(f"Error loading partner portal: {str(e)}")
        logging.error(f"Partner portal error: {str(e)}")

def render_partner_dashboard(user: Dict[str, Any], services: Dict[str, Any]):
    """Render partner dashboard overview"""
    try:
        st.subheader("Partner Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Content Published",
                "156",
                delta="+12 this month"
            )
        
        with col2:
            st.metric(
                "Total Views",
                "2.4M",
                delta="+340K this week"
            )
        
        with col3:
            st.metric(
                "Revenue Earned",
                "$3,245",
                delta="+$456 this month"
            )
        
        with col4:
            st.metric(
                "Performance Score",
                "8.7/10",
                delta="+0.3"
            )
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Submit New Article", key="quick_new_article"):
                st.session_state.show_article_form = True
        
        with col2:
            if st.button("📊 View Analytics", key="quick_analytics"):
                st.session_state.active_tab = "Analytics"
        
        with col3:
            if st.button("💰 Revenue Report", key="quick_revenue"):
                st.session_state.show_revenue_report = True
        
        with col4:
            if st.button("⚙️ Account Settings", key="quick_settings"):
                st.session_state.active_tab = "Settings"
        
        # Recent activity
        render_recent_partner_activity(user, services)
        
        # Performance overview
        render_performance_overview(user, services)
        
    except Exception as e:
        st.error(f"Error rendering partner dashboard: {str(e)}")

def render_content_management(user: Dict[str, Any], services: Dict[str, Any]):
    """Render content management interface"""
    try:
        st.subheader("Content Management")
        
        # Content management tabs
        content_tab1, content_tab2, content_tab3 = st.tabs([
            "Submit Content",
            "Manage Articles", 
            "Content Guidelines"
        ])
        
        with content_tab1:
            render_content_submission_form(user, services)
        
        with content_tab2:
            render_article_management(user, services)
        
        with content_tab3:
            render_content_guidelines()
        
    except Exception as e:
        st.error(f"Error rendering content management: {str(e)}")

def render_content_submission_form(user: Dict[str, Any], services: Dict[str, Any]):
    """Render article submission form"""
    try:
        st.subheader("Submit New Article")
        
        with st.form("article_submission"):
            # Article details
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Article Title *", placeholder="Enter compelling article title")
                category = st.selectbox(
                    "Category *",
                    ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"]
                )
                source_name = st.text_input("Source Name *", value=user.get('organization', ''))
            
            with col2:
                tags = st.text_input("Tags", placeholder="technology, innovation, AI")
                priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
                publish_date = st.date_input("Preferred Publish Date", value=datetime.now().date())
            
            # Content
            st.subheader("Article Content")
            content = st.text_area(
                "Article Content *",
                height=300,
                placeholder="Write your article content here..."
            )
            
            # Summary
            summary = st.text_area(
                "Article Summary",
                height=100,
                placeholder="Brief summary (will be auto-generated if left empty)"
            )
            
            # Media attachments
            st.subheader("Media Attachments")
            col1, col2 = st.columns(2)
            
            with col1:
                featured_image = st.text_input("Featured Image URL", placeholder="https://example.com/image.jpg")
                video_url = st.text_input("Video URL", placeholder="https://youtube.com/watch?v=...")
            
            with col2:
                source_url = st.text_input("Original Source URL", placeholder="https://originalsource.com/article")
                external_links = st.text_area("Additional Links", height=80, placeholder="One URL per line")
            
            # Submission options
            st.subheader("Submission Options")
            col1, col2 = st.columns(2)
            
            with col1:
                draft_mode = st.checkbox("Save as Draft", help="Article will not be submitted for review")
                notify_on_approval = st.checkbox("Notify on Approval", value=True)
            
            with col2:
                exclusive_content = st.checkbox("Exclusive Content", help="Content exclusive to this platform")
                allow_syndication = st.checkbox("Allow Syndication", value=True)
            
            # Submit button
            submitted = st.form_submit_button("Submit Article", type="primary")
            
            if submitted:
                if title and content and category:
                    success = submit_article(
                        title, content, category, user, services,
                        summary=summary,
                        tags=tags,
                        priority=priority,
                        draft_mode=draft_mode,
                        featured_image=featured_image,
                        source_url=source_url
                    )
                    
                    if success:
                        st.success("Article submitted successfully!")
                        if not draft_mode:
                            st.info("Your article has been submitted for review and will be processed by our editorial team.")
                    else:
                        st.error("Failed to submit article. Please try again.")
                else:
                    st.error("Please fill in all required fields (marked with *)")
        
    except Exception as e:
        st.error(f"Error rendering submission form: {str(e)}")

def render_article_management(user: Dict[str, Any], services: Dict[str, Any]):
    """Render article management interface"""
    try:
        st.subheader("Your Articles")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox("Status", ["All", "Draft", "Pending", "Approved", "Rejected"])
        
        with col2:
            category_filter = st.selectbox("Category", ["All"] + ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"])
        
        with col3:
            date_filter = st.selectbox("Date Range", ["All Time", "Last 7 days", "Last 30 days", "Last 90 days"])
        
        with col4:
            if st.button("🔄 Refresh", key="refresh_articles"):
                st.rerun()
        
        # Article list
        articles = get_partner_articles(user, services, status_filter, category_filter, date_filter)
        
        if articles:
            for article in articles:
                render_article_row(article, user, services)
        else:
            st.info("No articles found matching your criteria.")
        
        # Pagination
        if len(articles) >= 20:
            if st.button("Load More Articles", key="load_more_partner_articles"):
                st.rerun()
        
    except Exception as e:
        st.error(f"Error rendering article management: {str(e)}")

def render_article_row(article: Dict[str, Any], user: Dict[str, Any], services: Dict[str, Any]):
    """Render individual article row"""
    try:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{article['title']}**")
                st.caption(f"{article['category']} • {article.get('created_at', 'Unknown date')}")
                
                # Status badge
                status = article.get('status', 'draft')
                status_colors = {
                    'draft': '🟡',
                    'pending': '🟠',
                    'approved': '🟢',
                    'rejected': '🔴'
                }
                st.write(f"{status_colors.get(status, '⚫')} {status.title()}")
            
            with col2:
                views = article.get('views', 0)
                st.metric("Views", f"{views:,}")
            
            with col3:
                engagement = article.get('engagement_score', 0)
                st.metric("Engagement", f"{engagement:.1f}")
            
            with col4:
                # Action buttons
                if st.button("📝", key=f"edit_{article['id']}", help="Edit article"):
                    st.session_state.edit_article_id = article['id']
                
                if st.button("📊", key=f"stats_{article['id']}", help="View statistics"):
                    show_article_statistics(article)
                
                if st.button("🗑️", key=f"delete_{article['id']}", help="Delete article"):
                    delete_article(article['id'], services)
            
            st.divider()
        
    except Exception as e:
        st.error(f"Error rendering article row: {str(e)}")

def render_partner_analytics(user: Dict[str, Any], services: Dict[str, Any]):
    """Render partner-specific analytics"""
    try:
        st.subheader("Partner Analytics")
        
        # Time range selector
        col1, col2 = st.columns([1, 3])
        
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
            )
        
        # Analytics metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", "156", delta="+12")
        
        with col2:
            st.metric("Total Views", "2.4M", delta="+15%")
        
        with col3:
            st.metric("Avg. Engagement", "7.8", delta="+0.5")
        
        with col4:
            st.metric("Revenue Share", "$3,245", delta="+$456")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance over time
            render_performance_chart(user, services, time_range)
        
        with col2:
            # Category distribution
            render_category_distribution_chart(user, services)
        
        # Detailed analytics table
        render_detailed_analytics_table(user, services)
        
    except Exception as e:
        st.error(f"Error rendering partner analytics: {str(e)}")

def render_revenue_sharing(user: Dict[str, Any], services: Dict[str, Any]):
    """Render revenue sharing interface"""
    try:
        st.subheader("Revenue Sharing")
        
        # Revenue overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Earned", "$3,245.67", delta="+$456.78")
        
        with col2:
            st.metric("This Month", "$456.78", delta="+$67.89")
        
        with col3:
            st.metric("Revenue Share %", "15%", help="Your current revenue share percentage")
        
        with col4:
            st.metric("Next Payment", "Dec 15", delta="3 days")
        
        # Revenue breakdown
        st.subheader("Revenue Breakdown")
        render_revenue_breakdown_chart(user, services)
        
        # Payment history
        st.subheader("Payment History")
        render_payment_history(user, services)
        
        # Revenue optimization tips
        st.subheader("Revenue Optimization")
        render_revenue_tips()
        
    except Exception as e:
        st.error(f"Error rendering revenue sharing: {str(e)}")

def render_partner_settings(user: Dict[str, Any], services: Dict[str, Any]):
    """Render partner settings interface"""
    try:
        st.subheader("Partner Settings")
        
        # Account information
        with st.form("partner_settings"):
            st.subheader("Account Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                organization = st.text_input("Organization Name", value=user.get('organization', ''))
                contact_name = st.text_input("Contact Name", value=user.get('name', ''))
                email = st.text_input("Email", value=user.get('email', ''))
            
            with col2:
                phone = st.text_input("Phone", value=user.get('phone', ''))
                website = st.text_input("Website", placeholder="https://yourwebsite.com")
                timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"])
            
            # Content preferences
            st.subheader("Content Preferences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                preferred_categories = st.multiselect(
                    "Preferred Categories",
                    ["World", "Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science"],
                    default=["Technology", "Business"]
                )
                
                content_format = st.selectbox("Preferred Content Format", ["Article", "Video", "Podcast", "Infographic"])
            
            with col2:
                notification_preferences = st.multiselect(
                    "Notifications",
                    ["Article Approval", "Payment Updates", "Performance Reports", "Platform Updates"],
                    default=["Article Approval", "Payment Updates"]
                )
                
                auto_publish = st.checkbox("Auto-publish approved content", value=True)
            
            # API settings
            st.subheader("API Settings")
            
            api_key = st.text_input("API Key", value="pk_test_...", type="password", help="Your API key for content submission")
            webhook_url = st.text_input("Webhook URL", placeholder="https://yoursite.com/webhook")
            
            # Save settings
            if st.form_submit_button("Save Settings", type="primary"):
                save_partner_settings(user, {
                    'organization': organization,
                    'contact_name': contact_name,
                    'email': email,
                    'phone': phone,
                    'website': website,
                    'timezone': timezone,
                    'preferred_categories': preferred_categories,
                    'notification_preferences': notification_preferences,
                    'auto_publish': auto_publish,
                    'webhook_url': webhook_url
                })
                st.success("Settings saved successfully!")
        
    except Exception as e:
        st.error(f"Error rendering partner settings: {str(e)}")

def submit_article(title: str, content: str, category: str, user: Dict[str, Any], 
                  services: Dict[str, Any], **kwargs) -> bool:
    """Submit article for review"""
    try:
        # Create article data
        article_data = {
            'title': title,
            'content': content,
            'category': category,
            'author_id': user['id'],
            'source': user.get('organization', 'Partner'),
            'status': 'draft' if kwargs.get('draft_mode') else 'pending',
            'summary': kwargs.get('summary', ''),
            'tags': kwargs.get('tags', ''),
            'priority': kwargs.get('priority', 'Normal'),
            'featured_image': kwargs.get('featured_image', ''),
            'source_url': kwargs.get('source_url', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # In production, this would save to database
        # For now, we'll simulate success
        return True
        
    except Exception as e:
        logging.error(f"Error submitting article: {str(e)}")
        return False

def get_partner_articles(user: Dict[str, Any], services: Dict[str, Any], 
                        status_filter: str, category_filter: str, date_filter: str) -> List[Dict[str, Any]]:
    """Get articles for the partner"""
    try:
        # Sample articles - in production, this would query the database
        articles = [
            {
                'id': 1,
                'title': 'Latest Technology Trends in 2024',
                'category': 'Technology',
                'status': 'approved',
                'created_at': '2024-01-15',
                'views': 15420,
                'engagement_score': 8.5
            },
            {
                'id': 2,
                'title': 'Business Impact of AI Revolution',
                'category': 'Business',
                'status': 'pending',
                'created_at': '2024-01-14',
                'views': 0,
                'engagement_score': 0.0
            },
            {
                'id': 3,
                'title': 'Healthcare Innovation Breakthrough',
                'category': 'Health',
                'status': 'draft',
                'created_at': '2024-01-13',
                'views': 0,
                'engagement_score': 0.0
            }
        ]
        
        # Apply filters
        if status_filter != 'All':
            articles = [a for a in articles if a['status'] == status_filter.lower()]
        
        if category_filter != 'All':
            articles = [a for a in articles if a['category'] == category_filter]
        
        return articles
        
    except Exception as e:
        logging.error(f"Error getting partner articles: {str(e)}")
        return []

def show_article_statistics(article: Dict[str, Any]):
    """Show detailed article statistics"""
    try:
        with st.expander(f"Statistics for: {article['title']}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Views", f"{article.get('views', 0):,}")
            
            with col2:
                st.metric("Likes", f"{article.get('likes', 0):,}")
            
            with col3:
                st.metric("Shares", f"{article.get('shares', 0):,}")
            
            with col4:
                st.metric("Comments", f"{article.get('comments', 0):,}")
            
            # Performance chart would go here
            st.info("Detailed performance charts coming soon!")
        
    except Exception as e:
        st.error(f"Error showing article statistics: {str(e)}")

def delete_article(article_id: int, services: Dict[str, Any]):
    """Delete an article"""
    try:
        # Confirmation dialog
        if st.button("Confirm Delete", key=f"confirm_delete_{article_id}"):
            # In production, this would delete from database
            st.success("Article deleted successfully!")
            st.rerun()
        
    except Exception as e:
        st.error(f"Error deleting article: {str(e)}")

def render_content_guidelines():
    """Render content guidelines for partners"""
    try:
        st.subheader("Content Guidelines")
        
        st.markdown("""
        ### Editorial Standards
        
        **Quality Requirements:**
        - Articles must be original and well-researched
        - Minimum 500 words for full articles
        - Proper grammar and spelling
        - Clear, engaging headlines
        - Factual accuracy required
        
        **Content Types:**
        - News articles and reports
        - Analysis and opinion pieces
        - Industry insights
        - Educational content
        
        **Prohibited Content:**
        - Plagiarized material
        - Misleading information
        - Hate speech or discrimination
        - Spam or promotional content
        - Unverified claims
        
        **SEO Best Practices:**
        - Use relevant keywords naturally
        - Include meta descriptions
        - Optimize for readability
        - Add relevant tags
        
        **Revenue Optimization:**
        - High-quality content earns higher revenue share
        - Trending topics get better placement
        - Engagement metrics affect earnings
        - Regular publishing increases visibility
        """)
        
    except Exception as e:
        st.error(f"Error rendering content guidelines: {str(e)}")

def render_recent_partner_activity(user: Dict[str, Any], services: Dict[str, Any]):
    """Render recent partner activity"""
    try:
        st.subheader("Recent Activity")
        
        # Sample recent activities
        activities = [
            {"type": "article_approved", "title": "Tech Innovation Article", "time": "2 hours ago"},
            {"type": "payment_received", "amount": "$156.78", "time": "1 day ago"},
            {"type": "article_submitted", "title": "Business Trends Analysis", "time": "3 days ago"},
        ]
        
        for activity in activities:
            if activity['type'] == 'article_approved':
                st.success(f"✅ Article approved: {activity['title']} - {activity['time']}")
            elif activity['type'] == 'payment_received':
                st.info(f"💰 Payment received: {activity['amount']} - {activity['time']}")
            elif activity['type'] == 'article_submitted':
                st.warning(f"📝 Article submitted: {activity['title']} - {activity['time']}")
        
    except Exception as e:
        st.error(f"Error rendering recent activity: {str(e)}")

def render_performance_overview(user: Dict[str, Any], services: Dict[str, Any]):
    """Render performance overview charts"""
    try:
        st.subheader("Performance Overview")
        
        # Sample performance data
        df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Views': [100 + i * 10 + (i % 7) * 50 for i in range(30)],
            'Revenue': [10 + i * 2 + (i % 7) * 5 for i in range(30)]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(df, x='Date', y='Views', title='Daily Views')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(df, x='Date', y='Revenue', title='Daily Revenue')
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering performance overview: {str(e)}")

def render_performance_chart(user: Dict[str, Any], services: Dict[str, Any], time_range: str):
    """Render performance chart"""
    try:
        # Sample data based on time range
        if time_range == "Last 7 days":
            periods = 7
        elif time_range == "Last 30 days":
            periods = 30
        else:
            periods = 90
        
        df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=periods, freq='D'),
            'Performance': [70 + i * 2 + (i % 7) * 5 for i in range(periods)]
        })
        
        fig = px.line(df, x='Date', y='Performance', title=f'Performance Trend - {time_range}')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering performance chart: {str(e)}")

def render_category_distribution_chart(user: Dict[str, Any], services: Dict[str, Any]):
    """Render category distribution chart"""
    try:
        # Sample category data
        categories = ['Technology', 'Business', 'Health', 'Politics', 'Sports']
        values = [35, 25, 20, 15, 5]
        
        fig = px.pie(values=values, names=categories, title='Content by Category')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering category distribution chart: {str(e)}")

def render_detailed_analytics_table(user: Dict[str, Any], services: Dict[str, Any]):
    """Render detailed analytics table"""
    try:
        st.subheader("Detailed Analytics")
        
        # Sample detailed analytics data
        data = {
            'Article': ['Tech Trends 2024', 'AI in Business', 'Health Innovation', 'Market Analysis'],
            'Views': [15420, 12330, 9870, 8450],
            'Engagement': [8.5, 7.8, 9.2, 6.9],
            'Revenue': ['$156.78', '$134.23', '$98.76', '$87.65'],
            'Status': ['Active', 'Active', 'Active', 'Active']
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering detailed analytics table: {str(e)}")

def render_revenue_breakdown_chart(user: Dict[str, Any], services: Dict[str, Any]):
    """Render revenue breakdown chart"""
    try:
        # Sample revenue breakdown
        sources = ['Article Views', 'Premium Subscriptions', 'Affiliate Sales', 'Sponsored Content']
        amounts = [1245.67, 890.45, 567.89, 234.56]
        
        fig = px.bar(x=sources, y=amounts, title='Revenue by Source')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering revenue breakdown chart: {str(e)}")

def render_payment_history(user: Dict[str, Any], services: Dict[str, Any]):
    """Render payment history table"""
    try:
        # Sample payment history
        payments = {
            'Date': ['2024-01-15', '2023-12-15', '2023-11-15', '2023-10-15'],
            'Amount': ['$456.78', '$389.45', '$523.67', '$445.23'],
            'Status': ['Paid', 'Paid', 'Paid', 'Paid'],
            'Method': ['Bank Transfer', 'PayPal', 'Bank Transfer', 'PayPal']
        }
        
        df = pd.DataFrame(payments)
        st.dataframe(df, use_container_width=True)
        
        # Download payment report
        if st.button("📄 Download Payment Report"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"payment_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"Error rendering payment history: {str(e)}")

def render_revenue_tips():
    """Render revenue optimization tips"""
    try:
        st.markdown("""
        ### Revenue Optimization Tips
        
        **Content Quality:**
        - Focus on trending topics
        - Write engaging headlines
        - Include relevant images
        - Optimize for mobile reading
        
        **Engagement:**
        - Respond to comments
        - Share on social media
        - Cross-reference other articles
        - Use data and statistics
        
        **Timing:**
        - Publish during peak hours
        - Follow news cycles
        - Plan seasonal content
        - Maintain regular schedule
        
        **SEO:**
        - Use relevant keywords
        - Optimize meta descriptions
        - Include internal links
        - Add alt text to images
        """)
        
    except Exception as e:
        st.error(f"Error rendering revenue tips: {str(e)}")

def save_partner_settings(user: Dict[str, Any], settings: Dict[str, Any]):
    """Save partner settings"""
    try:
        # In production, this would update the database
        # For now, we'll simulate success
        logging.info(f"Saving settings for user {user['id']}: {settings}")
        return True
        
    except Exception as e:
        logging.error(f"Error saving partner settings: {str(e)}")
        return False
