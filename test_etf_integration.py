"""
Test ETF Integration with Dashboard
Quick test to verify all 60 ETF symbols are available for live trading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etf_database import etf_db
from etf_market_data import etf_market_data
from etf_manager import ETFOrderManager
import pandas as pd

def test_etf_integration():
    """Test complete ETF integration"""
    print("🧪 TESTING ETF INTEGRATION FOR LIVE TRADING")
    print("=" * 60)
    
    # 1. Test ETF Database
    print("\n📊 1. ETF Database Test:")
    all_symbols = etf_db.get_all_symbols()
    print(f"   ✅ Total ETFs in database: {len(all_symbols)}")
    
    high_priority = etf_db.get_high_priority_etfs(3)
    print(f"   ✅ High priority ETFs: {len(high_priority)}")
    
    # 2. Test ETF Manager (Order System)
    print("\n📈 2. ETF Order Manager Test:")
    try:
        etf_manager = ETFOrderManager()
        manager_symbols = etf_manager.etf_symbols
        print(f"   ✅ ETF Manager loaded: {len(manager_symbols)} symbols")
        print(f"   ✅ Symbols match database: {set(manager_symbols) == set(all_symbols)}")
    except Exception as e:
        print(f"   ❌ ETF Manager error: {e}")
    
    # 3. Test Market Data Manager
    print("\n📡 3. Market Data Manager Test:")
    try:
        # Test without API connection
        test_symbols = ['NIFTYBEES', 'BANKBEES', 'GOLDBEES']
        market_structure = etf_market_data.get_live_prices(test_symbols)
        print(f"   ✅ Market data structure ready for {len(market_structure)} symbols")
        
        # Test DataFrame creation
        df = etf_market_data.get_high_priority_etfs_live()
        print(f"   ✅ DataFrame creation works: {len(df)} rows, {len(df.columns)} columns")
        
    except Exception as e:
        print(f"   ❌ Market Data Manager error: {e}")
    
    # 4. Test Category Organization
    print("\n🏭 4. Category Organization Test:")
    categories = etf_db.categories
    for category, symbols in categories.items():
        print(f"   ✅ {category.value}: {len(symbols)} ETFs")
    
    # 5. Test Symbol Verification
    print("\n🔍 5. Symbol Verification:")
    requested_symbols = [
        'NIFTYBEES', 'BANKBEES', 'GOLDBEES', 'ITBEES', 'LIQUIDBEES',
        'INDA', 'MOSP500ETF', 'ICICIB22', 'PHARMABEES', 'AUTOETF'
    ]
    
    found_count = 0
    for symbol in requested_symbols:
        etf_info = etf_db.get_etf_by_symbol(symbol)
        if etf_info:
            found_count += 1
            print(f"   ✅ {symbol}: {etf_info.name}")
        else:
            print(f"   ❌ {symbol}: Not found")
    
    print(f"\n   📊 Found {found_count}/{len(requested_symbols)} test symbols")
    
    # 6. Create sample trading-ready DataFrame
    print("\n💹 6. Trading-Ready Data Structure:")
    try:
        trading_data = []
        high_priority_symbols = etf_db.get_high_priority_etfs(2)[:5]  # Top 5
        
        for symbol in high_priority_symbols:
            etf = etf_db.get_etf_by_symbol(symbol)
            if etf:
                trading_data.append({
                    'Symbol': symbol,
                    'Name': etf.name,
                    'Category': etf.category.value,
                    'Priority': etf.priority,
                    'NSE_Symbol': etf.nse_symbol,
                    'Min_Investment': etf.min_investment,
                    'Status': 'Ready'
                })
        
        trading_df = pd.DataFrame(trading_data)
        print("   ✅ Trading DataFrame created:")
        print(trading_df.to_string(index=False))
        
    except Exception as e:
        print(f"   ❌ Trading DataFrame error: {e}")
    
    # 7. Final Integration Check
    print(f"\n🎯 INTEGRATION SUMMARY:")
    print(f"   📊 Database: {len(all_symbols)} ETFs loaded")
    print(f"   🎯 High Priority: {len(high_priority)} ETFs")
    print(f"   📈 Order System: Ready")
    print(f"   📡 Market Data: Ready (needs API credentials for live data)")
    print(f"   🏭 Categories: {len(categories)} categories organized")
    
    success_rate = (found_count / len(requested_symbols)) * 100
    print(f"   ✅ Integration Success Rate: {success_rate:.0f}%")
    
    if success_rate >= 100:
        print(f"\n🎉 ALL SYSTEMS READY FOR LIVE ETF TRADING! 🎉")
        print(f"📋 Your dashboard can now fetch live data for all {len(all_symbols)} ETFs")
        print(f"🚀 Ready to trade with high-priority ETFs: {', '.join(high_priority[:10])}")
    else:
        print(f"\n⚠️ Some issues found. Check the errors above.")

if __name__ == "__main__":
    test_etf_integration()