"""
🔧 INTEGRATED LIVE TRADING SYSTEM WITH CAPITAL MANAGEMENT
========================================================

This integrates the simulation logic with your existing ETF trading system
for real-time trading with proper capital allocation and profit booking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_capital_manager import CapitalManager, TradingSystemIntegrator
from dynamic_capital_allocator import DynamicCapitalAllocator, TradeSignal, ActiveTrade
from etf_manager import ETFOrderManager
from data_manager import DataManager
from custom_strategy import CustomETFStrategy
from notification_system import NotificationManager
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from loguru import logger
import json

class LiveTradingSystem:
    """Integrated live trading system with capital management"""
    
    def __init__(self, initial_capital: float = 1000000):
        """Initialize the complete live trading system"""
        
        # Initialize Dynamic Capital Allocator with your exact strategy
        self.capital_allocator = DynamicCapitalAllocator(
            total_capital=initial_capital,
            deployment_percentage=0.70,  # 70% deployment as per your strategy
            reserve_percentage=0.30,     # 30% reserve (never touched)
            per_trade_percentage=0.05    # 5% of deployment capital per trade
        )
        
        # Also keep the existing capital manager for compatibility
        self.capital_manager = CapitalManager(
            initial_capital=initial_capital,
            deployment_pct=0.70,
            reserve_pct=0.30,
            per_trade_pct=0.05,
            profit_target=0.03,
            brokerage_pct=0.003
        )
        
        self.integrator = TradingSystemIntegrator(self.capital_manager)
        
        # Initialize existing components
        try:
            self.etf_manager = ETFOrderManager()
            self.data_manager = DataManager()
            self.strategy = CustomETFStrategy()
            self.notification = NotificationManager()
            
            logger.info("✅ All trading components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some components failed to initialize: {e}")
            logger.info("Continuing with Yahoo Finance data only...")
            
            # Fallback to Yahoo Finance only
            self.etf_manager = None
            self.data_manager = None
            self.strategy = CustomETFStrategy()
            self.notification = None
        
        # ETF watchlist for Indian market
        self.etf_watchlist = [
            'GOLDBEES.NS',    # Gold ETF
            'NIFTYBEES.NS',   # Nifty 50 ETF
            'BANKBEES.NS',    # Banking ETF
            'JUNIORBEES.NS',  # Junior Nifty ETF
            'LIQUIDBEES.NS',  # Liquid ETF
            'ITBEES.NS',      # IT Sector ETF
            'PHARMBEES.NS',   # Pharma ETF
            'PSUBANK.NS'      # PSU Bank ETF
        ]
        
        # Trading state
        self.is_running = False
        self.last_scan_time = None
        self.scan_interval = 60  # seconds
        
        logger.info(f"🚀 Live Trading System initialized with ₹{initial_capital:,.2f}")
    
    def get_market_data(self) -> dict:
        """Get real-time market data for all ETFs"""
        market_data = {}
        
        try:
            # Fetch data for all ETFs in watchlist
            for symbol in self.etf_watchlist:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.history(period='1d', interval='1m')
                    
                    if not info.empty:
                        current_price = float(info['Close'].iloc[-1])
                        market_data[symbol.replace('.NS', '')] = current_price
                        
                except Exception as e:
                    logger.warning(f"Failed to get data for {symbol}: {e}")
                    continue
            
            logger.info(f"📊 Retrieved market data for {len(market_data)} ETFs")
            return market_data
            
        except Exception as e:
            logger.error(f"Market data retrieval error: {e}")
            return {}
    
    def scan_for_opportunities(self, market_data: dict) -> list:
        """Scan for trading opportunities using 1% dip strategy"""
        opportunities = []
        
        for symbol, current_price in market_data.items():
            try:
                # Get historical data for trend analysis
                full_symbol = f"{symbol}.NS"
                ticker = yf.Ticker(full_symbol)
                hist = ticker.history(period='5d', interval='1h')
                
                if len(hist) < 10:
                    continue
                
                # Calculate recent high (last 24 hours)
                recent_high = hist['High'].tail(24).max()
                
                # Check for 1% dip from recent high
                dip_from_high = (recent_high - current_price) / recent_high
                
                if dip_from_high >= 0.01:  # 1% or more dip
                    # Check if we can afford this trade
                    position_info = self.capital_manager.get_position_size(symbol, current_price)
                    
                    if position_info['can_trade']:
                        opportunities.append({
                            'symbol': symbol,
                            'current_price': current_price,
                            'recent_high': recent_high,
                            'dip_percentage': dip_from_high * 100,
                            'investment_amount': position_info['investment_amount'],
                            'target_price': position_info['target_price'],
                            'expected_profit': position_info['expected_profit'],
                            'confidence': 'HIGH' if dip_from_high >= 0.015 else 'MEDIUM'
                        })
            
            except Exception as e:
                logger.warning(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by dip percentage (highest first)
        opportunities.sort(key=lambda x: x['dip_percentage'], reverse=True)
        
        logger.info(f"🔍 Found {len(opportunities)} trading opportunities")
        return opportunities
    
    def execute_trades(self, opportunities: list) -> list:
        """Execute trades for identified opportunities"""
        executed_trades = []
        
        for opp in opportunities:
            # Check if we still have capital
            if not self.capital_manager.can_open_position():
                logger.info("💰 No more capital available for new trades")
                break
            
            symbol = opp['symbol']
            current_price = opp['current_price']
            
            # Try to execute the trade
            if self.etf_manager:
                try:
                    # Use actual broker API
                    order_result = self.etf_manager.place_buy_order(
                        symbol=symbol,
                        quantity=int(opp['investment_amount'] / current_price),
                        price=current_price
                    )
                    
                    if order_result.get('status') == 'success':
                        position = self.capital_manager.open_position(symbol, current_price)
                        if position:
                            executed_trades.append({
                                'symbol': symbol,
                                'action': 'BUY',
                                'position_id': position.id,
                                'price': current_price,
                                'amount': position.amount,
                                'broker_order_id': order_result.get('order_id'),
                                'timestamp': datetime.now()
                            })
                            
                            # Send notification
                            if self.notification:
                                self.notification.send_notification(
                                    f"🎯 BUY ORDER: {symbol} at ₹{current_price:.2f} | "
                                    f"Amount: ₹{position.amount:,.2f} | "
                                    f"Target: ₹{opp['target_price']:.2f}"
                                )
                    
                except Exception as e:
                    logger.error(f"Failed to execute trade for {symbol}: {e}")
                    continue
            
            else:
                # Simulation mode
                position = self.capital_manager.open_position(symbol, current_price)
                if position:
                    executed_trades.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'position_id': position.id,
                        'price': current_price,
                        'amount': position.amount,
                        'broker_order_id': 'SIM_' + str(position.id),
                        'timestamp': datetime.now()
                    })
                    
                    logger.info(f"🎯 SIMULATED BUY: {symbol} at ₹{current_price:.2f}")
        
        logger.info(f"✅ Executed {len(executed_trades)} trades")
        return executed_trades
    
    def manage_existing_positions(self, market_data: dict) -> list:
        """Manage existing positions for profit taking or stop loss"""
        results = []
        
        # Get position recommendations
        recommendations = self.capital_manager.evaluate_positions(market_data)
        
        for rec in recommendations:
            symbol = rec['symbol']
            current_price = rec['current_price']
            action = rec['action']
            
            if action in ['TAKE_PROFIT', 'STOP_LOSS']:
                # Execute sell order
                if self.etf_manager:
                    try:
                        # Calculate shares to sell
                        position = None
                        for pos in self.capital_manager.open_positions:
                            if pos.symbol == symbol:
                                position = pos
                                break
                        
                        if position:
                            shares = int(position.amount / position.entry_price)
                            
                            order_result = self.etf_manager.place_sell_order(
                                symbol=symbol,
                                quantity=shares,
                                price=current_price
                            )
                            
                            if order_result.get('status') == 'success':
                                close_result = self.capital_manager.close_position(
                                    symbol, current_price, rec['reason']
                                )
                                
                                if close_result:
                                    results.append(close_result)
                                    
                                    # Send notification
                                    if self.notification:
                                        profit_pct = close_result['profit_pct']
                                        self.notification.send_notification(
                                            f"💰 SELL ORDER: {symbol} at ₹{current_price:.2f} | "
                                            f"Profit: ₹{close_result['net_profit']:.2f} ({profit_pct:.2f}%) | "
                                            f"Reason: {rec['reason']}"
                                        )
                    
                    except Exception as e:
                        logger.error(f"Failed to close position for {symbol}: {e}")
                        continue
                
                else:
                    # Simulation mode
                    close_result = self.capital_manager.close_position(
                        symbol, current_price, rec['reason']
                    )
                    
                    if close_result:
                        results.append(close_result)
                        logger.info(f"💰 SIMULATED SELL: {symbol} - {rec['reason']}")
            
            elif action == 'PROFIT_ALERT':
                logger.info(f"🔔 PROFIT ALERT: {symbol} showing {rec['unrealized_pnl_pct']:.1f}% gain")
        
        return results
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        logger.info("🔄 Starting trading cycle...")
        
        try:
            # 1. Get market data
            market_data = self.get_market_data()
            if not market_data:
                logger.warning("No market data available, skipping cycle")
                return
            
            # 2. Manage existing positions first
            closed_positions = self.manage_existing_positions(market_data)
            
            # 3. Scan for new opportunities
            opportunities = self.scan_for_opportunities(market_data)
            
            # 4. Execute new trades (limit to 3 per cycle)
            new_trades = self.execute_trades(opportunities[:3])
            
            # 5. Log capital snapshot
            self.integrator.log_capital_snapshot()
            
            # 6. Print summary
            summary = self.capital_manager.get_trading_summary()
            
            logger.info(f"📊 Cycle Summary: Capital ₹{summary['current_capital']:,.2f} | "
                       f"Profit ₹{summary['total_profit']:,.2f} | "
                       f"Positions {summary['open_positions']} | "
                       f"New Trades {len(new_trades)} | "
                       f"Closed {len(closed_positions)}")
            
            self.last_scan_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def start_live_trading(self):
        """Start the live trading system"""
        logger.info("🚀 Starting live trading system...")
        self.is_running = True
        
        try:
            while self.is_running:
                # Check if it's market hours (9:15 AM to 3:30 PM IST)
                now = datetime.now()
                
                # For demo, we'll trade any time. In production, add market hours check
                if True:  # Replace with proper market hours check
                    self.run_trading_cycle()
                    
                    # Wait for next cycle
                    time.sleep(self.scan_interval)
                
                else:
                    logger.info("🕒 Outside market hours, waiting...")
                    time.sleep(300)  # Check every 5 minutes
                
        except KeyboardInterrupt:
            logger.info("👋 Stopping live trading system...")
            self.stop_trading()
        
        except Exception as e:
            logger.error(f"Fatal error in live trading: {e}")
            self.stop_trading()
    
    def stop_trading(self):
        """Stop the trading system and save state"""
        logger.info("🛑 Stopping trading system...")
        self.is_running = False
        
        # Save final state
        filename = self.capital_manager.save_state()
        
        # Print final summary
        summary = self.capital_manager.get_trading_summary()
        
        print("\\n🎯 FINAL TRADING SUMMARY")
        print("=" * 40)
        print(f"Initial Capital:     ₹{summary['initial_capital']:,.2f}")
        print(f"Final Capital:       ₹{summary['current_capital']:,.2f}")
        print(f"Total Profit:        ₹{summary['total_profit']:,.2f}")
        print(f"Profit Percentage:   {summary['total_profit_pct']:.3f}%")
        print(f"Trades Completed:    {summary['total_trades_completed']}")
        print(f"Open Positions:      {summary['open_positions']}")
        print(f"Average Profit:      ₹{summary['avg_profit_per_trade']:,.2f} per trade")
        
        logger.info(f"Final state saved to {filename}")

def demo_integrated_system():
    """Run a demo of the integrated trading system"""
    print("🚀 INTEGRATED LIVE TRADING SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize system with your simulation parameters
    system = LiveTradingSystem(initial_capital=1000000)  # 10 lakhs
    
    print("\\n1. System initialized with simulation parameters:")
    print("   - Initial Capital: ₹10,00,000")
    print("   - Deployment: 70% (₹7,00,000)")
    print("   - Reserve: 30% (₹3,00,000)")
    print("   - Per Trade: 5% of deployment (₹35,000)")
    print("   - Profit Target: 3%")
    print("   - Brokerage: 0.3%")
    
    print("\\n2. Running 3 trading cycles (demo mode)...")
    
    for cycle in range(1, 4):
        print(f"\\n📅 CYCLE {cycle}")
        print("-" * 20)
        system.run_trading_cycle()
        time.sleep(2)  # Short delay for demo
    
    print("\\n3. Final Results:")
    system.stop_trading()

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Demo integrated system (3 cycles)")
    print("2. Start live trading (continuous)")
    print("3. Capital management only")
    
    choice = input("\\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_integrated_system()
        
    elif choice == "2":
        capital = float(input("Enter initial capital (default 1000000): ") or 1000000)
        system = LiveTradingSystem(initial_capital=capital)
        
        print(f"\\n🚀 Starting live trading with ₹{capital:,.2f}")
        print("Press Ctrl+C to stop...")
        
        system.start_live_trading()
        
    elif choice == "3":
        # Run capital management demo from enhanced_capital_manager.py
        from enhanced_capital_manager import CapitalManager
        
        manager = CapitalManager(1000000)
        summary = manager.get_trading_summary()
        
        print("\\n📊 Capital Management Summary:")
        for key, value in summary.items():
            if isinstance(value, float) and 'capital' in key:
                print(f"  {key}: ₹{value:,.2f}")
            else:
                print(f"  {key}: {value}")
    
    else:
        print("Invalid choice")