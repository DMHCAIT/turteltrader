"""
Turtle Trader - Data Management Module
Handles market data collection, storage, and distribution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import threading
import time
from loguru import logger
# yfinance import removed - using only Kite API for real data

from core.config import config, Constants
from core.api_client import api_client
from kite_api_client import KiteAPIClient

class DataManager:
    """Centralized data management system"""
    
    def __init__(self):
        self.db_path = "data/market_data.db"
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = config.getint("MARKET_DATA", "CACHE_EXPIRY", 300)  # 5 minutes
        self.running = False
        self.update_thread = None
        
        # Initialize database
        self._init_database()
        
        # Initialize Kite API client
        self.kite = None
        self._init_kite_client()
        
    def start(self):
        """Start data management services"""
        self.running = True
        self.update_thread = threading.Thread(target=self._background_update, daemon=True)
        self.update_thread.start()
        logger.info("Data Manager started")
    
    def stop(self):
        """Stop data management services"""
        self.running = False
        logger.info("Data Manager stopped")
    
    def _init_database(self):
        """Initialize SQLite database for data storage"""
        import os
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create market data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    datetime TIMESTAMP NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    interval TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, exchange, datetime, interval)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_datetime 
                ON market_data(symbol, datetime)
            """)
            
            conn.commit()
    
    def _init_kite_client(self):
        """Initialize Kite API client"""
        try:
            self.kite = KiteAPIClient()
            if not self.kite.test_connection():
                raise ConnectionError("Kite API connection test failed.")
            logger.info("✅ DataManager initialized with active Kite API connection")
        except Exception as e:
            logger.error(f"❌ Failed to initialize KiteAPIClient in DataManager: {e}")
            self.kite = None
    
    def get_historical_data(self, symbol: str, days: int = 30, 
                          interval: str = Constants.DAY,
                          exchange: str = Constants.NSE) -> pd.DataFrame:
        """Get historical data for a symbol from Kite API only - no fallbacks allowed"""
        
        # Check cache first
        cache_key = f"{symbol}_{interval}_{days}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Only use Breeze API - no fallbacks
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            data = api_client.get_historical_data(
                symbol=symbol,
                exchange=exchange,
                product_type="cash",
                interval=interval,
                from_date=from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                to_date=to_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            )
            
            if not data.empty:
                # Store in database
                self._store_data(symbol, exchange, data, interval)
                
                # Cache the data
                self._cache_data(cache_key, data)
                
                return data
            else:
                raise ConnectionError(f"Breeze API returned empty data for {symbol}")
            
        except Exception as e:
            logger.error(f"Breeze API failed for {symbol}: {e}")
            # NO FALLBACKS - RAISE ERROR TO FORCE REAL API CONNECTION
            raise ConnectionError(f"Failed to get real data from Breeze API for {symbol}. No fallback data allowed.")
    
    def get_real_time_data(self, symbol: str, exchange: str = Constants.NSE) -> pd.DataFrame:
        """Get real-time data for a symbol using Kite API LTP"""
        
        cache_key = f"{symbol}_realtime"
        if self._is_cache_valid(cache_key, duration=30):  # 30 seconds cache for real-time
            return self.cache[cache_key]
        
        try:
            # Primary: Use Kite API for LTP
            instrument_key = f"NSE:{symbol}"
            ltp_data = self.kite.get_ltp([instrument_key])
            
            if ltp_data and instrument_key in ltp_data:
                ltp = float(ltp_data[instrument_key]['last_price'])
                
                # Get detailed quote for OHLC data
                quote_data = self.kite.get_quote([instrument_key])
                
                current_time = datetime.now()
                
                if quote_data and instrument_key in quote_data:
                    quote = quote_data[instrument_key]
                    ohlc = quote.get('ohlc', {})
                    
                    data = pd.DataFrame({
                        'open': [float(ohlc.get('open', ltp))],
                        'high': [float(ohlc.get('high', ltp))],
                        'low': [float(ohlc.get('low', ltp))],
                        'close': [ltp],  # LTP as current close
                        'volume': [int(quote.get('volume', 0))]
                    }, index=[current_time])
                else:
                    # Fallback with just LTP
                    data = pd.DataFrame({
                        'open': [ltp],
                        'high': [ltp],
                        'low': [ltp],
                        'close': [ltp],
                        'volume': [0]
                    }, index=[current_time])
                
                # Cache the data
                self._cache_data(cache_key, data, duration=30)
                logger.debug(f"📊 LTP for {symbol}: ₹{ltp:.2f}")
                
                return data
            
            # Fallback: Try Breeze API if Kite fails
            quotes = api_client.get_quotes(symbol, exchange)
            
            if quotes:
                # Convert to DataFrame format
                current_time = datetime.now()
                data = pd.DataFrame({
                    'open': [float(quotes[0].get('open', 0))],
                    'high': [float(quotes[0].get('high', 0))],
                    'low': [float(quotes[0].get('low', 0))],
                    'close': [float(quotes[0].get('ltp', 0))],
                    'volume': [int(quotes[0].get('total_quantity_traded', 0))]
                }, index=[current_time])
                
                # Cache the data
                self._cache_data(cache_key, data, duration=30)
                
                return data
            
        except Exception as e:
            logger.debug(f"Error getting real-time data for {symbol}: {e}")
        
        return pd.DataFrame()
    
    def get_ltp(self, symbol: str) -> Optional[float]:
        """Get Last Traded Price for a symbol"""
        try:
            instrument_key = f"NSE:{symbol}"
            ltp_data = self.kite.get_ltp([instrument_key])
            
            if ltp_data and instrument_key in ltp_data:
                ltp = float(ltp_data[instrument_key]['last_price'])
                logger.debug(f"📊 {symbol} LTP: ₹{ltp:.2f}")
                return ltp
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get LTP for {symbol}: {e}")
            return None
    
    def get_all_ltps(self, symbols: List[str]) -> Dict[str, float]:
        """Get LTP for multiple symbols at once with improved error handling"""
        ltps = {}
        
        if not self.kite:
            logger.error("❌ Cannot fetch LTPs: DataManager has no active Kite connection.")
            return {symbol: 0.0 for symbol in symbols}
        
        # Process in batches to avoid API limits
        batch_size = 50
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            try:
                # Prepare instruments list
                instruments = [f"NSE:{symbol}" for symbol in batch_symbols]
                
                logger.info(f"Fetching LTP for batch {i//batch_size + 1} ({len(batch_symbols)} symbols)")
                
                # Try LTP method first
                ltp_data = self.kite.get_ltp(instruments)
                
                if ltp_data:
                    for symbol in batch_symbols:
                        instrument_key = f"NSE:{symbol}"
                        if instrument_key in ltp_data:
                            try:
                                ltp = float(ltp_data[instrument_key]['last_price'])
                                ltps[symbol] = ltp if ltp > 0 else 0.0
                                if ltp > 0:
                                    logger.debug(f"✅ {symbol}: ₹{ltp:.2f}")
                            except (KeyError, ValueError, TypeError) as e:
                                logger.warning(f"⚠️ Failed to parse LTP for {symbol}: {e}")
                                ltps[symbol] = 0.0
                        else:
                            logger.warning(f"⚠️ No data for {symbol}")
                            ltps[symbol] = 0.0
                else:
                    # If LTP fails, try quote method as fallback
                    logger.warning("LTP method failed, trying quote method...")
                    try:
                        quote_data = self.kite.get_quote(instruments)
                        if quote_data:
                            for symbol in batch_symbols:
                                instrument_key = f"NSE:{symbol}"
                                if instrument_key in quote_data:
                                    quote = quote_data[instrument_key]
                                    # Try multiple price fields
                                    price = quote.get('last_price') or quote.get('ltp') or quote.get('close') or 0
                                    ltps[symbol] = float(price) if price else 0.0
                                else:
                                    ltps[symbol] = 0.0
                        else:
                            # Mark all symbols in this batch as 0
                            for symbol in batch_symbols:
                                ltps[symbol] = 0.0
                    except Exception as fallback_error:
                        logger.error(f"❌ Quote fallback also failed: {fallback_error}")
                        for symbol in batch_symbols:
                            ltps[symbol] = 0.0
                
                # Small delay between batches
                if i + batch_size < len(symbols):
                    time.sleep(0.2)
                    
            except Exception as e:
                logger.error(f"❌ Failed to get LTPs for batch {batch_symbols}: {e}")
                # Mark all symbols in the failed batch as 0
                for symbol in batch_symbols:
                    ltps[symbol] = 0.0
        
        valid_count = len([p for p in ltps.values() if p > 0])
        logger.info(f"✅ LTP fetch complete: {valid_count}/{len(symbols)} symbols with valid prices")
        
        if valid_count < len(symbols) * 0.3:  # Less than 30% success
            logger.warning(f"⚠️ Low success rate for LTP fetch: {valid_count}/{len(symbols)}")
        
        return ltps
    
    def _store_data(self, symbol: str, exchange: str, data: pd.DataFrame, interval: str):
        """Store data in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for timestamp, row in data.iterrows():
                    conn.execute("""
                        INSERT OR REPLACE INTO market_data 
                        (symbol, exchange, datetime, open, high, low, close, volume, interval)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol, exchange, timestamp, 
                        float(row['open']), float(row['high']), float(row['low']), 
                        float(row['close']), int(row.get('volume', 0)), interval
                    ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing data for {symbol}: {e}")
    
    def _get_data_from_db(self, symbol: str, exchange: str, days: int, interval: str) -> pd.DataFrame:
        """Retrieve data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                from_date = datetime.now() - timedelta(days=days)
                
                query = """
                    SELECT datetime, open, high, low, close, volume
                    FROM market_data
                    WHERE symbol = ? AND exchange = ? AND interval = ? 
                          AND datetime >= ?
                    ORDER BY datetime
                """
                
                data = pd.read_sql_query(
                    query, conn, 
                    params=(symbol, exchange, interval, from_date),
                    parse_dates=['datetime'],
                    index_col='datetime'
                )
                
                return data
                
        except Exception as e:
            logger.error(f"Error retrieving data from DB for {symbol}: {e}")
            return pd.DataFrame()
    
    def _cache_data(self, key: str, data: pd.DataFrame, duration: int = None):
        """Cache data with expiry"""
        if duration is None:
            duration = self.cache_duration
            
        self.cache[key] = data.copy()
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=duration)
    
    def _is_cache_valid(self, key: str, duration: int = None) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        expiry_time = self.cache_expiry.get(key)
        if expiry_time is None:
            return False
        
        return datetime.now() < expiry_time
    
    def _background_update(self):
        """Background thread for data updates"""
        while self.running:
            try:
                # Clean expired cache entries
                current_time = datetime.now()
                expired_keys = [
                    key for key, expiry in self.cache_expiry.items()
                    if current_time > expiry
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                    del self.cache_expiry[key]
                
                time.sleep(60)  # Clean every minute
                
            except Exception as e:
                logger.error(f"Error in background data update: {e}")
                time.sleep(60)
    
    # Yahoo Finance functions removed - using only Breeze API for real data

# Export main class
__all__ = ['DataManager']
