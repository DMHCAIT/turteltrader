"""
🚀 LIVE-LIKE TRADING SIMULATION WITH CAPITAL MANAGEMENT
=====================================================

This implements the exact simulation logic you described with:
- 70% deployment, 30% reserve allocation
- 5% per trade allocation from deployment capital  
- 3% profit target with 0.3% brokerage charges
- Dynamic recalculation after each trade
"""

import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from typing import Dict, List, Optional
import json

class LiveTradingSimulator:
    """Live-like trading simulator with proper capital management"""
    
    def __init__(self, initial_capital: float = 1000000):
        """Initialize simulator with capital parameters"""
        
        # Capital Configuration
        self.initial_capital = initial_capital
        self.total_capital = initial_capital
        self.deployment_pct = 0.70  # 70% for trading
        self.reserve_pct = 0.30     # 30% buffer
        self.per_trade_pct = 0.05   # 5% of deployment capital per trade
        
        # Trading Parameters
        self.profit_pct = 0.03      # 3% profit target
        self.charge_pct = 0.003     # 0.3% brokerage/charges
        
        # Trading State
        self.open_trades = []
        self.closed_trades = []
        self.trade_counter = 0
        self.day = 1
        
        # Calculate initial allocations
        self.recalculate_allocations()
        
        logger.info(f"Trading Simulator initialized with ₹{initial_capital:,.2f}")
        self.print_capital_summary()
    
    def recalculate_allocations(self):
        """Recalculate capital allocations after profit booking"""
        self.deployment_capital = self.total_capital * self.deployment_pct
        self.reserve_capital = self.total_capital * self.reserve_pct
        self.per_trade_allocation = self.deployment_capital * self.per_trade_pct
        
        # Calculate allocated and available capital
        self.allocated_capital = sum(trade['amount'] for trade in self.open_trades)
        self.available_deployment = self.deployment_capital - self.allocated_capital
    
    def print_capital_summary(self):
        """Print current capital allocation summary"""
        print(f"📊 CAPITAL SUMMARY (Day {self.day})")
        print("-" * 40)
        print(f"Total Capital:       ₹{self.total_capital:,.2f}")
        print(f"Deployment (70%):    ₹{self.deployment_capital:,.2f}")
        print(f"Reserve (30%):       ₹{self.reserve_capital:,.2f}")
        print(f"Per Trade Amount:    ₹{self.per_trade_allocation:,.2f}")
        print(f"Allocated:           ₹{self.allocated_capital:,.2f}")
        print(f"Available:           ₹{self.available_deployment:,.2f}")
        print(f"Open Trades:         {len(self.open_trades)}")
        print()
    
    def can_place_trade(self) -> bool:
        """Check if we can place a new trade"""
        return self.available_deployment >= self.per_trade_allocation
    
    def place_trade(self, etf_name: str) -> bool:
        """Place a buy trade"""
        if not self.can_place_trade():
            logger.warning(f"Insufficient capital for new trade. Available: ₹{self.available_deployment:,.2f}")
            return False
        
        self.trade_counter += 1
        
        trade = {
            'id': self.trade_counter,
            'etf': etf_name,
            'amount': self.per_trade_allocation,
            'entry_day': self.day,
            'entry_time': datetime.now(),
            'status': 'OPEN'
        }
        
        self.open_trades.append(trade)
        self.recalculate_allocations()
        
        logger.info(f"🎯 BUY {etf_name}: ₹{self.per_trade_allocation:,.2f} allocated")
        logger.info(f"   Available Deployment: ₹{self.available_deployment:,.2f}")
        
        return True
    
    def close_trade(self, etf_name: str) -> bool:
        """Close a trade and book profit"""
        trade_to_close = None
        
        for trade in self.open_trades:
            if trade['etf'] == etf_name:
                trade_to_close = trade
                break
        
        if not trade_to_close:
            logger.error(f"No open trade found for {etf_name}")
            return False
        
        # Calculate profit and charges
        trade_amount = trade_to_close['amount']
        gross_profit = trade_amount * self.profit_pct
        charges = trade_amount * self.charge_pct
        net_profit = gross_profit - charges
        
        # Update capital
        self.total_capital += net_profit
        
        # Move to closed trades
        trade_to_close.update({
            'exit_day': self.day,
            'exit_time': datetime.now(),
            'gross_profit': gross_profit,
            'charges': charges,
            'net_profit': net_profit,
            'status': 'CLOSED'
        })
        
        self.closed_trades.append(trade_to_close)
        self.open_trades.remove(trade_to_close)
        
        # Recalculate allocations with new capital
        self.recalculate_allocations()
        
        logger.info(f"💰 SELL {etf_name}: Net Profit ₹{net_profit:.2f}")
        logger.info(f"   Gross Profit: ₹{gross_profit:.2f}")
        logger.info(f"   Charges: ₹{charges:.2f}")
        logger.info(f"   New Total Capital: ₹{self.total_capital:.2f}")
        
        return True
    
    def advance_day(self):
        """Advance to next trading day"""
        self.day += 1
        logger.info(f"📅 Advancing to Day {self.day}")
    
    def run_5_day_simulation(self):
        """Run the exact 5-day simulation as described"""
        print("🚀 STARTING 5-DAY LIVE-LIKE TRADING SIMULATION")
        print("=" * 60)
        
        # Day 1: Buy 3 ETFs
        print("\\n📅 DAY 1 - Initial Trades")
        self.place_trade("A")
        self.place_trade("B") 
        self.place_trade("C")
        self.print_capital_summary()
        
        # Day 2: Sell A, Buy D
        print("\\n📅 DAY 2 - First Profit Booking")
        self.advance_day()
        self.close_trade("A")
        self.place_trade("D")
        self.print_capital_summary()
        
        # Day 3: Sell B, Buy E
        print("\\n📅 DAY 3 - Second Profit Booking")
        self.advance_day()
        self.close_trade("B")
        self.place_trade("E")
        self.print_capital_summary()
        
        # Day 4: Sell C, Buy F
        print("\\n📅 DAY 4 - Third Profit Booking")
        self.advance_day()
        self.close_trade("C")
        self.place_trade("F")
        self.print_capital_summary()
        
        # Day 5: Sell D, Buy G
        print("\\n📅 DAY 5 - Fourth Profit Booking")
        self.advance_day()
        self.close_trade("D")
        self.place_trade("G")
        self.print_capital_summary()
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final simulation summary"""
        print("\\n🎉 5-DAY SIMULATION COMPLETE")
        print("=" * 50)
        
        total_profit = self.total_capital - self.initial_capital
        profit_pct = (total_profit / self.initial_capital) * 100
        
        print(f"Initial Capital:     ₹{self.initial_capital:,.2f}")
        print(f"Final Capital:       ₹{self.total_capital:.2f}")
        print(f"Total Profit:        ₹{total_profit:.2f} ({profit_pct:.3f}%)")
        print(f"Trades Completed:    {len(self.closed_trades)}")
        print(f"Open Positions:      {len(self.open_trades)}")
        
        print(f"\\n📊 OPEN TRADES:")
        for trade in self.open_trades:
            print(f"   {trade['etf']}: ₹{trade['amount']:,.2f} (Day {trade['entry_day']})")
        
        print(f"\\n📈 CLOSED TRADES:")
        for trade in self.closed_trades:
            print(f"   {trade['etf']}: ₹{trade['net_profit']:.2f} profit (Day {trade['entry_day']}-{trade['exit_day']})")
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.total_capital,
            'total_profit': total_profit,
            'profit_percentage': profit_pct,
            'trades_completed': len(self.closed_trades),
            'open_positions': len(self.open_trades)
        }
    
    def create_detailed_table(self) -> pd.DataFrame:
        """Create detailed trading table as shown in your example"""
        table_data = []
        
        # Reconstruct the trading sequence
        all_trades = self.closed_trades + self.open_trades
        all_trades.sort(key=lambda x: (x['entry_day'], x['id']))
        
        running_capital = self.initial_capital
        
        for trade in all_trades:
            # Entry record
            entry_record = {
                'Day': trade['entry_day'],
                'Action': 'Buy',
                'ETF': trade['etf'],
                'Allocated (₹)': f"{trade['amount']:,.2f}",
                'Total Capital (₹)': f"{running_capital:,.2f}",
                'Status': 'Open'
            }
            table_data.append(entry_record)
            
            # Exit record if trade is closed
            if trade['status'] == 'CLOSED':
                running_capital += trade['net_profit']
                exit_record = {
                    'Day': trade['exit_day'],
                    'Action': 'Sell (Profit)',
                    'ETF': trade['etf'],
                    'Allocated (₹)': f"{trade['net_profit']:.2f}",
                    'Total Capital (₹)': f"{running_capital:,.2f}",
                    'Status': 'Closed'
                }
                table_data.append(exit_record)
        
        return pd.DataFrame(table_data)
    
    def export_results(self, filename: str = None):
        """Export simulation results to JSON and CSV"""
        if filename is None:
            filename = f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Export summary
        summary = {
            'simulation_date': datetime.now().isoformat(),
            'parameters': {
                'initial_capital': self.initial_capital,
                'deployment_pct': self.deployment_pct,
                'reserve_pct': self.reserve_pct,
                'per_trade_pct': self.per_trade_pct,
                'profit_pct': self.profit_pct,
                'charge_pct': self.charge_pct
            },
            'results': {
                'final_capital': self.total_capital,
                'total_profit': self.total_capital - self.initial_capital,
                'profit_percentage': ((self.total_capital - self.initial_capital) / self.initial_capital) * 100,
                'trades_completed': len(self.closed_trades),
                'open_positions': len(self.open_trades)
            },
            'closed_trades': self.closed_trades,
            'open_trades': self.open_trades
        }
        
        with open(f"{filename}.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Export detailed table
        table = self.create_detailed_table()
        table.to_csv(f"{filename}.csv", index=False)
        
        print(f"✅ Results exported to {filename}.json and {filename}.csv")

# Enhanced simulator with real ETF integration
class RealETFSimulator(LiveTradingSimulator):
    """Simulator that can work with real ETF data"""
    
    def __init__(self, initial_capital: float = 1000000):
        super().__init__(initial_capital)
        
        # Real ETF symbols for Indian market
        self.etf_symbols = [
            'GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'JUNIORBEES', 
            'LIQUIDBEES', 'ITBEES', 'PHARMBEES', 'PSUBANK'
        ]
        self.symbol_index = 0
    
    def get_next_etf_symbol(self) -> str:
        """Get next ETF symbol for realistic trading"""
        symbol = self.etf_symbols[self.symbol_index % len(self.etf_symbols)]
        self.symbol_index += 1
        return symbol
    
    def run_realistic_simulation(self, days: int = 5):
        """Run simulation with realistic ETF symbols"""
        print(f"🚀 RUNNING {days}-DAY REALISTIC ETF SIMULATION")
        print("=" * 60)
        
        for day in range(1, days + 1):
            self.day = day
            print(f"\\n📅 DAY {day}")
            
            # Place 1-3 trades per day if capital allows
            trades_today = 0
            max_trades_per_day = 3
            
            while trades_today < max_trades_per_day and self.can_place_trade():
                etf = self.get_next_etf_symbol()
                if self.place_trade(etf):
                    trades_today += 1
                else:
                    break
            
            # Close some trades if we have open positions (simulate profit booking)
            if len(self.open_trades) >= 2 and day > 1:
                # Close oldest trade
                oldest_trade = min(self.open_trades, key=lambda x: x['entry_day'])
                self.close_trade(oldest_trade['etf'])
            
            self.print_capital_summary()
        
        self.print_final_summary()

if __name__ == "__main__":
    print("Choose simulation type:")
    print("1. Exact 5-day simulation as described")
    print("2. Realistic ETF simulation")
    print("3. Custom simulation")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Run exact simulation
        sim = LiveTradingSimulator(1000000)  # 10 lakhs
        sim.run_5_day_simulation()
        sim.export_results("exact_simulation")
        
    elif choice == "2":
        # Run realistic simulation
        capital = float(input("Enter initial capital (default 1000000): ") or 1000000)
        days = int(input("Enter number of days (default 5): ") or 5)
        
        sim = RealETFSimulator(capital)
        sim.run_realistic_simulation(days)
        sim.export_results("realistic_simulation")
        
    elif choice == "3":
        # Custom simulation
        capital = float(input("Enter initial capital: "))
        deployment = float(input("Enter deployment percentage (0.70 for 70%): "))
        per_trade = float(input("Enter per trade percentage (0.05 for 5%): "))
        profit = float(input("Enter profit target percentage (0.03 for 3%): "))
        charges = float(input("Enter charges percentage (0.003 for 0.3%): "))
        
        sim = LiveTradingSimulator(capital)
        sim.deployment_pct = deployment
        sim.per_trade_pct = per_trade
        sim.profit_pct = profit
        sim.charge_pct = charges
        sim.recalculate_allocations()
        
        sim.run_5_day_simulation()
        sim.export_results("custom_simulation")
    
    else:
        print("Invalid choice")