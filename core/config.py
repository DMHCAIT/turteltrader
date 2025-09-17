"""
Turtle Trader - Advanced AI/ML Trading System
Core Configuration and Utilities Module
"""

import os
import sys
import configparser
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path

class Config:
    """Configuration manager for the trading system"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            self.config.read(self.config_file)
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
            
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
            
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except Exception:
            return fallback
            
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except Exception:
            return fallback
            
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.get("LOGGING", "LOG_LEVEL", "INFO")
        log_file = self.get("LOGGING", "LOG_FILE", "logs/turtle_trader.log")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure loguru
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )

class Constants:
    """Trading system constants"""
    
    # Market hours
    MARKET_OPEN = "09:15"
    MARKET_CLOSE = "15:30"
    
    # Position types
    LONG = "LONG"
    SHORT = "SHORT"
    
    # Order types
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stoploss"
    
    # Order actions
    BUY = "buy"
    SELL = "sell"
    
    # Product types
    CASH = "cash"
    MARGIN = "margin"
    FUTURES = "futures"
    OPTIONS = "options"
    
    # Exchanges
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    BFO = "BFO"
    MCX = "MCX"
    
    # Time intervals
    MINUTE_1 = "1minute"
    MINUTE_5 = "5minute"
    MINUTE_30 = "30minute"
    DAY = "1day"
    
    # Risk metrics
    VAR = "VaR"
    CVAR = "CVaR"
    DRAWDOWN = "MaxDrawdown"
    SHARPE = "SharpeRatio"
    SORTINO = "SortinoRatio"
    
    # ML model types
    LSTM = "LSTM"
    GRU = "GRU"
    TRANSFORMER = "Transformer"
    XGBOOST = "XGBoost"
    LIGHTGBM = "LightGBM"
    CATBOOST = "CatBoost"
    ENSEMBLE = "Ensemble"

class Utils:
    """Utility functions for the trading system"""
    
    @staticmethod
    def is_market_open() -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        market_open = datetime.strptime(Constants.MARKET_OPEN, "%H:%M").time()
        market_close = datetime.strptime(Constants.MARKET_CLOSE, "%H:%M").time()
        
        return market_open <= now.time() <= market_close
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as Indian currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def calculate_position_size(capital: float, risk_percent: float, stop_loss_percent: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = capital * (risk_percent / 100)
        position_size = risk_amount / (stop_loss_percent / 100)
        return min(position_size, capital * 0.2)  # Max 20% of capital per position
    
    @staticmethod
    def generate_order_id() -> str:
        """Generate unique order ID"""
        return f"TT_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or len(symbol) < 2:
            return False
        return symbol.replace("&", "").replace("-", "").isalnum()
    
    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """Calculate returns from price series"""
        return prices.pct_change().dropna()
    
    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
        """Calculate rolling volatility"""
        return returns.rolling(window=window).std() * np.sqrt(252)
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def normalize_data(data: np.ndarray) -> np.ndarray:
        """Normalize data using min-max scaling"""
        return (data - data.min()) / (data.max() - data.min())
    
    @staticmethod
    def standardize_data(data: np.ndarray) -> np.ndarray:
        """Standardize data using z-score"""
        return (data - data.mean()) / data.std()

class MarketDataValidator:
    """Validator for market data quality"""
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> Dict[str, Any]:
        """Validate OHLCV data quality"""
        issues = []
        
        # Check required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for negative prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns and (df[col] <= 0).any():
                issues.append(f"Negative or zero prices in {col}")
        
        # Check OHLC logic
        if all(col in df.columns for col in price_cols):
            ohlc_issues = df[
                (df['high'] < df['low']) | 
                (df['high'] < df['open']) | 
                (df['high'] < df['close']) |
                (df['low'] > df['open']) | 
                (df['low'] > df['close'])
            ]
            if not ohlc_issues.empty:
                issues.append(f"OHLC logic violations: {len(ohlc_issues)} rows")
        
        # Check for missing data
        missing_data = df.isnull().sum()
        if missing_data.any():
            issues.append(f"Missing data: {missing_data.to_dict()}")
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate rows: {duplicates}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data_points': len(df),
            'date_range': f"{df.index.min()} to {df.index.max()}" if hasattr(df.index, 'min') else None
        }

# Global configuration instance
config = Config()

# Export main classes and functions
__all__ = [
    'Config',
    'Constants', 
    'Utils',
    'MarketDataValidator',
    'config'
]
