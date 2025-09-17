"""
🔧 FIXED BREEZE API CLIENT
=========================

This is a properly working Breeze API client using the official breeze-connect library
"""

from breeze_connect import BreezeConnect
import configparser
from datetime import datetime
from loguru import logger
import json
from typing import Dict, List, Optional

class FixedBreezeAPIClient:
    """Working Breeze API client with proper implementation"""
    
    def __init__(self, config_path="config.ini"):
        """Initialize with config file"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # API Configuration
        self.api_key = self.config.get('BREEZE_API', 'API_KEY', fallback='')
        self.api_secret = self.config.get('BREEZE_API', 'API_SECRET', fallback='')
        self.session_token = self.config.get('BREEZE_API', 'SESSION_TOKEN', fallback='')
        
        # Initialize Breeze Connect
        self.breeze = BreezeConnect(api_key=self.api_key)
        self.is_authenticated = False
        
        # Set session token if available
        if self.session_token:
            self.breeze.session_token = self.session_token
            self.is_authenticated = True
            
        logger.info("Fixed Breeze API client initialized")
    
    def generate_session(self) -> bool:
        """Generate fresh session token"""
        try:
            logger.info("Generating fresh session token...")
            
            session_data = self.breeze.generate_session(
                api_secret=self.api_secret,
                source="WEB"
            )
            
            if session_data and session_data.get("Success"):
                self.session_token = session_data.get("session_token")
                self.is_authenticated = True
                
                # Update config file with new token
                self.config.set('BREEZE_API', 'SESSION_TOKEN', self.session_token)
                with open('config.ini', 'w') as f:
                    self.config.write(f)
                
                logger.info("✅ Session token generated successfully")
                return True
            else:
                logger.error(f"Session generation failed: {session_data}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating session: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            if not self.is_authenticated:
                logger.warning("Not authenticated - attempting to generate session")
                if not self.generate_session():
                    return False
            
            # Test with customer details
            customer = self.breeze.get_customer_details()
            
            if customer and customer.get("Success"):
                logger.info("✅ API connection successful")
                return True
            else:
                logger.error(f"API test failed: {customer}")
                
                # Try regenerating session if it failed
                if customer and "session" in str(customer).lower():
                    logger.info("Session expired - regenerating...")
                    return self.generate_session()
                
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_account_funds(self) -> Optional[Dict]:
        """Get account fund details"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            funds = self.breeze.get_funds()
            
            if funds and funds.get("Success"):
                return {
                    'available_cash': float(funds.get('cash_available', 0)),
                    'margin_used': float(funds.get('margin_used', 0)),
                    'margin_available': float(funds.get('margin_available', 0)),
                    'total_cash': float(funds.get('total_cash_available', 0))
                }
            else:
                logger.error(f"Funds API failed: {funds}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting funds: {e}")
            return None
    
    def get_quote(self, stock_code: str, exchange_code: str = "NSE") -> Optional[Dict]:
        """Get real-time quote for ETF"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            quote = self.breeze.get_quotes(
                stock_code=stock_code,
                exchange_code=exchange_code,
                expiry_date="",
                product_type="cash",
                right="",
                strike_price=""
            )
            
            if quote and quote.get("Success"):
                return {
                    'symbol': stock_code,
                    'ltp': float(quote.get('ltp', 0)),
                    'open': float(quote.get('open', 0)),
                    'high': float(quote.get('high', 0)),
                    'low': float(quote.get('low', 0)),
                    'previous_close': float(quote.get('prev_close', 0)),
                    'change': float(quote.get('change', 0)),
                    'change_percent': float(quote.get('percentage_change', 0)),
                    'volume': int(quote.get('volume', 0)),
                    'timestamp': datetime.now()
                }
            else:
                logger.error(f"Quote failed for {stock_code}: {quote}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting quote for {stock_code}: {e}")
            return None
    
    def get_portfolio(self) -> Optional[List[Dict]]:
        """Get portfolio holdings"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            portfolio = self.breeze.get_portfolio_holdings()
            
            if portfolio and portfolio.get("Success"):
                holdings = []
                for holding in portfolio.get("stock_holdings", []):
                    holdings.append({
                        'symbol': holding.get('stock_code', ''),
                        'quantity': int(holding.get('quantity', 0)),
                        'average_price': float(holding.get('average_price', 0)),
                        'current_price': float(holding.get('current_price', 0)),
                        'pnl': float(holding.get('pnl', 0)),
                        'pnl_percent': float(holding.get('pnl_percentage', 0))
                    })
                return holdings
            else:
                logger.error(f"Portfolio API failed: {portfolio}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return None
    
    def place_order(self, 
                   stock_code: str,
                   exchange_code: str = "NSE",
                   product: str = "MTF",  # MTF or CNC
                   action: str = "BUY",   # BUY or SELL
                   order_type: str = "MARKET",  # MARKET or LIMIT
                   quantity: int = 1,
                   price: float = 0,  # 0 for market orders
                   stoploss: float = 0,
                   validity: str = "DAY") -> Optional[str]:
        """Place order with proper error handling"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            logger.info(f"Placing {action} order for {quantity} {stock_code}")
            logger.info(f"Product: {product} | Type: {order_type} | Price: ₹{price}")
            
            order = self.breeze.place_order(
                stock_code=stock_code,
                exchange_code=exchange_code,
                product=product,
                action=action,
                order_type=order_type,
                stoploss=str(stoploss),
                quantity=str(quantity),
                price=str(price),
                validity=validity,
                validity_date="",
                disclosed_quantity="",
                expiry_date="",
                right="",
                strike_price="",
                user_remark="TurtleTrader"
            )
            
            if order and order.get("Success"):
                order_id = order.get("order_id")
                logger.info(f"✅ Order placed successfully! Order ID: {order_id}")
                return order_id
            else:
                logger.error(f"Order failed: {order}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            order = self.breeze.get_order_detail(order_id=order_id)
            
            if order and order.get("Success"):
                return {
                    'order_id': order_id,
                    'status': order.get('order_status', ''),
                    'quantity': int(order.get('quantity', 0)),
                    'filled_quantity': int(order.get('filled_quantity', 0)),
                    'price': float(order.get('price', 0)),
                    'average_price': float(order.get('average_price', 0))
                }
            else:
                logger.error(f"Order status failed: {order}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return False
            
            result = self.breeze.cancel_order(order_id=order_id)
            
            if result and result.get("Success"):
                logger.info(f"✅ Order {order_id} cancelled successfully")
                return True
            else:
                logger.error(f"Cancel failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_positions(self) -> Optional[List[Dict]]:
        """Get current positions"""
        try:
            if not self.is_authenticated and not self.test_connection():
                return None
            
            positions = self.breeze.get_positions()
            
            if positions and positions.get("Success"):
                pos_list = []
                for pos in positions.get("positions", []):
                    pos_list.append({
                        'symbol': pos.get('stock_code', ''),
                        'product': pos.get('product', ''),
                        'quantity': int(pos.get('quantity', 0)),
                        'average_price': float(pos.get('average_price', 0)),
                        'current_price': float(pos.get('current_price', 0)),
                        'pnl': float(pos.get('pnl', 0)),
                        'pnl_percent': float(pos.get('pnl_percentage', 0))
                    })
                return pos_list
            else:
                logger.error(f"Positions API failed: {positions}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None

# Create global instance
fixed_breeze_client = FixedBreezeAPIClient()

if __name__ == "__main__":
    print("🔧 TESTING FIXED BREEZE API CLIENT")
    print("="*50)
    
    client = FixedBreezeAPIClient()
    
    # Test connection
    if client.test_connection():
        print("✅ Connection successful")
        
        # Test funds
        funds = client.get_account_funds()
        if funds:
            print(f"💰 Available Cash: ₹{funds['available_cash']:,.2f}")
        
        # Test ETF quotes
        for symbol in ['GOLDBEES', 'NIFTYBEES', 'BANKBEES']:
            quote = client.get_quote(symbol)
            if quote:
                print(f"📊 {symbol}: ₹{quote['ltp']:.2f} ({quote['change_percent']:+.2f}%)")
        
        print("🎉 Fixed Breeze API client is working!")
        
    else:
        print("❌ Connection failed")
        print("💡 Run breeze_api_fixer.py to generate fresh session token")