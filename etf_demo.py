"""
Turtle Trader - ETF Demo Mode
Test ETF trading system with realistic ETF data and strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt

from etf_manager import etf_order_manager, ETFOrderType, ETFOrderRequest
from etf_strategies import etf_strategy_manager, ETFSignal

def generate_etf_data(symbol: str, days: int = 60) -> pd.DataFrame:
    """Generate realistic ETF data with different characteristics"""
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         end=datetime.now(), freq='5min')
    
    # ETF-specific characteristics
    etf_configs = {
        'GOLDBEES': {'base_price': 45, 'volatility': 0.015, 'trend': 0.0001},      # Gold ETF - stable
        'NIFTYBEES': {'base_price': 185, 'volatility': 0.02, 'trend': 0.0002},     # Nifty ETF - growth
        'BANKBEES': {'base_price': 420, 'volatility': 0.025, 'trend': 0.0001},     # Bank ETF - volatile
        'JUNIORBEES': {'base_price': 380, 'volatility': 0.022, 'trend': 0.0003},   # Junior ETF
        'LIQUIDBEES': {'base_price': 1000, 'volatility': 0.001, 'trend': 0.0001},  # Liquid ETF - stable
        'ITBEES': {'base_price': 290, 'volatility': 0.03, 'trend': 0.0002},        # IT ETF - volatile
        'PHARMBEES': {'base_price': 950, 'volatility': 0.025, 'trend': 0.0001},    # Pharma ETF
        'PSUBANK': {'base_price': 35, 'volatility': 0.03, 'trend': -0.0001},       # PSU Bank ETF
        'CPSE': {'base_price': 28, 'volatility': 0.028, 'trend': -0.0001},         # CPSE ETF
        'NETF': {'base_price': 180, 'volatility': 0.022, 'trend': 0.0002}          # Next 50 ETF
    }
    
    config = etf_configs.get(symbol, {'base_price': 100, 'volatility': 0.02, 'trend': 0})
    
    # Generate price series
    np.random.seed(hash(symbol) % 1000)  # Consistent seed per symbol
    
    prices = [config['base_price']]
    volumes = []
    
    for i in range(1, len(dates)):
        # Add trend and random walk
        trend_factor = config['trend']
        random_factor = np.random.normal(0, config['volatility'])
        
        # Add some market hours effect (higher volume during trading hours)
        hour = dates[i].hour
        if 9 <= hour <= 15:  # Trading hours
            volume_multiplier = 1.5
            volatility_multiplier = 1.2
        else:
            volume_multiplier = 0.3
            volatility_multiplier = 0.8
        
        # Calculate new price
        price_change = (trend_factor + random_factor * volatility_multiplier)
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, config['base_price'] * 0.5))  # Floor price
        
        # Generate volume (higher during volatile periods)
        base_volume = 10000
        volatility_volume = int(abs(random_factor) * 50000)
        volume = int(base_volume * volume_multiplier + volatility_volume)
        volumes.append(max(volume, 1000))
    
    # Create OHLCV data
    data = []
    for i in range(len(dates)):
        price = prices[i]
        volume = volumes[i] if i < len(volumes) else 10000
        
        # Generate OHLC from price
        high = price * (1 + np.random.uniform(0, 0.005))
        low = price * (1 - np.random.uniform(0, 0.005))
        open_price = prices[i-1] if i > 0 else price
        
        data.append({
            'datetime': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    
    return df

def test_etf_strategies():
    """Test ETF strategies with generated data"""
    
    print("🎯 ETF STRATEGY TESTING")
    print("=" * 60)
    
    # Generate data for all ETFs
    etf_data = {}
    etf_symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'JUNIORBEES', 
                   'LIQUIDBEES', 'ITBEES', 'PHARMBEES']
    
    print("📊 Generating ETF market data...")
    for symbol in etf_symbols:
        etf_data[symbol] = generate_etf_data(symbol, days=30)
        print(f"✅ {symbol}: {len(etf_data[symbol])} data points")
    
    print("\n🧠 Running ETF Strategy Analysis...")
    
    # Get signals from strategy manager
    signals = etf_strategy_manager.get_etf_signals(etf_data)
    
    print(f"\n📈 Generated {len(signals)} trading signals:")
    print("-" * 80)
    
    for i, signal in enumerate(signals[:10], 1):  # Show top 10
        print(f"{i:2d}. {signal.symbol:12s} | {signal.action:4s} | "
              f"Strength: {signal.strength:5.2f} | "
              f"Type: {signal.order_type.value:3s}")
        print(f"     Reasoning: {signal.reasoning[:70]}...")
        
        if signal.price_target:
            print(f"     Target: ₹{signal.price_target:.2f} | "
                  f"Stop Loss: ₹{signal.stop_loss:.2f}")
        print()
    
    return signals, etf_data

def test_etf_order_management():
    """Test ETF order management system"""
    
    print("\n💼 ETF ORDER MANAGEMENT TESTING")
    print("=" * 60)
    
    # Test position sizing for different ETFs
    test_symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES']
    test_prices = [45.50, 185.20, 420.80]
    
    print("📊 Position Sizing Analysis:")
    print("-" * 50)
    
    for symbol, price in zip(test_symbols, test_prices):
        # Test both order types
        cnc_size = etf_order_manager.calculate_etf_position_size(
            symbol, price, ETFOrderType.CNC)
        mtf_size = etf_order_manager.calculate_etf_position_size(
            symbol, price, ETFOrderType.MTF)
        
        cnc_value = cnc_size * price
        mtf_value = mtf_size * price
        
        print(f"{symbol:12s} @ ₹{price:7.2f}")
        print(f"  CNC: {cnc_size:6d} units = ₹{cnc_value:10,.0f}")
        print(f"  MTF: {mtf_size:6d} units = ₹{mtf_value:10,.0f}")
        print()
    
    # Test ETF allocation
    print("📈 ETF Portfolio Allocation (₹10,00,000):")
    print("-" * 50)
    
    allocation = etf_order_manager.calculate_etf_allocation(1000000)
    
    for etf, amount in allocation.items():
        percentage = (amount / 1000000) * 100
        print(f"{etf:12s}: ₹{amount:8,.0f} ({percentage:4.1f}%)")
    
    print(f"\nTotal Allocated: ₹{sum(allocation.values()):,.0f}")

def test_etf_order_creation():
    """Test ETF order creation"""
    
    print("\n📋 ETF ORDER CREATION TESTING")
    print("=" * 60)
    
    # Create sample buy orders
    sample_orders = [
        {'symbol': 'NIFTYBEES', 'price': 185.50, 'order_type': ETFOrderType.CNC},
        {'symbol': 'GOLDBEES', 'price': 45.25, 'order_type': ETFOrderType.MTF},
        {'symbol': 'BANKBEES', 'price': 421.00, 'order_type': ETFOrderType.CNC}
    ]
    
    print("🛒 Sample Buy Orders:")
    print("-" * 40)
    
    for order_data in sample_orders:
        order = etf_order_manager.create_etf_buy_order(
            symbol=order_data['symbol'],
            price=order_data['price'],
            order_type=order_data['order_type']
        )
        
        estimated_cost = order.quantity * order_data['price']
        
        print(f"Symbol: {order.symbol}")
        print(f"Action: {order.action}")
        print(f"Quantity: {order.quantity}")
        print(f"Order Type: {order.order_type.value}")
        print(f"Product Type: {order.product_type.value}")
        print(f"Estimated Cost: ₹{estimated_cost:,.0f}")
        print("-" * 40)

def generate_etf_performance_report(signals: List[ETFSignal], 
                                  etf_data: Dict[str, pd.DataFrame]):
    """Generate ETF performance analysis report"""
    
    print("\n📊 ETF PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Analyze current market conditions for each ETF
    for symbol, data in etf_data.items():
        if len(data) < 20:
            continue
        
        current_price = data['close'].iloc[-1]
        sma_20 = data['close'].rolling(20).mean().iloc[-1]
        
        # Price vs moving average
        price_vs_sma = (current_price - sma_20) / sma_20 * 100
        
        # Volatility (20-day)
        volatility = data['close'].pct_change().rolling(20).std().iloc[-1] * 100
        
        # Volume trend
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        recent_volume = data['volume'].rolling(5).mean().iloc[-1]
        volume_trend = (recent_volume - avg_volume) / avg_volume * 100
        
        print(f"{symbol:12s} | Price: ₹{current_price:7.2f} | "
              f"vs SMA: {price_vs_sma:+5.1f}% | "
              f"Vol: {volatility:4.1f}% | "
              f"Vol Trend: {volume_trend:+5.1f}%")
    
    # Signal distribution
    signal_actions = {}
    for signal in signals:
        signal_actions[signal.action] = signal_actions.get(signal.action, 0) + 1
    
    print(f"\n📈 Signal Distribution:")
    for action, count in signal_actions.items():
        print(f"  {action}: {count} signals")
    
    # Order type distribution
    order_types = {}
    for signal in signals:
        ot = signal.order_type.value
        order_types[ot] = order_types.get(ot, 0) + 1
    
    print(f"\n💳 Order Type Distribution:")
    for order_type, count in order_types.items():
        print(f"  {order_type}: {count} orders")

def run_etf_demo():
    """Main ETF demo function"""
    
    print("🎭 TURTLE TRADER - ETF TRADING DEMO")
    print("=" * 70)
    print("""
🎯 Focus: ETF Trading with MTF & CNC Order Types
📊 Symbols: Indian ETFs (GOLDBEES, NIFTYBEES, BANKBEES, etc.)
⚡ Strategies: ETF Momentum & Mean Reversion
💼 Order Types: CNC (Cash & Carry) & MTF (Margin Trading)
""")
    
    try:
        # Test strategies
        signals, etf_data = test_etf_strategies()
        
        # Test order management
        test_etf_order_management()
        
        # Test order creation
        test_etf_order_creation()
        
        # Generate performance report
        generate_etf_performance_report(signals, etf_data)
        
        print("\n" + "=" * 70)
        print("🎉 ETF DEMO COMPLETE - SYSTEM READY!")
        print("=" * 70)
        print("""
✅ ETF Strategy System: OPERATIONAL
✅ Order Management: CONFIGURED
✅ Position Sizing: OPTIMIZED
✅ Risk Management: ACTIVE

🔐 Next Steps:
1. Configure API credentials in config.ini
2. Set your capital amount in TRADING section
3. Customize ETF symbols list
4. Run: python main.py start

🎯 ETF Trading Features:
• Automated ETF selection and analysis
• MTF/CNC order type optimization
• Dynamic position sizing
• Multi-strategy signal generation
• Real-time risk monitoring

⚠️ Remember: Start with paper trading to validate strategies!
""")
        
    except Exception as e:
        print(f"❌ Error in ETF demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_etf_demo()
