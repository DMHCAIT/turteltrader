"""
Custom ETF Strategy Demo
Test the 1% Dip Buy, 3% Target Sell, 5% Loss Alert strategy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt

from custom_strategy import custom_etf_strategy, CustomSignal, PositionStatus

def generate_realistic_etf_data_with_dips(symbol: str, days: int = 5) -> pd.DataFrame:
    """Generate ETF data with realistic price movements and dips"""
    
    # Base prices for different ETFs
    etf_base_prices = {
        'GOLDBEES': 45.0,
        'NIFTYBEES': 185.0,
        'BANKBEES': 420.0,
        'JUNIORBEES': 380.0,
        'LIQUIDBEES': 1000.0,
        'ITBEES': 290.0,
        'PHARMBEES': 950.0,
    }
    
    base_price = etf_base_prices.get(symbol, 100.0)
    
    # Generate trading days (only weekdays)
    dates = []
    current_date = datetime.now() - timedelta(days=days)
    
    while len(dates) <= days:
        if current_date.weekday() < 5:  # Monday=0, Friday=4
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Generate daily OHLCV data with some dips
    data = []
    current_price = base_price
    
    for i, date in enumerate(dates):
        # Create scenarios: some days with dips, some with gains
        if i == 1:  # Yesterday - set a baseline
            daily_change = np.random.normal(0, 0.01)  # Small random change
        elif i == len(dates) - 1:  # Today - create opportunities
            # 50% chance of a dip (good for buying)
            if np.random.random() < 0.5:
                daily_change = np.random.uniform(-0.025, -0.008)  # 0.8% to 2.5% dip
            else:
                daily_change = np.random.uniform(-0.005, 0.015)   # Small change to gain
        else:
            daily_change = np.random.normal(0, 0.012)  # Normal volatility
        
        # Calculate new price
        new_price = current_price * (1 + daily_change)
        
        # Generate intraday OHLC
        high = new_price * (1 + np.random.uniform(0, 0.008))
        low = new_price * (1 - np.random.uniform(0, 0.008))
        open_price = current_price
        close_price = new_price
        
        # Generate volume (higher on volatile days)
        base_volume = 50000
        volatility_volume = int(abs(daily_change) * 200000)
        volume = base_volume + volatility_volume + np.random.randint(0, 30000)
        
        data.append({
            'datetime': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
        
        current_price = new_price
    
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    
    return df

def test_custom_strategy():
    """Test custom ETF strategy with generated data"""
    
    print("🎯 CUSTOM ETF STRATEGY TESTING")
    print("=" * 70)
    print(f"""
📋 Strategy Rules:
• Buy when ETF drops 1%+ from yesterday's close
• Sell when profit reaches 3%
• Alert when loss reaches 5%
• One position per ETF until sold
• MTF orders first, CNC fallback

🎮 Current Settings:
• Buy Dip: {custom_etf_strategy.buy_dip_percent}%
• Sell Target: {custom_etf_strategy.sell_target_percent}%
• Loss Alert: {custom_etf_strategy.loss_alert_percent}%
• MTF Priority: {custom_etf_strategy.mtf_first_priority}
""")
    
    # Generate data for multiple ETFs
    etf_symbols = ['GOLDBEES', 'NIFTYBEES', 'BANKBEES', 'JUNIORBEES', 'ITBEES']
    etf_market_data = {}
    
    print("📊 Generating Market Data...")
    print("-" * 50)
    
    for symbol in etf_symbols:
        etf_market_data[symbol] = generate_realistic_etf_data_with_dips(symbol)
        
        # Display current vs yesterday prices
        data = etf_market_data[symbol]
        today_price = data['close'].iloc[-1]
        yesterday_price = data['close'].iloc[-2] if len(data) >= 2 else today_price
        
        change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
        change_indicator = "📉" if change_percent < 0 else "📈"
        
        print(f"{symbol:12s}: ₹{today_price:7.2f} | "
              f"Yesterday: ₹{yesterday_price:7.2f} | "
              f"{change_indicator} {change_percent:+5.2f}%")
    
    print(f"\n🔍 Analyzing for Trading Signals...")
    print("-" * 50)
    
    # Get signals from custom strategy
    signals = custom_etf_strategy.get_signals(etf_market_data)
    
    if signals:
        print(f"🎯 Found {len(signals)} Trading Signals:")
        print("-" * 70)
        
        for i, signal in enumerate(signals, 1):
            urgency_emoji = {"HIGH": "🔥", "MEDIUM": "⚡", "LOW": "📝"}
            action_emoji = {"BUY": "🛒", "SELL": "💰", "ALERT": "🚨"}
            
            print(f"{i}. {action_emoji.get(signal.action, '📊')} {signal.action} {signal.symbol}")
            print(f"   Price: ₹{signal.current_price:.2f} | Yesterday: ₹{signal.yesterday_close:.2f}")
            print(f"   Order Type: {signal.order_type.value} | Urgency: {urgency_emoji.get(signal.urgency, '')} {signal.urgency}")
            print(f"   Reason: {signal.reason}")
            print()
        
        # Simulate processing signals
        print("⚡ Processing Signals...")
        print("-" * 50)
        
        custom_etf_strategy.process_signals(signals)
        
        # Show position summary
        summary = custom_etf_strategy.get_position_summary()
        
        if summary['total_positions'] > 0:
            print(f"\n💼 Open Positions Summary:")
            print("-" * 50)
            print(f"Total Positions: {summary['total_positions']}")
            print(f"Total Invested: ₹{summary['total_invested']:,.0f}")
            print()
            
            for symbol, position in summary['positions'].items():
                print(f"{symbol:12s}: ₹{position['entry_price']:7.2f} x {position['quantity']:4d} = ₹{position['invested']:8,.0f}")
                print(f"             Target: ₹{position['target']:7.2f} | Alert: ₹{position['alert']:7.2f} | Type: {position['order_type']}")
                print()
        
    else:
        print("📝 No trading signals found with current market conditions")
        print("💡 Strategy is waiting for:")
        print("   • 1%+ price dips for new buy opportunities")
        print("   • 3% profits for existing positions to sell") 
        print("   • 5% losses for alert notifications")

def simulate_multi_day_trading():
    """Simulate strategy over multiple days"""
    
    print(f"\n📅 MULTI-DAY TRADING SIMULATION")
    print("=" * 70)
    
    # Simulate 3 days of trading
    for day in range(1, 4):
        print(f"\n🌅 Day {day} Trading Session")
        print("-" * 40)
        
        # Generate fresh data for this day
        etf_data = {}
        for symbol in ['NIFTYBEES', 'GOLDBEES', 'BANKBEES']:
            etf_data[symbol] = generate_realistic_etf_data_with_dips(symbol, days=5)
        
        signals = custom_etf_strategy.get_signals(etf_data)
        
        if signals:
            print(f"Found {len(signals)} signals on Day {day}")
            for signal in signals[:3]:  # Show top 3
                print(f"  • {signal.action} {signal.symbol} @ ₹{signal.current_price:.2f}")
            
            # Process signals
            custom_etf_strategy.process_signals(signals)
        else:
            print(f"No signals on Day {day}")
        
        # Show daily summary
        summary = custom_etf_strategy.get_position_summary()
        print(f"End of Day {day}: {summary['total_positions']} positions, ₹{summary['total_invested']:,.0f} invested")

def display_strategy_guide():
    """Display strategy usage guide"""
    
    print(f"\n📚 CUSTOM STRATEGY USAGE GUIDE")
    print("=" * 70)
    print("""
🎯 HOW THE STRATEGY WORKS:

1. 📊 MARKET SCANNING:
   • Monitors your ETF list every minute during market hours
   • Compares current price with yesterday's closing price
   • Identifies dip opportunities and profit targets

2. 🛒 BUY SIGNALS:
   • Triggers when ETF drops 1%+ from yesterday's close
   • Prefers MTF orders (4x leverage) when margin available
   • Falls back to CNC orders if MTF not available
   • Only one position per ETF at a time

3. 💰 SELL SIGNALS:
   • Automatically sells when profit reaches 3%
   • Uses same order type as original buy order
   • Closes position completely

4. 🚨 LOSS ALERTS:
   • Sends alert when loss reaches 5%
   • Doesn't auto-sell, gives you decision control
   • Reminds you to review the position

🔧 CUSTOMIZATION OPTIONS:

In config.ini [TRADING] section:
• BUY_DIP_PERCENT = 1.0        (1% dip to trigger buy)
• SELL_TARGET_PERCENT = 3.0    (3% profit to trigger sell)
• LOSS_ALERT_PERCENT = 5.0     (5% loss to trigger alert)
• MTF_FIRST_PRIORITY = true    (Try MTF first, CNC fallback)
• ONE_POSITION_PER_ETF = true  (Prevent multiple positions)

🚀 TO START USING:

1. python custom_strategy_demo.py  # Test with demo data
2. python main.py start            # Start live trading
3. python main.py status           # Monitor positions

⚠️ IMPORTANT REMINDERS:

• Strategy works only during market hours (9:15 AM - 3:30 PM)
• Requires sufficient balance for CNC and margin for MTF
• Start with small amounts to test the strategy
• Monitor positions regularly, especially near loss alert levels
• Can be combined with your existing risk management rules
""")

def run_custom_demo():
    """Main demo function"""
    
    print("🎭 CUSTOM ETF STRATEGY DEMO")
    print("=" * 70)
    
    try:
        # Test basic strategy
        test_custom_strategy()
        
        # Simulate multi-day trading
        simulate_multi_day_trading()
        
        # Display guide
        display_strategy_guide()
        
        print(f"\n🎉 CUSTOM STRATEGY DEMO COMPLETE!")
        print("=" * 70)
        print("""
✅ Your Custom Strategy is Ready!

🎯 Strategy Features Tested:
• 1% dip detection and buy signal generation
• 3% profit target and sell signal generation  
• 5% loss alert system
• MTF priority with CNC fallback
• One position per ETF rule

🚀 Next Steps:
1. Review the config.ini settings
2. Adjust percentages if needed
3. Start with demo mode: python main.py start
4. Monitor with: python main.py positions

💡 Pro Tips:
• Start with 2-3 ETFs to test
• Monitor during volatile market days
• Keep some cash for additional opportunities
• Review performance weekly

Happy Trading! 🎯📈💰
""")
        
    except Exception as e:
        print(f"❌ Error in custom demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_custom_demo()
