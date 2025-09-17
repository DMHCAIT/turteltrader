"""
Turtle Trader - Breeze API Integration Module
Advanced API client with authentication, rate limiting, and error handling
"""

import time
import json
import hashlib
import hmac
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import requests
import websocket
import threading
from loguru import logger
import pandas as pd
from dataclasses import dataclass
from enum import Enum

from core.config import config, Constants, Utils

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PLACED = "placed"
    PARTIAL = "partial"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ProductType(Enum):
    """Product type enumeration"""
    CASH = "cash"
    MARGIN = "margin"
    FUTURES = "futures"
    OPTIONS = "options"
    BTST = "btst"

@dataclass
class Position:
    """Position data structure"""
    symbol: str
    exchange: str
    product_type: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    unrealized_pnl: float
    
@dataclass
class Order:
    """Order data structure"""
    order_id: str
    symbol: str
    exchange: str
    product_type: str
    action: str
    order_type: str
    quantity: int
    price: float
    status: OrderStatus
    timestamp: datetime

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 100, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def can_make_call(self) -> bool:
        """Check if we can make an API call"""
        with self.lock:
            now = time.time()
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record an API call"""
        with self.lock:
            self.calls.append(time.time())
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        while not self.can_make_call():
            time.sleep(1)
        self.record_call()

class BreezeAPIClient:
    """Advanced Breeze API client with comprehensive features"""
    
    def __init__(self):
        self.api_key = config.get("BREEZE_API", "API_KEY")
        self.api_secret = config.get("BREEZE_API", "API_SECRET")
        self.session_token = None
        self.base_url = config.get("BREEZE_API", "BASE_URL")
        self.rate_limiter = RateLimiter(max_calls=100, time_window=60)
        self.session = requests.Session()
        self.websocket = None
        self.is_connected = False
        self.callbacks = {}
        
        # Setup session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TurtleTrader/1.0'
        })
        
        logger.info("Breeze API client initialized")
    
    def _generate_checksum(self, timestamp: str, data: str = "") -> str:
        """Generate checksum for API authentication"""
        message = timestamp + data + self.api_secret
        return hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _get_headers(self, data: str = "") -> Dict[str, str]:
        """Get headers with authentication"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        checksum = self._generate_checksum(timestamp, data)
        
        headers = {
            'X-Checksum': f"token {checksum}",
            'X-Timestamp': timestamp,
            'X-AppKey': self.api_key,
        }
        
        if self.session_token:
            headers['X-SessionToken'] = self.session_token
            
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated API request with rate limiting"""
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}{endpoint}"
        json_data = json.dumps(data) if data else ""
        headers = self._get_headers(json_data)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, json=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('Status') != 200:
                raise Exception(f"API Error: {result.get('Error', 'Unknown error')}")
            
            return result.get('Success', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"API error: {e}")
            raise
    
    def authenticate(self, session_token: str) -> Dict:
        """Authenticate with Breeze API"""
        self.session_token = session_token
        
        try:
            customer_details = self.get_customer_details()
            self.is_connected = True
            logger.info("Successfully authenticated with Breeze API")
            return customer_details
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def get_customer_details(self) -> Dict:
        """Get customer details"""
        return self._make_request('GET', 'customerdetails')
    
    def get_funds(self) -> Dict:
        """Get account funds information"""
        return self._make_request('GET', 'funds')
    
    def set_funds(self, transaction_type: str, amount: float, segment: str) -> Dict:
        """Set funds for trading segment"""
        data = {
            'transaction_type': transaction_type,
            'amount': str(amount),
            'segment': segment
        }
        return self._make_request('POST', 'funds', data)
    
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        result = self._make_request('GET', 'portfoliopositions')
        positions = []
        
        for pos_data in result:
            position = Position(
                symbol=pos_data.get('stock_code'),
                exchange=pos_data.get('exchange_code'),
                product_type=pos_data.get('product_type'),
                quantity=int(pos_data.get('quantity', 0)),
                average_price=float(pos_data.get('average_price', 0)),
                current_price=float(pos_data.get('ltp', 0)),
                pnl=float(pos_data.get('pnl', 0)),
                unrealized_pnl=float(pos_data.get('unrealized_profit', 0))
            )
            positions.append(position)
        
        return positions
    
    def get_holdings(self) -> Dict:
        """Get demat holdings"""
        return self._make_request('GET', 'dematholdings')
    
    def place_order(self, 
                   symbol: str,
                   exchange: str,
                   product: str,
                   action: str,
                   order_type: str,
                   quantity: int,
                   price: float = 0,
                   stop_loss: float = 0,
                   validity: str = "day",
                   disclosed_quantity: int = 0,
                   expiry_date: Optional[str] = None,
                   right: Optional[str] = None,
                   strike_price: Optional[float] = None,
                   user_remark: str = "") -> str:
        """Place a trading order"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'product': product,
            'action': action,
            'order_type': order_type,
            'quantity': str(quantity),
            'price': str(price),
            'validity': validity,
            'disclosed_quantity': str(disclosed_quantity),
            'user_remark': user_remark[:20]  # Max 20 characters
        }
        
        if stop_loss > 0:
            data['stoploss'] = str(stop_loss)
        
        if expiry_date:
            data['expiry_date'] = expiry_date
        if right:
            data['right'] = right
        if strike_price:
            data['strike_price'] = str(strike_price)
        
        result = self._make_request('POST', 'order', data)
        order_id = result.get('order_id')
        
        logger.info(f"Order placed: {order_id} - {action} {quantity} {symbol}")
        return order_id
    
    def cancel_order(self, order_id: str, exchange: str) -> Dict:
        """Cancel an order"""
        data = {
            'order_id': order_id,
            'exchange_code': exchange
        }
        result = self._make_request('DELETE', 'order', data)
        logger.info(f"Order cancelled: {order_id}")
        return result
    
    def modify_order(self, 
                    order_id: str,
                    exchange: str,
                    quantity: Optional[int] = None,
                    price: Optional[float] = None,
                    order_type: Optional[str] = None,
                    stop_loss: Optional[float] = None) -> Dict:
        """Modify an existing order"""
        
        data = {
            'order_id': order_id,
            'exchange_code': exchange
        }
        
        if quantity:
            data['quantity'] = str(quantity)
        if price:
            data['price'] = str(price)
        if order_type:
            data['order_type'] = order_type
        if stop_loss:
            data['stoploss'] = str(stop_loss)
        
        # Add required fields for F&O
        data.update({
            'expiry_date': "",
            'right': "",
            'strike_price': ""
        })
        
        result = self._make_request('PUT', 'order', data)
        logger.info(f"Order modified: {order_id}")
        return result
    
    def get_order_details(self, order_id: str, exchange: str) -> Dict:
        """Get details of a specific order"""
        data = {
            'order_id': order_id,
            'exchange_code': exchange
        }
        return self._make_request('GET', 'order', data)
    
    def get_order_list(self, exchange: str, from_date: str, to_date: str) -> List[Dict]:
        """Get list of orders for a date range"""
        data = {
            'exchange_code': exchange,
            'from_date': from_date,
            'to_date': to_date
        }
        return self._make_request('GET', 'order', data)
    
    def get_quotes(self, 
                  symbol: str,
                  exchange: str,
                  product_type: str = "cash",
                  expiry_date: str = "",
                  right: str = "",
                  strike_price: str = "0") -> Dict:
        """Get real-time quotes"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'product_type': product_type,
            'expiry_date': expiry_date,
            'right': right,
            'strike_price': strike_price
        }
        return self._make_request('GET', 'quotes', data)
    
    def get_historical_data(self,
                           symbol: str,
                           exchange: str,
                           product_type: str,
                           interval: str,
                           from_date: str,
                           to_date: str,
                           expiry_date: str = "",
                           right: str = "",
                           strike_price: str = "0") -> pd.DataFrame:
        """Get historical OHLCV data"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'product_type': product_type,
            'interval': interval,
            'from_date': from_date,
            'to_date': to_date,
            'expiry_date': expiry_date,
            'right': right,
            'strike_price': strike_price
        }
        
        result = self._make_request('GET', 'historicalcharts', data)
        
        # Convert to DataFrame
        df = pd.DataFrame(result)
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            
            # Convert price columns to float
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if 'volume' in df.columns:
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        return df
    
    def get_option_chain(self, 
                        symbol: str,
                        exchange: str,
                        expiry_date: str,
                        product_type: str = "options") -> Dict:
        """Get option chain data"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'expiry_date': expiry_date,
            'product_type': product_type,
            'right': "",
            'strike_price': ""
        }
        return self._make_request('GET', 'OptionChain', data)
    
    def square_off_position(self,
                           symbol: str,
                           exchange: str,
                           product: str,
                           action: str,
                           quantity: int,
                           order_type: str = "market",
                           expiry_date: str = "",
                           right: str = "",
                           strike_price: str = "0") -> str:
        """Square off a position"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'product_type': product,
            'action': action,
            'quantity': str(quantity),
            'order_type': order_type,
            'price': "0",
            'validity': "day",
            'expiry_date': expiry_date,
            'right': right,
            'strike_price': strike_price,
            'disclosed_quantity': "0",
            'stoploss_price': "0",
            'validity_date': "",
            'trade_password': "",
            'source_flag': ""
        }
        
        result = self._make_request('POST', 'squareoff', data)
        order_id = result.get('order_id')
        logger.info(f"Position squared off: {order_id}")
        return order_id
    
    def get_margin_calculator(self, positions: List[Dict], exchange: str) -> Dict:
        """Calculate margin requirements"""
        data = {
            'list_of_positions': positions,
            'exchange_code': exchange
        }
        return self._make_request('POST', 'margincalculator', data)
    
    def preview_order(self, 
                     symbol: str,
                     exchange: str,
                     product: str,
                     order_type: str,
                     price: float,
                     action: str,
                     quantity: int) -> Dict:
        """Preview order charges and details"""
        
        data = {
            'stock_code': symbol,
            'exchange_code': exchange,
            'product': product,
            'order_type': order_type,
            'price': str(price),
            'action': action,
            'quantity': str(quantity),
            'specialflag': 'N'
        }
        return self._make_request('GET', 'preview_order', data)
    
    def get_trade_list(self,
                      from_date: str,
                      to_date: str,
                      exchange: str,
                      product_type: str = "",
                      action: str = "",
                      symbol: str = "") -> List[Dict]:
        """Get trade history"""
        
        data = {
            'from_date': from_date,
            'to_date': to_date,
            'exchange_code': exchange,
            'product_type': product_type,
            'action': action,
            'stock_code': symbol
        }
        return self._make_request('GET', 'trades', data)
    
    def get_names(self, exchange: str, symbol: str) -> Dict:
        """Get ICICI specific stock codes/tokens"""
        data = {
            'exchange_code': exchange,
            'stock_code': symbol
        }
        # Note: This endpoint might need different implementation
        # as it's not clearly documented in the API
        try:
            return self._make_request('GET', 'names', data)
        except:
            logger.warning(f"Could not get names for {symbol}")
            return {}
    
    def close(self):
        """Close API connection and cleanup"""
        if self.websocket:
            self.websocket.close()
        self.session.close()
        logger.info("Breeze API client closed")

# Global API client instance
api_client = BreezeAPIClient()

# Export main classes
__all__ = [
    'BreezeAPIClient',
    'OrderStatus',
    'ProductType',
    'Position',
    'Order',
    'api_client'
]
