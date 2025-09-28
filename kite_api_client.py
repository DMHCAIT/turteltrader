"""
KITE API CLIENT - PRODUCTION READY
Clean Kite API client for real data only
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from kiteconnect import KiteConnect
from core.config import get_config
from loguru import logger

@dataclass
class Position:
    symbol: str
    quantity: int
    average_price: float
    ltp: float
    pnl: float
    day_change: float
    
@dataclass 
class Order:
    order_id: str
    symbol: str
    transaction_type: str
    quantity: int
    price: float
    status: str
    timestamp: datetime

class KiteAPIClient:
    """Production Kite API Client - Real data only"""
    
    def __init__(self, api_key: str = None, access_token: str = None):
        config = get_config()
        
        self.api_key = api_key or config.get('KITE_API', 'api_key')
        self.access_token = access_token or config.get('KITE_API', 'access_token')
        
        if not self.api_key or not self.access_token:
            raise ValueError("Kite API credentials required")
        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        logger.info("Kite API client initialized")
    
    def test_connection(self) -> bool:
        try:
            profile = self.kite.profile()
            if profile and 'user_id' in profile:
                logger.info(f"Kite API connection successful - User: {profile['user_id']}")
                return True
            return False
        except Exception as e:
            logger.error(f"Kite API connection failed: {e}")
            return False
    
    def get_funds(self) -> Optional[Dict[str, Any]]:
        try:
            margins = self.kite.margins()
            if margins and 'equity' in margins:
                logger.info("Account margins fetched successfully")
                return margins
            return None
        except Exception as e:
            logger.error(f"Failed to get margins: {e}")
            return None
    
    def get_ltp(self, symbols: List[str]) -> Dict[str, float]:
        try:
            formatted_symbols = [f"NSE:{symbol}" for symbol in symbols]
            ltp_data = self.kite.ltp(formatted_symbols)
            
            result = {}
            for symbol in symbols:
                nse_symbol = f"NSE:{symbol}"
                if nse_symbol in ltp_data and 'last_price' in ltp_data[nse_symbol]:
                    result[symbol] = ltp_data[nse_symbol]['last_price']
                else:
                    logger.warning(f"No LTP data for {symbol}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to get LTP: {e}")
            return {}
    
    def get_positions(self) -> List[Position]:
        try:
            positions_data = self.kite.positions()
            logger.info("Positions fetched successfully")
            
            positions = []
            if positions_data and 'day' in positions_data:
                for pos in positions_data['day']:
                    if pos['quantity'] != 0:
                        positions.append(Position(
                            symbol=pos['tradingsymbol'],
                            quantity=pos['quantity'],
                            average_price=pos['average_price'],
                            ltp=pos['last_price'],
                            pnl=pos['pnl'],
                            day_change=pos['day_change']
                        ))
            
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_quote(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        try:
            formatted_symbols = [f"NSE:{symbol}" for symbol in symbols]
            quote_data = self.kite.quote(formatted_symbols)
            
            result = {}
            for symbol in symbols:
                nse_symbol = f"NSE:{symbol}"
                if nse_symbol in quote_data:
                    result[symbol] = quote_data[nse_symbol]
                else:
                    logger.warning(f"No quote data for {symbol}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to get quotes: {e}")
            return {}

# Global client instance
_kite_client = None

def get_kite_client() -> KiteAPIClient:
    global _kite_client
    
    if _kite_client is None:
        try:
            _kite_client = KiteAPIClient()
        except Exception as e:
            logger.error(f"Failed to initialize Kite client: {e}")
            raise
    
    return _kite_client

def test_kite_connection() -> bool:
    try:
        client = get_kite_client()
        return client.test_connection()
    except Exception as e:
        logger.error(f"Kite connection test failed: {e}")
        return False
