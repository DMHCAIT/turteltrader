"""
🚀 KITE API CLIENT - ZERODHA INTEGRATION
======================================

Complete Kite Connect API integration for live trading
Supports real-time data, portfolio management, and order execution
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import configparser
from loguru import logger

try:
    from kiteconnect import KiteConnect
except ImportError:
    logger.error("❌ kiteconnect library not found. Install with: pip install kiteconnect")
    raise

class KiteAPIClient:
    """Kite Connect API Client for Zerodha integration"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize Kite Connect client"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Get API credentials from config
        self.api_key = self.config.get('KITE_API', 'API_KEY', fallback='')
        self.api_secret = self.config.get('KITE_API', 'API_SECRET', fallback='')
        self.access_token = self.config.get('KITE_API', 'ACCESS_TOKEN', fallback='')
        
        if not self.api_key:
            raise ValueError("❌ Kite API key not found in config.ini")
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.api_key)
        
        if self.access_token:
            self.kite.set_access_token(self.access_token)
            logger.info("✅ Kite API client initialized with access token")
        else:
            logger.warning("⚠️ No access token found - authentication required")
    
    def generate_session(self, request_token: str) -> str:
        """Generate session using request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            
            # Update config with access token
            self.config.set('KITE_API', 'ACCESS_TOKEN', self.access_token)
            with open('config.ini', 'w') as f:
                self.config.write(f)
            
            self.kite.set_access_token(self.access_token)
            logger.info("✅ Kite session generated successfully")
            return self.access_token
            
        except Exception as e:
            logger.error(f"❌ Failed to generate Kite session: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            profile = self.kite.profile()
            if profile and 'user_id' in profile:
                logger.info(f"✅ Kite API connection successful - User: {profile['user_id']}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Kite API connection failed: {e}")
            return False
    
    def get_profile(self) -> Optional[Dict]:
        """Get user profile"""
        try:
            return self.kite.profile()
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            return None
    
    def get_funds(self) -> Optional[Dict]:
        """Get account funds"""
        try:
            margins = self.kite.margins()
            if margins:
                return margins.get('equity', {})
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get funds: {e}")
            return None
    
    def get_positions(self) -> Optional[Dict]:
        """Get current positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            return None
    
    def get_holdings(self) -> Optional[List]:
        """Get portfolio holdings"""
        try:
            return self.kite.holdings()
        except Exception as e:
            logger.error(f"❌ Failed to get holdings: {e}")
            return None
    
    def get_quote(self, instruments: List[str]) -> Optional[Dict]:
        """Get live quotes for instruments"""
        try:
            return self.kite.quote(instruments)
        except Exception as e:
            logger.error(f"❌ Failed to get quote: {e}")
            return None
    
    def get_ltp(self, instruments: List[str]) -> Optional[Dict]:
        """Get Last Traded Price for instruments"""
        try:
            return self.kite.ltp(instruments)
        except Exception as e:
            logger.error(f"❌ Failed to get LTP: {e}")
            return None
    
    def get_historical_data(self, instrument_token: int, from_date: datetime, 
                           to_date: datetime, interval: str = "day") -> Optional[pd.DataFrame]:
        """Get historical data"""
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                return df
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical data: {e}")
            return None
    
    def get_instruments(self, exchange: str = "NSE") -> Optional[pd.DataFrame]:
        """Get instruments list"""
        try:
            instruments = self.kite.instruments(exchange)
            return pd.DataFrame(instruments)
        except Exception as e:
            logger.error(f"❌ Failed to get instruments: {e}")
            return None
    
    def place_order(self, variety: str, exchange: str, tradingsymbol: str,
                   transaction_type: str, quantity: int, product: str,
                   order_type: str, price: float = 0, validity: str = "DAY") -> Optional[str]:
        """Place an order"""
        try:
            order_id = self.kite.place_order(
                variety=variety,
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=product,
                order_type=order_type,
                price=price,
                validity=validity
            )
            
            logger.info(f"✅ Order placed successfully - ID: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def get_orders(self) -> Optional[List]:
        """Get all orders"""
        try:
            return self.kite.orders()
        except Exception as e:
            logger.error(f"❌ Failed to get orders: {e}")
            return None
    
    def get_order_history(self, order_id: str) -> Optional[List]:
        """Get order history"""
        try:
            return self.kite.order_history(order_id)
        except Exception as e:
            logger.error(f"❌ Failed to get order history: {e}")
            return None
    
    def cancel_order(self, variety: str, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.kite.cancel_order(variety=variety, order_id=order_id)
            logger.info(f"✅ Order cancelled - ID: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel order: {e}")
            return False
    
    def modify_order(self, variety: str, order_id: str, **kwargs) -> bool:
        """Modify an order"""
        try:
            self.kite.modify_order(variety=variety, order_id=order_id, **kwargs)
            logger.info(f"✅ Order modified - ID: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to modify order: {e}")
            return False

# Global instance
kite_client = None

def get_kite_client() -> KiteAPIClient:
    """Get global Kite API client instance"""
    global kite_client
    if kite_client is None:
        kite_client = KiteAPIClient()
    return kite_client

# Export main class and function
__all__ = ['KiteAPIClient', 'get_kite_client']