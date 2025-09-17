"""
📊 REAL-TIME ACCOUNT BALANCE MONITOR
==================================

Automatic monitoring and adjustment of capital allocation based on 
real Breeze API account balance changes.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from loguru import logger
import json

from real_account_balance import RealAccountBalanceManager, AccountBalance
from dynamic_capital_allocator import DynamicCapitalAllocator


@dataclass
class BalanceChangeEvent:
    """Event triggered when significant balance change is detected"""
    timestamp: datetime
    old_balance: float
    new_balance: float
    change_amount: float
    change_percentage: float
    trigger_reason: str


class RealTimeAccountMonitor:
    """Real-time account balance monitoring and auto-adjustment system"""
    
    def __init__(self, 
                 capital_allocator: DynamicCapitalAllocator,
                 check_interval_minutes: int = 5,
                 significant_change_threshold: float = 0.05,  # 5% change threshold
                 auto_adjust: bool = True):
        """
        Initialize real-time monitor
        
        Args:
            capital_allocator: The capital allocator to monitor/adjust
            check_interval_minutes: How often to check balance (minutes)
            significant_change_threshold: Threshold for significant changes (%)
            auto_adjust: Whether to automatically adjust allocation on changes
        """
        
        self.capital_allocator = capital_allocator
        self.balance_manager = RealAccountBalanceManager()
        self.check_interval = timedelta(minutes=check_interval_minutes)
        self.change_threshold = significant_change_threshold
        self.auto_adjust = auto_adjust
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_balance = None
        self.balance_history = []
        self.change_events = []
        
        # Callbacks for events
        self.on_balance_change_callbacks = []
        self.on_significant_change_callbacks = []
        
        logger.info(f"📊 Real-time monitor initialized - Check interval: {check_interval_minutes}min")
    
    def add_balance_change_callback(self, callback: Callable[[BalanceChangeEvent], None]):
        """Add callback for balance change events"""
        self.on_balance_change_callbacks.append(callback)
    
    def add_significant_change_callback(self, callback: Callable[[BalanceChangeEvent], None]):
        """Add callback for significant balance change events"""
        self.on_significant_change_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start real-time balance monitoring"""
        if self.is_monitoring:
            logger.warning("⚠️ Monitor already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 Real-time balance monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time balance monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("⏹️ Real-time balance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop (runs in background thread)"""
        logger.info("🔄 Balance monitoring loop started")
        
        while self.is_monitoring:
            try:
                self._check_balance_changes()
                time.sleep(self.check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _check_balance_changes(self):
        """Check for balance changes and trigger events"""
        try:
            # Get current balance
            current_balance = self.balance_manager.get_current_balance(force_refresh=True)
            if not current_balance:
                return
            
            # Store balance history
            self.balance_history.append({
                'timestamp': current_balance.timestamp,
                'free_cash': current_balance.free_cash,
                'available_cash': current_balance.available_cash,
                'portfolio_value': current_balance.portfolio_value
            })
            
            # Keep only last 100 entries
            if len(self.balance_history) > 100:
                self.balance_history = self.balance_history[-100:]
            
            # Check for changes if we have previous balance
            if self.last_balance:
                change_amount = current_balance.free_cash - self.last_balance.free_cash
                
                if abs(change_amount) > 0:  # Any change
                    change_percentage = abs(change_amount) / self.last_balance.free_cash
                    
                    # Create change event
                    event = BalanceChangeEvent(
                        timestamp=datetime.now(),
                        old_balance=self.last_balance.free_cash,
                        new_balance=current_balance.free_cash,
                        change_amount=change_amount,
                        change_percentage=change_percentage,
                        trigger_reason='balance_update'
                    )
                    
                    # Log the change
                    direction = "📈" if change_amount > 0 else "📉"
                    logger.info(f"{direction} Balance change detected: ₹{change_amount:+,.2f} "
                               f"({change_percentage:+.2%})")
                    
                    # Trigger callbacks
                    for callback in self.on_balance_change_callbacks:
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"❌ Balance change callback error: {e}")
                    
                    # Check if significant change
                    if change_percentage >= self.change_threshold:
                        logger.warning(f"🚨 SIGNIFICANT balance change: {change_percentage:.2%}")
                        
                        # Store significant change
                        self.change_events.append(event)
                        
                        # Trigger significant change callbacks
                        for callback in self.on_significant_change_callbacks:
                            try:
                                callback(event)
                            except Exception as e:
                                logger.error(f"❌ Significant change callback error: {e}")
                        
                        # Auto-adjust if enabled
                        if self.auto_adjust:
                            self._auto_adjust_allocation(event)
            
            # Update last balance
            self.last_balance = current_balance
            
        except Exception as e:
            logger.error(f"❌ Balance check error: {e}")
    
    def _auto_adjust_allocation(self, event: BalanceChangeEvent):
        """Automatically adjust capital allocation after significant balance change"""
        try:
            logger.info("⚡ Auto-adjusting capital allocation...")
            
            success = self.capital_allocator.refresh_real_balance()
            if success:
                logger.info("✅ Capital allocation auto-adjusted successfully")
                
                # Log new allocation details
                status = self.capital_allocator.get_real_balance_status()
                if 'allocation_status' in status:
                    alloc = status['allocation_status']
                    logger.info(f"💼 New Allocation - Deployable: ₹{alloc['deployable_capital']:,.2f}, "
                               f"Per Trade: ₹{alloc['per_trade_amount']:,.2f}")
            else:
                logger.error("❌ Failed to auto-adjust capital allocation")
                
        except Exception as e:
            logger.error(f"❌ Auto-adjustment error: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status and statistics"""
        return {
            'monitoring': {
                'is_active': self.is_monitoring,
                'check_interval_minutes': self.check_interval.total_seconds() / 60,
                'auto_adjust_enabled': self.auto_adjust,
                'change_threshold_pct': self.change_threshold * 100
            },
            'balance_history': {
                'total_entries': len(self.balance_history),
                'oldest_entry': self.balance_history[0]['timestamp'].isoformat() if self.balance_history else None,
                'latest_entry': self.balance_history[-1]['timestamp'].isoformat() if self.balance_history else None
            },
            'change_events': {
                'total_significant_changes': len(self.change_events),
                'last_significant_change': self.change_events[-1].timestamp.isoformat() if self.change_events else None
            },
            'current_balance': {
                'free_cash': self.last_balance.free_cash if self.last_balance else None,
                'last_updated': self.last_balance.timestamp.isoformat() if self.last_balance else None
            }
        }
    
    def force_balance_check(self) -> Dict:
        """Force an immediate balance check and return results"""
        logger.info("🔍 Forcing immediate balance check...")
        
        try:
            self._check_balance_changes()
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'current_balance': self.last_balance.free_cash if self.last_balance else None,
                'message': 'Balance check completed successfully'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'message': 'Balance check failed'
            }


def setup_default_monitoring(capital_allocator: DynamicCapitalAllocator) -> RealTimeAccountMonitor:
    """Set up default monitoring with standard callbacks"""
    
    monitor = RealTimeAccountMonitor(
        capital_allocator=capital_allocator,
        check_interval_minutes=5,
        significant_change_threshold=0.05,  # 5%
        auto_adjust=True
    )
    
    # Add default callbacks
    def log_balance_changes(event: BalanceChangeEvent):
        direction = "💰" if event.change_amount > 0 else "💸"
        logger.info(f"{direction} Balance: ₹{event.old_balance:,.2f} → ₹{event.new_balance:,.2f}")
    
    def alert_significant_changes(event: BalanceChangeEvent):
        logger.warning(f"🚨 ALERT: {event.change_percentage:.1%} balance change - "
                      f"₹{event.change_amount:+,.2f}")
    
    monitor.add_balance_change_callback(log_balance_changes)
    monitor.add_significant_change_callback(alert_significant_changes)
    
    return monitor


def test_monitoring_system():
    """Test the real-time monitoring system"""
    print("🔍 Testing Real-Time Account Monitor...")
    
    try:
        # Create capital allocator with real balance
        allocator = DynamicCapitalAllocator(use_real_balance=True)
        
        # Set up monitoring
        monitor = setup_default_monitoring(allocator)
        
        print("✅ Monitor created successfully")
        
        # Test status
        status = monitor.get_monitoring_status()
        print(f"📊 Monitoring Status: {status['monitoring']['is_active']}")
        
        # Test force check
        result = monitor.force_balance_check()
        print(f"🔍 Force check result: {result['status']}")
        
        if result['status'] == 'success':
            print(f"💰 Current Balance: ₹{result['current_balance']:,.2f}")
        
        # Test brief monitoring (5 seconds)
        print("\n🔄 Starting 5-second monitoring test...")
        monitor.start_monitoring()
        time.sleep(5)
        monitor.stop_monitoring()
        print("⏹️ Monitoring test complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_monitoring_system()