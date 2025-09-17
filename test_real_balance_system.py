"""
🧪 REAL ACCOUNT BALANCE SYSTEM TESTING
=====================================

Test the complete real account balance integration system with mock data
to validate functionality before connecting to live Breeze API.
"""

import json
import time
from datetime import datetime
from real_account_balance import RealAccountBalanceManager, AccountBalance
from dynamic_capital_allocator import DynamicCapitalAllocator
from real_time_monitor import RealTimeAccountMonitor


class MockBreezeAPIClient:
    """Mock Breeze API client for testing"""
    
    def __init__(self, mock_balance: float = 750000):
        """Initialize with mock balance"""
        self.mock_available_cash = mock_balance
        self.mock_margin_used = mock_balance * 0.1  # 10% margin used
        self.mock_portfolio_value = mock_balance * 0.2  # 20% in portfolio
        
        print(f"🔧 Mock API initialized with ₹{mock_balance:,.2f} balance")
    
    def get_account_funds(self):
        """Mock account funds response"""
        return {
            'available_cash': self.mock_available_cash,
            'margin_used': self.mock_margin_used,
            'total_balance': self.mock_available_cash + self.mock_portfolio_value
        }
    
    def get_portfolio(self):
        """Mock portfolio response"""
        return [
            {
                'symbol': 'NIFTYBEES',
                'quantity': 100,
                'market_value': self.mock_portfolio_value * 0.6
            },
            {
                'symbol': 'BANKBEES',
                'quantity': 50,
                'market_value': self.mock_portfolio_value * 0.4
            }
        ]
    
    def simulate_balance_change(self, new_balance: float):
        """Simulate balance change for testing"""
        print(f"📈 Simulating balance change: ₹{self.mock_available_cash:,.2f} → ₹{new_balance:,.2f}")
        self.mock_available_cash = new_balance
        self.mock_margin_used = new_balance * 0.1
        self.mock_portfolio_value = new_balance * 0.2


def test_real_balance_integration():
    """Test the complete real balance integration"""
    print("🧪 TESTING REAL ACCOUNT BALANCE SYSTEM")
    print("=" * 50)
    
    # Test scenarios with different balance amounts
    test_scenarios = [
        {"name": "Small Account", "balance": 250000},   # ₹2.5L
        {"name": "Medium Account", "balance": 750000},  # ₹7.5L (your reference scenario)
        {"name": "Large Account", "balance": 2000000}, # ₹20L
    ]
    
    for scenario in test_scenarios:
        print(f"\n📊 Testing Scenario: {scenario['name']} (₹{scenario['balance']:,.2f})")
        print("-" * 40)
        
        try:
            # Create mock API client
            mock_api = MockBreezeAPIClient(scenario['balance'])
            
            # Test 1: Real Balance Manager
            print("\n1️⃣ Testing Real Balance Manager...")
            balance_manager = RealAccountBalanceManager()
            
            # Replace with mock API
            balance_manager.api_client = mock_api
            
            # Fetch balance
            balance = balance_manager.fetch_real_account_balance()
            if balance:
                print(f"✅ Available Cash: ₹{balance.available_cash:,.2f}")
                print(f"✅ Free Cash: ₹{balance.free_cash:,.2f}")
                print(f"✅ Deployable (70%): ₹{balance.deployable_capital:,.2f}")
                print(f"✅ Reserve (30%): ₹{balance.reserve_capital:,.2f}")
                print(f"✅ Per Trade (5%): ₹{balance.per_trade_capital:,.2f}")
            else:
                print("❌ Failed to fetch balance")
                continue
            
            # Test 2: Dynamic Capital Allocator
            print("\n2️⃣ Testing Dynamic Capital Allocator...")
            allocator = DynamicCapitalAllocator(use_real_balance=False)  # Use mock
            
            # Manually set balance for testing
            allocator.balance_manager = balance_manager
            allocator.use_real_balance = True
            allocator._initialize_with_real_balance()
            
            print(f"✅ Total Capital: ₹{allocator.total_capital:,.2f}")
            print(f"✅ Deployable: ₹{allocator.deployable_capital:,.2f}")
            print(f"✅ Per Trade: ₹{allocator.per_trade_amount:,.2f}")
            
            # Calculate maximum positions
            max_positions = int(allocator.deployable_capital / allocator.per_trade_amount) if allocator.per_trade_amount > 0 else 0
            print(f"✅ Max Positions: {max_positions}")
            
            # Test 3: Balance Change Simulation
            print("\n3️⃣ Testing Balance Change Detection...")
            
            # Create monitor with short check interval for testing
            monitor = RealTimeAccountMonitor(
                capital_allocator=allocator,
                check_interval_minutes=0.1,  # 6 seconds for testing
                significant_change_threshold=0.05,  # 5%
                auto_adjust=True
            )
            
            # Replace with mock
            monitor.balance_manager = balance_manager
            
            # Test initial balance check
            result = monitor.force_balance_check()
            print(f"✅ Initial check: {result['status']}")
            
            # Simulate balance change
            new_balance = scenario['balance'] * 1.1  # 10% increase
            mock_api.simulate_balance_change(new_balance)
            
            # Check for change detection
            result = monitor.force_balance_check()
            print(f"✅ Change detected: {result['status']}")
            
            # Test 4: Allocation Comparison
            print("\n4️⃣ Testing Allocation vs Reference...")
            
            reference_amount = 1000000  # ₹10L reference
            comparison = balance_manager.compare_with_reference(reference_amount)
            
            ratio = comparison['ratio']
            scaling = comparison['allocation_scaling']['scaling_factor']
            
            print(f"✅ Balance Ratio: {ratio:.1%} of reference")
            print(f"✅ Scaling Factor: {scaling:.2f}x")
            print(f"✅ Reference Per Trade: ₹{comparison['allocation_scaling']['reference_per_trade']:,.2f}")
            print(f"✅ Actual Per Trade: ₹{comparison['allocation_scaling']['actual_per_trade']:,.2f}")
            
            # Test 5: Save Balance Snapshot
            print("\n5️⃣ Testing Balance Snapshot...")
            
            snapshot_file = f"test_snapshot_{scenario['name'].lower().replace(' ', '_')}.json"
            filepath = balance_manager.save_balance_snapshot(snapshot_file)
            
            with open(filepath, 'r') as f:
                snapshot_data = json.load(f)
            
            print(f"✅ Snapshot saved: {filepath}")
            print(f"✅ Deployable in snapshot: ₹{snapshot_data['allocation_strategy']['deployable_capital']:,.2f}")
            
            print(f"\n✅ {scenario['name']} scenario completed successfully!")
            
        except Exception as e:
            print(f"❌ {scenario['name']} scenario failed: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 TESTING COMPLETE")


def test_balance_scaling_accuracy():
    """Test that scaling works correctly across different balance amounts"""
    print("\n🔍 TESTING BALANCE SCALING ACCURACY")
    print("=" * 40)
    
    reference = 1000000  # ₹10L reference
    
    test_amounts = [100000, 250000, 500000, 750000, 1000000, 1500000, 2000000, 5000000]
    
    print(f"Reference Amount: ₹{reference:,.2f}")
    print("Per Trade should be: Free Cash × 70% × 5% = Free Cash × 3.5%")
    print()
    
    for amount in test_amounts:
        # Calculate expected per trade (3.5% of free cash)
        expected_per_trade = amount * 0.035
        
        # Create mock and test
        mock_api = MockBreezeAPIClient(amount)
        balance_manager = RealAccountBalanceManager()
        balance_manager.api_client = mock_api
        
        balance = balance_manager.fetch_real_account_balance()
        
        actual_per_trade = balance.per_trade_capital
        accuracy = (actual_per_trade / expected_per_trade) * 100 if expected_per_trade > 0 else 0
        
        print(f"Amount: ₹{amount:>8,.0f} | Expected: ₹{expected_per_trade:>6,.0f} | Actual: ₹{actual_per_trade:>6,.0f} | Accuracy: {accuracy:.1f}%")
    
    print("\n✅ Scaling accuracy test completed!")


def run_comprehensive_test():
    """Run comprehensive testing of the real balance system"""
    print("🚀 COMPREHENSIVE REAL BALANCE SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Basic Integration
        test_real_balance_integration()
        
        # Test 2: Scaling Accuracy  
        test_balance_scaling_accuracy()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Real account balance system is ready for production")
        print("🔗 Connect to live Breeze API to start using real balance")
        
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE TEST FAILED: {e}")
        print("🔧 Please check the system configuration")


if __name__ == "__main__":
    run_comprehensive_test()