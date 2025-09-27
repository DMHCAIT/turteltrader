"""
🏦 REAL ACCOUNT BALANCE INTEGRATION
==================================

Dynamic Capital Allocation based on ACTUAL Kite API account balance
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from kite_api_client import KiteAPIClient


@dataclass
class AccountBalance:
    """Real-time account balance data"""
    available_cash: float
    margin_used: float
    total_balance: float
    portfolio_value: float
    free_cash: float
    timestamp: datetime
    
    @property
    def deployable_capital(self) -> float:
        """70% of available cash as per your strategy"""
        return self.free_cash * 0.70
    
    @property
    def reserve_capital(self) -> float:
        """30% reserve as per your strategy"""
        return self.free_cash * 0.30
    
    @property
    def per_trade_capital(self) -> float:
        """5% per trade of deployable capital"""
        return self.deployable_capital * 0.05


class RealAccountBalanceManager:
    """Manage real-time account balance and dynamic allocation"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize with Kite API client"""
        self.api_client = KiteAPIClient(config_path)
        self.last_balance_check = None
        self.current_balance = None
        self.balance_cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Log setup
        logger.info("🏦 Real Account Balance Manager initialized")
    
    def fetch_real_account_balance(self) -> Optional[AccountBalance]:
        """Fetch real account balance from Kite API"""
        try:
            logger.info("📡 Fetching real account balance from Kite API...")
            
            # Get account margins from Kite API (this contains balance info)
            margins_response = self.api_client.get_margins()
            funds_response = margins_response  # Use margins for funds data
            if not funds_response:
                logger.error("❌ Failed to fetch account funds - Check API connection and credentials")
                logger.error("💡 Possible issues: 1) Access token expired 2) API credentials missing 3) Network timeout")
                return None
            
            # Get portfolio holdings from Kite API
            portfolio_response = self.api_client.get_holdings()
            portfolio_value = 0.0
            
            if portfolio_response and isinstance(portfolio_response, list):
                for holding in portfolio_response:
                    try:
                        # Calculate portfolio value (quantity * last_price)
                        quantity = float(holding.get('quantity', 0))
                        last_price = float(holding.get('last_price', 0))
                        portfolio_value += quantity * last_price
                    except (ValueError, TypeError):
                        continue
            
            # Extract balance information from Kite API margins response
            # Kite API margins response structure: {'equity': {...}, 'commodity': {...}}
            equity_margins = funds_response.get('equity', {})
            available_margins = equity_margins.get('available', {})
            utilised_margins = equity_margins.get('utilised', {})
            
            # Use live_balance (actual available balance) instead of cash
            available_cash = float(available_margins.get('live_balance', 0))
            margin_used = float(utilised_margins.get('debits', 0))
            total_balance = float(equity_margins.get('net', available_cash))
            
            # Calculate free cash (available for trading)
            free_cash = available_cash - margin_used
            
            balance = AccountBalance(
                available_cash=available_cash,
                margin_used=margin_used,
                total_balance=total_balance,
                portfolio_value=portfolio_value,
                free_cash=max(0, free_cash),  # Ensure non-negative
                timestamp=datetime.now()
            )
            
            self.current_balance = balance
            self.last_balance_check = datetime.now()
            
            logger.info(f"✅ Account balance updated: ₹{available_cash:,.2f} available")
            return balance
            
        except Exception as e:
            logger.error(f"❌ Error fetching account balance: {e}")
            return None
    
    def get_current_balance(self, force_refresh: bool = False) -> Optional[AccountBalance]:
        """Get current account balance (cached or fresh)"""
        
        # Check if we need to refresh cache
        if (force_refresh or 
            self.last_balance_check is None or 
            datetime.now() - self.last_balance_check > self.balance_cache_duration):
            
            return self.fetch_real_account_balance()
        
        return self.current_balance
    
    def get_dynamic_allocation(self, force_refresh: bool = False) -> Optional[Dict]:
        """Get dynamic capital allocation based on real account balance"""
        
        balance = self.get_current_balance(force_refresh)
        if not balance:
            logger.warning("⚠️ Could not fetch account balance for allocation")
            return None
        
        allocation = {
            'timestamp': balance.timestamp.isoformat(),
            'account_summary': {
                'total_balance': balance.total_balance,
                'available_cash': balance.available_cash,
                'margin_used': balance.margin_used,
                'portfolio_value': balance.portfolio_value,
                'free_cash': balance.free_cash
            },
            'allocation_strategy': {
                'deployable_capital': balance.deployable_capital,
                'reserve_capital': balance.reserve_capital,
                'per_trade_amount': balance.per_trade_capital,
                'max_positions': int(balance.deployable_capital / balance.per_trade_capital) if balance.per_trade_capital > 0 else 0
            },
            'allocation_percentages': {
                'deployment_pct': 70.0,
                'reserve_pct': 30.0,
                'per_trade_pct': 5.0,
                'profit_target_pct': 3.0,
                'brokerage_pct': 0.3
            }
        }
        
        logger.info(f"💼 Dynamic allocation: ₹{balance.deployable_capital:,.2f} deployable")
        return allocation
    
    def save_balance_snapshot(self, filepath: Optional[str] = None) -> str:
        """Save current balance snapshot to JSON"""
        
        allocation = self.get_dynamic_allocation()
        if not allocation:
            raise ValueError("Cannot save balance snapshot - no balance data available")
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"real_balance_snapshot_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(allocation, f, indent=2)
        
        logger.info(f"💾 Balance snapshot saved to {filepath}")
        return filepath
    
    def compare_with_reference(self, reference_amount: float = 1000000) -> Dict:
        """Compare current balance with your reference amount (₹10L)"""
        
        balance = self.get_current_balance()
        if not balance:
            return {'error': 'Could not fetch current balance'}
        
        comparison = {
            'reference_amount': reference_amount,
            'actual_amount': balance.free_cash,
            'difference': balance.free_cash - reference_amount,
            'ratio': balance.free_cash / reference_amount if reference_amount > 0 else 0,
            'allocation_scaling': {
                'reference_deployable': reference_amount * 0.70,
                'actual_deployable': balance.deployable_capital,
                'reference_per_trade': reference_amount * 0.70 * 0.05,
                'actual_per_trade': balance.per_trade_capital,
                'scaling_factor': balance.free_cash / reference_amount if reference_amount > 0 else 0
            }
        }
        
        logger.info(f"📊 Balance vs Reference: {comparison['ratio']:.2%} of reference")
        return comparison


def test_real_balance_integration():
    """Test the real balance integration system"""
    print("🔍 Testing Real Account Balance Integration...")
    
    try:
        # Initialize manager
        manager = RealAccountBalanceManager()
        
        # Test balance fetch
        print("\n📡 Fetching real account balance...")
        balance = manager.get_current_balance(force_refresh=True)
        
        if balance:
            print(f"✅ Balance fetched successfully!")
            print(f"💰 Available Cash: ₹{balance.available_cash:,.2f}")
            print(f"📊 Free Cash: ₹{balance.free_cash:,.2f}")
            print(f"🎯 Deployable (70%): ₹{balance.deployable_capital:,.2f}")
            print(f"🛡️ Reserve (30%): ₹{balance.reserve_capital:,.2f}")
            print(f"💸 Per Trade (5%): ₹{balance.per_trade_capital:,.2f}")
            
            # Get dynamic allocation
            allocation = manager.get_dynamic_allocation()
            if allocation:
                max_positions = allocation['allocation_strategy']['max_positions']
                print(f"🔢 Max Simultaneous Positions: {max_positions}")
            
            # Compare with reference
            comparison = manager.compare_with_reference()
            print(f"📈 Scaling vs ₹10L reference: {comparison['ratio']:.2%}")
            
            # Save snapshot
            filepath = manager.save_balance_snapshot()
            print(f"💾 Snapshot saved: {filepath}")
            
        else:
            print("❌ Could not fetch balance - check API connection")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_real_balance_integration()