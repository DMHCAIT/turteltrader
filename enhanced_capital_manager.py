"""
📊 ENHANCED CAPITAL MANAGEMENT SYSTEM
===================================

This integrates the simulation logic into your existing trading system
for real-time capital management with the exact parameters you specified.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from loguru import logger

@dataclass
class TradePosition:
    """Represents a trading position"""
    id: int
    symbol: str
    amount: float
    entry_price: float
    entry_time: datetime
    status: str  # 'OPEN', 'CLOSED'
    target_profit: float = 0.03  # 3%
    stop_loss: float = 0.05      # 5%
    
    def calculate_current_pnl(self, current_price: float) -> Dict:
        """Calculate current P&L for the position"""
        price_change_pct = (current_price - self.entry_price) / self.entry_price
        
        return {
            'unrealized_pnl_pct': price_change_pct,
            'unrealized_pnl_amount': self.amount * price_change_pct,
            'should_take_profit': price_change_pct >= self.target_profit,
            'should_stop_loss': price_change_pct <= -self.stop_loss
        }

class CapitalManager:
    """Advanced capital management system based on your simulation parameters"""
    
    def __init__(self, 
                 initial_capital: float = 1000000,
                 deployment_pct: float = 0.70,
                 reserve_pct: float = 0.30,
                 per_trade_pct: float = 0.05,
                 profit_target: float = 0.03,
                 brokerage_pct: float = 0.003):
        
        # Core capital parameters
        self.initial_capital = initial_capital
        self.total_capital = initial_capital
        self.deployment_pct = deployment_pct
        self.reserve_pct = reserve_pct
        self.per_trade_pct = per_trade_pct
        self.profit_target = profit_target
        self.brokerage_pct = brokerage_pct
        
        # Trading state
        self.open_positions: List[TradePosition] = []
        self.closed_positions: List[TradePosition] = []
        self.position_counter = 0
        self.total_trades_completed = 0
        
        # Performance tracking
        self.total_gross_profit = 0.0
        self.total_charges = 0.0
        self.total_net_profit = 0.0
        
        # Calculate initial allocations
        self.recalculate_allocations()
        
        logger.info(f"Capital Manager initialized with ₹{initial_capital:,.2f}")
        self._log_capital_status()
    
    def recalculate_allocations(self):
        """Recalculate all capital allocations based on current total capital"""
        self.deployment_capital = self.total_capital * self.deployment_pct
        self.reserve_capital = self.total_capital * self.reserve_pct
        self.per_trade_allocation = self.deployment_capital * self.per_trade_pct
        
        # Calculate allocated and available capital
        self.allocated_capital = sum(pos.amount for pos in self.open_positions)
        self.available_deployment = self.deployment_capital - self.allocated_capital
        
        # Risk metrics
        self.utilization_pct = (self.allocated_capital / self.deployment_capital) * 100 if self.deployment_capital > 0 else 0
        self.positions_count = len(self.open_positions)
        
    def _log_capital_status(self):
        """Log current capital allocation status"""
        logger.info(f"💰 Capital Status: Total ₹{self.total_capital:,.2f} | "
                   f"Available ₹{self.available_deployment:,.2f} | "
                   f"Utilization {self.utilization_pct:.1f}% | "
                   f"Positions {self.positions_count}")
    
    def can_open_position(self) -> bool:
        """Check if we can open a new trading position"""
        return self.available_deployment >= self.per_trade_allocation
    
    def get_position_size(self, symbol: str, current_price: float) -> Dict:
        """Calculate optimal position size for a trade"""
        if not self.can_open_position():
            return {'can_trade': False, 'reason': 'Insufficient capital'}
        
        # Calculate shares we can buy
        max_investment = self.per_trade_allocation
        shares_to_buy = int(max_investment / current_price)
        actual_investment = shares_to_buy * current_price
        
        # Calculate targets
        target_price = current_price * (1 + self.profit_target)
        stop_loss_price = current_price * (1 - 0.05)  # 5% stop loss
        
        return {
            'can_trade': True,
            'symbol': symbol,
            'shares': shares_to_buy,
            'investment_amount': actual_investment,
            'entry_price': current_price,
            'target_price': target_price,
            'stop_loss_price': stop_loss_price,
            'expected_profit': actual_investment * self.profit_target,
            'max_loss': actual_investment * 0.05
        }
    
    def open_position(self, symbol: str, current_price: float) -> Optional[TradePosition]:
        """Open a new trading position"""
        position_info = self.get_position_size(symbol, current_price)
        
        if not position_info['can_trade']:
            logger.warning(f"Cannot open position for {symbol}: {position_info.get('reason', 'Unknown')}")
            return None
        
        self.position_counter += 1
        
        position = TradePosition(
            id=self.position_counter,
            symbol=symbol,
            amount=position_info['investment_amount'],
            entry_price=current_price,
            entry_time=datetime.now(),
            status='OPEN'
        )
        
        self.open_positions.append(position)
        self.recalculate_allocations()
        
        logger.info(f"🎯 OPENED: {symbol} | ₹{position.amount:,.2f} | "
                   f"Shares: {position_info['shares']} | "
                   f"Target: ₹{position_info['target_price']:.2f}")
        
        self._log_capital_status()
        return position
    
    def close_position(self, symbol: str, current_price: float, reason: str = "Manual") -> Optional[Dict]:
        """Close an open position and calculate P&L"""
        position_to_close = None
        
        for pos in self.open_positions:
            if pos.symbol == symbol:
                position_to_close = pos
                break
        
        if not position_to_close:
            logger.error(f"No open position found for {symbol}")
            return None
        
        # Calculate P&L
        shares = int(position_to_close.amount / position_to_close.entry_price)
        gross_proceeds = shares * current_price
        gross_profit = gross_proceeds - position_to_close.amount
        charges = gross_proceeds * self.brokerage_pct
        net_profit = gross_profit - charges
        
        profit_pct = (net_profit / position_to_close.amount) * 100
        
        # Update capital
        self.total_capital += net_profit
        
        # Update performance tracking
        self.total_gross_profit += gross_profit
        self.total_charges += charges
        self.total_net_profit += net_profit
        self.total_trades_completed += 1
        
        # Move position to closed
        position_to_close.status = 'CLOSED'
        self.closed_positions.append(position_to_close)
        self.open_positions.remove(position_to_close)
        
        # Recalculate allocations with new capital
        self.recalculate_allocations()
        
        result = {
            'symbol': symbol,
            'position_id': position_to_close.id,
            'entry_price': position_to_close.entry_price,
            'exit_price': current_price,
            'shares': shares,
            'investment': position_to_close.amount,
            'gross_proceeds': gross_proceeds,
            'gross_profit': gross_profit,
            'charges': charges,
            'net_profit': net_profit,
            'profit_pct': profit_pct,
            'reason': reason,
            'new_total_capital': self.total_capital
        }
        
        logger.info(f"💰 CLOSED: {symbol} | Net: ₹{net_profit:.2f} ({profit_pct:.2f}%) | "
                   f"Reason: {reason} | New Capital: ₹{self.total_capital:,.2f}")
        
        self._log_capital_status()
        return result
    
    def evaluate_positions(self, market_data: Dict[str, float]) -> List[Dict]:
        """Evaluate all open positions for profit taking or stop loss"""
        recommendations = []
        
        for position in self.open_positions:
            if position.symbol in market_data:
                current_price = market_data[position.symbol]
                pnl = position.calculate_current_pnl(current_price)
                
                recommendation = {
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'current_price': current_price,
                    'unrealized_pnl_pct': pnl['unrealized_pnl_pct'] * 100,
                    'unrealized_pnl_amount': pnl['unrealized_pnl_amount'],
                    'action': 'HOLD'
                }
                
                if pnl['should_take_profit']:
                    recommendation['action'] = 'TAKE_PROFIT'
                    recommendation['reason'] = f"Target profit {self.profit_target*100}% reached"
                elif pnl['should_stop_loss']:
                    recommendation['action'] = 'STOP_LOSS'
                    recommendation['reason'] = "Stop loss triggered at -5%"
                elif pnl['unrealized_pnl_pct'] >= 1.5:  # 1.5% profit alert
                    recommendation['action'] = 'PROFIT_ALERT'
                    recommendation['reason'] = "Good profit, consider booking"
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def auto_manage_positions(self, market_data: Dict[str, float]) -> List[Dict]:
        """Automatically manage positions based on profit/loss targets"""
        results = []
        recommendations = self.evaluate_positions(market_data)
        
        for rec in recommendations:
            if rec['action'] in ['TAKE_PROFIT', 'STOP_LOSS']:
                symbol = rec['symbol']
                current_price = rec['current_price']
                reason = rec['reason']
                
                result = self.close_position(symbol, current_price, reason)
                if result:
                    results.append(result)
        
        return results
    
    def get_trading_summary(self) -> Dict:
        """Get comprehensive trading performance summary"""
        total_profit_pct = ((self.total_capital - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.total_capital,
            'total_profit': self.total_capital - self.initial_capital,
            'total_profit_pct': total_profit_pct,
            'deployment_capital': self.deployment_capital,
            'reserve_capital': self.reserve_capital,
            'allocated_capital': self.allocated_capital,
            'available_capital': self.available_deployment,
            'utilization_pct': self.utilization_pct,
            'open_positions': len(self.open_positions),
            'total_trades_completed': self.total_trades_completed,
            'total_gross_profit': self.total_gross_profit,
            'total_charges': self.total_charges,
            'total_net_profit': self.total_net_profit,
            'avg_profit_per_trade': self.total_net_profit / max(self.total_trades_completed, 1),
            'win_rate': 'N/A'  # Would need to track wins/losses
        }
    
    def save_state(self, filename: str = None):
        """Save current capital management state"""
        if filename is None:
            filename = f"capital_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        state = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'initial_capital': self.initial_capital,
                'deployment_pct': self.deployment_pct,
                'reserve_pct': self.reserve_pct,
                'per_trade_pct': self.per_trade_pct,
                'profit_target': self.profit_target,
                'brokerage_pct': self.brokerage_pct
            },
            'current_state': self.get_trading_summary(),
            'open_positions': [
                {
                    'id': pos.id,
                    'symbol': pos.symbol,
                    'amount': pos.amount,
                    'entry_price': pos.entry_price,
                    'entry_time': pos.entry_time.isoformat(),
                    'status': pos.status
                }
                for pos in self.open_positions
            ],
            'closed_positions': len(self.closed_positions)
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Capital state saved to {filename}")
        return filename

# Integration helper for existing trading system
class TradingSystemIntegrator:
    """Integrates capital management with existing trading system"""
    
    def __init__(self, capital_manager: CapitalManager):
        self.capital_manager = capital_manager
        self.db_path = "data/trading_data.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for capital management"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS capital_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_capital REAL NOT NULL,
                    deployment_capital REAL NOT NULL,
                    allocated_capital REAL NOT NULL,
                    available_capital REAL NOT NULL,
                    open_positions INTEGER NOT NULL,
                    total_trades INTEGER NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS position_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    profit REAL,
                    charges REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def log_capital_snapshot(self):
        """Log current capital status to database"""
        try:
            summary = self.capital_manager.get_trading_summary()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO capital_snapshots 
                (timestamp, total_capital, deployment_capital, allocated_capital, 
                 available_capital, open_positions, total_trades)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                summary['current_capital'],
                summary['deployment_capital'],
                summary['allocated_capital'],
                summary['available_capital'],
                summary['open_positions'],
                summary['total_trades_completed']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging capital snapshot: {e}")

if __name__ == "__main__":
    # Demo of the capital management system
    print("🚀 Capital Management System Demo")
    
    # Initialize with 10 lakh capital
    manager = CapitalManager(initial_capital=1000000)
    
    # Simulate some trades
    print("\\n1. Opening positions...")
    manager.open_position("NIFTYBEES", 180.50)
    manager.open_position("GOLDBEES", 45.25)
    manager.open_position("BANKBEES", 420.75)
    
    print("\\n2. Current summary:")
    summary = manager.get_trading_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: ₹{value:,.2f}" if 'capital' in key or 'profit' in key else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\\n3. Simulating price changes and position management...")
    # Simulate market data with price changes
    market_data = {
        "NIFTYBEES": 186.12,  # +3.1% gain
        "GOLDBEES": 44.80,    # -1.0% loss
        "BANKBEES": 433.77    # +3.1% gain
    }
    
    # Evaluate and auto-manage positions
    results = manager.auto_manage_positions(market_data)
    
    print("\\n4. Final summary after auto-management:")
    final_summary = manager.get_trading_summary()
    profit = final_summary['total_profit']
    profit_pct = final_summary['total_profit_pct']
    print(f"Total Profit: ₹{profit:,.2f} ({profit_pct:.3f}%)")
    
    # Save state
    manager.save_state()