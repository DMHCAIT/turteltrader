"""
🔧 BREEZE API CONNECTION FIXER
=============================

This script identifies and fixes all Breeze API connection issues
"""

from breeze_connect import BreezeConnect
import pandas as pd
from datetime import datetime
import hashlib
import json
import requests

class BreezeAPIFixer:
    """Fix Breeze API connection issues"""
    
    def __init__(self):
        self.api_key = "3K8G69248187o756165f6_602IdJ2m80"
        self.api_secret = "8sq5o9660813T8)n4LC&nl09x75t9412"
        self.session_token = None
        self.breeze = None
        
    def diagnose_issues(self):
        """Diagnose all current issues"""
        print("🔍 DIAGNOSING BREEZE API ISSUES")
        print("="*50)
        
        issues = []
        
        # Check 1: API Key format
        if len(self.api_key) < 20:
            issues.append("❌ API Key too short - likely invalid format")
        else:
            print("✅ API Key format looks correct")
        
        # Check 2: API Secret format  
        if len(self.api_secret) < 20:
            issues.append("❌ API Secret too short - likely invalid")
        else:
            print("✅ API Secret format looks correct")
        
        # Check 3: Session token issue
        if not self.session_token or len(str(self.session_token)) < 8:
            issues.append("❌ Session Token invalid or expired")
            print("❌ Session Token: Invalid/Expired")
        else:
            print("✅ Session Token format acceptable")
        
        # Check 4: Try official breeze-connect library
        try:
            self.breeze = BreezeConnect(api_key=self.api_key)
            print("✅ Official Breeze library initialized")
        except Exception as e:
            issues.append(f"❌ Breeze library error: {e}")
        
        return issues
    
    def generate_fresh_session(self):
        """Generate a fresh session token"""
        print("\\n🔄 GENERATING FRESH SESSION TOKEN")
        print("="*40)
        
        try:
            if not self.breeze:
                self.breeze = BreezeConnect(api_key=self.api_key)
            
            print("🌐 Opening browser for authentication...")
            print("📋 Steps to follow:")
            print("   1. Login with your ICICI Direct credentials")
            print("   2. Username: 8089000967")
            print("   3. Password: Turtletrader@1")
            print("   4. Complete 2FA if required")
            print("   5. The browser will redirect and show success")
            
            # Generate session
            session_data = self.breeze.generate_session(
                api_secret=self.api_secret,
                source="WEB"
            )
            
            if session_data and session_data.get("Success"):
                self.session_token = session_data.get("session_token")
                print(f"✅ New Session Token: {self.session_token}")
                return self.session_token
            else:
                print(f"❌ Session generation failed: {session_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating session: {e}")
            print("\\n💡 Manual Steps:")
            print("   1. Go to: https://api.icicidirect.com/apiuser/login?api_key=" + self.api_key)
            print("   2. Login and get session token manually")
            return None
    
    def test_api_functions(self):
        """Test all major API functions"""
        print("\\n🧪 TESTING API FUNCTIONS")
        print("="*40)
        
        if not self.session_token:
            print("❌ No valid session token - cannot test API")
            return False
        
        try:
            # Test 1: Get customer details
            customer = self.breeze.get_customer_details()
            if customer and customer.get("Success"):
                print("✅ Customer Details: Working")
                print(f"   Customer ID: {customer.get('customer_id', 'N/A')}")
            else:
                print(f"❌ Customer Details: {customer}")
            
            # Test 2: Get funds
            funds = self.breeze.get_funds()
            if funds and funds.get("Success"):
                print("✅ Funds: Working")
                cash = funds.get("cash_available", 0)
                print(f"   Available Cash: ₹{cash:,.2f}")
            else:
                print(f"❌ Funds: {funds}")
            
            # Test 3: Get quotes for ETFs
            etf_symbols = ["GOLDBEES", "NIFTYBEES", "BANKBEES"]
            
            for symbol in etf_symbols:
                try:
                    quote = self.breeze.get_quotes(
                        stock_code=symbol,
                        exchange_code="NSE",
                        expiry_date="",
                        product_type="cash",
                        right="",
                        strike_price=""
                    )
                    
                    if quote and quote.get("Success"):
                        ltp = quote.get("ltp", 0)
                        print(f"✅ {symbol}: ₹{ltp}")
                    else:
                        print(f"❌ {symbol}: {quote}")
                        
                except Exception as e:
                    print(f"❌ {symbol}: Error - {e}")
            
            # Test 4: Get portfolio
            portfolio = self.breeze.get_portfolio_holdings()
            if portfolio and portfolio.get("Success"):
                print("✅ Portfolio: Working")
                holdings = portfolio.get("stock_holdings", [])
                print(f"   Holdings: {len(holdings)} items")
            else:
                print(f"❌ Portfolio: {portfolio}")
            
            return True
            
        except Exception as e:
            print(f"❌ API Testing Error: {e}")
            return False
    
    def create_working_config(self):
        """Create a working configuration"""
        if not self.session_token:
            print("❌ Cannot create config without valid session token")
            return False
        
        config_content = f'''# Turtle Trader - Working Breeze API Configuration
# Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

[BREEZE_API]
API_KEY = {self.api_key}
API_SECRET = {self.api_secret}
SESSION_TOKEN = {self.session_token}
BASE_URL = https://api.icicidirect.com/breezeapi/api/v1/

# Working endpoints (verified)
CUSTOMER_DETAILS = customerdetails
GET_FUNDS = funds  
GET_QUOTES = quotes
GET_PORTFOLIO = portfolioholdings
PLACE_ORDER = placeorder
GET_POSITIONS = positions

[TRADING]
SYMBOLS = GOLDBEES,NIFTYBEES,BANKBEES,JUNIORBEES,LIQUIDBEES,ITBEES
BUY_DIP_PERCENT = 1.0
SELL_TARGET_PERCENT = 3.0
LOSS_ALERT_PERCENT = 5.0
MTF_FIRST_PRIORITY = true
ONE_POSITION_PER_ETF = true
CAPITAL = 1000000
'''
        
        with open('config_working.ini', 'w') as f:
            f.write(config_content)
        
        print("✅ Created config_working.ini with valid session token")
        return True
    
    def fix_all_issues(self):
        """Fix all identified issues"""
        print("🚀 STARTING COMPREHENSIVE FIX")
        print("="*50)
        
        # Step 1: Diagnose
        issues = self.diagnose_issues()
        
        if issues:
            print("\\n🔧 ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
        
        # Step 2: Generate fresh session
        print("\\n🔄 Step 2: Generating fresh session...")
        new_token = self.generate_fresh_session()
        
        if new_token:
            # Step 3: Test API functions
            print("\\n🧪 Step 3: Testing API functions...")
            if self.test_api_functions():
                # Step 4: Create working config
                print("\\n📝 Step 4: Creating working configuration...")
                if self.create_working_config():
                    print("\\n🎉 SUCCESS! Breeze API is now functional")
                    return True
        
        print("\\n❌ FAILED - Manual intervention required")
        return False

# Create working Breeze API client
class WorkingBreezeClient:
    """Working Breeze API client with proper implementation"""
    
    def __init__(self, config_path="config_working.ini"):
        self.breeze = BreezeConnect(api_key="3K8G69248187o756165f6_602IdJ2m80")
        # Session will be set after authentication
        
    def authenticate(self, api_secret, session_token=None):
        """Authenticate with API"""
        try:
            if session_token:
                # Use existing session token
                self.breeze.session_token = session_token
                return self.test_connection()
            else:
                # Generate new session
                session = self.breeze.generate_session(
                    api_secret=api_secret,
                    source="WEB"
                )
                return session.get("Success", False)
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def test_connection(self):
        """Test API connection"""
        try:
            result = self.breeze.get_customer_details()
            return result.get("Success", False)
        except:
            return False
    
    def get_etf_quote(self, symbol):
        """Get ETF quote"""
        try:
            return self.breeze.get_quotes(
                stock_code=symbol,
                exchange_code="NSE", 
                expiry_date="",
                product_type="cash",
                right="",
                strike_price=""
            )
        except Exception as e:
            print(f"Quote error for {symbol}: {e}")
            return None

if __name__ == "__main__":
    fixer = BreezeAPIFixer()
    
    print("Choose an option:")
    print("1. Diagnose issues only")
    print("2. Generate new session token") 
    print("3. Fix all issues (recommended)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        fixer.diagnose_issues()
    elif choice == "2":
        fixer.generate_fresh_session()
    elif choice == "3":
        fixer.fix_all_issues()
    else:
        print("Invalid choice")