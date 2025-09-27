"""
🚀 ENHANCED TURTLE TRADER - REAL-TIME INTRADAY SYSTEM
===================================================

Combines multiple monitoring systems for comprehensive market coverage:

1. Second-by-second price monitoring (real_time_etf_monitor)
2. Minute-by-minute candlestick analysis (minute_candle_analyzer) 
3. Multi-timeframe pattern detection (1min, 5min, 15min)
4. Enhanced entry/exit timing with technical confirmations

Your strategy now checks EVERY price movement in real-time!
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from loguru import logger
import json

from real_time_etf_monitor import RealTimeETFMonitor
from minute_candle_analyzer import MinuteCandleAnalyzer, IntraDaySignal
from custom_strategy import CustomSignal
from dynamic_capital_allocator import DynamicCapitalAllocator
from etf_universe_config import (
    get_high_priority_etfs, get_etf_allocation_weight, 
    get_etf_info, ETFRiskLevel, print_etf_universe_summary
)


class EnhancedTurtleTrader:
    """
    Enhanced Turtle Trading System with real-time intraday monitoring
    
    Features:
    - Real-time price monitoring (every second)
    - Minute candlestick pattern analysis
    - Multi-timeframe signal confirmation
    - Enhanced entry/exit timing
    - Risk management with position sizing
    """
    
    def __init__(self):
        """Initialize enhanced turtle trading system"""
        
        # Core components
        self.real_time_monitor = RealTimeETFMonitor()
        self.candle_analyzer = MinuteCandleAnalyzer() 
        self.capital_allocator = DynamicCapitalAllocator(use_real_balance=True)
        
        # System settings
        self.monitoring_active = False
        self.analysis_interval = 60  # Analyze candlestick patterns every 60 seconds
        self.signal_confidence_threshold = 60  # Minimum confidence for signals
        
        # Smart ETF selection - Focus on high priority ETFs for better performance
        self.focus_mode = True  # Set to False to monitor all 65 ETFs
        self.priority_etfs = get_high_priority_etfs()  # Priority 1-3 ETFs only
        
        # Signal management
        self.confirmed_signals: List[Dict] = []
        self.signal_history: List[Dict] = []
        self.last_candle_analysis = None
        
        # Performance tracking
        self.session_stats = {
            'start_time': None,
            'real_time_signals': 0,
            'candle_signals': 0,
            'confirmed_signals': 0,
            'trades_executed': 0,
            'total_pnl': 0.0
        }
        
        logger.info("🚀 Enhanced Turtle Trader System initialized")
        logger.info("📊 Real-time monitoring + Candlestick analysis ready")
    
    async def initialize_system(self):
        """Initialize all system components"""
        logger.info("🔧 Initializing Enhanced Turtle Trading System...")
        
        try:
            # Initialize capital allocator
            await asyncio.to_thread(self.capital_allocator.update_balance)
            balance = self.capital_allocator.total_balance
            deployable = self.capital_allocator.deployable_capital
            
            logger.info(f"💰 Account Balance: ₹{balance:,.0f}")
            logger.info(f"💰 Deployable Capital: ₹{deployable:,.0f}")
            
            # Initialize real-time monitor
            await asyncio.to_thread(self.real_time_monitor.initialize_yesterday_closes)
            
            if not self.real_time_monitor.yesterday_closes:
                logger.error("❌ Could not initialize yesterday closes")
                return False
            
            logger.info(f"✅ Yesterday closes loaded: {len(self.real_time_monitor.yesterday_closes)} ETFs")
            
            # Initialize candle analyzer
            await asyncio.to_thread(self.candle_analyzer.initialize_tokens)
            
            if not self.candle_analyzer.instrument_tokens:
                logger.error("❌ Could not initialize instrument tokens")
                return False
            
            logger.info(f"✅ Instrument tokens loaded: {len(self.candle_analyzer.instrument_tokens)} ETFs")
            
            # Print ETF selection summary
            if self.focus_mode:
                logger.info(f"🎯 FOCUS MODE: Monitoring {len(self.priority_etfs)} high-priority ETFs")
                logger.info(f"   Priority ETFs: {', '.join(self.priority_etfs[:10])}{'...' if len(self.priority_etfs) > 10 else ''}")
            else:
                logger.info(f"🌐 FULL MODE: Monitoring all {len(self.real_time_monitor.etf_symbols)} ETFs")
            
            # System ready
            logger.info("✅ Enhanced Turtle Trading System initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def start_monitoring(self):
        """Start comprehensive monitoring system"""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoring already active")
            return
        
        # Initialize system first
        if not await self.initialize_system():
            logger.error("❌ Cannot start monitoring - initialization failed")
            return
        
        logger.info("🚀 Starting Enhanced Turtle Trading Monitoring...")
        self.monitoring_active = True
        self.session_stats['start_time'] = datetime.now()
        
        # Start real-time monitor in separate thread
        await asyncio.to_thread(self.real_time_monitor.start_monitoring)
        
        logger.info("✅ Real-time price monitoring active (every 1 second)")
        logger.info("📊 Candlestick analysis will run every 60 seconds")
        logger.info("🎯 Looking for: Enhanced entry/exit signals with confirmations")
        
        # Start main monitoring loop
        await self.monitoring_loop()
    
    async def monitoring_loop(self):
        """Main monitoring loop with enhanced signal detection"""
        logger.info("🔄 Enhanced monitoring loop started...")
        
        candle_analysis_counter = 0
        
        while self.monitoring_active:
            try:
                # Run candlestick analysis every minute
                if candle_analysis_counter % self.analysis_interval == 0:
                    await self.run_candle_analysis()
                
                # Check for confirmed signals and process them
                await self.process_confirmed_signals()
                
                # Update system stats
                await self.update_session_stats()
                
                # Log status every 5 minutes
                if candle_analysis_counter % 300 == 0 and candle_analysis_counter > 0:
                    await self.log_system_status()
                
                candle_analysis_counter += 1
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def run_candle_analysis(self):
        """Run comprehensive candlestick analysis"""
        try:
            logger.debug("📊 Running candlestick pattern analysis...")
            
            # Get intraday signals from candle analyzer
            signals = await asyncio.to_thread(self.candle_analyzer.get_realtime_signals)
            
            if signals:
                self.session_stats['candle_signals'] += len(signals)
                
                # Filter high-confidence signals
                strong_signals = [s for s in signals if s.strength in ["STRONG", "MEDIUM"]]
                
                if strong_signals:
                    logger.info(f"📊 Found {len(strong_signals)} strong candlestick signals")
                    
                    # Cross-reference with real-time monitor signals
                    await self.cross_validate_signals(strong_signals)
            
            self.last_candle_analysis = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error in candle analysis: {e}")
    
    async def cross_validate_signals(self, candle_signals: List[IntraDaySignal]):
        """Cross-validate candlestick signals with real-time price data"""
        for signal in candle_signals:
            try:
                # Get current live price
                live_price = await asyncio.to_thread(
                    self.real_time_monitor.get_live_price, 
                    signal.symbol
                )
                
                if not live_price:
                    continue
                
                # Check if signal is still valid (price within 0.5% of signal price)
                price_diff_pct = abs(live_price - signal.price) / signal.price * 100
                
                if price_diff_pct <= 0.5:  # Signal still valid
                    
                    # For BUY signals, check if it's still a dip
                    if signal.signal_type == "BUY":
                        yesterday_close = self.real_time_monitor.yesterday_closes.get(signal.symbol)
                        if yesterday_close:
                            current_change = (live_price - yesterday_close) / yesterday_close * 100
                            
                            # Confirm it's still a dip (at least 0.5% down)
                            if current_change <= -0.5:
                                await self.create_confirmed_signal(signal, live_price, "CANDLE_VALIDATED")
                    
                    # For SELL signals, check if we have position
                    elif signal.signal_type == "SELL":
                        if signal.symbol in self.real_time_monitor.active_positions:
                            await self.create_confirmed_signal(signal, live_price, "EXIT_VALIDATED")
                
            except Exception as e:
                logger.debug(f"Error validating signal for {signal.symbol}: {e}")
    
    async def create_confirmed_signal(self, base_signal: IntraDaySignal, current_price: float, validation_type: str):
        """Create a confirmed trading signal"""
        confirmed_signal = {
            'symbol': base_signal.symbol,
            'action': base_signal.signal_type,
            'price': current_price,
            'timestamp': datetime.now(),
            'timeframe': base_signal.timeframe,
            'strength': base_signal.strength,
            'risk_level': base_signal.risk_level,
            'validation': validation_type,
            'supporting_indicators': base_signal.supporting_indicators,
            'original_signal_time': base_signal.timestamp,
            'processed': False
        }
        
        self.confirmed_signals.append(confirmed_signal)
        self.session_stats['confirmed_signals'] += 1
        
        logger.info(f"✅ CONFIRMED {base_signal.signal_type}: {base_signal.symbol} @ ₹{current_price:.2f}")
        logger.info(f"   Validation: {validation_type}")
        logger.info(f"   Strength: {base_signal.strength} | Risk: {base_signal.risk_level}")
        logger.info(f"   Timeframe: {base_signal.timeframe}")
    
    async def process_confirmed_signals(self):
        """Process confirmed signals for execution"""
        unprocessed = [s for s in self.confirmed_signals if not s['processed']]
        
        for signal in unprocessed:
            try:
                # Check if signal is still fresh (within last 2 minutes)
                age = datetime.now() - signal['timestamp']
                if age.total_seconds() > 120:  # 2 minutes
                    signal['processed'] = True
                    logger.debug(f"⏰ Signal expired for {signal['symbol']}")
                    continue
                
                # Process based on action
                if signal['action'] == "BUY":
                    success = await self.execute_enhanced_buy(signal)
                elif signal['action'] == "SELL":
                    success = await self.execute_enhanced_sell(signal)
                
                if success:
                    self.session_stats['trades_executed'] += 1
                    logger.info(f"✅ Trade executed for {signal['symbol']}")
                
                signal['processed'] = True
                
            except Exception as e:
                logger.error(f"❌ Error processing signal for {signal['symbol']}: {e}")
                signal['processed'] = True
    
    async def execute_enhanced_buy(self, signal: Dict) -> bool:
        """Execute enhanced buy order with confirmations"""
        try:
            symbol = signal['symbol']
            current_price = signal['price']
            
            # Double-check we don't already have a position
            if symbol in self.real_time_monitor.active_positions:
                logger.warning(f"⚠️ Already have position in {symbol}")
                return False
            
            # Enhanced position sizing based on multiple factors
            base_position_pct = 3.0  # Base 3% of deployable capital
            
            # Get ETF metadata for smart sizing
            etf_info = get_etf_info(symbol)
            allocation_weight = get_etf_allocation_weight(symbol)
            
            # Adjust based on signal strength
            if signal['strength'] == "STRONG" and signal['risk_level'] == "LOW":
                signal_multiplier = 1.2  # 20% increase for strong signals
            elif signal['strength'] == "MEDIUM":
                signal_multiplier = 1.0  # Base position
            else:
                signal_multiplier = 0.8  # 20% decrease for weak signals
            
            # Adjust based on ETF allocation weight (0.2 to 1.0)
            # Higher weight = larger position
            position_pct = base_position_pct * signal_multiplier * allocation_weight
            
            # Risk-based caps
            etf_risk = etf_info.get('risk_level')
            if etf_risk == ETFRiskLevel.VERY_HIGH:
                position_pct = min(position_pct, 2.0)  # Max 2% for very high risk
            elif etf_risk == ETFRiskLevel.HIGH:
                position_pct = min(position_pct, 3.5)  # Max 3.5% for high risk
            elif etf_risk == ETFRiskLevel.LOW:
                position_pct = min(position_pct, 5.0)  # Max 5% for low risk
            
            # Calculate shares
            position_value = self.capital_allocator.deployable_capital * (position_pct / 100)
            shares = int(position_value / current_price)
            actual_value = shares * current_price
            
            if shares > 0:
                logger.info(f"💰 ENHANCED BUY: {shares} shares of {symbol}")
                logger.info(f"   Position Value: ₹{actual_value:,.0f} ({position_pct:.1f}%)")
                logger.info(f"   Signal Strength: {signal['strength']} | Risk: {signal['risk_level']}")
                logger.info(f"   ETF Risk Level: {etf_info.get('risk_level', 'Unknown').value if etf_info.get('risk_level') else 'Unknown'}")
                logger.info(f"   Allocation Weight: {allocation_weight:.1f}x")
                logger.info(f"   Timeframe: {signal['timeframe']}")
                
                # Use real-time monitor's execution logic
                custom_signal = CustomSignal(
                    symbol=symbol,
                    action="BUY",
                    current_price=current_price,
                    yesterday_close=self.real_time_monitor.yesterday_closes.get(symbol, current_price),
                    reason=f"Enhanced signal: {', '.join(signal['supporting_indicators'])}",
                    order_type=self.real_time_monitor.strategy.determine_order_type(symbol),
                    urgency="HIGH" if signal['strength'] == "STRONG" else "MEDIUM"
                )
                
                return await asyncio.to_thread(
                    self.real_time_monitor.execute_buy_signal, 
                    custom_signal
                )
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error executing enhanced buy: {e}")
            return False
    
    async def execute_enhanced_sell(self, signal: Dict) -> bool:
        """Execute enhanced sell order"""
        try:
            symbol = signal['symbol']
            
            if symbol in self.real_time_monitor.active_positions:
                custom_signal = CustomSignal(
                    symbol=symbol,
                    action="SELL",
                    current_price=signal['price'],
                    yesterday_close=self.real_time_monitor.active_positions[symbol].entry_price,
                    reason=f"Enhanced exit: {', '.join(signal['supporting_indicators'])}",
                    order_type=self.real_time_monitor.active_positions[symbol].order_type,
                    urgency="HIGH"
                )
                
                return await asyncio.to_thread(
                    self.real_time_monitor.execute_sell_signal,
                    custom_signal
                )
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error executing enhanced sell: {e}")
            return False
    
    async def update_session_stats(self):
        """Update session statistics"""
        # Get stats from real-time monitor
        monitor_stats = self.real_time_monitor.get_monitoring_status()
        
        self.session_stats['real_time_signals'] = monitor_stats['performance']['signals_generated']
        
        # Calculate total unrealized P&L
        total_pnl = 0.0
        for position_data in monitor_stats['positions'].values():
            total_pnl += position_data['unrealized_pnl']
        
        self.session_stats['total_pnl'] = total_pnl
    
    async def log_system_status(self):
        """Log comprehensive system status"""
        uptime = datetime.now() - self.session_stats['start_time']
        
        logger.info("📊 ENHANCED SYSTEM STATUS")
        logger.info("=" * 50)
        logger.info(f"⏱️ Uptime: {uptime}")
        logger.info(f"🔔 Real-time signals: {self.session_stats['real_time_signals']}")
        logger.info(f"📊 Candle signals: {self.session_stats['candle_signals']}")
        logger.info(f"✅ Confirmed signals: {self.session_stats['confirmed_signals']}")
        logger.info(f"💼 Trades executed: {self.session_stats['trades_executed']}")
        
        # Position summary
        active_positions = len(self.real_time_monitor.active_positions)
        logger.info(f"📈 Active positions: {active_positions}")
        
        if self.session_stats['total_pnl'] != 0:
            logger.info(f"💰 Total P&L: ₹{self.session_stats['total_pnl']:+,.0f}")
        
        logger.info(f"🕐 Last candle analysis: {self.last_candle_analysis}")
    
    async def stop_monitoring(self):
        """Stop enhanced monitoring system"""
        if not self.monitoring_active:
            logger.warning("⚠️ Monitoring not active")
            return
        
        logger.info("⏹️ Stopping Enhanced Turtle Trading System...")
        self.monitoring_active = False
        
        # Stop real-time monitor
        await asyncio.to_thread(self.real_time_monitor.stop_monitoring)
        
        # Print final session summary
        await self.log_system_status()
        
        logger.info("✅ Enhanced Turtle Trading System stopped")
    
    def get_system_summary(self) -> Dict:
        """Get comprehensive system summary"""
        return {
            'session_stats': self.session_stats,
            'monitoring_active': self.monitoring_active,
            'real_time_monitor': self.real_time_monitor.get_monitoring_status(),
            'confirmed_signals': len(self.confirmed_signals),
            'signal_history': len(self.signal_history),
            'last_candle_analysis': self.last_candle_analysis.isoformat() if self.last_candle_analysis else None
        }


async def run_enhanced_turtle_trader():
    """Run the enhanced turtle trading system"""
    print("🚀 ENHANCED TURTLE TRADER - REAL-TIME INTRADAY SYSTEM")
    print("=" * 60)
    
    trader = EnhancedTurtleTrader()
    
    try:
        print("🔧 Initializing enhanced system...")
        print("⚡ This system monitors:")
        print("   • Every second: Live price movements")
        print("   • Every minute: Candlestick patterns") 
        print("   • Multi-timeframe: 1min, 5min, 15min analysis")
        print("   • Real-time confirmations: Cross-validated signals")
        print()
        
        # Start monitoring
        await trader.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring interrupted by user")
        await trader.stop_monitoring()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await trader.stop_monitoring()
    
    finally:
        # Final summary
        summary = trader.get_system_summary()
        print("\n📊 SESSION SUMMARY:")
        print(f"   Real-time signals: {summary['session_stats']['real_time_signals']}")
        print(f"   Candle signals: {summary['session_stats']['candle_signals']}")
        print(f"   Confirmed signals: {summary['confirmed_signals']}")
        print(f"   Trades executed: {summary['session_stats']['trades_executed']}")


if __name__ == "__main__":
    asyncio.run(run_enhanced_turtle_trader())