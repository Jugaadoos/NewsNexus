import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from config import ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET

class ZohoIntegration:
    def __init__(self):
        self.client_id = ZOHO_CLIENT_ID
        self.client_secret = ZOHO_CLIENT_SECRET
        self.base_url = "https://www.zohoapis.com"
        self.auth_url = "https://accounts.zoho.com/oauth/v2"
        self.access_token = None
        self.refresh_token = None
        
        # Service endpoints
        self.services = {
            "crm": f"{self.base_url}/crm/v2",
            "books": f"{self.base_url}/books/v3",
            "commerce": f"{self.base_url}/commerce/v1",
            "inventory": f"{self.base_url}/inventory/v1",
            "creator": f"{self.base_url}/creator/v2",
            "campaigns": f"{self.base_url}/campaigns/v1"
        }
    
    def get_access_token(self, authorization_code: str) -> Dict:
        """Get access token using authorization code"""
        try:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "redirect_uri": "https://your-domain.com/zoho/callback"
            }
            
            response = requests.post(f"{self.auth_url}/token", data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.refresh_token = token_data["refresh_token"]
                return token_data
            else:
                return {"error": "Failed to get access token"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def refresh_access_token(self) -> Dict:
        """Refresh access token"""
        try:
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(f"{self.auth_url}/token", data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                return token_data
            else:
                return {"error": "Failed to refresh token"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def make_api_request(self, service: str, endpoint: str, method: str = "GET", 
                        data: Dict = None, params: Dict = None) -> Dict:
        """Make API request to Zoho service"""
        try:
            if not self.access_token:
                return {"error": "No access token available"}
            
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.services[service]}/{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"error": "Unsupported HTTP method"}
            
            if response.status_code == 401:
                # Token expired, try to refresh
                refresh_result = self.refresh_access_token()
                if "error" not in refresh_result:
                    # Retry request with new token
                    headers["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
                    response = requests.request(method, url, headers=headers, json=data, params=params)
            
            return response.json() if response.content else {"status": "success"}
            
        except Exception as e:
            return {"error": str(e)}
    
    # CRM Integration
    def create_crm_contact(self, contact_data: Dict) -> Dict:
        """Create contact in Zoho CRM"""
        data = {
            "data": [
                {
                    "First_Name": contact_data.get("first_name", ""),
                    "Last_Name": contact_data.get("last_name", ""),
                    "Email": contact_data.get("email", ""),
                    "Phone": contact_data.get("phone", ""),
                    "Lead_Source": "News Platform",
                    "Company": contact_data.get("company", ""),
                    "Title": contact_data.get("title", ""),
                    "Subscription_Tier": contact_data.get("subscription_tier", "free"),
                    "Registration_Date": contact_data.get("registration_date", datetime.now().isoformat())
                }
            ]
        }
        
        return self.make_api_request("crm", "Contacts", "POST", data)
    
    def update_crm_contact(self, contact_id: str, contact_data: Dict) -> Dict:
        """Update contact in Zoho CRM"""
        data = {
            "data": [contact_data]
        }
        
        return self.make_api_request("crm", f"Contacts/{contact_id}", "PUT", data)
    
    def create_crm_deal(self, deal_data: Dict) -> Dict:
        """Create deal in Zoho CRM"""
        data = {
            "data": [
                {
                    "Deal_Name": deal_data.get("deal_name", ""),
                    "Stage": deal_data.get("stage", "Qualification"),
                    "Amount": deal_data.get("amount", 0),
                    "Contact_Name": deal_data.get("contact_id", ""),
                    "Closing_Date": deal_data.get("closing_date", ""),
                    "Type": deal_data.get("type", "Subscription"),
                    "Lead_Source": "News Platform"
                }
            ]
        }
        
        return self.make_api_request("crm", "Deals", "POST", data)
    
    # Books Integration
    def create_customer(self, customer_data: Dict) -> Dict:
        """Create customer in Zoho Books"""
        data = {
            "contact_name": customer_data.get("name", ""),
            "contact_type": "customer",
            "customer_sub_type": "individual",
            "contact_persons": [
                {
                    "first_name": customer_data.get("first_name", ""),
                    "last_name": customer_data.get("last_name", ""),
                    "email": customer_data.get("email", ""),
                    "phone": customer_data.get("phone", "")
                }
            ],
            "billing_address": {
                "address": customer_data.get("address", ""),
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "zip": customer_data.get("zip", ""),
                "country": customer_data.get("country", "")
            }
        }
        
        return self.make_api_request("books", "contacts", "POST", data)
    
    def create_subscription_invoice(self, invoice_data: Dict) -> Dict:
        """Create subscription invoice in Zoho Books"""
        data = {
            "customer_id": invoice_data.get("customer_id", ""),
            "invoice_number": invoice_data.get("invoice_number", ""),
            "date": invoice_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "due_date": invoice_data.get("due_date", ""),
            "line_items": [
                {
                    "name": invoice_data.get("subscription_name", "News Subscription"),
                    "description": invoice_data.get("description", "Monthly news subscription"),
                    "rate": invoice_data.get("amount", 0),
                    "quantity": 1,
                    "tax_id": invoice_data.get("tax_id", "")
                }
            ],
            "payment_terms": 15,
            "payment_terms_label": "Net 15"
        }
        
        return self.make_api_request("books", "invoices", "POST", data)
    
    def record_payment(self, payment_data: Dict) -> Dict:
        """Record payment in Zoho Books"""
        data = {
            "customer_id": payment_data.get("customer_id", ""),
            "payment_mode": payment_data.get("payment_method", "online"),
            "amount": payment_data.get("amount", 0),
            "date": payment_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "reference_number": payment_data.get("reference_number", ""),
            "description": payment_data.get("description", "Subscription payment"),
            "invoices": [
                {
                    "invoice_id": payment_data.get("invoice_id", ""),
                    "amount_applied": payment_data.get("amount", 0)
                }
            ]
        }
        
        return self.make_api_request("books", "customerpayments", "POST", data)
    
    # Commerce Integration
    def create_product(self, product_data: Dict) -> Dict:
        """Create product in Zoho Commerce"""
        data = {
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "price": product_data.get("price", 0),
            "category": product_data.get("category", ""),
            "sku": product_data.get("sku", ""),
            "stock_quantity": product_data.get("stock_quantity", 0),
            "status": "active",
            "digital_product": product_data.get("digital_product", True)
        }
        
        return self.make_api_request("commerce", "products", "POST", data)
    
    def create_order(self, order_data: Dict) -> Dict:
        """Create order in Zoho Commerce"""
        data = {
            "customer_id": order_data.get("customer_id", ""),
            "order_items": order_data.get("items", []),
            "billing_address": order_data.get("billing_address", {}),
            "shipping_address": order_data.get("shipping_address", {}),
            "payment_method": order_data.get("payment_method", ""),
            "order_status": "confirmed",
            "total_amount": order_data.get("total_amount", 0)
        }
        
        return self.make_api_request("commerce", "orders", "POST", data)
    
    # Inventory Integration
    def create_item(self, item_data: Dict) -> Dict:
        """Create item in Zoho Inventory"""
        data = {
            "name": item_data.get("name", ""),
            "description": item_data.get("description", ""),
            "rate": item_data.get("price", 0),
            "sku": item_data.get("sku", ""),
            "category_id": item_data.get("category_id", ""),
            "item_type": "service",
            "product_type": "service",
            "is_taxable": True,
            "status": "active"
        }
        
        return self.make_api_request("inventory", "items", "POST", data)
    
    def update_item_stock(self, item_id: str, stock_data: Dict) -> Dict:
        """Update item stock in Zoho Inventory"""
        data = {
            "quantity_available": stock_data.get("quantity", 0),
            "warehouse_id": stock_data.get("warehouse_id", "")
        }
        
        return self.make_api_request("inventory", f"items/{item_id}/stock", "PUT", data)
    
    # Campaigns Integration
    def create_email_campaign(self, campaign_data: Dict) -> Dict:
        """Create email campaign in Zoho Campaigns"""
        data = {
            "campaign_name": campaign_data.get("name", ""),
            "subject": campaign_data.get("subject", ""),
            "from_email": campaign_data.get("from_email", ""),
            "from_name": campaign_data.get("from_name", ""),
            "reply_to": campaign_data.get("reply_to", ""),
            "html_content": campaign_data.get("html_content", ""),
            "mailing_list_ids": campaign_data.get("mailing_list_ids", []),
            "campaign_type": "regular"
        }
        
        return self.make_api_request("campaigns", "campaigns", "POST", data)
    
    def add_contact_to_list(self, list_id: str, contact_data: Dict) -> Dict:
        """Add contact to mailing list"""
        data = {
            "contact_email": contact_data.get("email", ""),
            "contact_name": contact_data.get("name", ""),
            "first_name": contact_data.get("first_name", ""),
            "last_name": contact_data.get("last_name", ""),
            "phone": contact_data.get("phone", "")
        }
        
        return self.make_api_request("campaigns", f"lists/{list_id}/contacts", "POST", data)
    
    # Analytics Integration
    def get_crm_analytics(self, date_range: str = "last_30_days") -> Dict:
        """Get CRM analytics"""
        params = {
            "date_range": date_range
        }
        
        return self.make_api_request("crm", "analytics/leads", "GET", params=params)
    
    def get_books_analytics(self, date_range: str = "last_30_days") -> Dict:
        """Get Books analytics"""
        params = {
            "date_range": date_range
        }
        
        return self.make_api_request("books", "reports/profit_and_loss", "GET", params=params)
    
    def sync_user_data(self, user_data: Dict) -> Dict:
        """Sync user data across all Zoho services"""
        results = {}
        
        # Create CRM contact
        crm_contact = self.create_crm_contact(user_data)
        results["crm_contact"] = crm_contact
        
        # Create Books customer
        books_customer = self.create_customer(user_data)
        results["books_customer"] = books_customer
        
        # Add to campaigns mailing list
        if user_data.get("email"):
            campaign_contact = self.add_contact_to_list("default_list", user_data)
            results["campaign_contact"] = campaign_contact
        
        return results
    
    def process_subscription_purchase(self, subscription_data: Dict) -> Dict:
        """Process subscription purchase through Zoho ecosystem"""
        results = {}
        
        # Create invoice in Books
        invoice = self.create_subscription_invoice(subscription_data)
        results["invoice"] = invoice
        
        # Record payment
        if subscription_data.get("payment_confirmed"):
            payment = self.record_payment(subscription_data)
            results["payment"] = payment
        
        # Create deal in CRM
        deal_data = {
            "deal_name": f"Subscription - {subscription_data.get('user_name', 'Unknown')}",
            "stage": "Closed Won",
            "amount": subscription_data.get("amount", 0),
            "contact_id": subscription_data.get("contact_id", ""),
            "closing_date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Subscription"
        }
        
        deal = self.create_crm_deal(deal_data)
        results["deal"] = deal
        
        return results
    
    def get_comprehensive_analytics(self) -> Dict:
        """Get comprehensive analytics from all Zoho services"""
        analytics = {}
        
        # CRM analytics
        crm_analytics = self.get_crm_analytics()
        analytics["crm"] = crm_analytics
        
        # Books analytics
        books_analytics = self.get_books_analytics()
        analytics["books"] = books_analytics
        
        # Combine metrics
        analytics["summary"] = {
            "total_contacts": crm_analytics.get("total_contacts", 0),
            "total_deals": crm_analytics.get("total_deals", 0),
            "total_revenue": books_analytics.get("total_revenue", 0),
            "active_subscriptions": crm_analytics.get("active_subscriptions", 0)
        }
        
        return analytics

# Initialize Zoho integration
zoho = ZohoIntegration()

# Export functions
def sync_user_to_zoho(user_data: Dict) -> Dict:
    """Sync user data to Zoho"""
    return zoho.sync_user_data(user_data)

def process_subscription_in_zoho(subscription_data: Dict) -> Dict:
    """Process subscription through Zoho"""
    return zoho.process_subscription_purchase(subscription_data)

def get_zoho_analytics() -> Dict:
    """Get Zoho analytics"""
    return zoho.get_comprehensive_analytics()

def create_zoho_customer(customer_data: Dict) -> Dict:
    """Create customer in Zoho Books"""
    return zoho.create_customer(customer_data)

def create_zoho_invoice(invoice_data: Dict) -> Dict:
    """Create invoice in Zoho Books"""
    return zoho.create_subscription_invoice(invoice_data)

def record_zoho_payment(payment_data: Dict) -> Dict:
    """Record payment in Zoho Books"""
    return zoho.record_payment(payment_data)
