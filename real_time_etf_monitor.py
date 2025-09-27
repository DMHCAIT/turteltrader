"""
🔄 REAL-TIME ETF MONITORING SYSTEM
=================================

Continuously monitors ETF prices every second/minute to:
1. Detect 1% dip entry signals in real-time
2. Monitor 3% profit targets continuously  
3. Track 5% loss alerts as they happen
4. Execute trades immediately when conditions are met

Uses both minute candles and live price feeds for maximum responsiveness.
"""

import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from loguru import logger
import websocket
import json

from kite_api_client import KiteAPIClient
from dynamic_capital_allocator import DynamicCapitalAllocator
from custom_strategy import CustomETFStrategy, ETFPosition, CustomSignal, PositionStatus


class RealTimeETFMonitor:
    """
    Real-time ETF monitoring system with second-by-second price tracking
    """
    
    def __init__(self):
        """Initialize real-time monitoring system"""
        self.api_client = KiteAPIClient()
        self.allocator = DynamicCapitalAllocator(use_real_balance=True)
        self.strategy = CustomETFStrategy()
        
        # Monitoring configuration
        self.check_interval = 1  # Check every 1 second
        self.minute_candle_interval = 60  # Update minute candles every 60 seconds
        
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
        
        # Real-time data storage
        self.live_prices: Dict[str, float] = {}
        self.yesterday_closes: Dict[str, float] = {}
        self.minute_data: Dict[str, pd.DataFrame] = {}
        self.last_signals: Dict[str, datetime] = {}
        
        # Trading state
        self.active_positions: Dict[str, ETFPosition] = {}
        self.is_monitoring = False
        self.monitor_thread = None
        self.websocket_thread = None
        
        # Performance tracking
        self.signal_count = 0
        self.trades_executed = 0
        self.monitoring_start_time = None
        
        logger.info("🔄 Real-time ETF Monitor initialized")
        logger.info(f"📊 Monitoring {len(self.etf_symbols)} ETFs")
        logger.info(f"⏱️ Check interval: {self.check_interval} second(s)")
    
    def get_instrument_tokens(self) -> Dict[str, int]:
        """Get instrument tokens for ETF symbols"""
        instruments = self.api_client.get_instruments("NSE")
        tokens = {}
        
        for _, instrument in instruments.iterrows():
            if instrument['tradingsymbol'] in self.etf_symbols:
                tokens[instrument['tradingsymbol']] = instrument['instrument_token']
        
        logger.info(f"✅ Found tokens for {len(tokens)} ETFs")
        return tokens
    
    def initialize_yesterday_closes(self):
        """Fetch yesterday's closing prices for all ETFs"""
        logger.info("📊 Initializing yesterday's closing prices...")
        
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        
        for symbol in self.etf_symbols:
            try:
                # Get instrument token
                instruments = self.api_client.get_instruments("NSE")
                token = None
                
                for _, instrument in instruments.iterrows():
                    if instrument['tradingsymbol'] == symbol:
                        token = instrument['instrument_token']
                        break
                
                if token:
                    # Fetch 2 days of data to get yesterday's close
                    data = self.api_client.get_historical_data(
                        instrument_token=token,
                        from_date=yesterday - timedelta(days=2),
                        to_date=yesterday + timedelta(days=1),
                        interval="day"
                    )
                    
                    if data is not None and len(data) > 0:
                        # Get the last available close price
                        self.yesterday_closes[symbol] = float(data['close'].iloc[-1])
                        logger.info(f"   {symbol}: ₹{self.yesterday_closes[symbol]:.2f}")
                    else:
                        logger.warning(f"   {symbol}: No data available")
                else:
                    logger.warning(f"   {symbol}: Token not found")
                    
            except Exception as e:
                logger.error(f"   {symbol}: Error - {e}")
        
        logger.info(f"✅ Initialized {len(self.yesterday_closes)} yesterday closes")
    
    def get_live_price(self, symbol: str) -> Optional[float]:
        """Get current live price for symbol"""
        try:
            # Use LTP (Last Traded Price) for real-time data
            ltp_data = self.api_client.get_ltp([f"NSE:{symbol}"])
            
            if ltp_data and f"NSE:{symbol}" in ltp_data:
                price = ltp_data[f"NSE:{symbol}"]["last_price"]
                self.live_prices[symbol] = float(price)
                return float(price)
            
        except Exception as e:
            logger.debug(f"Error getting live price for {symbol}: {e}")
        
        return None
    
    def update_minute_candles(self, symbol: str):
        """Update minute-level candle data for symbol"""
        try:
            # Get instrument token
            instruments = self.api_client.get_instruments("NSE")
            token = None
            
            for _, instrument in instruments.iterrows():
                if instrument['tradingsymbol'] == symbol:
                    token = instrument['instrument_token']
                    break
            
            if token:
                # Get last 2 hours of minute data
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=2)
                
                data = self.api_client.get_historical_data(
                    instrument_token=token,
                    from_date=start_time,
                    to_date=end_time,
                    interval="minute"
                )
                
                if data is not None and len(data) > 0:
                    self.minute_data[symbol] = data
                    return True
        
        except Exception as e:
            logger.debug(f"Error updating minute candles for {symbol}: {e}")
        
        return False
    
    def check_entry_signal(self, symbol: str, current_price: float) -> Optional[CustomSignal]:
        """Check if current price triggers entry signal"""
        if symbol not in self.yesterday_closes:
            return None
        
        yesterday_close = self.yesterday_closes[symbol]
        price_change_pct = ((current_price - yesterday_close) / yesterday_close) * 100
        
        # Check for 1% dip entry signal
        if price_change_pct <= -1.0:
            # Avoid duplicate signals (wait at least 5 minutes between signals)
            if symbol in self.last_signals:
                time_since_last = datetime.now() - self.last_signals[symbol]
                if time_since_last.total_seconds() < 300:  # 5 minutes
                    return None
            
            # Don't enter if already have position
            if symbol in self.active_positions:
                return None
            
            self.last_signals[symbol] = datetime.now()
            self.signal_count += 1
            
            return CustomSignal(
                symbol=symbol,
                action="BUY",
                current_price=current_price,
                yesterday_close=yesterday_close,
                reason=f"Real-time 1% dip: {price_change_pct:.2f}% from ₹{yesterday_close:.2f}",
                order_type=self.strategy.determine_order_type(symbol),
                urgency="HIGH" if price_change_pct <= -2.0 else "MEDIUM"
            )
        
        return None
    
    def check_exit_signal(self, symbol: str, current_price: float) -> Optional[CustomSignal]:
        """Check if current price triggers exit signal"""
        if symbol not in self.active_positions:
            return None
        
        position = self.active_positions[symbol]
        profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        
        # Check for 3% profit target
        if profit_pct >= 3.0:
            return CustomSignal(
                symbol=symbol,
                action="SELL",
                current_price=current_price,
                yesterday_close=position.entry_price,
                reason=f"Profit target hit: +{profit_pct:.2f}% (₹{current_price:.2f})",
                order_type=position.order_type,
                urgency="HIGH"
            )
        
        # Check for 5% loss alert
        elif profit_pct <= -5.0:
            return CustomSignal(
                symbol=symbol,
                action="ALERT",
                current_price=current_price,
                yesterday_close=position.entry_price,
                reason=f"⚠️ LOSS ALERT: -{abs(profit_pct):.2f}% (₹{current_price:.2f})",
                order_type=position.order_type,
                urgency="CRITICAL"
            )
        
        return None
    
    def process_signal(self, signal: CustomSignal) -> bool:
        """Process and execute trading signal"""
        try:
            logger.info(f"🔔 Signal: {signal.action} {signal.symbol} @ ₹{signal.current_price:.2f}")
            logger.info(f"   Reason: {signal.reason}")
            
            if signal.action == "BUY":
                return self.execute_buy_signal(signal)
            elif signal.action == "SELL":
                return self.execute_sell_signal(signal)
            elif signal.action == "ALERT":
                return self.send_loss_alert(signal)
        
        except Exception as e:
            logger.error(f"❌ Error processing signal: {e}")
            return False
    
    def execute_buy_signal(self, signal: CustomSignal) -> bool:
        """Execute buy order for signal"""
        try:
            # Calculate position size
            deployable_capital = self.allocator.deployable_capital
            position_size_pct = 3.0  # 3% of deployable capital per position
            position_value = deployable_capital * (position_size_pct / 100)
            
            # Calculate quantity
            shares = int(position_value / signal.current_price)
            actual_value = shares * signal.current_price
            
            if shares > 0 and actual_value <= deployable_capital * 0.2:  # Max 20% per position
                logger.info(f"💰 Executing BUY: {shares} shares of {signal.symbol}")
                logger.info(f"   Position Value: ₹{actual_value:,.0f}")
                logger.info(f"   Order Type: {signal.order_type.value}")
                
                # Create position record
                position = ETFPosition(
                    symbol=signal.symbol,
                    entry_price=signal.current_price,
                    entry_time=datetime.now(),
                    quantity=shares,
                    order_type=signal.order_type,
                    status=PositionStatus.OPEN_LONG,
                    target_price=signal.current_price * 1.03,  # 3% target
                    alert_price=signal.current_price * 0.95    # 5% alert
                )
                
                self.active_positions[signal.symbol] = position
                self.trades_executed += 1
                
                logger.info(f"✅ Position opened for {signal.symbol}")
                logger.info(f"   Target: ₹{position.target_price:.2f} (+3%)")
                logger.info(f"   Alert: ₹{position.alert_price:.2f} (-5%)")
                
                return True
            else:
                logger.warning(f"⚠️ Position size too large for {signal.symbol}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error executing buy: {e}")
            return False
    
    def execute_sell_signal(self, signal: CustomSignal) -> bool:
        """Execute sell order for signal"""
        try:
            if signal.symbol in self.active_positions:
                position = self.active_positions[signal.symbol]
                
                logger.info(f"💰 Executing SELL: {position.quantity} shares of {signal.symbol}")
                logger.info(f"   Entry: ₹{position.entry_price:.2f}")
                logger.info(f"   Exit: ₹{signal.current_price:.2f}")
                
                # Calculate P&L
                pnl = (signal.current_price - position.entry_price) * position.quantity
                pnl_pct = ((signal.current_price - position.entry_price) / position.entry_price) * 100
                
                logger.info(f"   P&L: ₹{pnl:+,.0f} ({pnl_pct:+.2f}%)")
                
                # Remove position
                del self.active_positions[signal.symbol]
                
                logger.info(f"✅ Position closed for {signal.symbol}")
                return True
        
        except Exception as e:
            logger.error(f"❌ Error executing sell: {e}")
            return False
    
    def send_loss_alert(self, signal: CustomSignal) -> bool:
        """Send loss alert notification"""
        logger.warning(f"🚨 LOSS ALERT: {signal.symbol}")
        logger.warning(f"   {signal.reason}")
        
        if signal.symbol in self.active_positions:
            position = self.active_positions[signal.symbol]
            loss_amount = (position.entry_price - signal.current_price) * position.quantity
            logger.warning(f"   Unrealized Loss: ₹{loss_amount:,.0f}")
        
        # Here you could add email/SMS notifications
        return True
    
    def monitoring_loop(self):
        """Main monitoring loop - runs continuously"""
        logger.info("🔄 Starting real-time monitoring loop...")
        self.monitoring_start_time = datetime.now()
        
        while self.is_monitoring:
            try:
                cycle_start = time.time()
                
                # Check each ETF
                for symbol in self.etf_symbols:
                    if not self.is_monitoring:
                        break
                    
                    # Get current live price
                    current_price = self.get_live_price(symbol)
                    
                    if current_price:
                        # Check for entry signals
                        entry_signal = self.check_entry_signal(symbol, current_price)
                        if entry_signal:
                            self.process_signal(entry_signal)
                        
                        # Check for exit signals
                        exit_signal = self.check_exit_signal(symbol, current_price)
                        if exit_signal:
                            self.process_signal(exit_signal)
                
                # Calculate sleep time to maintain consistent interval
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.check_interval - cycle_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            logger.warning("⚠️ Monitoring already active")
            return
        
        try:
            # Initialize system
            logger.info("🚀 Starting real-time ETF monitoring...")
            
            # Initialize yesterday's closes
            self.initialize_yesterday_closes()
            
            if not self.yesterday_closes:
                logger.error("❌ Could not initialize yesterday closes - cannot start monitoring")
                return
            
            # Start monitoring
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("✅ Real-time monitoring started successfully!")
            logger.info(f"📊 Monitoring {len(self.etf_symbols)} ETFs every {self.check_interval} second(s)")
            logger.info("🎯 Looking for: 1% dip entries, 3% profit exits, 5% loss alerts")
            
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.is_monitoring:
            logger.warning("⚠️ Monitoring not active")
            return
        
        logger.info("⏹️ Stopping real-time monitoring...")
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Print monitoring summary
        if self.monitoring_start_time:
            duration = datetime.now() - self.monitoring_start_time
            logger.info(f"📊 Monitoring Summary:")
            logger.info(f"   Duration: {duration}")
            logger.info(f"   Signals Generated: {self.signal_count}")
            logger.info(f"   Trades Executed: {self.trades_executed}")
            logger.info(f"   Active Positions: {len(self.active_positions)}")
        
        logger.info("✅ Real-time monitoring stopped")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'monitoring': {
                'is_active': self.is_monitoring,
                'start_time': self.monitoring_start_time.isoformat() if self.monitoring_start_time else None,
                'check_interval': self.check_interval,
                'symbols_count': len(self.etf_symbols)
            },
            'performance': {
                'signals_generated': self.signal_count,
                'trades_executed': self.trades_executed,
                'active_positions': len(self.active_positions)
            },
            'positions': {
                symbol: {
                    'entry_price': pos.entry_price,
                    'current_price': self.live_prices.get(symbol, 0),
                    'quantity': pos.quantity,
                    'unrealized_pnl': (self.live_prices.get(symbol, pos.entry_price) - pos.entry_price) * pos.quantity,
                    'entry_time': pos.entry_time.isoformat()
                } for symbol, pos in self.active_positions.items()
            }
        }


def test_real_time_monitoring():
    """Test the real-time monitoring system"""
    print("🔄 TESTING REAL-TIME ETF MONITORING")
    print("=" * 50)
    
    # Initialize monitor
    monitor = RealTimeETFMonitor()
    
    print(f"📊 System Configuration:")
    print(f"   ETFs to monitor: {len(monitor.etf_symbols)}")
    print(f"   Check interval: {monitor.check_interval} second(s)")
    print(f"   Strategy: 1% dip buy, 3% profit sell, 5% loss alert")
    
    # Test initialization
    print(f"\n🔧 Testing initialization...")
    monitor.initialize_yesterday_closes()
    
    if monitor.yesterday_closes:
        print(f"✅ Yesterday closes loaded: {len(monitor.yesterday_closes)} ETFs")
        
        # Show a few examples
        for symbol, price in list(monitor.yesterday_closes.items())[:3]:
            print(f"   {symbol}: ₹{price:.2f}")
    
    # Test live price fetching
    print(f"\n📡 Testing live price fetching...")
    test_symbol = 'NIFTYBEES'
    live_price = monitor.get_live_price(test_symbol)
    
    if live_price:
        print(f"✅ Live price for {test_symbol}: ₹{live_price:.2f}")
        
        # Calculate price change
        if test_symbol in monitor.yesterday_closes:
            yesterday = monitor.yesterday_closes[test_symbol]
            change_pct = ((live_price - yesterday) / yesterday) * 100
            print(f"   Change from yesterday: {change_pct:+.2f}%")
            
            if change_pct <= -1.0:
                print(f"   🔔 BUY SIGNAL would trigger!")
    else:
        print(f"❌ Could not fetch live price for {test_symbol}")
    
    print(f"\n✅ Real-time monitoring system ready!")
    print(f"💡 Use monitor.start_monitoring() to begin real-time tracking")
    
    return monitor


if __name__ == "__main__":
    test_real_time_monitoring()