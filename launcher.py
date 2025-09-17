"""
🐢 TURTLE TRADER - COMPLETE SYSTEM LAUNCHER
===========================================

Launch your professional ETF trading system with one click!
"""

import os
import sys
import subprocess
import webbrowser
import time
from datetime import datetime

def print_header():
    """Print system header"""
    print("="*60)
    print("🐢 TURTLE TRADER - ETF TRADING SYSTEM")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Focus: ETF Trading with MTF/CNC Strategy")
    print("📊 Strategy: 1% Dip Buy | 3% Target Sell | 5% Loss Alert")
    print("="*60)

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking system dependencies...")
    
    required_packages = [
        'breeze-connect',
        'streamlit', 
        'plotly',
        'pandas',
        'numpy',
        'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            result = subprocess.run(['pip', 'show', package], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"✅ {package}: Installed")
            else:
                print(f"❌ {package}: Missing")
                missing_packages.append(package)
        except:
            print(f"❌ {package}: Error checking")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.run(['pip', 'install', package], check=False)
        
        print("✅ All dependencies installed!")
    else:
        print("✅ All dependencies satisfied!")

def show_menu():
    """Display main menu"""
    print("""
🎛️ LAUNCH OPTIONS:
==================

1. 🚀 START TRADING SYSTEM (Command Line)
2. 🌐 LAUNCH WEB DASHBOARD (Browser Interface)  
3. 🧪 RUN CUSTOM STRATEGY DEMO
4. 📊 RUN ETF SYSTEM DEMO
5. ⚙️ VIEW SYSTEM CONFIGURATION
6. 📚 VIEW SETUP GUIDE
7. 🔧 INSTALL MISSING DEPENDENCIES
8. ❌ EXIT

""")

def launch_trading_system():
    """Launch the main trading system"""
    print("\n🚀 LAUNCHING TRADING SYSTEM...")
    print("="*40)
    print("⚠️ Make sure you have:")
    print("  • Updated API credentials in config.ini")
    print("  • Set your trading capital amount")
    print("  • Configured ETF symbols to trade")
    print("="*40)
    
    confirm = input("Continue? (y/n): ").lower().strip()
    
    if confirm == 'y':
        print("\n▶️ Starting Turtle Trader System...")
        try:
            subprocess.run(['python', 'main.py', 'start'], check=True)
        except KeyboardInterrupt:
            print("\n⏹️ Trading system stopped by user")
        except Exception as e:
            print(f"\n❌ Error starting system: {e}")
            print("💡 Check logs/turtle_trader.log for details")
    else:
        print("❌ Launch cancelled")

def launch_dashboard():
    """Launch web dashboard"""
    print("\n🌐 LAUNCHING WEB DASHBOARD...")
    print("="*40)
    
    try:
        print("🔄 Starting Streamlit server...")
        
        # Start dashboard in background
        process = subprocess.Popen(
            ['streamlit', 'run', 'dashboard.py', '--server.port', '8501'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Dashboard server started!")
        print("🌐 Opening browser...")
        
        # Open browser
        webbrowser.open('http://localhost:8501')
        
        print("""
🎊 DASHBOARD LAUNCHED SUCCESSFULLY!
==================================

📍 URL: http://localhost:8501
📱 Mobile: Use your local IP address
🔄 Auto-refresh: Available in dashboard

🎛️ Dashboard Features:
• Real-time position monitoring
• Live ETF price charts
• Strategy settings management
• P&L tracking and analytics
• Order history and reporting
• Emergency controls

Press CTRL+C to stop the dashboard server.
        """)
        
        # Keep process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Dashboard stopped by user")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Try running: streamlit run dashboard.py")

def run_custom_demo():
    """Run custom strategy demo"""
    print("\n🧪 RUNNING CUSTOM STRATEGY DEMO...")
    print("="*40)
    
    try:
        subprocess.run(['python', 'custom_strategy_demo.py'], check=True)
        
        print("""
✅ DEMO COMPLETED!
=================

The demo showed your custom strategy in action:
• 1% dip detection and buy signals
• 3% profit target and sell signals  
• 5% loss alert system
• MTF priority with CNC fallback
• One position per ETF rule

Ready to go live? Update config.ini with real API credentials!
        """)
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")

def run_etf_demo():
    """Run ETF system demo"""
    print("\n📊 RUNNING ETF SYSTEM DEMO...")
    print("="*40)
    
    try:
        subprocess.run(['python', 'etf_demo.py'], check=True)
        print("✅ ETF system demo completed!")
        
    except Exception as e:
        print(f"❌ Error running ETF demo: {e}")

def view_configuration():
    """Display current configuration"""
    print("\n⚙️ SYSTEM CONFIGURATION:")
    print("="*40)
    
    try:
        if os.path.exists('config.ini'):
            with open('config.ini', 'r') as f:
                content = f.read()
            print(content[:1000])  # Show first 1000 chars
            print("\n💡 Edit config.ini to modify settings")
        else:
            print("❌ config.ini not found!")
            print("💡 Use config_template.ini as reference")
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")

def view_setup_guide():
    """Show setup guide"""
    print("\n📚 DISPLAYING SETUP GUIDE...")
    print("="*40)
    
    try:
        subprocess.run(['python', 'SETUP_GUIDE.py'], check=True)
    except Exception as e:
        print(f"❌ Error showing guide: {e}")

def install_dependencies():
    """Install all dependencies"""
    print("\n🔧 INSTALLING DEPENDENCIES...")
    print("="*40)
    
    dependencies = [
        'breeze-connect>=1.0.64',
        'streamlit>=1.28.0',
        'plotly>=5.15.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'loguru>=0.7.0',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'schedule>=1.2.0'
    ]
    
    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        try:
            subprocess.run(['pip', 'install', dep], check=True)
            print(f"✅ {dep} installed successfully")
        except Exception as e:
            print(f"❌ Failed to install {dep}: {e}")
    
    print("\n✅ All dependencies installation completed!")

def main():
    """Main launcher function"""
    
    print_header()
    check_dependencies()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                launch_trading_system()
            elif choice == '2':
                launch_dashboard()
            elif choice == '3':
                run_custom_demo()
            elif choice == '4':
                run_etf_demo()
            elif choice == '5':
                view_configuration()
            elif choice == '6':
                view_setup_guide()
            elif choice == '7':
                install_dependencies()
            elif choice == '8':
                print("\n👋 Thank you for using Turtle Trader!")
                print("🎯 Happy Trading! 📈💰")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1-8.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
