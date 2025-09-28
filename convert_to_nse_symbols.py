#!/usr/bin/env python3
"""
🔄 NSE SYMBOL CONVERTER
====================

Script to add .NS suffix to all ETF symbols for NSE compatibility.
Converts: NIFTYBEES → NIFTYBEES.NS
"""

import re

def convert_etf_symbols_to_nse():
    """Convert all ETF symbols to NSE format by adding .NS suffix"""
    
    file_path = "/Users/rubeenakhan/Downloads/Turtel trader/etf_universe_config.py"
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all ETF symbol definitions
    symbol_pattern = r"    '([A-Z0-9]+)': \{"
    
    # Find all matches
    matches = re.findall(symbol_pattern, content)
    
    print("🔍 Found ETF symbols to convert:")
    for i, symbol in enumerate(matches, 1):
        print(f"   {i:2d}. {symbol} → {symbol}.NS")
    
    print(f"\\n📊 Total symbols to update: {len(matches)}")
    
    # Replace each symbol with .NS version
    updated_content = content
    conversion_count = 0
    
    for symbol in matches:
        old_pattern = f"    '{symbol}': {{"
        new_pattern = f"    '{symbol}.NS': {{"
        
        if old_pattern in updated_content:
            updated_content = updated_content.replace(old_pattern, new_pattern)
            conversion_count += 1
            print(f"   ✅ {symbol} → {symbol}.NS")
    
    # Write the updated content back
    with open(file_path, 'w') as f:
        f.write(updated_content)
    
    print(f"\\n🎉 SUCCESS: Updated {conversion_count} ETF symbols to NSE format!")
    print(f"📝 File updated: {file_path}")
    
    return conversion_count

if __name__ == "__main__":
    print("🔄 Converting ETF symbols to NSE format...")
    print("=" * 50)
    
    count = convert_etf_symbols_to_nse()
    
    print(f"\\n✅ COMPLETED: {count} symbols now have .NS suffix")
    print("🎯 All ETF symbols are now NSE-compatible!")
    print("\\n📋 Examples:")
    print("   • NIFTYBEES → NIFTYBEES.NS")
    print("   • GOLDBEES → GOLDBEES.NS") 
    print("   • BANKBEES → BANKBEES.NS")