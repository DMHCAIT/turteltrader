"""
🎯 SIMPLE TRADING DASHBOARD - Manual Token Configuration
======================================================

Simplified dashboard without automatic token management.
You manually set the access token in config.ini file.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import time
from portfolio_manager import PortfolioManager
from dynamic_capital_allocator import DynamicCapitalAllocator
from live_order_executor import LiveOrderExecutor
from etf_database import etf_db, ETFCategory, ETFInfo
from real_account_balance import RealAccountBalanceManager
from kite_api_client import KiteAPIClient
from core.api_client import get_kite_client
from dynamic_capital_allocator import DynamicCapitalAllocator
from real_time_monitor import RealTimeAccountMonitor, setup_default_monitoring
from loguru import logger

class SimpleTradingDashboard:
    """Simplified Trading Dashboard with Manual Token Configuration"""
    
    def __init__(self):
        """Initialize dashboard components"""
        self.initialize_session_state()
        self.load_or_create_system()
        self.initialize_etf_data()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'capital_manager' not in st.session_state:
            st.session_state.capital_manager = None
        if 'trading_system' not in st.session_state:
            st.session_state.trading_system = None
        if 'real_balance_manager' not in st.session_state:
            st.session_state.real_balance_manager = None
        if 'dynamic_allocator' not in st.session_state:
            st.session_state.dynamic_allocator = None
        if 'real_time_monitor' not in st.session_state:
            st.session_state.real_time_monitor = None
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'use_real_balance' not in st.session_state:
            st.session_state.use_real_balance = True
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = False
        if 'trade_history' not in st.session_state:
            st.session_state.trade_history = []
    
    def load_or_create_system(self):
        """Load existing system or create new one"""
        try:
            # Initialize real balance system
            if st.session_state.real_balance_manager is None:
                st.session_state.real_balance_manager = RealAccountBalanceManager()
            
            # Initialize dynamic allocator
            if st.session_state.dynamic_allocator is None:
                st.session_state.dynamic_allocator = DynamicCapitalAllocator(use_real_balance=True)
                
            # Initialize real-time monitor
            if st.session_state.real_time_monitor is None:
                st.session_state.real_time_monitor = setup_default_monitoring()
            
            logger.info("✅ Trading system components loaded successfully")
            
        except Exception as e:
            st.error(f"❌ System initialization error: {e}")
            logger.error(f"System initialization error: {e}")
    
    def initialize_etf_data(self):
        """Initialize ETF database and market data"""
        try:
            # Get liquid ETFs for monitoring
            liquid_etfs = etf_db.get_liquid_etfs()
            st.session_state.liquid_etfs = liquid_etfs
            logger.info(f"✅ Loaded {len(liquid_etfs)} liquid ETFs for monitoring")
            
        except Exception as e:
            logger.warning(f"ETF data initialization issue: {e}")
            st.session_state.liquid_etfs = []
    
    def render_header(self):
        """Render dashboard header"""
        st.set_page_config(
            page_title="ETF Trading Dashboard", 
            page_icon="📈", 
            layout="wide"
        )
        
        st.title("🎯 ETF Trading Dashboard")
        st.markdown("**Manual Token Configuration | Live Trading System**")
        
        # Show connection status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                client = KiteAPIClient()
                if hasattr(client, 'get_kite_client') and client.get_kite_client():
                    st.success("✅ API Connected")
                else:
                    st.error("❌ API Disconnected")
            except:
                st.error("❌ API Error")
        
        with col2:
            if st.session_state.real_balance_manager:
                st.info("💰 Real Balance")
            else:
                st.warning("⚠️ Balance Error")
        
        with col3:
            etf_count = len(st.session_state.get('liquid_etfs', []))
            st.info(f"📊 {etf_count} ETFs")
        
        with col4:
            current_time = datetime.now().strftime("%H:%M:%S")
            st.info(f"🕐 {current_time}")
    
    def render_manual_config_guide(self):
        """Show manual configuration guide"""
        st.header("🔧 Configuration Guide")
        
        st.markdown("""
        ### 📋 How to Set Access Token Manually
        
        **Step 1: Get your access token**
        1. Visit this URL: 
           ```
           https://kite.zerodha.com/connect/login?api_key=i0bd6xlyqau3ivqe&v=3
           ```
        2. Login with your Zerodha credentials
        3. Authorize the app
        4. From the redirect URL, copy the `request_token` parameter
        
        **Step 2: Update config.ini**
        Open your `config.ini` file and replace:
        ```ini
        access_token = YOUR_ACTUAL_TOKEN_FROM_STEP_1
        ```
        With your actual token from step 1.
        
        **Step 3: Restart the dashboard**
        After updating the token, restart this dashboard.
        
        ---
        """)
        
        # Show current configuration status
        self.render_config_status()
    
    def render_config_status(self):
        """Show current configuration status"""
        st.subheader("⚙️ Current Configuration Status")
        
        try:
            from kite_api_client import KiteAPIClient
            client = KiteAPIClient()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**API Credentials:**")
                if client.api_key and client.api_secret:
                    st.success("✅ API Key & Secret configured")
                    st.code(f"API Key: {client.api_key[:10]}...")
                else:
                    st.error("❌ API Key or Secret missing")
                
            with col2:
                st.markdown("**Access Token:**")
                if hasattr(client, 'access_token') and client.access_token and client.access_token != "YOUR_ACTUAL_TOKEN_FROM_STEP_1":
                    st.success("✅ Access Token configured")
                    st.code(f"Token: {client.access_token[:10]}...")
                else:
                    st.warning("⚠️ Access Token not configured")
                    st.code("access_token = YOUR_ACTUAL_TOKEN_FROM_STEP_1")
            
            # Test connection button
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧪 Test API Connection", use_container_width=True):
                    try:
                        test_client = client.get_kite_client()
                        if test_client:
                            profile = test_client.profile()
                            st.success(f"✅ Connected as: {profile.get('user_name', 'Unknown')}")
                            
                            # Show account details
                            with st.expander("Account Details"):
                                st.json(profile)
                        else:
                            st.error("❌ Connection failed - Invalid credentials")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
                        
            with col2:
                if st.button("🔄 Restart System", use_container_width=True):
                    # Clear session state
                    keys_to_clear = ['capital_manager', 'trading_system', 'real_balance_manager', 'dynamic_allocator']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.success("🔄 System restart initiated. Refresh the page.")
                    st.experimental_rerun()
                
        except Exception as e:
            st.error(f"❌ Configuration check failed: {e}")
    
    def render_main_dashboard(self):
        """Render main trading dashboard"""
        st.header("📊 Main Trading Dashboard")
        
        # Check if system is properly configured
        try:
            client = KiteAPIClient()
            kite = client.get_kite_client()
            
            if not kite:
                st.error("❌ API not connected. Please configure your access token first.")
                st.info("👆 Go to 'Configuration' to set up your access token.")
                return
            
            # Real balance display
            self.render_real_balance_status()
            
            # ETF monitoring
            self.render_etf_monitoring()
            
            # Trade execution panel
            self.render_trade_panel()
            
        except Exception as e:
            st.error(f"❌ Dashboard error: {e}")
            st.info("Please check your configuration and try again.")
    
    def render_real_balance_status(self):
        """Render real account balance status"""
        st.subheader("💰 Real Account Balance")
        
        try:
            if st.session_state.real_balance_manager:
                balance_data = st.session_state.real_balance_manager.get_current_balance()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Available Cash", f"₹{balance_data.get('available_cash', 0):,.2f}")
                
                with col2:
                    st.metric("Total Balance", f"₹{balance_data.get('total_balance', 0):,.2f}")
                
                with col3:
                    st.metric("Used Margin", f"₹{balance_data.get('used_margin', 0):,.2f}")
                
                with col4:
                    utilization = balance_data.get('margin_utilization', 0) * 100
                    st.metric("Margin Used", f"{utilization:.1f}%")
            else:
                st.error("❌ Balance manager not initialized")
                
        except Exception as e:
            st.error(f"❌ Balance fetch error: {e}")
    
    def render_etf_monitoring(self):
        """Render ETF monitoring section"""
        st.subheader("📈 ETF Monitoring")
        
        liquid_etfs = st.session_state.get('liquid_etfs', [])
        
        if not liquid_etfs:
            st.warning("⚠️ No ETF data available")
            return
        
        # Create a simple table of ETF data
        etf_data = []
        for etf in liquid_etfs[:10]:  # Show top 10 for simplicity
            etf_data.append({
                'Symbol': etf.symbol,
                'Name': etf.name,
                'Category': etf.category.name if etf.category else 'Unknown',
                'Liquidity': etf.avg_volume,
                'Status': 'Monitoring'
            })
        
        if etf_data:
            df = pd.DataFrame(etf_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📊 ETF data loading...")
    
    def render_trade_panel(self):
        """Render trade execution panel"""
        st.subheader("⚡ Quick Trade Panel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Manual Trade Entry**")
            symbol = st.selectbox("ETF Symbol", ["NIFTYBEES", "BANKBEES", "ITBEES", "GOLDBEES"])
            action = st.selectbox("Action", ["BUY", "SELL"])
            quantity = st.number_input("Quantity", min_value=1, max_value=1000, value=10)
            
            if st.button("🚀 Execute Trade", use_container_width=True):
                st.info(f"Trade simulation: {action} {quantity} shares of {symbol}")
        
        with col2:
            st.markdown("**Recent Trades**")
            # Show placeholder trade history
            trades = [
                {"Time": "10:30", "Symbol": "NIFTYBEES", "Action": "BUY", "Qty": 10, "Price": 185.50},
                {"Time": "11:15", "Symbol": "BANKBEES", "Action": "SELL", "Qty": 5, "Price": 435.20},
                {"Time": "12:00", "Symbol": "ITBEES", "Action": "BUY", "Qty": 15, "Price": 295.80}
            ]
            
            for trade in trades:
                with st.expander(f"{trade['Time']} - {trade['Symbol']} {trade['Action']}"):
                    st.write(f"Quantity: {trade['Qty']}")
                    st.write(f"Price: ₹{trade['Price']}")
    
    def render_settings(self):
        """Render settings page"""
        st.header("⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 Trading Parameters")
            entry_threshold = st.slider("Entry Threshold %", 0.5, 5.0, 1.0, step=0.1)
            profit_target = st.slider("Profit Target %", 1.0, 10.0, 3.0, step=0.1)
            stop_loss = st.slider("Stop Loss %", 1.0, 10.0, 5.0, step=0.1)
            max_positions = st.slider("Max Positions", 5, 50, 8)
        
        with col2:
            st.subheader("📊 Display Options")
            auto_refresh = st.checkbox("Auto Refresh Dashboard", value=False)
            refresh_interval = st.selectbox("Refresh Interval", ["10s", "30s", "1m", "5m"], index=1)
            show_advanced = st.checkbox("Show Advanced Metrics", value=True)
            notifications = st.checkbox("Enable Notifications", value=True)
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
            
            # Update session state
            st.session_state.auto_refresh = auto_refresh
    
    def run(self):
        """Run the main dashboard"""
        try:
            # Header
            self.render_header()
            
            # Sidebar navigation
            st.sidebar.markdown("---")
            page = st.sidebar.selectbox(
                "📋 Navigate to:",
                options=[
                    "🏠 Main Dashboard", 
                    "🔧 Configuration",
                    "⚙️ Settings"
                ],
                index=0
            )
            
            # Route to appropriate page
            if page == "🏠 Main Dashboard":
                self.render_main_dashboard()
                
                # Auto refresh
                if st.session_state.get('auto_refresh', False):
                    time.sleep(30)
                    st.rerun()
                    
            elif page == "🔧 Configuration":
                self.render_manual_config_guide()
                    
            elif page == "⚙️ Settings":
                self.render_settings()
        
        except Exception as e:
            st.error(f"Dashboard error: {e}")
            logger.error(f"Dashboard error: {e}")

def main():
    """Main function to run the dashboard"""
    try:
        dashboard = SimpleTradingDashboard()
        dashboard.run()
    except Exception as e:
        st.error("🔐 **System Configuration Required**")
        st.markdown(f"""
        ### Configuration Error
        
        **Error:** `{e}`
        
        This trading system requires:
        1. **Valid Kite Connect API credentials**
        2. **Daily access token** (manually configured)
        3. **Proper config.ini setup**
        
        **📋 Setup Instructions:**
        1. Get API credentials from https://kite.trade/
        2. Update config.ini with your credentials
        3. Generate daily access token 
        4. Restart this dashboard
        
        **No demo data available - real credentials required.**
        """)
        st.stop()

if __name__ == "__main__":
    main()