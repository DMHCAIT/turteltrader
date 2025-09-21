"""
🎯 DEPENDENCY CHECK & INSTALLATION VERIFICATION
==============================================

Run this script to verify all dependencies are correctly installed
"""

import sys
import subprocess
from pathlib import Path

def check_import(module_name, description=""):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description} - Error: {e}")
        return False

def main():
    """Check all required dependencies"""
    print("🐢 TURTLE TRADER - DEPENDENCY CHECK")
    print("=" * 50)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python Version: {python_version}")
    
    if sys.version_info.major < 3 or sys.version_info.minor < 8:
        print("⚠️  Warning: Python 3.8+ recommended")
    
    print("\n📦 Checking Core Dependencies:")
    print("-" * 30)
    
    # Core dependencies
    dependencies = [
        ("streamlit", "Web dashboard framework"),
        ("pandas", "Data manipulation library"),
        ("numpy", "Numerical computing"),
        ("requests", "HTTP library for API calls"),
        ("plotly", "Interactive plotting"),
        ("yfinance", "Financial data provider"),
        ("loguru", "Advanced logging"),
        ("breeze_connect", "ICICI Breeze API")
    ]
    
    all_good = True
    for module, desc in dependencies:
        if not check_import(module, desc):
            all_good = False
    
    print("\n🔧 Checking Project Modules:")
    print("-" * 30)
    
    # Project modules
    project_modules = [
        ("breeze_api_client", "Breeze API client"),
        ("trading_dashboard", "Main dashboard"),
        ("portfolio_manager", "Portfolio management"),
        ("custom_strategy", "Trading strategy"),
        ("data_manager", "Market data manager"),
        ("live_order_executor", "Order execution"),
        ("dynamic_capital_allocator", "Capital allocation"),
        ("real_account_balance", "Real balance integration")
    ]
    
    for module, desc in project_modules:
        try:
            check_import(module, desc)
        except Exception as e:
            print(f"⚠️  {module} - {desc} - Warning: {e}")
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("\n🚀 Ready to launch dashboard:")
        print("   ./run_dashboard.sh")
        print("   OR")
        print("   streamlit run app.py")
    else:
        print("❌ Some dependencies missing. Run:")
        print("   pip install -r requirements.txt")
    
    print("\n💡 Tips:")
    print("   - Use virtual environment for isolation")
    print("   - Update session token daily for live trading")
    print("   - Test in DEMO mode before going live")

if __name__ == "__main__":
    main()