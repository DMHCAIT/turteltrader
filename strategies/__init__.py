"""
Turtle Trader - Advanced Trading Strategies Module
Comprehensive trading strategies with AI/ML integration
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import talib
from loguru import logger

from core.config import config, Constants
from core.api_client import api_client, Position, Order
from ml_models import model_manager

class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    signal: SignalType
    confidence: float
    price: float
    timestamp: pd.Timestamp
    strategy: str
    metadata: Dict[str, Any] = None

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.positions = {}
        self.signals_history = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate trading signals from market data"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate position size for a signal"""
        pass
    
    def validate_signal(self, signal: TradingSignal, current_positions: Dict) -> bool:
        """Validate if signal should be executed"""
        # Check if we already have a position
        if signal.symbol in current_positions:
            current_pos = current_positions[signal.symbol]
            if (signal.signal in [SignalType.BUY, SignalType.STRONG_BUY] and current_pos.quantity > 0) or \
               (signal.signal in [SignalType.SELL, SignalType.STRONG_SELL] and current_pos.quantity < 0):
                return False
        
        # Check confidence threshold
        min_confidence = self.parameters.get('min_confidence', 0.6)
        if signal.confidence < min_confidence:
            return False
        
        return True

class TurtleStrategy(BaseStrategy):
    """Classic Turtle Trading Strategy with AI enhancements"""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 55, atr_period: int = 14):
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'atr_period': atr_period,
            'position_size_percent': 2.0,
            'max_pyramid_levels': 4,
            'risk_per_trade': 1.0
        }
        super().__init__("Turtle Strategy", parameters)
    
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate Turtle trading signals"""
        signals = []
        
        if len(data) < self.parameters['slow_period']:
            return signals
        
        # Calculate breakout levels
        fast_high = data['high'].rolling(window=self.parameters['fast_period']).max()
        fast_low = data['low'].rolling(window=self.parameters['fast_period']).min()
        slow_high = data['high'].rolling(window=self.parameters['slow_period']).max()
        slow_low = data['low'].rolling(window=self.parameters['slow_period']).min()
        
        # Calculate ATR for position sizing
        atr = talib.ATR(data['high'].values, data['low'].values, data['close'].values, 
                       timeperiod=self.parameters['atr_period'])
        
        # Get the latest values
        current_price = data['close'].iloc[-1]
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        current_atr = atr[-1]
        
        # Check for breakout signals
        if current_high > slow_high.iloc[-2]:  # Long breakout
            confidence = self._calculate_confidence(data, "long")
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.BUY if confidence < 0.8 else SignalType.STRONG_BUY,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'breakout_level': slow_high.iloc[-2],
                    'atr': current_atr,
                    'stop_loss': current_price - (2 * current_atr),
                    'take_profit': current_price + (4 * current_atr)
                }
            )
            signals.append(signal)
            
        elif current_low < slow_low.iloc[-2]:  # Short breakout
            confidence = self._calculate_confidence(data, "short")
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.SELL if confidence < 0.8 else SignalType.STRONG_SELL,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'breakout_level': slow_low.iloc[-2],
                    'atr': current_atr,
                    'stop_loss': current_price + (2 * current_atr),
                    'take_profit': current_price - (4 * current_atr)
                }
            )
            signals.append(signal)
        
        # Check for exit signals using fast breakout
        elif current_low < fast_low.iloc[-2]:  # Exit long
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.SELL,
                confidence=0.9,  # High confidence for exits
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={'exit_type': 'fast_breakout_exit'}
            )
            signals.append(signal)
            
        elif current_high > fast_high.iloc[-2]:  # Exit short
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.BUY,
                confidence=0.9,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={'exit_type': 'fast_breakout_exit'}
            )
            signals.append(signal)
        
        return signals
    
    def _calculate_confidence(self, data: pd.DataFrame, direction: str) -> float:
        """Calculate signal confidence using multiple factors"""
        confidence_factors = []
        
        # Volume confirmation
        if 'volume' in data.columns:
            recent_volume = data['volume'].tail(5).mean()
            avg_volume = data['volume'].tail(20).mean()
            volume_factor = min(recent_volume / avg_volume, 2.0) / 2.0
            confidence_factors.append(volume_factor)
        
        # Momentum confirmation
        momentum = talib.MOM(data['close'].values, timeperiod=10)
        momentum_factor = 0.5 + (abs(momentum[-1]) / data['close'].iloc[-1]) * 10
        momentum_factor = min(momentum_factor, 1.0)
        if (direction == "long" and momentum[-1] > 0) or (direction == "short" and momentum[-1] < 0):
            confidence_factors.append(momentum_factor)
        else:
            confidence_factors.append(1 - momentum_factor)
        
        # Volatility factor (lower volatility = higher confidence)
        atr = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=14)
        volatility_factor = 1 - min(atr[-1] / data['close'].iloc[-1], 0.1) * 10
        confidence_factors.append(volatility_factor)
        
        # Overall confidence
        confidence = np.mean(confidence_factors)
        return max(0.1, min(0.99, confidence))
    
    def calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate position size using Turtle position sizing rules"""
        if signal.metadata is None or 'atr' not in signal.metadata:
            return 0
        
        atr = signal.metadata['atr']
        risk_per_trade = self.parameters['risk_per_trade'] / 100
        
        # Calculate dollar volatility (1 ATR movement in dollars)
        dollar_volatility = atr
        
        # Calculate position size
        risk_amount = available_capital * risk_per_trade
        position_size = int(risk_amount / dollar_volatility)
        
        # Limit position size to reasonable percentage of capital
        max_position_value = available_capital * 0.2  # Max 20% per position
        max_shares = int(max_position_value / signal.price)
        
        return min(position_size, max_shares)

class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy with statistical analysis"""
    
    def __init__(self, lookback_period: int = 20, std_threshold: float = 2.0):
        parameters = {
            'lookback_period': lookback_period,
            'std_threshold': std_threshold,
            'min_confidence': 0.7
        }
        super().__init__("Mean Reversion Strategy", parameters)
    
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate mean reversion signals"""
        signals = []
        
        if len(data) < self.parameters['lookback_period']:
            return signals
        
        # Calculate moving average and standard deviation
        ma = data['close'].rolling(window=self.parameters['lookback_period']).mean()
        std = data['close'].rolling(window=self.parameters['lookback_period']).std()
        
        # Calculate z-score
        z_score = (data['close'] - ma) / std
        
        current_price = data['close'].iloc[-1]
        current_z_score = z_score.iloc[-1]
        
        # Generate signals based on z-score
        if current_z_score > self.parameters['std_threshold']:
            # Price is too high, expect reversion down
            confidence = min(0.95, 0.5 + abs(current_z_score) * 0.1)
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.SELL,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'z_score': current_z_score,
                    'mean': ma.iloc[-1],
                    'std': std.iloc[-1],
                    'target_price': ma.iloc[-1]
                }
            )
            signals.append(signal)
            
        elif current_z_score < -self.parameters['std_threshold']:
            # Price is too low, expect reversion up
            confidence = min(0.95, 0.5 + abs(current_z_score) * 0.1)
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'z_score': current_z_score,
                    'mean': ma.iloc[-1],
                    'std': std.iloc[-1],
                    'target_price': ma.iloc[-1]
                }
            )
            signals.append(signal)
        
        return signals
    
    def calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate position size for mean reversion"""
        # Conservative position sizing for mean reversion
        position_value = available_capital * 0.05  # 5% per position
        return int(position_value / signal.price)

class MomentumStrategy(BaseStrategy):
    """Momentum strategy using multiple timeframes"""
    
    def __init__(self, short_period: int = 12, long_period: int = 26):
        parameters = {
            'short_period': short_period,
            'long_period': long_period,
            'rsi_period': 14,
            'min_confidence': 0.65
        }
        super().__init__("Momentum Strategy", parameters)
    
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate momentum signals"""
        signals = []
        
        if len(data) < self.parameters['long_period']:
            return signals
        
        # Calculate MACD
        macd, macd_signal, macd_hist = talib.MACD(
            data['close'].values,
            fastperiod=self.parameters['short_period'],
            slowperiod=self.parameters['long_period'],
            signalperiod=9
        )
        
        # Calculate RSI
        rsi = talib.RSI(data['close'].values, timeperiod=self.parameters['rsi_period'])
        
        # Calculate moving averages
        sma_20 = talib.SMA(data['close'].values, timeperiod=20)
        sma_50 = talib.SMA(data['close'].values, timeperiod=50)
        
        current_price = data['close'].iloc[-1]
        
        # Check for bullish momentum
        if (macd[-1] > macd_signal[-1] and macd[-2] <= macd_signal[-2] and
            rsi[-1] > 50 and sma_20[-1] > sma_50[-1]):
            
            confidence = self._calculate_momentum_confidence(data, "bullish")
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'macd': macd[-1],
                    'macd_signal': macd_signal[-1],
                    'rsi': rsi[-1],
                    'sma_20': sma_20[-1],
                    'sma_50': sma_50[-1]
                }
            )
            signals.append(signal)
        
        # Check for bearish momentum
        elif (macd[-1] < macd_signal[-1] and macd[-2] >= macd_signal[-2] and
              rsi[-1] < 50 and sma_20[-1] < sma_50[-1]):
            
            confidence = self._calculate_momentum_confidence(data, "bearish")
            signal = TradingSignal(
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal=SignalType.SELL,
                confidence=confidence,
                price=current_price,
                timestamp=data.index[-1],
                strategy=self.name,
                metadata={
                    'macd': macd[-1],
                    'macd_signal': macd_signal[-1],
                    'rsi': rsi[-1],
                    'sma_20': sma_20[-1],
                    'sma_50': sma_50[-1]
                }
            )
            signals.append(signal)
        
        return signals
    
    def _calculate_momentum_confidence(self, data: pd.DataFrame, direction: str) -> float:
        """Calculate momentum confidence"""
        # Volume confirmation
        volume_factor = 0.5
        if 'volume' in data.columns:
            recent_volume = data['volume'].tail(3).mean()
            avg_volume = data['volume'].tail(20).mean()
            volume_factor = min(recent_volume / avg_volume, 2.0) / 2.0
        
        # Price action confirmation
        price_change = (data['close'].iloc[-1] - data['close'].iloc[-5]) / data['close'].iloc[-5]
        price_factor = min(abs(price_change) * 20, 1.0)
        
        confidence = (volume_factor + price_factor) / 2
        return max(0.5, min(0.95, confidence))
    
    def calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate position size for momentum strategy"""
        # Moderate position sizing for momentum
        position_value = available_capital * 0.08  # 8% per position
        return int(position_value / signal.price)

class AIEnhancedStrategy(BaseStrategy):
    """AI/ML enhanced trading strategy"""
    
    def __init__(self, model_type: str = "ensemble", prediction_horizon: int = 5):
        parameters = {
            'model_type': model_type,
            'prediction_horizon': prediction_horizon,
            'min_confidence': 0.7,
            'lookback_period': 100
        }
        super().__init__("AI Enhanced Strategy", parameters)
    
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate AI-powered signals"""
        signals = []
        
        if len(data) < self.parameters['lookback_period']:
            return signals
        
        symbol = data.attrs.get('symbol', 'UNKNOWN')
        
        try:
            # Get ML prediction
            predictions = model_manager.predict(symbol, data, self.parameters['model_type'])
            
            if len(predictions) == 0:
                logger.warning(f"No predictions available for {symbol}")
                return signals
            
            # Use the latest prediction
            prediction = predictions[-1]
            current_price = data['close'].iloc[-1]
            
            # Convert prediction to signal
            if prediction > 0.01:  # 1% threshold for buy
                signal_type = SignalType.BUY if prediction < 0.03 else SignalType.STRONG_BUY
                confidence = min(0.95, 0.5 + abs(prediction) * 10)
                
                signal = TradingSignal(
                    symbol=symbol,
                    signal=signal_type,
                    confidence=confidence,
                    price=current_price,
                    timestamp=data.index[-1],
                    strategy=self.name,
                    metadata={
                        'prediction': prediction,
                        'expected_return': prediction,
                        'target_price': current_price * (1 + prediction)
                    }
                )
                signals.append(signal)
                
            elif prediction < -0.01:  # -1% threshold for sell
                signal_type = SignalType.SELL if prediction > -0.03 else SignalType.STRONG_SELL
                confidence = min(0.95, 0.5 + abs(prediction) * 10)
                
                signal = TradingSignal(
                    symbol=symbol,
                    signal=signal_type,
                    confidence=confidence,
                    price=current_price,
                    timestamp=data.index[-1],
                    strategy=self.name,
                    metadata={
                        'prediction': prediction,
                        'expected_return': prediction,
                        'target_price': current_price * (1 + prediction)
                    }
                )
                signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error generating AI signals for {symbol}: {e}")
        
        return signals
    
    def calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate position size based on AI confidence"""
        # Dynamic position sizing based on confidence and expected return
        base_allocation = 0.1  # 10% base allocation
        confidence_multiplier = signal.confidence
        
        if signal.metadata and 'expected_return' in signal.metadata:
            return_multiplier = min(abs(signal.metadata['expected_return']) * 5, 1.0)
        else:
            return_multiplier = 1.0
        
        position_allocation = base_allocation * confidence_multiplier * return_multiplier
        position_value = available_capital * position_allocation
        
        return int(position_value / signal.price)

class StrategyManager:
    """Manager for multiple trading strategies"""
    
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []
        self.performance_metrics = {}
        
    def add_strategy(self, strategy: BaseStrategy):
        """Add a strategy to the manager"""
        self.strategies[strategy.name] = strategy
        logger.info(f"Added strategy: {strategy.name}")
    
    def activate_strategy(self, strategy_name: str):
        """Activate a strategy"""
        if strategy_name in self.strategies:
            if strategy_name not in self.active_strategies:
                self.active_strategies.append(strategy_name)
                logger.info(f"Activated strategy: {strategy_name}")
        else:
            logger.error(f"Strategy not found: {strategy_name}")
    
    def deactivate_strategy(self, strategy_name: str):
        """Deactivate a strategy"""
        if strategy_name in self.active_strategies:
            self.active_strategies.remove(strategy_name)
            logger.info(f"Deactivated strategy: {strategy_name}")
    
    def generate_all_signals(self, symbol: str, data: pd.DataFrame) -> List[TradingSignal]:
        """Generate signals from all active strategies"""
        all_signals = []
        
        # Add symbol to data attributes for strategies to use
        data.attrs['symbol'] = symbol
        
        for strategy_name in self.active_strategies:
            strategy = self.strategies[strategy_name]
            try:
                signals = strategy.generate_signals(data)
                all_signals.extend(signals)
                logger.debug(f"{strategy_name} generated {len(signals)} signals for {symbol}")
            except Exception as e:
                logger.error(f"Error generating signals from {strategy_name}: {e}")
        
        return all_signals
    
    def consensus_signal(self, signals: List[TradingSignal]) -> Optional[TradingSignal]:
        """Generate consensus signal from multiple strategies"""
        if not signals:
            return None
        
        # Group signals by type
        buy_signals = [s for s in signals if s.signal in [SignalType.BUY, SignalType.STRONG_BUY]]
        sell_signals = [s for s in signals if s.signal in [SignalType.SELL, SignalType.STRONG_SELL]]
        
        # Calculate weighted consensus
        if len(buy_signals) > len(sell_signals):
            avg_confidence = np.mean([s.confidence for s in buy_signals])
            if avg_confidence > 0.7:
                return TradingSignal(
                    symbol=signals[0].symbol,
                    signal=SignalType.STRONG_BUY if avg_confidence > 0.8 else SignalType.BUY,
                    confidence=avg_confidence,
                    price=signals[0].price,
                    timestamp=signals[0].timestamp,
                    strategy="Consensus",
                    metadata={'contributing_strategies': len(buy_signals)}
                )
        elif len(sell_signals) > len(buy_signals):
            avg_confidence = np.mean([s.confidence for s in sell_signals])
            if avg_confidence > 0.7:
                return TradingSignal(
                    symbol=signals[0].symbol,
                    signal=SignalType.STRONG_SELL if avg_confidence > 0.8 else SignalType.SELL,
                    confidence=avg_confidence,
                    price=signals[0].price,
                    timestamp=signals[0].timestamp,
                    strategy="Consensus",
                    metadata={'contributing_strategies': len(sell_signals)}
                )
        
        return None
    
    def get_strategy_performance(self, strategy_name: str) -> Dict:
        """Get performance metrics for a strategy"""
        return self.performance_metrics.get(strategy_name, {})

# Initialize default strategies
def create_default_strategies() -> StrategyManager:
    """Create and configure default strategies"""
    manager = StrategyManager()
    
    # Add strategies
    manager.add_strategy(TurtleStrategy())
    manager.add_strategy(MeanReversionStrategy())
    manager.add_strategy(MomentumStrategy())
    manager.add_strategy(AIEnhancedStrategy())
    
    # Activate strategies based on configuration
    manager.activate_strategy("Turtle Strategy")
    manager.activate_strategy("AI Enhanced Strategy")
    
    return manager

# Global strategy manager
strategy_manager = create_default_strategies()

# Export main classes
__all__ = [
    'SignalType',
    'TradingSignal',
    'BaseStrategy',
    'TurtleStrategy',
    'MeanReversionStrategy', 
    'MomentumStrategy',
    'AIEnhancedStrategy',
    'StrategyManager',
    'strategy_manager'
]
