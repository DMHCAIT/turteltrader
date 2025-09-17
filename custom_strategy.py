"""
Custom ETF Strategy: 1% Dip Buy, 3% Profit Sell
ETF Trading with MTF Priority and CNC Fallback

Strategy Rules:
1. Buy ETF when price drops 1% from yesterday's close
2. Sell when profit reaches 3%
3. Alert when loss reaches 5%
4. Only one position per ETF until sold
5. MTF orders first, CNC as fallback
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from etf_manager import ETFOrderType, ETFOrderRequest, etf_order_manager
from core.config import config

logger = logging.getLogger(__name__)

class PositionStatus(Enum):
    NO_POSITION = "NO_POSITION"
    OPEN_LONG = "OPEN_LONG"
    WAITING_SELL = "WAITING_SELL"

@dataclass
class ETFPosition:
    symbol: str
    entry_price: float
    entry_time: datetime
    quantity: int
    order_type: ETFOrderType
    status: PositionStatus
    target_price: float
    alert_price: float

@dataclass
class CustomSignal:
    symbol: str
    action: str  # BUY, SELL, ALERT
    current_price: float
    yesterday_close: float
    reason: str
    order_type: ETFOrderType
    urgency: str  # HIGH, MEDIUM, LOW

class CustomETFStrategy:
    """
    Custom ETF Strategy: 1% Dip Buy, 3% Target Sell, 5% Loss Alert
    """
    
    def __init__(self):
        self.name = "Custom ETF Dip Strategy"
        self.positions: Dict[str, ETFPosition] = {}
        
        # Strategy parameters from config
        self.buy_dip_percent = float(config.get('TRADING', 'BUY_DIP_PERCENT', fallback='1.0'))
        self.sell_target_percent = float(config.get('TRADING', 'SELL_TARGET_PERCENT', fallback='3.0'))
        self.loss_alert_percent = float(config.get('TRADING', 'LOSS_ALERT_PERCENT', fallback='5.0'))
        self.mtf_first_priority = config.getboolean('TRADING', 'MTF_FIRST_PRIORITY', fallback=True)
        self.one_position_per_etf = config.getboolean('TRADING', 'ONE_POSITION_PER_ETF', fallback=True)
        
        # ETF symbols to monitor
        self.etf_symbols = config.get('TRADING', 'SYMBOLS', fallback='').split(',')
        self.etf_symbols = [s.strip() for s in self.etf_symbols if s.strip()]
        
        logger.info(f"Custom ETF Strategy initialized")
        logger.info(f"Buy Dip: {self.buy_dip_percent}%, Sell Target: {self.sell_target_percent}%")
        logger.info(f"Loss Alert: {self.loss_alert_percent}%, MTF Priority: {self.mtf_first_priority}")
        logger.info(f"Monitoring ETFs: {self.etf_symbols}")
    
    def get_yesterday_close(self, symbol: str, current_data: pd.DataFrame) -> Optional[float]:
        """Get yesterday's closing price for the ETF"""
        try:
            if len(current_data) < 2:
                return None
            
            # Get the previous day's close (assuming data is sorted by time)
            yesterday_close = current_data['close'].iloc[-2]
            return float(yesterday_close)
            
        except Exception as e:
            logger.error(f"Error getting yesterday close for {symbol}: {e}")
            return None
    
    def calculate_price_change_percent(self, current_price: float, yesterday_close: float) -> float:
        """Calculate percentage change from yesterday's close"""
        if yesterday_close == 0:
            return 0
        return ((current_price - yesterday_close) / yesterday_close) * 100
    
    def determine_order_type(self, symbol: str) -> ETFOrderType:
        """
        Determine order type: MTF first priority, CNC fallback
        """
        if not self.mtf_first_priority:
            return ETFOrderType.CNC
        
        try:
            # Try MTF first
            if etf_order_manager._check_mtf_margin_available(symbol):
                logger.info(f"Using MTF for {symbol} - sufficient margin available")
                return ETFOrderType.MTF
            else:
                logger.info(f"MTF not available for {symbol}, falling back to CNC")
                return ETFOrderType.CNC
        except Exception as e:
            logger.warning(f"Error checking MTF availability for {symbol}: {e}")
            logger.info(f"Defaulting to CNC for {symbol}")
            return ETFOrderType.CNC
    
    def check_buy_signal(self, symbol: str, current_price: float, 
                        yesterday_close: float) -> Optional[CustomSignal]:
        """
        Check if ETF qualifies for buy signal (1% dip from yesterday close)
        """
        # Don't buy if already have position
        if symbol in self.positions and self.positions[symbol].status != PositionStatus.NO_POSITION:
            return None
        
        # Calculate price change from yesterday
        price_change = self.calculate_price_change_percent(current_price, yesterday_close)
        
        # Buy signal: price dropped by at least 1% from yesterday's close
        if price_change <= -self.buy_dip_percent:
            order_type = self.determine_order_type(symbol)
            
            return CustomSignal(
                symbol=symbol,
                action="BUY",
                current_price=current_price,
                yesterday_close=yesterday_close,
                reason=f"Price dip {price_change:.2f}% from yesterday close (₹{yesterday_close:.2f})",
                order_type=order_type,
                urgency="HIGH" if price_change <= -2.0 else "MEDIUM"
            )
        
        return None
    
    def check_sell_signal(self, position: ETFPosition, current_price: float) -> Optional[CustomSignal]:
        """
        Check if position should be sold (3% profit target)
        """
        profit_percent = ((current_price - position.entry_price) / position.entry_price) * 100
        
        # Sell signal: profit reached target
        if profit_percent >= self.sell_target_percent:
            return CustomSignal(
                symbol=position.symbol,
                action="SELL",
                current_price=current_price,
                yesterday_close=position.entry_price,  # Using entry price as reference
                reason=f"Target reached: {profit_percent:.2f}% profit (₹{current_price:.2f})",
                order_type=position.order_type,
                urgency="HIGH"
            )
        
        return None
    
    def check_alert_signal(self, position: ETFPosition, current_price: float) -> Optional[CustomSignal]:
        """
        Check if position needs loss alert (5% loss)
        """
        loss_percent = ((position.entry_price - current_price) / position.entry_price) * 100
        
        # Alert signal: loss reached alert threshold
        if loss_percent >= self.loss_alert_percent:
            return CustomSignal(
                symbol=position.symbol,
                action="ALERT",
                current_price=current_price,
                yesterday_close=position.entry_price,
                reason=f"⚠️ LOSS ALERT: {loss_percent:.2f}% loss (₹{current_price:.2f})",
                order_type=position.order_type,
                urgency="HIGH"
            )
        
        return None
    
    def analyze_etf(self, symbol: str, market_data: pd.DataFrame) -> List[CustomSignal]:
        """
        Analyze single ETF for buy/sell/alert signals
        """
        signals = []
        
        try:
            if len(market_data) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return signals
            
            current_price = float(market_data['close'].iloc[-1])
            yesterday_close = self.get_yesterday_close(symbol, market_data)
            
            if yesterday_close is None:
                logger.warning(f"Could not get yesterday close for {symbol}")
                return signals
            
            # Check existing position first
            if symbol in self.positions:
                position = self.positions[symbol]
                
                if position.status == PositionStatus.OPEN_LONG:
                    # Check for sell signal
                    sell_signal = self.check_sell_signal(position, current_price)
                    if sell_signal:
                        signals.append(sell_signal)
                    
                    # Check for alert signal
                    alert_signal = self.check_alert_signal(position, current_price)
                    if alert_signal:
                        signals.append(alert_signal)
            
            else:
                # No position - check for buy signal
                buy_signal = self.check_buy_signal(symbol, current_price, yesterday_close)
                if buy_signal:
                    signals.append(buy_signal)
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
        
        return signals
    
    def execute_buy_order(self, signal: CustomSignal) -> bool:
        """
        Execute buy order and track position
        """
        try:
            # Create buy order
            order = etf_order_manager.create_etf_buy_order(
                symbol=signal.symbol,
                price=signal.current_price,
                order_type=signal.order_type
            )
            
            # Calculate target and alert prices
            target_price = signal.current_price * (1 + self.sell_target_percent / 100)
            alert_price = signal.current_price * (1 - self.loss_alert_percent / 100)
            
            # Track position
            self.positions[signal.symbol] = ETFPosition(
                symbol=signal.symbol,
                entry_price=signal.current_price,
                entry_time=datetime.now(),
                quantity=order.quantity,
                order_type=signal.order_type,
                status=PositionStatus.OPEN_LONG,
                target_price=target_price,
                alert_price=alert_price
            )
            
            logger.info(f"✅ BUY ORDER: {signal.symbol} @ ₹{signal.current_price:.2f}")
            logger.info(f"   Order Type: {signal.order_type.value}")
            logger.info(f"   Quantity: {order.quantity}")
            logger.info(f"   Target: ₹{target_price:.2f} ({self.sell_target_percent}%)")
            logger.info(f"   Alert: ₹{alert_price:.2f} ({self.loss_alert_percent}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing buy order for {signal.symbol}: {e}")
            return False
    
    def execute_sell_order(self, signal: CustomSignal) -> bool:
        """
        Execute sell order and close position
        """
        try:
            position = self.positions.get(signal.symbol)
            if not position:
                logger.error(f"No position found for {signal.symbol}")
                return False
            
            # Create sell order
            order = etf_order_manager.create_etf_sell_order(
                symbol=signal.symbol,
                quantity=position.quantity,
                price=signal.current_price
            )
            
            # Calculate profit/loss
            profit_amount = (signal.current_price - position.entry_price) * position.quantity
            profit_percent = ((signal.current_price - position.entry_price) / position.entry_price) * 100
            
            # Close position
            self.positions[signal.symbol].status = PositionStatus.NO_POSITION
            
            logger.info(f"✅ SELL ORDER: {signal.symbol} @ ₹{signal.current_price:.2f}")
            logger.info(f"   Profit: ₹{profit_amount:.2f} ({profit_percent:.2f}%)")
            logger.info(f"   Entry: ₹{position.entry_price:.2f}")
            logger.info(f"   Quantity: {position.quantity}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing sell order for {signal.symbol}: {e}")
            return False
    
    def send_alert(self, signal: CustomSignal):
        """
        Send loss alert notification
        """
        position = self.positions.get(signal.symbol)
        if not position:
            return
        
        alert_msg = f"🚨 LOSS ALERT: {signal.symbol}\n"
        alert_msg += f"Current: ₹{signal.current_price:.2f}\n"
        alert_msg += f"Entry: ₹{position.entry_price:.2f}\n"
        alert_msg += f"Loss: {signal.reason}\n"
        alert_msg += f"Consider reviewing position!"
        
        logger.warning(alert_msg)
        print(f"\n{alert_msg}\n")  # Console alert
    
    def get_signals(self, etf_market_data: Dict[str, pd.DataFrame]) -> List[CustomSignal]:
        """
        Main method to get all trading signals
        """
        all_signals = []
        
        logger.info(f"🔍 Analyzing {len(etf_market_data)} ETFs for custom strategy signals...")
        
        for symbol, data in etf_market_data.items():
            if symbol in self.etf_symbols:
                signals = self.analyze_etf(symbol, data)
                all_signals.extend(signals)
        
        # Sort by urgency
        urgency_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_signals.sort(key=lambda x: urgency_order.get(x.urgency, 3))
        
        return all_signals
    
    def process_signals(self, signals: List[CustomSignal]):
        """
        Process and execute trading signals
        """
        for signal in signals:
            try:
                if signal.action == "BUY":
                    self.execute_buy_order(signal)
                elif signal.action == "SELL":
                    self.execute_sell_order(signal)
                elif signal.action == "ALERT":
                    self.send_alert(signal)
                    
            except Exception as e:
                logger.error(f"Error processing signal for {signal.symbol}: {e}")
    
    def get_position_summary(self) -> Dict:
        """
        Get summary of current positions
        """
        summary = {
            'total_positions': len([p for p in self.positions.values() 
                                  if p.status == PositionStatus.OPEN_LONG]),
            'positions': {},
            'total_invested': 0
        }
        
        for symbol, position in self.positions.items():
            if position.status == PositionStatus.OPEN_LONG:
                invested_amount = position.entry_price * position.quantity
                summary['positions'][symbol] = {
                    'entry_price': position.entry_price,
                    'quantity': position.quantity,
                    'invested': invested_amount,
                    'target': position.target_price,
                    'alert': position.alert_price,
                    'order_type': position.order_type.value
                }
                summary['total_invested'] += invested_amount
        
        return summary

# Initialize the custom strategy
custom_etf_strategy = CustomETFStrategy()

if __name__ == "__main__":
    print("🎯 Custom ETF Strategy: 1% Dip Buy, 3% Target Sell, 5% Loss Alert")
    print("📊 ETF symbols:", custom_etf_strategy.etf_symbols)
    print("🎮 Strategy parameters:")
    print(f"   • Buy dip: {custom_etf_strategy.buy_dip_percent}%")
    print(f"   • Sell target: {custom_etf_strategy.sell_target_percent}%")
    print(f"   • Loss alert: {custom_etf_strategy.loss_alert_percent}%")
    print(f"   • MTF priority: {custom_etf_strategy.mtf_first_priority}")
    print(f"   • One position per ETF: {custom_etf_strategy.one_position_per_etf}")
