"""
🔴 CRITICAL: LIVE ORDER EXECUTION BRIDGE
=====================================

This bridges your dashboard to actual Breeze API order placement
"""

import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from kite_api_client import KiteAPIClient

class LiveOrderExecutor:
    """Execute real orders through Breeze API"""
    
    def __init__(self):
        self.client = None
        self.is_live_mode = False
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize live Kite API client"""
        try:
            # Initialize Kite API client
            self.client = KiteAPIClient()
            
            if self.client.test_connection():
                self.is_live_mode = True
                st.success("✅ Kite API Connected!")
            else:
                st.error("❌ Kite API Connection Failed - Check credentials and access token")
                self.is_live_mode = False
                
        except Exception as e:
            st.error(f"❌ Kite API initialization failed: {e}")
            self.is_live_mode = False
    
    def place_live_order(self, 
                        symbol: str,
                        action: str,  # BUY/SELL
                        quantity: int,
                        order_type: str = "MARKET",
                        product: str = "MTF",
                        price: float = 0) -> Optional[str]:
        """Place actual live order"""
        
        if not self.is_live_mode:
            st.error("❌ Not in live mode - cannot place real orders")
            return None
        
        try:
            # Confirm with user
            st.warning(f"⚠️ **LIVE ORDER**: {action} {quantity} {symbol} at MARKET price")
            
            if st.button(f"🔴 CONFIRM LIVE {action}", key=f"confirm_{symbol}_{action}"):
                
                # Place actual order
                order_id = self.client.place_order(
                    stock_code=symbol,
                    exchange_code="NSE",
                    product=product,
                    action=action,
                    order_type=order_type,
                    quantity=quantity,
                    price=price,
                    validity="DAY"
                )
                
                if order_id:
                    st.success(f"✅ **LIVE ORDER PLACED**: ID {order_id}")
                    
                    # Log the trade
                    self.log_trade(symbol, action, quantity, order_id)
                    return order_id
                else:
                    st.error("❌ Order placement failed")
                    return None
                    
        except Exception as e:
            st.error(f"❌ Order execution error: {e}")
            return None
    
    def get_live_positions(self) -> Dict[str, Any]:
        """Get actual portfolio positions"""
        if not self.is_live_mode:
            return {}
        
        try:
            positions = self.client.get_portfolio()
            return positions or {}
        except Exception as e:
            st.error(f"❌ Error fetching positions: {e}")
            return {}
    
    def get_live_balance(self) -> Dict[str, float]:
        """Get actual account balance"""
        if not self.is_live_mode:
            return {'available_cash': 0, 'margin_used': 0}
        
        try:
            funds = self.client.get_account_funds()
            return funds or {'available_cash': 0, 'margin_used': 0}
        except Exception as e:
            st.error(f"❌ Error fetching balance: {e}")
            return {'available_cash': 0, 'margin_used': 0}
    
    def log_trade(self, symbol: str, action: str, quantity: int, order_id: str):
        """Log executed trade"""
        trade_log = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'order_id': order_id,
            'status': 'EXECUTED'
        }
        
        # Save to session state for tracking
        if 'trade_log' not in st.session_state:
            st.session_state.trade_log = []
        
        st.session_state.trade_log.append(trade_log)

# Global instance
live_executor = LiveOrderExecutor()