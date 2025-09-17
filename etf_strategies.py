"""
Turtle Trader - ETF Trading Strategies
Specialized strategies for ETF trading with momentum and mean reversion
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from etf_manager import etf_order_manager, ETFOrderType, ETFOrderRequest

@dataclass
class ETFSignal:
    """ETF trading signal"""
    symbol: str
    action: str  # BUY/SELL/HOLD
    strength: float  # 0.0 to 1.0
    price_target: Optional[float]
    stop_loss: Optional[float]
    order_type: ETFOrderType
    reasoning: str

class ETFMomentumStrategy:
    """ETF Momentum strategy focusing on trend following"""
    
    def __init__(self):
        self.lookback_period = 20
        self.momentum_threshold = 0.02  # 2% momentum threshold
        self.volume_threshold = 1.5     # 50% above average volume
        
        logger.info("ETF Momentum Strategy initialized")
    
    def analyze_etf(self, symbol: str, data: pd.DataFrame) -> ETFSignal:
        """Analyze single ETF for momentum signals"""
        
        if len(data) < self.lookback_period:
            return ETFSignal(
                symbol=symbol, action="HOLD", strength=0.0,
                price_target=None, stop_loss=None,
                order_type=ETFOrderType.CNC,
                reasoning="Insufficient data"
            )
        
        # Calculate momentum indicators
        current_price = data['close'].iloc[-1]
        
        # Price momentum (20-day)
        price_20d_ago = data['close'].iloc[-self.lookback_period]
        price_momentum = (current_price - price_20d_ago) / price_20d_ago
        
        # Moving average trend
        sma_10 = data['close'].rolling(10).mean().iloc[-1]
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        ma_trend = (sma_10 - sma_20) / sma_20
        
        # Volume momentum
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # RSI for overbought/oversold
        rsi = self._calculate_rsi(data['close'], 14)
        current_rsi = rsi.iloc[-1]
        
        # Volatility (for position sizing)
        volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
        
        # Signal generation
        signal_strength = 0.0
        action = "HOLD"
        order_type = ETFOrderType.CNC
        reasoning_parts = []
        
        # Bullish momentum conditions
        if (price_momentum > self.momentum_threshold and 
            ma_trend > 0 and 
            volume_ratio > self.volume_threshold and
            current_rsi < 70):  # Not overbought
            
            action = "BUY"
            signal_strength = min(0.8, (price_momentum * 2 + ma_trend + 
                                      (volume_ratio - 1)) / 3)
            
            # Use MTF for strong momentum
            if signal_strength > 0.6 and volatility < 0.03:  # Low volatility
                order_type = ETFOrderType.MTF
                reasoning_parts.append("Strong momentum with low volatility - MTF")
            else:
                order_type = ETFOrderType.CNC
                reasoning_parts.append("Positive momentum - CNC")
            
            reasoning_parts.extend([
                f"Price momentum: {price_momentum:.2%}",
                f"MA trend: {ma_trend:.2%}",
                f"Volume ratio: {volume_ratio:.1f}",
                f"RSI: {current_rsi:.1f}"
            ])
        
        # Bearish momentum conditions  
        elif (price_momentum < -self.momentum_threshold and 
              ma_trend < -0.01 and
              current_rsi > 30):  # Not oversold
            
            action = "SELL"
            signal_strength = min(0.8, abs(price_momentum * 2 + ma_trend) / 2)
            order_type = ETFOrderType.CNC  # Always sell as CNC
            
            reasoning_parts.extend([
                "Negative momentum detected",
                f"Price momentum: {price_momentum:.2%}",
                f"MA trend: {ma_trend:.2%}",
                f"RSI: {current_rsi:.1f}"
            ])
        
        else:
            reasoning_parts.append("No clear momentum signal")
        
        # Calculate targets
        price_target = None
        stop_loss = None
        
        if action == "BUY":
            # Target based on recent range
            recent_high = data['high'].rolling(20).max().iloc[-1]
            price_target = min(current_price * 1.05, recent_high)
            stop_loss = current_price * 0.97  # 3% stop loss
        
        elif action == "SELL":
            recent_low = data['low'].rolling(20).min().iloc[-1]
            price_target = max(current_price * 0.95, recent_low)
            stop_loss = current_price * 1.03  # 3% stop loss for short
        
        return ETFSignal(
            symbol=symbol,
            action=action,
            strength=signal_strength,
            price_target=price_target,
            stop_loss=stop_loss,
            order_type=order_type,
            reasoning=" | ".join(reasoning_parts)
        )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

class ETFMeanReversionStrategy:
    """ETF Mean Reversion strategy for range-bound ETFs"""
    
    def __init__(self):
        self.bollinger_period = 20
        self.bollinger_std = 2
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
        logger.info("ETF Mean Reversion Strategy initialized")
    
    def analyze_etf(self, symbol: str, data: pd.DataFrame) -> ETFSignal:
        """Analyze ETF for mean reversion opportunities"""
        
        if len(data) < max(self.bollinger_period, self.rsi_period):
            return ETFSignal(
                symbol=symbol, action="HOLD", strength=0.0,
                price_target=None, stop_loss=None,
                order_type=ETFOrderType.CNC,
                reasoning="Insufficient data for mean reversion analysis"
            )
        
        current_price = data['close'].iloc[-1]
        
        # Bollinger Bands
        sma = data['close'].rolling(self.bollinger_period).mean()
        std = data['close'].rolling(self.bollinger_period).std()
        upper_band = sma + (std * self.bollinger_std)
        lower_band = sma - (std * self.bollinger_std)
        
        current_sma = sma.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        # RSI
        rsi = self._calculate_rsi(data['close'], self.rsi_period)
        current_rsi = rsi.iloc[-1]
        
        # Price position in bands
        band_position = (current_price - current_lower) / (current_upper - current_lower)
        
        # Trend strength (to avoid trading against strong trends)
        trend_strength = abs(current_price - current_sma) / current_sma
        
        # Signal generation
        action = "HOLD"
        signal_strength = 0.0
        order_type = ETFOrderType.CNC
        reasoning_parts = []
        
        # Oversold conditions (Buy signal)
        if (current_price <= current_lower and 
            current_rsi <= self.rsi_oversold and
            trend_strength < 0.05):  # Not in strong downtrend
            
            action = "BUY"
            signal_strength = (1 - band_position) * 0.8  # Stronger signal near lower band
            
            # Adjust for RSI
            rsi_factor = (self.rsi_oversold - current_rsi) / self.rsi_oversold
            signal_strength = min(0.8, signal_strength + rsi_factor * 0.2)
            
            order_type = ETFOrderType.CNC  # Conservative for mean reversion
            
            reasoning_parts.extend([
                "Oversold mean reversion opportunity",
                f"Price vs Lower Band: {((current_price - current_lower) / current_lower * 100):.1f}%",
                f"RSI: {current_rsi:.1f}",
                f"Band position: {band_position:.2f}"
            ])
        
        # Overbought conditions (Sell signal)
        elif (current_price >= current_upper and 
              current_rsi >= self.rsi_overbought and
              trend_strength < 0.05):  # Not in strong uptrend
            
            action = "SELL"
            signal_strength = band_position * 0.8  # Stronger signal near upper band
            
            # Adjust for RSI
            rsi_factor = (current_rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
            signal_strength = min(0.8, signal_strength + rsi_factor * 0.2)
            
            order_type = ETFOrderType.CNC
            
            reasoning_parts.extend([
                "Overbought mean reversion opportunity",
                f"Price vs Upper Band: {((current_price - current_upper) / current_upper * 100):.1f}%",
                f"RSI: {current_rsi:.1f}",
                f"Band position: {band_position:.2f}"
            ])
        
        else:
            reasoning_parts.append("No mean reversion signal - price within normal range")
        
        # Calculate targets
        price_target = None
        stop_loss = None
        
        if action == "BUY":
            price_target = current_sma  # Target mean reversion to SMA
            stop_loss = current_price * 0.98  # Tight stop for mean reversion
        
        elif action == "SELL":
            price_target = current_sma
            stop_loss = current_price * 1.02  # Tight stop for mean reversion
        
        return ETFSignal(
            symbol=symbol,
            action=action,
            strength=signal_strength,
            price_target=price_target,
            stop_loss=stop_loss,
            order_type=order_type,
            reasoning=" | ".join(reasoning_parts)
        )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

class ETFStrategyManager:
    """Manager for ETF-specific trading strategies"""
    
    def __init__(self):
        self.momentum_strategy = ETFMomentumStrategy()
        self.mean_reversion_strategy = ETFMeanReversionStrategy()
        
        # Strategy weights based on market conditions
        self.strategy_weights = {
            'momentum': 0.6,
            'mean_reversion': 0.4
        }
        
        logger.info("ETF Strategy Manager initialized")
    
    def get_etf_signals(self, market_data: Dict[str, pd.DataFrame]) -> List[ETFSignal]:
        """Get trading signals for all ETFs"""
        
        all_signals = []
        
        for symbol, data in market_data.items():
            if len(data) < 20:  # Minimum data requirement
                continue
            
            # Get signals from both strategies
            momentum_signal = self.momentum_strategy.analyze_etf(symbol, data)
            mean_rev_signal = self.mean_reversion_strategy.analyze_etf(symbol, data)
            
            # Combine signals with weights
            combined_signal = self._combine_signals(momentum_signal, mean_rev_signal)
            
            if combined_signal.action != "HOLD":
                all_signals.append(combined_signal)
        
        # Sort by signal strength
        all_signals.sort(key=lambda x: x.strength, reverse=True)
        
        return all_signals
    
    def _combine_signals(self, momentum: ETFSignal, mean_rev: ETFSignal) -> ETFSignal:
        """Combine signals from different strategies"""
        
        # If both strategies agree
        if momentum.action == mean_rev.action and momentum.action != "HOLD":
            combined_strength = (momentum.strength * self.strategy_weights['momentum'] + 
                               mean_rev.strength * self.strategy_weights['mean_reversion'])
            
            return ETFSignal(
                symbol=momentum.symbol,
                action=momentum.action,
                strength=combined_strength,
                price_target=momentum.price_target,
                stop_loss=momentum.stop_loss,
                order_type=momentum.order_type,
                reasoning=f"CONSENSUS: {momentum.reasoning} & {mean_rev.reasoning}"
            )
        
        # If strategies disagree, take the stronger signal
        elif momentum.strength > mean_rev.strength:
            return momentum
        elif mean_rev.strength > momentum.strength:
            return mean_rev
        
        # Default to hold if no clear signal
        return ETFSignal(
            symbol=momentum.symbol,
            action="HOLD",
            strength=0.0,
            price_target=None,
            stop_loss=None,
            order_type=ETFOrderType.CNC,
            reasoning="Conflicting signals - holding position"
        )

# Create global ETF strategy manager
etf_strategy_manager = ETFStrategyManager()

# Export classes and instance
__all__ = ['ETFSignal', 'ETFMomentumStrategy', 'ETFMeanReversionStrategy', 
           'ETFStrategyManager', 'etf_strategy_manager']
