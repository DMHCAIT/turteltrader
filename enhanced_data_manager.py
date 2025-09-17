"""
🔧 ENHANCED DATA MANAGER FOR LIVE TRADING
========================================

This replaces the broken Breeze API data with Yahoo Finance real-time feeds
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
from loguru import logger
from typing import Dict, List, Optional
import threading
import time

class EnhancedDataManager:
    """Enhanced data manager with Yahoo Finance fallback for live trading"""
    
    def __init__(self):
        self.indian_tz = pytz.timezone('Asia/Kolkata')
        self.cache = {}
        self.cache_expiry = {}
        self.running = False
        self.update_thread = None
        
        # ETF symbols mapping to Yahoo Finance
        self.etf_mapping = {
            'GOLDBEES': 'GOLDBEES.NS',
            'NIFTYBEES': 'NIFTYBEES.NS', 
            'BANKBEES': 'BANKBEES.NS',
            'JUNIORBEES': 'JUNIORBEES.NS',
            'LIQUIDBEES': 'LIQUIDBEES.NS',
            'ITBEES': 'ITBEES.NS',
            'PHARMBEES': 'PHARMBEES.NS',
            'PSUBANK': 'PSUBANK.NS',
            'CPSE': 'CPSE.NS',
            'NETF': 'NIFTY50.NS'  # Mapping for Next 50 ETF
        }
        
    def is_market_open(self) -> tuple:
        """Check if market is currently open with detailed status"""
        now = datetime.now(self.indian_tz)
        
        # Market holidays for 2025 (basic list)
        holidays = [
            "2025-01-26", "2025-03-14", "2025-04-14", "2025-04-18",
            "2025-08-15", "2025-10-02", "2025-11-01", "2025-12-25"
        ]
        
        today_str = now.strftime("%Y-%m-%d")
        
        # Check holiday
        if today_str in holidays:
            return False, "Holiday"
        
        # Check weekend
        if now.weekday() >= 5:
            return False, "Weekend"
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now < market_start:
            return False, f"Pre-market (opens in {(market_start - now).seconds // 60} min)"
        elif now > market_end:
            return False, f"After-hours (closed {(now - market_end).seconds // 60} min ago)"
        else:
            remaining = (market_end - now).seconds // 60
            return True, f"LIVE ({remaining} min remaining)"
    
    def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote using Yahoo Finance"""
        try:
            yahoo_symbol = self.etf_mapping.get(symbol, f"{symbol}.NS")
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get current data
            info = ticker.info
            history = ticker.history(period="2d", interval="1m")
            
            if history.empty:
                return None
            
            current_price = float(history['Close'].iloc[-1])
            previous_close = float(info.get('previousClose', current_price))
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else 0
            
            return {
                'symbol': symbol,
                'ltp': current_price,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'volume': int(history['Volume'].iloc[-1]) if 'Volume' in history else 0,
                'timestamp': history.index[-1].to_pydatetime(),
                'high': float(history['High'].iloc[-1]),
                'low': float(history['Low'].iloc[-1]),
                'open': float(history['Open'].iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Get historical data for analysis"""
        try:
            yahoo_symbol = self.etf_mapping.get(symbol, f"{symbol}.NS")
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return None
            
            # Add calculated fields
            hist['symbol'] = symbol
            hist['change'] = hist['Close'].diff()
            hist['change_percent'] = hist['Close'].pct_change() * 100
            
            return hist
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def start_real_time_monitoring(self, symbols: List[str]):
        """Start real-time monitoring for given symbols"""
        self.running = True
        
        def monitor():
            while self.running:
                try:
                    is_open, status = self.is_market_open()
                    logger.info(f"Market status: {status}")
                    
                    if is_open:
                        for symbol in symbols:
                            quote = self.get_real_time_quote(symbol)
                            if quote:
                                self.cache[symbol] = quote
                                self.cache_expiry[symbol] = datetime.now() + timedelta(minutes=1)
                                
                                logger.info(f"{symbol}: ₹{quote['ltp']:.2f} ({quote['change_percent']:+.2f}%)")
                    
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait longer on error
        
        self.update_thread = threading.Thread(target=monitor, daemon=True)
        self.update_thread.start()
        logger.info("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False
        logger.info("Real-time monitoring stopped")
    
    def get_cached_quote(self, symbol: str) -> Optional[Dict]:
        """Get cached quote if fresh, otherwise fetch new"""
        now = datetime.now()
        
        if (symbol in self.cache and 
            symbol in self.cache_expiry and 
            now < self.cache_expiry[symbol]):
            return self.cache[symbol]
        
        # Cache expired or doesn't exist, fetch new
        return self.get_real_time_quote(symbol)

# Test the enhanced data manager
if __name__ == "__main__":
    edm = EnhancedDataManager()
    
    print("🚀 TESTING ENHANCED DATA MANAGER")
    print("="*40)
    
    # Test market status
    is_open, status = edm.is_market_open()
    print(f"🕐 Market Status: {status}")
    
    # Test real-time quotes
    symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES']
    
    print("\n📊 Real-time Quotes:")
    for symbol in symbols:
        quote = edm.get_real_time_quote(symbol)
        if quote:
            print(f"✅ {symbol}: ₹{quote['ltp']:.2f} ({quote['change_percent']:+.2f}%) Vol: {quote['volume']:,}")
        else:
            print(f"❌ {symbol}: Failed to fetch")
    
    if is_open:
        print(f"\n🔄 Starting live monitoring for {len(symbols)} symbols...")
        edm.start_real_time_monitoring(symbols)
        
        try:
            for i in range(3):  # Run for 3 cycles
                time.sleep(35)
                print(f"\n📈 Update #{i+1}:")
                for symbol in symbols:
                    cached = edm.get_cached_quote(symbol)
                    if cached:
                        print(f"   {symbol}: ₹{cached['ltp']:.2f} ({cached['change_percent']:+.2f}%)")
        except KeyboardInterrupt:
            pass
        finally:
            edm.stop_monitoring()
    else:
        print("\n⏱️ Market closed - Live monitoring not started")