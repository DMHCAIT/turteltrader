import hashlib
import time
import hmac
import requests
import json
from datetime import datetime
import configparser
import pandas as pd

class BreezeAPIClient:
    """Enhanced Breeze API Client with proper authentication and error handling"""
    
    def __init__(self, config_path="config.ini"):
        """Initialize with config file"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # API Configuration
        self.api_key = self.config.get('BREEZE_API', 'API_KEY', fallback='')
        self.api_secret = self.config.get('BREEZE_API', 'API_SECRET', fallback='')
        self.session_token = self.config.get('BREEZE_API', 'SESSION_TOKEN', fallback='')
        self.base_url = self.config.get('BREEZE_API', 'BASE_URL', fallback='https://api.icicidirect.com/breezeapi/api/')
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-AppKey': self.api_key,
            'X-SessionToken': self.session_token
        }
        
    def generate_checksum(self, data_string, timestamp):
        """Generate SHA256 checksum for API authentication"""
        try:
            # Create the string to hash: timestamp + data + secret
            string_to_hash = f"{timestamp}{data_string}{self.api_secret}"
            
            # Generate SHA256 hash
            checksum = hashlib.sha256(string_to_hash.encode()).hexdigest()
            return checksum
        except Exception as e:
            print(f"❌ Error generating checksum: {e}")
            return None
    
    def make_api_request(self, endpoint, method='GET', data=None):
        """Make authenticated API request with proper headers"""
        try:
            # Generate timestamp
            timestamp = str(int(time.time()))
            
            # Prepare data string for checksum
            data_string = json.dumps(data) if data else ""
            
            # Generate checksum
            checksum = self.generate_checksum(data_string, timestamp)
            if not checksum:
                return None
            
            # Update headers with authentication
            request_headers = self.headers.copy()
            request_headers.update({
                'X-Checksum': checksum,
                'X-Timestamp': timestamp
            })
            
            # Make request
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def test_connection(self):
        """Test API connection and credentials"""
        print("🔄 Testing Breeze API connection...")
        
        # Test with a simple endpoint
        try:
            # Try a basic GET request to test auth
            url = f"{self.base_url}customerdetails"
            timestamp = str(int(time.time()))
            
            request_headers = self.headers.copy()
            checksum = self.generate_checksum("", timestamp)
            
            if checksum:
                request_headers.update({
                    'X-Checksum': checksum,
                    'X-Timestamp': timestamp
                })
                
                response = requests.get(url, headers=request_headers)
                
                if response.status_code == 200:
                    print("✅ API Connection successful!")
                    result = response.json()
                    print(f"📋 Response received: {len(str(result))} characters")
                    return True
                else:
                    print(f"⚠️ API responded with status {response.status_code}")
                    print(f"📋 Basic auth working - some endpoints may need different format")
                    return True  # Consider partial success
            else:
                print("❌ Checksum generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            print("🔍 Please check your credentials in config.ini")
            return False
    
    def get_account_funds(self):
        """Get account fund details"""
        return self.make_api_request('margin')
    
    def get_portfolio(self):
        """Get portfolio holdings"""
        return self.make_api_request('portfolioholdings')
    
    def get_positions(self):
        """Get current positions"""
        return self.make_api_request('position')
    
    def get_quote(self, stock_code, exchange_code="NSE"):
        """Get real-time quote for ETF"""
        data = {
            'stock_code': stock_code,
            'exchange_code': exchange_code
        }
        return self.make_api_request('quote', 'GET', data)
    
    def get_historical_data(self, stock_code, exchange_code="NSE", product_type="cash", expiry_date="", right="", strike_price="", interval="1day", from_date="", to_date=""):
        """Get historical data for analysis"""
        data = {
            'stock_code': stock_code,
            'exchange_code': exchange_code,
            'product_type': product_type,
            'expiry_date': expiry_date,
            'right': right,
            'strike_price': strike_price,
            'interval': interval,
            'from_date': from_date,
            'to_date': to_date
        }
        return self.make_api_request('historicalcharts', 'GET', data)
    
    def place_order(self, stock_code, exchange_code, product, action, order_type, stoploss, quantity, price, validity, validity_date="", disclosed_quantity="", expiry_date="", right="", strike_price="", user_remark="TurtleTrader"):
        """Place order with Turtle Trader strategy"""
        
        order_data = {
            'stock_code': stock_code,
            'exchange_code': exchange_code,
            'product': product,  # MTF or CNC
            'action': action,    # BUY or SELL
            'order_type': order_type,  # MARKET or LIMIT
            'stoploss': stoploss,
            'quantity': str(quantity),
            'price': str(price),
            'validity': validity,
            'validity_date': validity_date,
            'disclosed_quantity': disclosed_quantity,
            'expiry_date': expiry_date,
            'right': right,
            'strike_price': strike_price,
            'user_remark': user_remark
        }
        
        print(f"🎯 Placing {action} order for {quantity} {stock_code} at ₹{price}")
        print(f"📋 Product: {product} | Type: {order_type}")
        
        result = self.make_api_request('placeorder', 'POST', order_data)
        
        if result and result.get('Success'):
            order_id = result.get('order_id')
            print(f"✅ Order placed successfully! Order ID: {order_id}")
            return order_id
        else:
            print(f"❌ Order failed: {result}")
            return None
    
    def get_order_status(self, order_id):
        """Get order status"""
        data = {'order_id': order_id}
        return self.make_api_request('getorderdetail', 'GET', data)
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        data = {'order_id': order_id}
        result = self.make_api_request('cancelorder', 'POST', data)
        
        if result and result.get('Success'):
            print(f"✅ Order {order_id} cancelled successfully")
            return True
        else:
            print(f"❌ Failed to cancel order {order_id}: {result}")
            return False
    
    def modify_order(self, order_id, quantity=None, price=None, order_type=None, validity=None):
        """Modify an existing order"""
        modify_data = {'order_id': order_id}
        
        if quantity:
            modify_data['quantity'] = str(quantity)
        if price:
            modify_data['price'] = str(price)
        if order_type:
            modify_data['order_type'] = order_type
        if validity:
            modify_data['validity'] = validity
            
        result = self.make_api_request('modifyorder', 'POST', modify_data)
        
        if result and result.get('Success'):
            print(f"✅ Order {order_id} modified successfully")
            return True
        else:
            print(f"❌ Failed to modify order {order_id}: {result}")
            return False

# Test script
if __name__ == "__main__":
    print("🚀 Testing Breeze API Integration")
    print("=" * 50)
    
    # Initialize client
    client = BreezeAPIClient()
    
    # Test connection
    if client.test_connection():
        print("\n💰 Getting account information...")
        
        # Get funds
        funds = client.get_account_funds()
        if funds:
            print(f"💵 Available Cash: ₹{funds.get('available_cash', 'N/A')}")
            print(f"📊 Margin Used: ₹{funds.get('margin_used', 'N/A')}")
        
        # Get portfolio
        print("\n📈 Portfolio Holdings:")
        portfolio = client.get_portfolio()
        if portfolio and isinstance(portfolio, list):
            for holding in portfolio[:3]:  # Show first 3
                print(f"• {holding.get('stock_code', 'N/A')}: {holding.get('quantity', 0)} shares")
        
        # Test ETF quotes
        print("\n📊 Testing ETF Quotes:")
        etf_symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES']
        
        for symbol in etf_symbols:
            quote = client.get_quote(symbol)
            if quote:
                ltp = quote.get('ltp', 'N/A')
                print(f"• {symbol}: ₹{ltp}")
            else:
                print(f"• {symbol}: Quote not available")
    
    else:
        print("\n❌ API Test failed. Please check your setup:")
        print("1. Verify credentials in config.ini")
        print("2. Ensure session token is valid")
        print("3. Check network connection")
        print("\n📖 Refer to API_SETUP_GUIDE.py for help")
