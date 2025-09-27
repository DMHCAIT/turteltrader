"""
🔔 LIVE BUY SIGNAL DEMONSTRATION
===============================

This script shows your turtle trading system's buy signal logic in action.
It demonstrates exactly when buy orders will be triggered based on 
yesterday's closing prices.

Current Status: System is WAITING for 1% dips to trigger buy signals.
"""

import time
from datetime import datetime
from real_time_etf_monitor import RealTimeETFMonitor

def demonstrate_buy_signals():
    """Demonstrate the live buy signal triggering logic"""
    print("🚀 LIVE BUY SIGNAL DEMONSTRATION")
    print("=" * 60)
    
    # Initialize monitor
    monitor = RealTimeETFMonitor()
    monitor.initialize_yesterday_closes()
    
    print(f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📊 Monitoring {len(monitor.yesterday_closes)} ETFs")
    print(f"💰 Account Balance: ₹104,947.30")
    print(f"🎯 Deployable Capital: ₹73,463.11")
    print()
    
    print("🔍 LIVE TRIGGER STATUS CHECK:")
    print("-" * 60)
    
    for symbol, yesterday_close in monitor.yesterday_closes.items():
        # Get current live price
        current_price = monitor.get_live_price(symbol)
        
        if current_price:
            # Calculate price change
            price_change_pct = ((current_price - yesterday_close) / yesterday_close) * 100
            
            # Calculate trigger levels
            trigger_1pct = yesterday_close * 0.99
            trigger_2pct = yesterday_close * 0.98
            
            # Determine status and action
            if price_change_pct <= -1.0:
                status = "🔔 BUY SIGNAL ACTIVE"
                action = "WOULD BUY NOW!"
                urgency = "🚨 IMMEDIATE"
                
                # Calculate position details
                position_value = 73463 * 0.03  # 3% base position
                shares = int(position_value / current_price)
                actual_investment = shares * current_price
                
                action_details = f"Buy {shares} shares = ₹{actual_investment:,.0f}"
                
            elif price_change_pct <= -0.5:
                remaining = abs(-1.0 - price_change_pct)
                status = f"⚠️ CLOSE TO TRIGGER"
                action = f"Need {remaining:.2f}% more drop"
                urgency = "🟡 WATCH CLOSELY"
                action_details = "Monitoring for entry"
                
            else:
                remaining = abs(-1.0 - price_change_pct)
                status = f"📈 MONITORING"
                action = f"Need {remaining:.2f}% drop"
                urgency = "🟢 NORMAL"
                action_details = "Waiting for dip"
            
            print(f"{symbol:12s} | ₹{yesterday_close:7.2f} → ₹{current_price:7.2f} ({price_change_pct:+5.2f}%)")
            print(f"{'':12s} | Status: {status}")
            print(f"{'':12s} | Action: {action}")
            print(f"{'':12s} | Details: {action_details}")
            print(f"{'':12s} | 1% Trigger: ₹{trigger_1pct:.2f} | 2% Trigger: ₹{trigger_2pct:.2f}")
            print("-" * 60)
        
        else:
            print(f"{symbol:12s} | ₹{yesterday_close:7.2f} → ❌ No live price")
            print(f"{'':12s} | Status: 📡 Waiting for market data")
            print("-" * 60)
    
    print("\n💡 HOW THE SYSTEM WORKS:")
    print("1️⃣ System checks prices EVERY 1 SECOND")
    print("2️⃣ When any ETF drops ≥1% from yesterday close:")
    print("   → 🔔 BUY SIGNAL triggers immediately")
    print("   → 💰 Calculates position size (3% of deployable capital)")
    print("   → 📈 Places buy order within seconds")
    print("3️⃣ Tracks position for 3% profit target or 5% loss alert")
    
    print(f"\n⏰ SYSTEM TIMING:")
    print(f"• Check frequency: Every 1 second")
    print(f"• Signal delay: < 5 seconds from trigger")
    print(f"• Duplicate protection: 5 minutes between same ETF signals")
    print(f"• No human intervention needed - fully automated!")
    
    print(f"\n🎯 NEXT ACTIONS NEEDED FOR BUY SIGNALS:")
    any_close = False
    
    for symbol, yesterday_close in monitor.yesterday_closes.items():
        current_price = monitor.get_live_price(symbol)
        if current_price:
            price_change_pct = ((current_price - yesterday_close) / yesterday_close) * 100
            remaining_drop = abs(-1.0 - price_change_pct)
            
            if remaining_drop <= 2.0:  # Within 2% of trigger
                trigger_price = yesterday_close * 0.99
                print(f"   {symbol}: Drop ₹{current_price - trigger_price:.2f} more to ₹{trigger_price:.2f}")
                any_close = True
    
    if not any_close:
        print(f"   All ETFs need significant drops (>1%) to trigger signals")
        print(f"   System will wait patiently for market dips...")
    
    print(f"\n🚀 TO START LIVE MONITORING:")
    print(f"   python enhanced_turtle_trader.py")
    print(f"   (System will execute buy signals automatically when triggered)")


if __name__ == "__main__":
    demonstrate_buy_signals()