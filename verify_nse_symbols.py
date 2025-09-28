#!/usr/bin/env python3
"""
✅ NSE SYMBOL VERIFICATION
========================

Script to verify that all ETF symbols are already in NSE format (.NS suffix).
"""

import re
from etf_universe_config import ETF_UNIVERSE

def verify_nse_symbols():
    """Verify that all ETF symbols have .NS suffix"""
    
    print("✅ NSE Symbol Verification")
    print("=" * 50)
    
    all_symbols = list(ETF_UNIVERSE.keys())
    nse_symbols = [s for s in all_symbols if s.endswith('.NS')]
    non_nse_symbols = [s for s in all_symbols if not s.endswith('.NS')]
    
    print(f"📊 Total ETF Symbols: {len(all_symbols)}")
    print(f"🔗 NSE Format (.NS): {len(nse_symbols)}")
    print(f"❌ Non-NSE Format: {len(non_nse_symbols)}")
    
    if len(non_nse_symbols) == 0:
        print(f"\\n🎉 SUCCESS: All {len(all_symbols)} symbols are already in NSE format!")
        print("\\n📋 Sample NSE symbols:")
        for i, symbol in enumerate(nse_symbols[:10], 1):
            print(f"   {i:2d}. {symbol}")
        if len(nse_symbols) > 10:
            print(f"   ... and {len(nse_symbols) - 10} more")
    else:
        print(f"\\n⚠️ Found {len(non_nse_symbols)} symbols without .NS suffix:")
        for symbol in non_nse_symbols:
            print(f"   • {symbol} (needs → {symbol}.NS)")
    
    # Check for common ETF patterns
    common_etfs = ['NIFTYBEES.NS', 'GOLDBEES.NS', 'BANKBEES.NS', 'LIQUIDBEES.NS']
    found_common = [etf for etf in common_etfs if etf in all_symbols]
    
    print(f"\\n🎯 Common ETFs Status:")
    for etf in common_etfs:
        status = "✅ Found" if etf in all_symbols else "❌ Missing"
        print(f"   • {etf}: {status}")
    
    return len(non_nse_symbols) == 0

if __name__ == "__main__":
    success = verify_nse_symbols()
    
    print(f"\\n{'=' * 50}")
    if success:
        print("🎊 ALL SYMBOLS ARE NSE-COMPATIBLE!")
        print("✅ Your ETF universe is properly configured")
        print("🎯 Ready for Zerodha Kite API integration")
    else:
        print("⚠️ Some symbols need .NS suffix conversion")
        print("🔧 Run conversion script to fix")
    
    print(f"\\n📈 Dashboard: http://localhost:8504")
    print("📊 All backtesting will use NSE-format symbols")