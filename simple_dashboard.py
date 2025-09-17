"""
🐢 Turtle Trader Dashboard - Simple & Clean
Professional ETF Trading Interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page setup
st.set_page_config(
    page_title="🐢 Turtle Trader Dashboard",
    page_icon="🐢",
    layout="wide"
)

# Initialize session state
if 'trading_active' not in st.session_state:
    st.session_state.trading_active = False

# Custom CSS
st.markdown("""
<style>
    .big-font { font-size: 2.5rem !important; color: #1e88e5; text-align: center; }
    .status-on { color: #4caf50; font-weight: bold; }
    .status-off { color: #f44336; font-weight: bold; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 10px; color: white; text-align: center; 
    }
</style>
""", unsafe_allow_html=True)

def main_header():
    """Display main header"""
    st.markdown('<p class="big-font">🐢 Turtle Trader Dashboard</p>', unsafe_allow_html=True)
    
    status = "🟢 ACTIVE" if st.session_state.trading_active else "🔴 INACTIVE"
    st.markdown(f"<div style='text-align: center; font-size: 1.2rem;'>{status}</div>", unsafe_allow_html=True)

def control_panel():
    """Sidebar control panel"""
    st.sidebar.title("🎛️ Control Panel")
    
    if st.sidebar.button("▶️ START SYSTEM", key="start_btn"):
        st.session_state.trading_active = True
        st.sidebar.success("System Started!")
    
    if st.sidebar.button("⏹️ STOP SYSTEM", key="stop_btn"):
        st.session_state.trading_active = False
        st.sidebar.error("System Stopped!")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔴 EMERGENCY STOP", key="emergency_btn"):
        st.sidebar.warning("Emergency stop activated!")
    
    if st.sidebar.button("📊 REFRESH", key="refresh_btn"):
        st.rerun()

def key_metrics():
    """Display key metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💰 Capital", "₹10,00,000")
    
    with col2:
        st.metric("📈 P&L", "₹1,185", "+1.2%")
    
    with col3:
        st.metric("💼 Invested", "₹89,406")
    
    with col4:
        st.metric("💵 Available", "₹9,10,594")
    
    with col5:
        st.metric("📋 Positions", "3")

def positions_display():
    """Display current positions"""
    st.subheader("💼 Current Positions")
    
    # Sample data
    positions_data = {
        'Symbol': ['NIFTYBEES', 'GOLDBEES', 'BANKBEES'],
        'Quantity': [150, 650, 70],
        'Entry Price': ['₹185.50', '₹45.80', '₹420.00'],
        'Current Price': ['₹191.20', '₹44.95', '₹432.60'],
        'P&L': ['₹855', '₹-552', '₹882'],
        'P&L %': ['+3.07%', '-1.86%', '+3.00%'],
        'Type': ['MTF', 'CNC', 'MTF']
    }
    
    df = pd.DataFrame(positions_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Close NIFTYBEES", key="close_nifty"):
            st.success("Closing NIFTYBEES position")
    
    with col2:
        if st.button("🔄 Close GOLDBEES", key="close_gold"):
            st.success("Closing GOLDBEES position")
    
    with col3:
        if st.button("🔄 Close BANKBEES", key="close_bank"):
            st.success("Closing BANKBEES position")

def price_charts():
    """Display price charts"""
    st.subheader("📈 ETF Price Charts")
    
    # Generate sample data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # NIFTYBEES chart
        prices1 = []
        current = 185
        for _ in dates:
            current *= (1 + np.random.normal(0, 0.015))
            prices1.append(current)
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=dates, y=prices1, mode='lines', name='NIFTYBEES'))
        fig1.update_layout(title="NIFTYBEES - 30 Day Chart", height=300)
        st.plotly_chart(fig1, use_container_width=True)
        
        # GOLDBEES chart
        prices2 = []
        current = 45
        for _ in dates:
            current *= (1 + np.random.normal(0, 0.012))
            prices2.append(current)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dates, y=prices2, mode='lines', name='GOLDBEES', line=dict(color='gold')))
        fig2.update_layout(title="GOLDBEES - 30 Day Chart", height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # BANKBEES chart
        prices3 = []
        current = 420
        for _ in dates:
            current *= (1 + np.random.normal(0, 0.018))
            prices3.append(current)
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=dates, y=prices3, mode='lines', name='BANKBEES', line=dict(color='blue')))
        fig3.update_layout(title="BANKBEES - 30 Day Chart", height=300)
        st.plotly_chart(fig3, use_container_width=True)
        
        # P&L Chart
        pnl_data = np.random.normal(100, 300, len(dates)).cumsum()
        
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=dates, y=pnl_data, mode='lines', name='P&L', line=dict(color='green')))
        fig4.update_layout(title="Cumulative P&L", height=300)
        st.plotly_chart(fig4, use_container_width=True)

def strategy_settings():
    """Strategy configuration"""
    st.subheader("⚙️ Strategy Settings")
    
    with st.expander("🎯 Custom ETF Strategy Settings", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buy_dip = st.slider("📉 Buy Dip %", 0.5, 5.0, 1.0, 0.1, key="buy_dip_slider")
        
        with col2:
            sell_target = st.slider("📈 Sell Target %", 1.0, 10.0, 3.0, 0.5, key="sell_target_slider")
        
        with col3:
            loss_alert = st.slider("🚨 Loss Alert %", 3.0, 15.0, 5.0, 0.5, key="loss_alert_slider")
        
        col4, col5 = st.columns(2)
        
        with col4:
            mtf_priority = st.checkbox("🎯 MTF Priority", value=True, key="mtf_check")
        
        with col5:
            demo_mode = st.checkbox("🧪 Demo Mode", value=True, key="demo_check")
        
        # ETF Selection
        st.markdown("#### 📊 ETF Selection")
        etfs = st.multiselect(
            "Select ETFs to Trade",
            ['NIFTYBEES', 'GOLDBEES', 'BANKBEES', 'JUNIORBEES', 'LIQUIDBEES', 'ITBEES'],
            default=['NIFTYBEES', 'GOLDBEES', 'BANKBEES'],
            key="etf_selection"
        )
        
        # Capital Management
        col6, col7 = st.columns(2)
        
        with col6:
            capital = st.number_input("💰 Total Capital", 100000, 10000000, 1000000, 50000, key="capital_input")
        
        with col7:
            max_position = st.slider("📊 Max Position %", 5, 25, 15, key="max_pos_slider")
        
        if st.button("💾 Save Settings", key="save_settings"):
            st.success("✅ Settings saved!")
            st.info(f"""
            **Current Settings:**
            - Buy Dip: {buy_dip}%
            - Sell Target: {sell_target}%
            - Loss Alert: {loss_alert}%
            - MTF Priority: {mtf_priority}
            - Demo Mode: {demo_mode}
            - Capital: ₹{capital:,}
            - Active ETFs: {', '.join(etfs)}
            """)

def recent_alerts():
    """Display recent alerts"""
    st.subheader("🚨 Recent Alerts")
    
    alerts = [
        "🔴 GOLDBEES: 5.2% loss alert - Current: ₹44.95",
        "🟢 BANKBEES: 3.0% profit target reached - SOLD at ₹432.60", 
        "🟡 NIFTYBEES: 1.8% dip detected - BUY order placed",
        "🔵 System started at 14:35:22"
    ]
    
    for alert in alerts:
        st.info(alert)

def orders_history():
    """Display orders history"""
    st.subheader("📋 Recent Orders")
    
    orders_data = {
        'Time': ['14:35:22', '13:45:30', '12:30:15', '11:20:45'],
        'Symbol': ['NIFTYBEES', 'GOLDBEES', 'BANKBEES', 'ITBEES'],
        'Action': ['BUY', 'BUY', 'SELL', 'BUY'],
        'Quantity': [150, 650, 70, 100],
        'Price': ['₹185.50', '₹45.80', '₹432.60', '₹290.50'],
        'Status': ['✅ COMPLETED', '✅ COMPLETED', '✅ COMPLETED', '⏳ PENDING']
    }
    
    df_orders = pd.DataFrame(orders_data)
    st.dataframe(df_orders, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Orders", key="export_orders"):
            st.success("Orders exported successfully!")
    
    with col2:
        if st.button("📧 Email Report", key="email_report"):
            st.success("Report sent to your email!")

def main():
    """Main dashboard function"""
    
    # Header
    main_header()
    
    # Control panel
    control_panel()
    
    # Key metrics
    key_metrics()
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "💼 Positions", 
        "📈 Charts", 
        "⚙️ Settings", 
        "📋 Orders"
    ])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            positions_display()
        
        with col2:
            recent_alerts()
    
    with tab2:
        positions_display()
        
        # Portfolio pie chart
        st.subheader("📊 Portfolio Distribution")
        
        labels = ['NIFTYBEES', 'GOLDBEES', 'BANKBEES']
        values = [27825, 29770, 29400]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(title="Current Portfolio Allocation")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        price_charts()
    
    with tab4:
        strategy_settings()
    
    with tab5:
        orders_history()
    
    # Footer
    st.markdown("---")
    st.markdown("🐢 **Turtle Trader Dashboard** | Your Custom ETF Trading System")
    
    # Auto-refresh when active
    if st.session_state.trading_active:
        if st.button("🔄 Auto-refresh is ON", key="auto_refresh"):
            pass

if __name__ == "__main__":
    main()
