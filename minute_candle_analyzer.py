"""
📊 MINUTE-BY-MINUTE CANDLESTICK ANALYZER
=======================================

Advanced intraday analysis system that:
1. Fetches 1-minute, 5-minute, and 15-minute candles
2. Analyzes price action patterns in real-time
3. Detects micro-dips and recovery patterns
4. Provides enhanced entry/exit timing

Complements the real-time monitor with detailed candlestick analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger
import talib
from dataclasses import dataclass

from kite_api_client import KiteAPIClient


@dataclass
class CandlePattern:
    """Represents a detected candlestick pattern"""
    symbol: str
    pattern_name: str
    timestamp: datetime
    confidence: float  # 0-100
    signal_type: str   # "BUY", "SELL", "NEUTRAL"
    description: str
    ohlc_data: Dict[str, float]


@dataclass
class IntraDaySignal:
    """Intraday trading signal with timing details"""
    symbol: str
    signal_type: str
    timestamp: datetime
    price: float
    volume: int
    strength: str     # "WEAK", "MEDIUM", "STRONG"
    timeframe: str    # "1min", "5min", "15min"
    supporting_indicators: List[str]
    risk_level: str   # "LOW", "MEDIUM", "HIGH"


class MinuteCandleAnalyzer:
    """
    Analyzes minute-by-minute candlestick patterns for enhanced trading signals
    """
    
    def __init__(self):
        """Initialize the minute candle analyzer"""
        self.api_client = KiteAPIClient()
        
        # Analysis timeframes
        self.timeframes = ["minute", "5minute", "15minute"]
        
        # Complete ETF universe - All 65 ETFs available in Indian market
        self.etf_symbols = [
            # Major Index ETFs
            'NIFTYBEES', 'UTISENSETF', 'INDA', 'MOM150ETF', 'MOM250ETF', 
            'ICICINXT50', 'SETFNIF100', 'KOTAKNIFTY200', 'ABSLNIFTY500ETF', 'MOMMICROETF',
            
            # Sectoral ETFs
            'BANKBEES', 'ITBEES', 'PSUBANKBEES', 'PHARMABEES', 'FMCGBEES', 
            'ENERGYBEES', 'INFRAETF', 'AUTOETF', 'REALTYETF', 'MEDIAETF',
            'PRBANKETF', 'METALETF', 'COMMODETF', 'SERVICESETF', 'CONSUMETF',
            
            # Strategy & Factor ETFs
            'DIVOPPBEES', 'GROWTHETF', 'MNCETF', 'QUALITYETF', 'VALUEETF',
            'LOWVOLETF', 'EQUALWEIGHTETF', 'ALPHALVETF', 'ALPHA50ETF', 'EDELMOM30',
            
            # Government Securities & Bonds
            'GS813ETF', 'GS5YEARETF', 'BHARATBONDETFAPR30', 'BHARATBONDETFAPR25',
            'LIQUIDBEES', 'EDEL1DRATEETF', 'SBISDL26ETF', 'ICICISDL27ETF', 'HDFCGSEC30ETF',
            
            # International ETFs
            'ICICIB22', 'MON100ETF', 'MOSP500ETF', 'MOEAFEETF', 'MOEMETF',
            
            # Specialty ETFs
            'SILVERBEES', 'GOLDBEES', 'ICICIESGETF', 'CPSEETF',
            
            # ICICI ETFs
            'ICICIMID50', 'ICICISMALL100', 'ICICIHDIV', 'ICICIFINSERV',
            'ICICIHEALTH', 'ICICIDIGITAL', 'ICICIMANUF'
        ]
        
        # Cached data
        self.candle_data: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.instrument_tokens: Dict[str, int] = {}
        self.last_update: Dict[str, datetime] = {}
        
        # Pattern detection settings
        self.min_volume_threshold = 1000
        self.dip_threshold = -0.3  # 0.3% intraday dip
        self.bounce_threshold = 0.2  # 0.2% bounce from low
        
        logger.info("📊 Minute Candle Analyzer initialized")
        logger.info(f"🕐 Timeframes: {', '.join(self.timeframes)}")
        
    def initialize_tokens(self):
        """Initialize instrument tokens for all ETF symbols"""
        try:
            instruments = self.api_client.get_instruments("NSE")
            
            for _, instrument in instruments.iterrows():
                if instrument['tradingsymbol'] in self.etf_symbols:
                    self.instrument_tokens[instrument['tradingsymbol']] = instrument['instrument_token']
            
            logger.info(f"✅ Found tokens for {len(self.instrument_tokens)} ETFs")
            
        except Exception as e:
            logger.error(f"❌ Error initializing tokens: {e}")
    
    def fetch_candle_data(self, symbol: str, timeframe: str, hours_back: int = 4) -> Optional[pd.DataFrame]:
        """Fetch candlestick data for symbol and timeframe"""
        if symbol not in self.instrument_tokens:
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Map timeframe to Kite API format
            interval_map = {
                "minute": "minute",
                "5minute": "5minute", 
                "15minute": "15minute"
            }
            
            interval = interval_map.get(timeframe, "minute")
            token = self.instrument_tokens[symbol]
            
            data = self.api_client.get_historical_data(
                instrument_token=token,
                from_date=start_time,
                to_date=end_time,
                interval=interval
            )
            
            if data is not None and len(data) > 0:
                # Add technical indicators
                data = self.add_technical_indicators(data)
                
                # Store in cache
                if symbol not in self.candle_data:
                    self.candle_data[symbol] = {}
                self.candle_data[symbol][timeframe] = data
                self.last_update[f"{symbol}_{timeframe}"] = datetime.now()
                
                return data
            
        except Exception as e:
            logger.debug(f"Error fetching {timeframe} data for {symbol}: {e}")
        
        return None
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to candlestick data"""
        if len(df) < 20:
            return df
        
        try:
            # Moving averages
            df['ema_5'] = talib.EMA(df['close'], timeperiod=5)
            df['ema_10'] = talib.EMA(df['close'], timeperiod=10)
            df['ema_20'] = talib.EMA(df['close'], timeperiod=20)
            
            # RSI
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
            
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close'])
            
            # Volume indicators
            df['volume_ema'] = talib.EMA(df['volume'], timeperiod=10)
            df['volume_ratio'] = df['volume'] / df['volume_ema']
            
            # Price change percentages
            df['price_change'] = df['close'].pct_change() * 100
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close'] * 100
            
            # Support/Resistance levels (rolling min/max)
            df['support_5'] = df['low'].rolling(window=5).min()
            df['resistance_5'] = df['high'].rolling(window=5).max()
            
        except Exception as e:
            logger.debug(f"Error adding technical indicators: {e}")
        
        return df
    
    def detect_dip_patterns(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[CandlePattern]:
        """Detect dip patterns in candlestick data"""
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        try:
            # Get last 10 candles for pattern analysis
            recent_data = df.tail(10)
            
            for i in range(2, len(recent_data)):
                current = recent_data.iloc[i]
                prev = recent_data.iloc[i-1]
                prev2 = recent_data.iloc[i-2]
                
                # Pattern 1: Sudden dip with volume spike
                if (current['price_change'] <= self.dip_threshold and 
                    current['volume_ratio'] >= 1.5):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Volume Dip",
                        timestamp=current.name,
                        confidence=75,
                        signal_type="BUY",
                        description=f"Price dropped {current['price_change']:.2f}% with {current['volume_ratio']:.1f}x volume",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'], 
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
                
                # Pattern 2: Hammer/Doji at support
                body_size = abs(current['close'] - current['open'])
                candle_range = current['high'] - current['low']
                
                if (candle_range > 0 and body_size / candle_range < 0.3 and 
                    current['low'] <= current['support_5'] * 1.001):  # Near support
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Hammer at Support",
                        timestamp=current.name,
                        confidence=60,
                        signal_type="BUY",
                        description=f"Small body candle at support level ₹{current['support_5']:.2f}",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'], 
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
                
                # Pattern 3: Bounce from oversold RSI
                if (hasattr(current, 'rsi') and current['rsi'] < 30 and 
                    current['close'] > prev['close'] and
                    current['volume_ratio'] >= 1.2):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Oversold Bounce",
                        timestamp=current.name,
                        confidence=70,
                        signal_type="BUY",
                        description=f"Bounce from RSI {current['rsi']:.1f} with volume confirmation",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
                
                # Pattern 4: Break above EMA with momentum
                if (hasattr(current, 'ema_5') and hasattr(current, 'ema_10') and
                    current['close'] > current['ema_5'] and
                    current['ema_5'] > current['ema_10'] and
                    prev['close'] <= prev['ema_5']):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="EMA Breakout",
                        timestamp=current.name,
                        confidence=65,
                        signal_type="BUY",
                        description=f"Price broke above EMA5 (₹{current['ema_5']:.2f}) with momentum",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
        
        except Exception as e:
            logger.debug(f"Error detecting dip patterns: {e}")
        
        return patterns
    
    def detect_exit_patterns(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[CandlePattern]:
        """Detect exit/sell patterns in candlestick data"""
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        try:
            recent_data = df.tail(10)
            
            for i in range(2, len(recent_data)):
                current = recent_data.iloc[i]
                prev = recent_data.iloc[i-1]
                
                # Pattern 1: Shooting star at resistance
                body_size = abs(current['close'] - current['open'])
                upper_shadow = current['high'] - max(current['open'], current['close'])
                candle_range = current['high'] - current['low']
                
                if (candle_range > 0 and upper_shadow / candle_range > 0.6 and
                    current['high'] >= current['resistance_5'] * 0.999):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Shooting Star",
                        timestamp=current.name,
                        confidence=70,
                        signal_type="SELL",
                        description=f"Long upper shadow at resistance ₹{current['resistance_5']:.2f}",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
                
                # Pattern 2: Volume exhaustion
                if (current['volume_ratio'] < 0.5 and current['price_change'] > 1.0):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Volume Exhaustion",
                        timestamp=current.name,
                        confidence=60,
                        signal_type="SELL",
                        description=f"Price up {current['price_change']:.2f}% but volume only {current['volume_ratio']:.1f}x average",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
                
                # Pattern 3: Overbought with divergence
                if (hasattr(current, 'rsi') and current['rsi'] > 70 and
                    current['close'] > prev['close'] and
                    hasattr(current, 'macd_hist') and current['macd_hist'] < prev['macd_hist']):
                    
                    patterns.append(CandlePattern(
                        symbol=symbol,
                        pattern_name="Overbought Divergence",
                        timestamp=current.name,
                        confidence=75,
                        signal_type="SELL",
                        description=f"RSI {current['rsi']:.1f} with MACD divergence",
                        ohlc_data={
                            'open': current['open'],
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close'],
                            'volume': current['volume']
                        }
                    ))
        
        except Exception as e:
            logger.debug(f"Error detecting exit patterns: {e}")
        
        return patterns
    
    def analyze_symbol(self, symbol: str) -> Dict[str, List[CandlePattern]]:
        """Perform complete candlestick analysis for a symbol"""
        results = {}
        
        for timeframe in self.timeframes:
            # Fetch fresh data
            df = self.fetch_candle_data(symbol, timeframe, hours_back=6)
            
            if df is not None and len(df) > 0:
                # Detect patterns
                dip_patterns = self.detect_dip_patterns(df, symbol, timeframe)
                exit_patterns = self.detect_exit_patterns(df, symbol, timeframe)
                
                results[timeframe] = {
                    'dip_patterns': dip_patterns,
                    'exit_patterns': exit_patterns,
                    'latest_price': df['close'].iloc[-1],
                    'latest_volume': df['volume'].iloc[-1],
                    'data_points': len(df)
                }
        
        return results
    
    def get_realtime_signals(self) -> List[IntraDaySignal]:
        """Get real-time intraday signals across all ETFs"""
        signals = []
        
        if not self.instrument_tokens:
            self.initialize_tokens()
        
        logger.info("🔍 Scanning for intraday patterns...")
        
        for symbol in self.etf_symbols:
            try:
                # Analyze each timeframe
                analysis = self.analyze_symbol(symbol)
                
                for timeframe, data in analysis.items():
                    # Process dip patterns (BUY signals)
                    for pattern in data.get('dip_patterns', []):
                        signal = IntraDaySignal(
                            symbol=symbol,
                            signal_type="BUY",
                            timestamp=pattern.timestamp,
                            price=pattern.ohlc_data['close'],
                            volume=int(pattern.ohlc_data['volume']),
                            strength=self._get_signal_strength(pattern.confidence),
                            timeframe=timeframe,
                            supporting_indicators=[pattern.pattern_name],
                            risk_level=self._get_risk_level(pattern.confidence, timeframe)
                        )
                        signals.append(signal)
                    
                    # Process exit patterns (SELL signals)
                    for pattern in data.get('exit_patterns', []):
                        signal = IntraDaySignal(
                            symbol=symbol,
                            signal_type="SELL",
                            timestamp=pattern.timestamp,
                            price=pattern.ohlc_data['close'],
                            volume=int(pattern.ohlc_data['volume']),
                            strength=self._get_signal_strength(pattern.confidence),
                            timeframe=timeframe,
                            supporting_indicators=[pattern.pattern_name],
                            risk_level=self._get_risk_level(pattern.confidence, timeframe)
                        )
                        signals.append(signal)
            
            except Exception as e:
                logger.debug(f"Error analyzing {symbol}: {e}")
        
        # Sort signals by confidence (strength)
        signals.sort(key=lambda x: (x.strength, x.timeframe), reverse=True)
        
        logger.info(f"📊 Found {len(signals)} intraday signals")
        return signals
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convert confidence to signal strength"""
        if confidence >= 75:
            return "STRONG"
        elif confidence >= 60:
            return "MEDIUM"
        else:
            return "WEAK"
    
    def _get_risk_level(self, confidence: float, timeframe: str) -> str:
        """Determine risk level based on confidence and timeframe"""
        if timeframe == "minute" and confidence < 70:
            return "HIGH"
        elif confidence >= 75:
            return "LOW"
        else:
            return "MEDIUM"
    
    def print_signal_summary(self, signals: List[IntraDaySignal]):
        """Print a formatted summary of signals"""
        if not signals:
            print("📊 No intraday signals found at this time")
            return
        
        print(f"\n📊 INTRADAY SIGNALS SUMMARY")
        print("=" * 60)
        
        buy_signals = [s for s in signals if s.signal_type == "BUY"]
        sell_signals = [s for s in signals if s.signal_type == "SELL"]
        
        print(f"🟢 BUY Signals: {len(buy_signals)}")
        print(f"🔴 SELL Signals: {len(sell_signals)}")
        print(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Show top 5 strongest signals
        top_signals = signals[:5]
        
        if top_signals:
            print(f"\n🎯 TOP SIGNALS:")
            print("-" * 60)
            
            for i, signal in enumerate(top_signals, 1):
                action_emoji = "🟢" if signal.signal_type == "BUY" else "🔴"
                print(f"{i}. {action_emoji} {signal.symbol} @ ₹{signal.price:.2f}")
                print(f"   Timeframe: {signal.timeframe} | Strength: {signal.strength}")
                print(f"   Indicators: {', '.join(signal.supporting_indicators)}")
                print(f"   Risk: {signal.risk_level} | Volume: {signal.volume:,}")
                print()


def test_minute_analyzer():
    """Test the minute candle analyzer"""
    print("📊 TESTING MINUTE CANDLE ANALYZER")
    print("=" * 50)
    
    analyzer = MinuteCandleAnalyzer()
    
    # Initialize tokens
    analyzer.initialize_tokens()
    
    if analyzer.instrument_tokens:
        print(f"✅ Initialized tokens for {len(analyzer.instrument_tokens)} ETFs")
        
        # Test analysis on one symbol
        test_symbol = 'NIFTYBEES'
        print(f"\n🔍 Testing analysis on {test_symbol}...")
        
        analysis = analyzer.analyze_symbol(test_symbol)
        
        for timeframe, data in analysis.items():
            print(f"\n📈 {timeframe.upper()} Analysis:")
            print(f"   Data points: {data.get('data_points', 0)}")
            print(f"   Latest price: ₹{data.get('latest_price', 0):.2f}")
            print(f"   Dip patterns: {len(data.get('dip_patterns', []))}")
            print(f"   Exit patterns: {len(data.get('exit_patterns', []))}")
            
            # Show pattern details
            for pattern in data.get('dip_patterns', [])[:2]:
                print(f"     🟢 {pattern.pattern_name}: {pattern.description}")
            
            for pattern in data.get('exit_patterns', [])[:2]:
                print(f"     🔴 {pattern.pattern_name}: {pattern.description}")
        
        # Get real-time signals
        print(f"\n🔍 Getting real-time signals across all ETFs...")
        signals = analyzer.get_realtime_signals()
        analyzer.print_signal_summary(signals)
        
    else:
        print("❌ Could not initialize instrument tokens")
    
    return analyzer


if __name__ == "__main__":
    test_minute_analyzer()