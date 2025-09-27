"""
🎯 TURTLE TRADER - STREAMLIT CLOUD VERSION
=========================================

Cloud-compatible version of the Turtle Trading dashboard
Handles secrets management and demo mode for cloud deployment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Configure page
st.set_page_config(
    page_title="🐢 Turtle Trader Dashboard",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_environment():
    """Check if running locally or in cloud"""
    return "STREAMLIT_SHARING" in os.environ or "STREAMLIT_CLOUD" in os.environ

def load_demo_data():
    """Load demo data for cloud deployment"""
    # Generate sample ETF data
    etfs = [
        "NIFTYBEES", "JUNIORBEES", "BANKBEES", "GOLDBEES", "LIQUIDBEES",
        "ICICINXT50", "HDFCNIFTY", "SBIETF", "KOTAKNIFTY", "AXISBANK"
    ]
    
    data = []
    for etf in etfs:
        price = np.random.uniform(100, 500)
        change = np.random.uniform(-5, 5)
        data.append({
            'ETF': etf,
            'Current Price': f"₹{price:.2f}",
            'Change': f"{change:+.2f}%",
            'Volume': f"{np.random.randint(10000, 100000):,}",
            'Market Cap': f"₹{np.random.randint(1000, 10000):,}Cr"
        })
    
    return pd.DataFrame(data)

def main():
    """Main dashboard application"""
    
    # Header
    st.title("🐢 Turtle Trader Dashboard")
    st.markdown("---")
    
    # Check environment
    is_cloud = check_environment()
    
    if is_cloud:
        st.warning("🌩️ **Cloud Demo Mode** - This is a demonstration version running on Streamlit Cloud")
    else:
        st.success("🏠 **Local Mode** - Full functionality with live API connections")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Backtesting", "Strategy", "Settings"]
        )
    
    # Main content based on page selection
    if page == "Dashboard":
        render_dashboard_page(is_cloud)
    elif page == "Backtesting":
        render_backtesting_page(is_cloud)
    elif page == "Strategy":
        render_strategy_page()
    else:
        render_settings_page(is_cloud)

def render_dashboard_page(is_cloud):
    """Render main dashboard page"""
    st.header("📊 Market Overview")
    
    if is_cloud:
        # Demo mode
        st.info("📋 **Demo Data** - Real trading requires local deployment with API keys")
        
        # Sample metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Portfolio Value", "₹1,04,947", "+2.3%")
        with col2:
            st.metric("Available Cash", "₹73,463", "-1.2%")
        with col3:
            st.metric("Active Trades", "3", "+1")
        with col4:
            st.metric("Daily P&L", "₹+2,847", "+0.8%")
        
        # Demo ETF table
        df = load_demo_data()
        st.subheader("🏷️ ETF Watchlist")
        st.dataframe(df, use_container_width=True)
        
    else:
        # Try to load real data
        try:
            from trading_dashboard import TradingDashboard
            dashboard = TradingDashboard()
            dashboard.render_main_dashboard()
        except Exception as e:
            st.error(f"❌ Failed to load real data: {str(e)}")
            st.info("💡 Please ensure API credentials are configured in local config.ini")

def render_backtesting_page(is_cloud):
    """Render backtesting page"""
    st.header("📈 Strategy Backtesting")
    
    # Parameters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2023, 1, 1))
        initial_capital = st.number_input("Initial Capital (₹)", value=100000, step=10000)
    
    with col2:
        end_date = st.date_input("End Date", datetime.now())
        risk_per_trade = st.slider("Risk per Trade (%)", 1, 5, 2)
    
    if st.button("🚀 Run Backtest"):
        with st.spinner("Running backtest..."):
            # Generate sample backtest results
            dates = pd.date_range(start_date, end_date, freq='D')
            returns = np.random.normal(0.001, 0.02, len(dates))
            cumulative_returns = (1 + returns).cumprod()
            portfolio_value = initial_capital * cumulative_returns
            
            # Create chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_value,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#00ff88', width=2)
            ))
            
            fig.update_layout(
                title="Portfolio Performance",
                xaxis_title="Date",
                yaxis_title="Portfolio Value (₹)",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Return", f"{(cumulative_returns[-1]-1)*100:.2f}%")
            with col2:
                st.metric("Max Drawdown", f"{np.random.uniform(5, 15):.2f}%")
            with col3:
                st.metric("Sharpe Ratio", f"{np.random.uniform(0.5, 2.0):.2f}")

def render_strategy_page():
    """Render strategy configuration page"""
    st.header("🎯 Trading Strategy")
    
    st.subheader("Turtle Trading Rules")
    st.markdown("""
    **Entry Rules:**
    - Buy when price breaks above 20-day high
    - Position size based on Average True Range (ATR)
    - Maximum 4 units per market
    
    **Exit Rules:**
    - Exit when price breaks below 10-day low
    - Stop loss at 2 ATR from entry price
    - Take partial profits at 1:2 risk-reward ratio
    
    **Risk Management:**
    - Maximum 2% risk per trade
    - Position sizing based on volatility
    - Dynamic capital allocation
    """)

def render_settings_page(is_cloud):
    """Render settings page"""
    st.header("⚙️ Settings")
    
    if is_cloud:
        st.info("🌩️ **Cloud Deployment Settings**")
        st.markdown("""
        **For live trading, deploy locally with:**
        1. Clone the repository
        2. Configure `config.ini` with your API keys
        3. Run: `streamlit run trading_dashboard.py`
        
        **Required API Keys:**
        - Kite Connect API Key
        - Kite Connect API Secret
        - Session Token
        """)
        
        # Show secrets configuration
        st.subheader("Streamlit Secrets Configuration")
        st.code("""
# Add to Streamlit Cloud secrets:
API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here"
SESSION_TOKEN = "your_session_token_here"
BASE_URL = "https://api.kite.trade"
USERNAME = "your_username"
PASSWORD = "your_password"
        """)
    else:
        st.success("✅ **Local Deployment** - Full configuration available")
        
        # Configuration options
        st.subheader("Trading Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Capital Allocation (%)", 70, 90, 70)
            st.number_input("Risk per Trade (%)", 1, 5, 2)
        
        with col2:
            st.number_input("Max Positions", 5, 20, 10)
            st.selectbox("Trading Mode", ["Paper", "Live"])

if __name__ == "__main__":
    main()