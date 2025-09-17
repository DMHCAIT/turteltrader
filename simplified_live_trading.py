"""
🎯 SIMPLIFIED INTEGRATED LIVE TRADING SYSTEM
==========================================

This is a simplified version that integrates your simulation logic
with the existing trading system components that are working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_capital_manager import CapitalManager, TradingSystemIntegrator
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from loguru import logger
import json

class SimpleLiveTradingSystem:
    """Simplified live trading system with capital management"""
    
    def __init__(self, initial_capital: float = 1000000):
        """Initialize the trading system"""
        
        # Initialize capital management with your exact parameters
        self.capital_manager = CapitalManager(
            initial_capital=initial_capital,
            deployment_pct=0.70,    # 70% deployment
            reserve_pct=0.30,       # 30% reserve  
            per_trade_pct=0.05,     # 5% per trade
            profit_target=0.03,     # 3% profit target
            brokerage_pct=0.003     # 0.3% brokerage
        )
        
        self.integrator = TradingSystemIntegrator(self.capital_manager)
        
        # ETF watchlist (Indian market symbols)
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
        self.trading_day = 1
        self.total_cycles_run = 0
        
        logger.info(f"🚀 Trading System initialized with ₹{initial_capital:,.2f}")
        self.print_system_parameters()
    
    def print_system_parameters(self):
        """Print the system parameters matching your simulation"""
        print("\\n📋 SYSTEM PARAMETERS (Matching Your Simulation)")
        print("=" * 55)
        print(f"💰 Total Capital:        ₹{self.capital_manager.total_capital:,.2f}")
        print(f"📊 Deployment (70%):     ₹{self.capital_manager.deployment_capital:,.2f}")
        print(f"💎 Reserve (30%):        ₹{self.capital_manager.reserve_capital:,.2f}")  
        print(f"🎯 Per Trade (5%):       ₹{self.capital_manager.per_trade_allocation:,.2f}")
        print(f"📈 Profit Target:        {self.capital_manager.profit_target*100}%")
        print(f"💸 Brokerage:            {self.capital_manager.brokerage_pct*100}%")
        print()
    
    def get_live_etf_data(self) -> dict:
        """Get live ETF price data"""
        market_data = {}
        
        print("📡 Fetching live market data...")
        
        for symbol in self.etf_watchlist:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get recent data (last few minutes)
                info = ticker.history(period='1d', interval='1m')
                
                if not info.empty:
                    current_price = float(info['Close'].iloc[-1])
                    volume = float(info['Volume'].iloc[-1]) if not pd.isna(info['Volume'].iloc[-1]) else 0
                    
                    # Remove .NS suffix for cleaner symbol names
                    clean_symbol = symbol.replace('.NS', '')
                    
                    market_data[clean_symbol] = {
                        'price': current_price,
                        'volume': volume,
                        'timestamp': datetime.now()
                    }
                    
                    print(f"  ✅ {clean_symbol}: ₹{current_price:.2f}")
                
            except Exception as e:
                logger.warning(f"Failed to get data for {symbol}: {e}")
                continue
        
        print(f"📊 Retrieved data for {len(market_data)} ETFs\\n")
        return market_data
    
    def find_dip_opportunities(self, market_data: dict) -> list:
        """Find ETFs with 1%+ dips for buying opportunities"""
        opportunities = []
        
        print("🔍 Scanning for 1% dip opportunities...")
        
        for symbol, data in market_data.items():
            try:
                current_price = data['price']
                
                # Get historical data to find recent high
                full_symbol = f"{symbol}.NS"
                ticker = yf.Ticker(full_symbol)
                hist = ticker.history(period='2d', interval='5m')
                
                if len(hist) < 20:
                    continue
                
                # Find recent high (last 4 hours of trading)
                recent_high = hist['High'].tail(48).max()  # 48 * 5min = 4 hours
                
                # Calculate dip percentage
                dip_pct = (recent_high - current_price) / recent_high * 100
                
                if dip_pct >= 1.0:  # 1% or more dip
                    # Check if we can afford this trade
                    position_info = self.capital_manager.get_position_size(symbol, current_price)
                    
                    if position_info['can_trade']:
                        opportunity = {
                            'symbol': symbol,
                            'current_price': current_price,
                            'recent_high': recent_high,
                            'dip_pct': dip_pct,
                            'investment': position_info['investment_amount'],
                            'target_price': position_info['target_price'],
                            'expected_profit': position_info['expected_profit'],
                            'confidence': 'HIGH' if dip_pct >= 1.5 else 'MEDIUM'
                        }
                        
                        opportunities.append(opportunity)
                        
                        print(f"  🎯 {symbol}: {dip_pct:.1f}% dip from ₹{recent_high:.2f} to ₹{current_price:.2f}")
                
            except Exception as e:
                logger.warning(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by dip percentage (highest first)
        opportunities.sort(key=lambda x: x['dip_pct'], reverse=True)
        
        print(f"✅ Found {len(opportunities)} opportunities\\n")
        return opportunities
    
    def execute_buy_orders(self, opportunities: list, max_trades: int = 3) -> list:
        """Execute buy orders for top opportunities"""
        executed_trades = []
        
        if not opportunities:
            print("ℹ️ No buy opportunities found\\n")
            return executed_trades
        
        print(f"🛒 Executing buy orders (max {max_trades})...")
        
        for i, opp in enumerate(opportunities[:max_trades]):
            # Check if we still have capital
            if not self.capital_manager.can_open_position():
                print(f"  ⚠️ Insufficient capital for more trades")
                break
            
            symbol = opp['symbol']
            price = opp['current_price']
            
            # Open position (simulated for now)
            position = self.capital_manager.open_position(symbol, price)
            
            if position:
                trade_record = {
                    'day': self.trading_day,
                    'cycle': self.total_cycles_run + 1,
                    'action': 'BUY',
                    'symbol': symbol,
                    'price': price,
                    'amount': position.amount,
                    'dip_pct': opp['dip_pct'],
                    'target_price': opp['target_price'],
                    'expected_profit': opp['expected_profit'],
                    'position_id': position.id,
                    'timestamp': datetime.now()
                }
                
                executed_trades.append(trade_record)
                
                print(f"  ✅ BUY {symbol}: ₹{position.amount:,.2f} at ₹{price:.2f} "
                      f"({opp['dip_pct']:.1f}% dip)")
        
        print(f"✅ Executed {len(executed_trades)} buy orders\\n")
        return executed_trades
    
    def check_profit_targets(self, market_data: dict) -> list:
        """Check existing positions for profit taking"""
        closed_positions = []
        
        if not self.capital_manager.open_positions:
            return closed_positions
        
        print("💰 Checking positions for profit taking...")
        
        # Get current prices for open positions
        position_prices = {}
        for symbol, data in market_data.items():
            position_prices[symbol] = data['price']
        
        # Evaluate positions
        recommendations = self.capital_manager.evaluate_positions(position_prices)
        
        for rec in recommendations:
            symbol = rec['symbol']
            current_price = rec['current_price']
            action = rec['action']
            
            if action in ['TAKE_PROFIT', 'STOP_LOSS']:
                # Close the position
                close_result = self.capital_manager.close_position(
                    symbol, current_price, rec['reason']
                )
                
                if close_result:
                    closed_positions.append({
                        'day': self.trading_day,
                        'cycle': self.total_cycles_run + 1,
                        'action': 'SELL',
                        'symbol': symbol,
                        'exit_price': current_price,
                        'net_profit': close_result['net_profit'],
                        'profit_pct': close_result['profit_pct'],
                        'reason': rec['reason'],
                        'timestamp': datetime.now()
                    })
                    
                    print(f"  ✅ SELL {symbol}: ₹{close_result['net_profit']:.2f} profit "
                          f"({close_result['profit_pct']:.1f}%) - {rec['reason']}")
            
            elif action == 'PROFIT_ALERT':
                print(f"  🔔 {symbol}: {rec['unrealized_pnl_pct']:.1f}% unrealized gain")
        
        if closed_positions:
            print(f"✅ Closed {len(closed_positions)} positions\\n")
        else:
            print("ℹ️ No positions ready for closing\\n")
        
        return closed_positions
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        self.total_cycles_run += 1
        
        print(f"\\n🔄 TRADING CYCLE #{self.total_cycles_run} (Day {self.trading_day})")
        print("=" * 60)
        
        try:
            # 1. Get live market data
            market_data = self.get_live_etf_data()
            
            if not market_data:
                print("⚠️ No market data available, skipping cycle\\n")
                return
            
            # 2. Check existing positions for profit taking
            closed_positions = self.check_profit_targets(market_data)
            
            # 3. Look for new buying opportunities
            opportunities = self.find_dip_opportunities(market_data)
            
            # 4. Execute new trades (limit 2-3 per cycle)
            new_trades = self.execute_buy_orders(opportunities, max_trades=2)
            
            # 5. Print cycle summary
            self.print_cycle_summary(new_trades, closed_positions)
            
            # 6. Log to database
            self.integrator.log_capital_snapshot()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def print_cycle_summary(self, new_trades: list, closed_positions: list):
        """Print summary of the trading cycle"""
        summary = self.capital_manager.get_trading_summary()
        
        print("📊 CYCLE SUMMARY")
        print("-" * 30)
        print(f"💰 Total Capital:        ₹{summary['current_capital']:,.2f}")
        print(f"📈 Total Profit:         ₹{summary['total_profit']:,.2f} ({summary['total_profit_pct']:.3f}%)")
        print(f"🎯 Open Positions:       {summary['open_positions']}")
        print(f"💼 Available Capital:    ₹{summary['available_capital']:,.2f}")
        print(f"📊 Utilization:          {summary['utilization_pct']:.1f}%")
        print(f"🛒 New Trades:           {len(new_trades)}")
        print(f"💰 Closed Positions:     {len(closed_positions)}")
        print(f"✅ Completed Trades:     {summary['total_trades_completed']}")
        print()
    
    def simulate_5_day_trading(self):
        """Simulate 5 days of trading like your example"""
        print("🚀 STARTING 5-DAY LIVE-LIKE SIMULATION")
        print("=" * 70)
        self.print_system_parameters()
        
        for day in range(1, 6):
            self.trading_day = day
            
            print(f"\\n📅 DAY {day} - TRADING SESSION")
            print("=" * 40)
            
            # Run 2-3 cycles per day
            cycles_per_day = 2 if day <= 3 else 3
            
            for cycle in range(cycles_per_day):
                self.run_trading_cycle()
                
                # Short delay between cycles
                if cycle < cycles_per_day - 1:
                    time.sleep(1)
            
            # End of day summary
            self.print_end_of_day_summary()
            
        # Final summary
        self.print_final_summary()
    
    def print_end_of_day_summary(self):
        """Print end of day summary"""
        summary = self.capital_manager.get_trading_summary()
        
        print(f"\\n📋 END OF DAY {self.trading_day} SUMMARY")
        print("-" * 35)
        print(f"Capital: ₹{summary['current_capital']:,.2f} | "
              f"Profit: ₹{summary['total_profit']:,.2f} | "
              f"Positions: {summary['open_positions']} | "
              f"Trades: {summary['total_trades_completed']}")
        
        # Show open positions
        if self.capital_manager.open_positions:
            print("\\n🎯 Open Positions:")
            for pos in self.capital_manager.open_positions:
                entry_day = getattr(pos, 'entry_day', 'N/A')
                print(f"  {pos.symbol}: ₹{pos.amount:,.2f} (Day {entry_day})")
        
        print()
    
    def print_final_summary(self):
        """Print final simulation summary"""
        summary = self.capital_manager.get_trading_summary()
        
        print("\\n🎉 5-DAY SIMULATION COMPLETE")
        print("=" * 50)
        
        print(f"Initial Capital:     ₹{summary['initial_capital']:,.2f}")
        print(f"Final Capital:       ₹{summary['current_capital']:,.2f}")
        print(f"Total Profit:        ₹{summary['total_profit']:,.2f}")
        print(f"Profit Percentage:   {summary['total_profit_pct']:.3f}%")
        print(f"Trades Completed:    {summary['total_trades_completed']}")
        print(f"Open Positions:      {summary['open_positions']}")
        print(f"Average Profit:      ₹{summary['avg_profit_per_trade']:,.2f} per trade")
        
        # Compare with your simulation
        print("\\n📊 COMPARISON WITH YOUR SIMULATION:")
        print("-" * 40)
        your_final_capital = 1003780.89
        your_profit = 3780.89
        
        actual_profit = summary['total_profit']
        difference = actual_profit - your_profit
        
        print(f"Your Simulation:     ₹{your_final_capital:,.2f} (+₹{your_profit:.2f})")
        print(f"Live Simulation:     ₹{summary['current_capital']:,.2f} (+₹{actual_profit:.2f})")
        print(f"Difference:          ₹{difference:+.2f}")
        
        # Save results
        filename = self.capital_manager.save_state("live_simulation_results")
        print(f"\\n💾 Results saved to {filename}")

def run_simple_demo():
    """Run a simple demonstration"""
    print("🎯 SIMPLE LIVE TRADING DEMO")
    print("=" * 40)
    
    # Create system with your parameters
    system = SimpleLiveTradingSystem(initial_capital=1000000)
    
    print("\\nRunning 3 trading cycles...")
    
    for i in range(3):
        print(f"\\n⏰ Cycle {i+1}/3")
        system.run_trading_cycle()
        time.sleep(2)  # Brief pause
    
    print("\\n✅ Demo complete!")
    system.print_final_summary()

if __name__ == "__main__":
    print("Choose simulation mode:")
    print("1. Quick demo (3 cycles)")
    print("2. Full 5-day simulation") 
    print("3. Custom parameters")
    
    choice = input("\\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_simple_demo()
        
    elif choice == "2":
        system = SimpleLiveTradingSystem(initial_capital=1000000)
        system.simulate_5_day_trading()
        
    elif choice == "3":
        capital = float(input("Enter initial capital: "))
        system = SimpleLiveTradingSystem(initial_capital=capital)
        
        days = int(input("Enter number of days to simulate: "))
        
        for day in range(1, days + 1):
            system.trading_day = day
            cycles = int(input(f"Enter cycles for day {day}: "))
            
            for cycle in range(cycles):
                system.run_trading_cycle()
        
        system.print_final_summary()
    
    else:
        print("Invalid choice")