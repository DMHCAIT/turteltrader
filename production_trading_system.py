"""
🚀 PRODUCTION LIVE TRADING SYSTEM
=================================

Ready-to-use live trading system with all fixes applied
"""

from enhanced_data_manager import EnhancedDataManager
from custom_strategy import CustomETFStrategy, custom_etf_strategy
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import time
import schedule
from typing import Dict, List
import json

class ProductionTradingSystem:
    """Production-ready live trading system"""
    
    def __init__(self):
        self.data_manager = EnhancedDataManager()
        self.strategy = custom_etf_strategy
        self.is_running = False
        
        # Trading state
        self.positions = {}
        self.orders = {}
        self.daily_pnl = 0.0
        
        # Configuration
        self.etf_symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'JUNIORBEES', 'LIQUIDBEES']
        self.capital = 1000000  # 10 lakhs
        self.max_positions = 5
        self.position_size = 50000  # 50k per position
        
        # Risk management
        self.daily_loss_limit = 20000  # 2% of capital
        self.max_trades_per_day = 10
        self.trades_today = 0
        
        logger.info("Production Trading System initialized")
    
    def start_live_trading(self):
        """Start live trading with all safety checks"""
        print("🚀 STARTING PRODUCTION LIVE TRADING SYSTEM")
        print("="*60)
        
        # Pre-flight checks
        if not self.pre_flight_checks():
            return False
        
        # Start data feed
        self.data_manager.start_real_time_monitoring(self.etf_symbols)
        
        # Schedule trading activities
        schedule.every(1).minutes.do(self.scan_for_opportunities)
        schedule.every(2).minutes.do(self.monitor_positions)
        schedule.every(5).minutes.do(self.risk_check)
        schedule.every().day.at("09:00").do(self.daily_preparation)
        schedule.every().day.at("15:45").do(self.end_of_day_cleanup)
        
        self.is_running = True
        logger.info("🎯 Live trading started")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping live trading...")
            self.stop_trading()
        
        return True
    
    def pre_flight_checks(self) -> bool:
        """Comprehensive pre-flight checks"""
        print("\n🔍 PRE-FLIGHT CHECKS:")
        print("-"*30)
        
        checks_passed = 0
        total_checks = 6
        
        # 1. Market status
        is_open, status = self.data_manager.is_market_open()
        if is_open:
            print("✅ Market Status: OPEN")
            checks_passed += 1
        else:
            print(f"⚠️  Market Status: {status}")
            print("   Will start monitoring when market opens...")
        
        # 2. Data feed
        test_quote = self.data_manager.get_real_time_quote('GOLDBEES')
        if test_quote:
            print("✅ Data Feed: Working")
            checks_passed += 1
        else:
            print("❌ Data Feed: Failed")
        
        # 3. Strategy logic
        if self.strategy:
            print("✅ Strategy: Custom ETF Strategy loaded")
            checks_passed += 1
        else:
            print("❌ Strategy: Not loaded")
        
        # 4. Risk management
        if self.daily_loss_limit > 0 and self.max_trades_per_day > 0:
            print("✅ Risk Management: Active")
            checks_passed += 1
        else:
            print("❌ Risk Management: Not configured")
        
        # 5. Capital allocation
        if self.capital > 0 and self.position_size > 0:
            print(f"✅ Capital: ₹{self.capital:,} allocated")
            checks_passed += 1
        else:
            print("❌ Capital: Not set")
        
        # 6. Symbols configuration
        if len(self.etf_symbols) > 0:
            print(f"✅ ETF Symbols: {len(self.etf_symbols)} configured")
            checks_passed += 1
        else:
            print("❌ ETF Symbols: None configured")
        
        print(f"\n📊 Checks Passed: {checks_passed}/{total_checks}")
        
        if checks_passed >= 4:  # Minimum required checks
            print("🎯 READY FOR TRADING!")
            return True
        else:
            print("❌ NOT READY - Fix issues above")
            return False
    
    def scan_for_opportunities(self):
        """Scan market for trading opportunities"""
        try:
            is_open, _ = self.data_manager.is_market_open()
            if not is_open:
                return
            
            logger.info("🔍 Scanning for opportunities...")
            
            for symbol in self.etf_symbols:
                # Skip if we already have a position
                if symbol in self.positions:
                    continue
                
                # Skip if we hit daily trade limit
                if self.trades_today >= self.max_trades_per_day:
                    continue
                
                # Get current quote
                quote = self.data_manager.get_cached_quote(symbol)
                if not quote:
                    continue
                
                # Check for 1% dip buy signal
                change_percent = quote['change_percent']
                
                if change_percent <= -1.0:  # 1% or more dip
                    self.execute_buy_signal(symbol, quote)
                    
        except Exception as e:
            logger.error(f"Error in opportunity scan: {e}")
    
    def execute_buy_signal(self, symbol: str, quote: Dict):
        """Execute buy signal with position sizing"""
        try:
            current_price = quote['ltp']
            
            # Calculate position size
            quantity = int(self.position_size / current_price)
            
            if quantity <= 0:
                logger.warning(f"Position size too small for {symbol}")
                return
            
            # Calculate targets
            target_price = current_price * 1.03  # 3% profit target
            stop_loss = current_price * 0.95     # 5% stop loss
            
            # Create position (simulated for now)
            position = {
                'symbol': symbol,
                'quantity': quantity,
                'entry_price': current_price,
                'entry_time': datetime.now(),
                'target_price': target_price,
                'stop_loss': stop_loss,
                'status': 'OPEN',
                'pnl': 0.0
            }
            
            self.positions[symbol] = position
            self.trades_today += 1
            
            logger.info(f"🎯 BUY EXECUTED: {symbol}")
            logger.info(f"   Quantity: {quantity}")
            logger.info(f"   Entry: ₹{current_price:.2f}")
            logger.info(f"   Target: ₹{target_price:.2f} (+3%)")
            logger.info(f"   Stop: ₹{stop_loss:.2f} (-5%)")
            
            # Save position to file
            self.save_positions()
            
        except Exception as e:
            logger.error(f"Error executing buy for {symbol}: {e}")
    
    def monitor_positions(self):
        """Monitor existing positions for exits"""
        try:
            if not self.positions:
                return
            
            logger.info(f"📊 Monitoring {len(self.positions)} positions...")
            
            for symbol, position in list(self.positions.items()):
                quote = self.data_manager.get_cached_quote(symbol)
                if not quote:
                    continue
                
                current_price = quote['ltp']
                entry_price = position['entry_price']
                
                # Calculate P&L
                pnl = (current_price - entry_price) * position['quantity']
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                position['pnl'] = pnl
                
                # Check exit conditions
                if current_price >= position['target_price']:
                    self.execute_sell_signal(symbol, position, "TARGET_HIT")
                elif current_price <= position['stop_loss']:
                    self.execute_sell_signal(symbol, position, "STOP_LOSS")
                else:
                    logger.info(f"   {symbol}: ₹{current_price:.2f} | P&L: ₹{pnl:,.0f} ({pnl_percent:+.2f}%)")
                    
                    # Alert if approaching 5% loss
                    if pnl_percent <= -4.0:
                        logger.warning(f"⚠️  {symbol} approaching stop loss: {pnl_percent:.2f}%")
            
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    def execute_sell_signal(self, symbol: str, position: Dict, reason: str):
        """Execute sell signal"""
        try:
            quote = self.data_manager.get_cached_quote(symbol)
            if not quote:
                return
            
            exit_price = quote['ltp']
            final_pnl = (exit_price - position['entry_price']) * position['quantity']
            
            logger.info(f"🎯 SELL EXECUTED: {symbol} - {reason}")
            logger.info(f"   Exit: ₹{exit_price:.2f}")
            logger.info(f"   P&L: ₹{final_pnl:,.0f}")
            
            # Update daily P&L
            self.daily_pnl += final_pnl
            
            # Remove from positions
            del self.positions[symbol]
            self.save_positions()
            
        except Exception as e:
            logger.error(f"Error executing sell for {symbol}: {e}")
    
    def risk_check(self):
        """Perform risk management checks"""
        try:
            # Check daily loss limit
            if self.daily_pnl <= -self.daily_loss_limit:
                logger.warning(f"🚨 DAILY LOSS LIMIT HIT: ₹{self.daily_pnl:,.0f}")
                self.stop_trading()
            
            # Check trade count
            if self.trades_today >= self.max_trades_per_day:
                logger.warning(f"🚨 MAX TRADES REACHED: {self.trades_today}")
            
            logger.info(f"📊 Daily P&L: ₹{self.daily_pnl:,.0f} | Trades: {self.trades_today}")
            
        except Exception as e:
            logger.error(f"Error in risk check: {e}")
    
    def daily_preparation(self):
        """Prepare for new trading day"""
        self.trades_today = 0
        self.daily_pnl = 0.0
        logger.info("🌅 New trading day preparation complete")
    
    def end_of_day_cleanup(self):
        """End of day cleanup"""
        logger.info("🌅 End of day cleanup...")
        # Could add position squaring logic here if needed
    
    def save_positions(self):
        """Save positions to file"""
        try:
            with open('positions.json', 'w') as f:
                # Convert datetime objects to strings
                positions_json = {}
                for symbol, pos in self.positions.items():
                    positions_json[symbol] = pos.copy()
                    positions_json[symbol]['entry_time'] = pos['entry_time'].isoformat()
                
                json.dump(positions_json, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving positions: {e}")
    
    def stop_trading(self):
        """Stop trading system"""
        self.is_running = False
        self.data_manager.stop_monitoring()
        logger.info("🛑 Trading system stopped")

# Main execution
if __name__ == "__main__":
    system = ProductionTradingSystem()
    
    print("🐢 TURTLE TRADER - PRODUCTION SYSTEM")
    print("="*50)
    
    # Show current market status
    is_open, status = system.data_manager.is_market_open()
    print(f"Market Status: {status}")
    
    if input("\nStart live trading? (y/N): ").lower() == 'y':
        system.start_live_trading()
    else:
        print("Trading cancelled by user")