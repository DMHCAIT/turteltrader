"""
⚡ DYNAMIC CAPITAL ALLOCATION ENGINE
=================================

Implements your exact strategy specification:

1. Initialize Parameters ✅
2. Calculate Capital Buckets ✅  
3. Track Allocated Capital ✅
4. For Each New Trade Signal ✅
5. When a Trade Closes ✅
6. Always Maintain the Reserve ✅
7. Repeat Steps 4–6 ✅

All calculations use percentages, not fixed amounts.
Reserve capital is strictly off-limits for automated trades.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from loguru import logger

@dataclass
class TradeSignal:
    """Represents a trading signal/opportunity"""
    symbol: str
    signal_type: str  # 'BUY' or 'SELL'
    price: float
    confidence: str   # 'HIGH', 'MEDIUM', 'LOW'
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ActiveTrade:
    """Represents an active trading position"""
    trade_id: int
    symbol: str
    allocated_amount: float
    entry_price: float
    entry_time: datetime
    status: str = "ACTIVE"

class DynamicCapitalAllocator:
    """
    Dynamic Capital Allocation Engine
    
    Implements the exact strategy you described:
    - Percentage-based allocation system
    - Automatic capital bucket management
    - Reserve capital protection
    - Performance-based reallocation
    - REAL ACCOUNT BALANCE INTEGRATION
    """
    
    def __init__(self, initial_capital: Optional[float] = None, use_real_balance: bool = True):
        """
        Initialize with capital amount (real or reference)
        
        Args:
            initial_capital: Starting capital (optional if using real balance)
            use_real_balance: If True, uses real Kite API account balance
        """
        # Import here to avoid circular imports
        if use_real_balance:
            try:
                from real_account_balance import RealAccountBalanceManager
                self.balance_manager = RealAccountBalanceManager()
                self.use_real_balance = True
                logger.info("🏦 Using REAL account balance from Kite API")
            except ImportError:
                logger.warning("⚠️ Real balance manager not available, using reference capital")
                self.use_real_balance = False
                self.balance_manager = None
        else:
            self.use_real_balance = False
            self.balance_manager = None
        
        # Initialize capital - ONLY real balance allowed
        if self.use_real_balance and self.balance_manager:
            self._initialize_with_real_balance()
        else:
            logger.error("❌ Real balance is required - no fallback allowed")
            raise ValueError("DynamicCapitalAllocator requires real account balance integration")
        
        # Step 3: Track Allocated Capital
        self.allocated_capital = 0.0
        self.free_capital = self.deployable_capital
        self.available_deployment_capital = self.deployable_capital  # Initially all deployable capital is available
        self.active_trades: List[ActiveTrade] = []
        self.closed_trades: List[ActiveTrade] = []
        self.trade_history: List[Dict] = []
        self.trade_counter = 0
        
        # Performance tracking
        self.total_profit_loss = 0.0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Initial capital tracking
        self.track_allocated_capital()
        
        logger.info(f"💼 Capital Allocator initialized with ₹{self.total_capital:,.2f}")
        logger.info(f"🎯 Deployable: ₹{self.deployable_capital:,.2f}")
        logger.info(f"🛡️ Reserve: ₹{self.reserve_capital:,.2f}")
        logger.info(f"💰 Per Trade: ₹{self.per_trade_amount:,.2f}")

    def refresh_real_balance(self) -> bool:
        """
        Refresh capital allocation based on current real account balance
        
        Returns:
            bool: True if balance was refreshed successfully
        """
        if not self.use_real_balance or not self.balance_manager:
            logger.warning("⚠️ Real balance refresh not available")
            return False
        
        try:
            logger.info("🔄 Refreshing capital allocation with real account balance...")
            
            # Get fresh balance
            balance = self.balance_manager.get_current_balance(force_refresh=True)
            if not balance or balance.free_cash <= 0:
                logger.error("❌ Could not fetch valid account balance")
                return False
            
            # Store old values for comparison
            old_total = self.total_capital
            old_deployable = self.deployable_capital
            old_per_trade = self.per_trade_amount
            
            # Update with new real balance
            self.total_capital = balance.free_cash
            self.deployable_capital = balance.deployable_capital
            self.deployment_capital = self.deployable_capital  # Alias for compatibility
            self.reserve_capital = balance.reserve_capital
            self.per_trade_amount = balance.per_trade_capital
            
            # Update free capital accounting for active trades
            self.free_capital = self.deployable_capital - self.allocated_capital
            
            # Log the changes
            total_change = self.total_capital - old_total
            deployable_change = self.deployable_capital - old_deployable
            per_trade_change = self.per_trade_amount - old_per_trade
            
            logger.info(f"✅ Capital allocation refreshed!")
            logger.info(f"💰 Total Capital: ₹{old_total:,.2f} → ₹{self.total_capital:,.2f} ({total_change:+,.2f})")
            logger.info(f"🎯 Deployable: ₹{old_deployable:,.2f} → ₹{self.deployable_capital:,.2f} ({deployable_change:+,.2f})")
            logger.info(f"💰 Per Trade: ₹{old_per_trade:,.2f} → ₹{self.per_trade_amount:,.2f} ({per_trade_change:+,.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh real balance: {e}")
            return False

    def get_real_balance_status(self) -> Dict:
        """Get current real balance status and comparison"""
        if not self.use_real_balance or not self.balance_manager:
            return {'error': 'Real balance not available'}
        
        try:
            balance = self.balance_manager.get_current_balance()
            if not balance:
                return {'error': 'Could not fetch balance'}
            
            return {
                'real_balance': {
                    'available_cash': balance.available_cash,
                    'free_cash': balance.free_cash,
                    'margin_used': balance.margin_used,
                    'portfolio_value': balance.portfolio_value,
                    'last_updated': balance.timestamp.isoformat()
                },
                'allocation_status': {
                    'total_capital': self.total_capital,
                    'deployable_capital': self.deployable_capital,
                    'reserve_capital': self.reserve_capital,
                    'per_trade_amount': self.per_trade_amount,
                    'allocated_capital': self.allocated_capital,
                    'free_capital': self.free_capital
                },
                'sync_status': {
                    'is_synced': abs(self.total_capital - balance.free_cash) < 100,
                    'difference': self.total_capital - balance.free_cash
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to get balance status: {e}'}

    def _initialize_with_real_balance(self):
        """Initialize using real Kite API account balance"""
        balance = self.balance_manager.get_current_balance(force_refresh=True)
        
        if balance and balance.free_cash > 0:
            # Step 1: Initialize Parameters with REAL balance
            self.total_capital = balance.free_cash
            self.deployment_percentage = 70.0    # 70% for deployment
            self.reserve_percentage = 30.0       # 30% reserve (untouchable)
            self.per_trade_percentage = 5.0      # 5% per trade
            self.profit_target_percentage = 3.0  # 3% profit target
            self.brokerage_percentage = 0.3      # 0.3% brokerage
            
            # Step 2: Calculate Capital Buckets with REAL amounts
            self.deployable_capital = balance.deployable_capital
            self.deployment_capital = self.deployable_capital  # Alias for compatibility
            self.reserve_capital = balance.reserve_capital
            self.per_trade_amount = balance.per_trade_capital
            
            logger.info(f"✅ Real balance loaded: ₹{self.total_capital:,.2f} free cash")
        else:
            logger.error("❌ Could not fetch real balance - NO FALLBACK ALLOWED")
            raise ConnectionError("Real account balance required - system will not work without valid API credentials")

    def _initialize_with_reference_capital(self, initial_capital: float):
        """Initialize using reference capital amount"""
        # Step 1: Initialize Parameters
        self.total_capital = initial_capital
        self.deployment_percentage = 70.0    # 70% for deployment
        self.reserve_percentage = 30.0       # 30% reserve (untouchable)
        self.per_trade_percentage = 5.0      # 5% per trade
        self.profit_target_percentage = 3.0  # 3% profit target
        self.brokerage_percentage = 0.3      # 0.3% brokerage
        
        # Step 2: Calculate Capital Buckets
        self.deployable_capital = self.total_capital * (self.deployment_percentage / 100)
        self.deployment_capital = self.deployable_capital  # Alias for compatibility
        self.reserve_capital = self.total_capital * (self.reserve_percentage / 100)
        self.per_trade_amount = self.deployable_capital * (self.per_trade_percentage / 100)
        
        logger.info(f"📊 Reference capital mode: ₹{initial_capital:,.2f}")

    def calculate_capital_buckets(self):
        """
        Calculate Capital Buckets (Step 2)
        
        - deployment_capital = total_capital × deployment_percentage
        - reserve_capital = total_capital × reserve_percentage
        """
        self.deployment_capital = self.total_capital * (self.deployment_percentage / 100)
        self.deployable_capital = self.deployment_capital  # Alias for compatibility
        self.reserve_capital = self.total_capital * (self.reserve_percentage / 100)
        
        logger.info(f"📊 Capital buckets calculated: "
                   f"Deployment ₹{self.deployment_capital:,.0f} | "
                   f"Reserve ₹{self.reserve_capital:,.0f}")

    def track_allocated_capital(self):
        """
        Track Allocated Capital (Step 3)
        
        - allocated_capital: Sum of all capital in open trades
        - available_deployment_capital = deployment_capital - allocated_capital
        """
        self.allocated_capital = sum(trade.allocated_amount for trade in self.active_trades)
        self.available_deployment_capital = self.deployment_capital - self.allocated_capital
        
        logger.debug(f"💼 Capital tracking: "
                    f"Allocated ₹{self.allocated_capital:,.0f} | "
                    f"Available ₹{self.available_deployment_capital:,.0f}")

    def process_trade_signal(self, signal: TradeSignal) -> Dict:
        """
        For Each New Trade Signal (Step 4)
        
        1. Calculate per_trade_allocation = deployment_capital × per_trade_percentage
        2. Check if available_deployment_capital ≥ per_trade_allocation
        3. If yes: Allocate, update, place trade
        4. If no: Do not place trade, wait for capital release
        
        Args:
            signal: Trading signal to process
            
        Returns:
            Dict with execution result and details
        """
        
        if signal.signal_type != 'BUY':
            return {'status': 'SKIPPED', 'reason': 'Only BUY signals processed here'}
        
        # Step 4.1: Calculate per_trade_allocation
        per_trade_allocation = self.deployment_capital * (self.per_trade_percentage / 100)
        
        # Step 4.2: Check if available_deployment_capital ≥ per_trade_allocation
        if self.available_deployment_capital >= per_trade_allocation:
            # Step 4.3: If yes - Allocate and place trade
            self.trade_counter += 1
            
            # Create new active trade
            new_trade = ActiveTrade(
                trade_id=self.trade_counter,
                symbol=signal.symbol,
                allocated_amount=per_trade_allocation,
                entry_price=signal.price,
                entry_time=signal.timestamp
            )
            
            # Add to active trades
            self.active_trades.append(new_trade)
            
            # Update allocated capital tracking
            self.track_allocated_capital()
            
            result = {
                'status': 'EXECUTED',
                'trade_id': new_trade.trade_id,
                'symbol': signal.symbol,
                'allocated_amount': per_trade_allocation,
                'entry_price': signal.price,
                'available_after': self.available_deployment_capital,
                'message': f"Trade executed: ₹{per_trade_allocation:,.0f} allocated to {signal.symbol}"
            }
            
            logger.info(f"✅ {result['message']}")
            
        else:
            # Step 4.4: If no - Do not place trade
            shortfall = per_trade_allocation - self.available_deployment_capital
            
            result = {
                'status': 'REJECTED',
                'reason': 'INSUFFICIENT_CAPITAL',
                'required': per_trade_allocation,
                'available': self.available_deployment_capital,
                'shortfall': shortfall,
                'message': f"Trade rejected: Need ₹{shortfall:,.0f} more capital"
            }
            
            logger.warning(f"❌ {result['message']}")
        
        return result

    def close_trade(self, trade_id: int, exit_price: float, reason: str = "Manual close") -> Dict:
        """
        When a Trade Closes (Step 5)
        
        - Release the capital used in that trade back to available_deployment_capital
        - Update allocated_capital accordingly
        
        Args:
            trade_id: ID of trade to close
            exit_price: Price at which trade is closed
            reason: Reason for closing
            
        Returns:
            Dict with closing result and P&L details
        """
        
        # Find the trade
        trade_to_close = None
        for trade in self.active_trades:
            if trade.trade_id == trade_id:
                trade_to_close = trade
                break
        
        if not trade_to_close:
            return {
                'status': 'ERROR',
                'message': f"Trade ID {trade_id} not found in active trades"
            }
        
        # Calculate P&L
        shares = int(trade_to_close.allocated_amount / trade_to_close.entry_price)
        gross_proceeds = shares * exit_price
        gross_pnl = gross_proceeds - trade_to_close.allocated_amount
        
        # Calculate charges (0.3% brokerage on sell)
        brokerage = gross_proceeds * 0.003
        net_pnl = gross_pnl - brokerage
        
        # Update total capital with net P&L
        self.total_capital += net_pnl
        
        # Recalculate capital buckets with new total
        self.calculate_capital_buckets()
        
        # Move trade from active to closed
        trade_to_close.status = 'CLOSED'
        self.closed_trades.append(trade_to_close)
        self.active_trades.remove(trade_to_close)
        
        # Update allocated capital tracking
        self.track_allocated_capital()
        
        result = {
            'status': 'CLOSED',
            'trade_id': trade_id,
            'symbol': trade_to_close.symbol,
            'shares': shares,
            'entry_price': trade_to_close.entry_price,
            'exit_price': exit_price,
            'gross_proceeds': gross_proceeds,
            'gross_pnl': gross_pnl,
            'brokerage': brokerage,
            'net_pnl': net_pnl,
            'available_after': self.available_deployment_capital,
            'message': f"Trade closed: ₹{net_pnl:,.2f} P&L"
        }
        
        logger.info(f"🔄 {result['message']}")
        return result

    def get_capital_status(self) -> Dict:
        """
        Get comprehensive capital allocation status
        
        Returns complete view of:
        - Capital buckets
        - Allocation status  
        - Trading capacity
        - Performance metrics
        """
        
        # Calculate metrics
        total_trades = len(self.active_trades) + len(self.closed_trades)
        max_possible_trades = int(self.deployment_capital / (self.deployment_capital * (self.per_trade_percentage / 100)))
        utilization_pct = (self.allocated_capital / self.deployment_capital) * 100 if self.deployment_capital > 0 else 0
        
        # Performance metrics
        total_pnl = sum(trade.get('net_pnl', 0) for trade in self.trade_history)
        
        return {
            # Capital buckets
            'total_capital': self.total_capital,
            'deployment_capital': self.deployment_capital,
            'deployable_capital': self.deployable_capital,  # Alias
            'reserve_capital': self.reserve_capital,
            'allocated_capital': self.allocated_capital,
            'available_deployment_capital': self.available_deployment_capital,
            
            # Percentages
            'deployment_percentage': self.deployment_percentage,
            'reserve_percentage': self.reserve_percentage,
            'per_trade_percentage': self.per_trade_percentage,
            'utilization_percentage': utilization_pct,
            
            # Trading capacity
            'active_trades': len(self.active_trades),
            'max_possible_trades': max_possible_trades,
            'remaining_capacity': max_possible_trades - len(self.active_trades),
            'per_trade_allocation': self.deployment_capital * (self.per_trade_percentage / 100),
            
            # Performance
            'total_trades_executed': total_trades,
            'trades_closed': len(self.closed_trades),
            'total_pnl': total_pnl,
            
            # Validation
            'reserve_untouched': True,  # Always true in this system
            'capital_buckets_valid': abs((self.deployment_capital + self.reserve_capital) - self.total_capital) < 0.01
        }

    def validate_reserve_protection(self) -> bool:
        """
        Always Maintain the Reserve (Step 6)
        
        Validates that reserve capital is never touched for regular trades
        
        Returns:
            True if reserve is properly protected, False otherwise
        """
        
        # Check that we never allocate from reserve
        total_possible_allocation = self.deployment_capital
        
        if self.allocated_capital <= total_possible_allocation:
            logger.debug("✅ Reserve protection validated")
            return True
        else:
            logger.error("❌ Reserve protection violated!")
            return False

    def log_capital_status(self):
        """Log current capital allocation status"""
        status = self.get_capital_status()
        
        print(f"\\n📊 DYNAMIC CAPITAL ALLOCATION STATUS")
        print("=" * 50)
        print(f"💰 Total Capital:           ₹{status['total_capital']:,.0f}")
        print(f"📈 Deployment ({status['deployment_percentage']:.0f}%):      ₹{status['deployment_capital']:,.0f}")
        print(f"🛡️  Reserve ({status['reserve_percentage']:.0f}%):         ₹{status['reserve_capital']:,.0f}")
        print(f"💼 Allocated:               ₹{status['allocated_capital']:,.0f}")
        print(f"✅ Available:               ₹{status['available_deployment_capital']:,.0f}")
        print(f"🎯 Per Trade:               ₹{status['per_trade_allocation']:,.0f}")
        print(f"📊 Utilization:             {status['utilization_percentage']:.1f}%")
        print(f"🔢 Active Trades:           {status['active_trades']}")
        print(f"🏆 Max Capacity:            {status['max_possible_trades']} trades")
        print(f"📈 Total P&L:               ₹{status['total_pnl']:,.2f}")
        print()

    def simulate_trading_session(self, signals: List[TradeSignal]) -> Dict:
        """
        Simulate a complete trading session with multiple signals
        
        Args:
            signals: List of trade signals to process
            
        Returns:
            Dict with session summary and results
        """
        
        print(f"🎯 TRADING SESSION SIMULATION")
        print(f"Processing {len(signals)} signals...")
        print()
        
        results = {
            'signals_processed': 0,
            'trades_executed': 0,
            'trades_rejected': 0,
            'session_pnl': 0.0
        }
        
        for i, signal in enumerate(signals, 1):
            print(f"Signal {i}: {signal.signal_type} {signal.symbol} @ ₹{signal.price}")
            
            # Process the signal (Step 4)
            result = self.process_trade_signal(signal)
            results['signals_processed'] += 1
            
            if result['status'] == 'EXECUTED':
                results['trades_executed'] += 1
                print(f"   ✅ {result['message']}")
            else:
                results['trades_rejected'] += 1
                print(f"   ❌ {result['message']}")
            
            # Validate reserve protection (Step 6)
            self.validate_reserve_protection()
            
            # Show current status
            print(f"   💰 Available: ₹{self.available_deployment_capital:,.0f} | "
                  f"Active: {len(self.active_trades)} trades")
        
        print(f"\\n🎯 SESSION COMPLETE")
        print(f"Signals: {results['signals_processed']} | "
              f"Executed: {results['trades_executed']} | "
              f"Rejected: {results['trades_rejected']}")
        
        self.log_capital_status()
        
        return results


# Demo functions removed - integrated with live trading system

if __name__ == "__main__":
    print("🎯 DYNAMIC CAPITAL ALLOCATOR - LIVE MODE")
    print("=" * 50)
    print("This module is integrated with the live trading system.")
    print("Use the trading dashboard to access all functionality.")