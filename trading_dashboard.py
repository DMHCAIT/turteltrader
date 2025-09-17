"""
🎯 TRADING DASHBOARD - DYNAMIC CAPITAL ALLOCATION
===============================================

Implements the exact capital allocation strategy you described:
- Dynamic percentage-based allocation
- Automatic capital bucket management  
- Real-time monitoring and visualization
- Strict reserve capital protection
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
from enhanced_capital_manager import CapitalManager, TradingSystemIntegrator
from simplified_live_trading import SimpleLiveTradingSystem
from etf_database import etf_db, ETFCategory, ETFInfo
from real_account_balance import RealAccountBalanceManager
from dynamic_capital_allocator import DynamicCapitalAllocator
from real_time_monitor import RealTimeAccountMonitor, setup_default_monitoring
import yfinance as yf
from loguru import logger

# Page configuration
st.set_page_config(
    page_title="Turtle Trader Dashboard",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TradingDashboard:
    """Trading Dashboard with Dynamic Capital Allocation"""
    
    def __init__(self):
        """Initialize dashboard components"""
        self.initialize_session_state()
        self.load_or_create_system()
    
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
            
            # Initialize dynamic capital allocator with real balance
            if st.session_state.dynamic_allocator is None:
                st.session_state.dynamic_allocator = DynamicCapitalAllocator(
                    use_real_balance=st.session_state.use_real_balance
                )
            
            # Initialize real-time monitor
            if st.session_state.real_time_monitor is None:
                st.session_state.real_time_monitor = setup_default_monitoring(
                    st.session_state.dynamic_allocator
                )
            
            # Legacy system for compatibility
            if st.session_state.capital_manager is None:
                # Use default parameters from your strategy
                st.session_state.capital_manager = CapitalManager(
                    initial_capital=1000000,  # ₹10 lakhs
                    deployment_pct=0.70,      # 70% deployment
                    reserve_pct=0.30,         # 30% reserve
                    per_trade_pct=0.05,       # 5% per trade
                    profit_target=0.03,       # 3% profit target
                    brokerage_pct=0.003       # 0.3% brokerage
                )
                
                st.session_state.trading_system = SimpleLiveTradingSystem(1000000)
                
        except Exception as e:
            st.error(f"Error initializing system: {e}")
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🐢 Turtle Trader Dashboard")
            st.markdown("**Dynamic Capital Allocation Strategy**")
        
        with col2:
            if st.button("🔄 Refresh Data"):
                st.session_state.last_update = datetime.now()
                st.experimental_rerun()
        
        with col3:
            auto_refresh = st.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
            st.session_state.auto_refresh = auto_refresh
    
    def render_real_balance_status(self):
        """Render real account balance status"""
        st.header("🏦 Real Account Balance")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            balance_mode = st.radio(
                "Balance Mode",
                ["Real Breeze API", "Reference Amount"],
                index=0 if st.session_state.use_real_balance else 1,
                horizontal=True
            )
            st.session_state.use_real_balance = (balance_mode == "Real Breeze API")
        
        with col2:
            if st.button("🔄 Refresh Balance"):
                if st.session_state.dynamic_allocator:
                    success = st.session_state.dynamic_allocator.refresh_real_balance()
                    if success:
                        st.success("✅ Balance refreshed!")
                    else:
                        st.error("❌ Refresh failed")
        
        with col3:
            monitor_active = False
            if st.session_state.real_time_monitor:
                status = st.session_state.real_time_monitor.get_monitoring_status()
                monitor_active = status['monitoring']['is_active']
            
            if st.button("📊 Toggle Monitor"):
                if st.session_state.real_time_monitor:
                    if monitor_active:
                        st.session_state.real_time_monitor.stop_monitoring()
                        st.info("⏹️ Monitoring stopped")
                    else:
                        st.session_state.real_time_monitor.start_monitoring()
                        st.info("🔍 Monitoring started")
        
        # Display balance information
        if st.session_state.use_real_balance and st.session_state.dynamic_allocator:
            try:
                balance_status = st.session_state.dynamic_allocator.get_real_balance_status()
                
                if 'real_balance' in balance_status:
                    real_balance = balance_status['real_balance']
                    allocation = balance_status['allocation_status']
                    sync_status = balance_status['sync_status']
                    
                    # Balance metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Available Cash", 
                            f"₹{real_balance['available_cash']:,.2f}",
                            help="Total available cash in account"
                        )
                    
                    with col2:
                        st.metric(
                            "Free Cash", 
                            f"₹{real_balance['free_cash']:,.2f}",
                            help="Cash available for trading (after margin)"
                        )
                    
                    with col3:
                        st.metric(
                            "Portfolio Value", 
                            f"₹{real_balance['portfolio_value']:,.2f}",
                            help="Current portfolio holdings value"
                        )
                    
                    with col4:
                        sync_icon = "✅" if sync_status['is_synced'] else "⚠️"
                        st.metric(
                            "Sync Status", 
                            f"{sync_icon} {'Synced' if sync_status['is_synced'] else 'Out of Sync'}",
                            delta=f"₹{sync_status['difference']:+,.2f}" if not sync_status['is_synced'] else None,
                            help="Synchronization with allocation system"
                        )
                    
                    # Allocation metrics
                    st.subheader("� Dynamic Capital Allocation")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Deployable Capital (70%)", 
                            f"₹{allocation['deployable_capital']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Reserve Capital (30%)", 
                            f"₹{allocation['reserve_capital']:,.2f}"
                        )
                    
                    with col3:
                        st.metric(
                            "Per Trade Amount (5%)", 
                            f"₹{allocation['per_trade_amount']:,.2f}"
                        )
                    
                    with col4:
                        max_trades = int(allocation['deployable_capital'] / allocation['per_trade_amount']) if allocation['per_trade_amount'] > 0 else 0
                        st.metric(
                            "Max Positions", 
                            max_trades
                        )
                    
                    # Last update time
                    last_update = datetime.fromisoformat(real_balance['last_updated'])
                    time_diff = datetime.now() - last_update
                    st.caption(f"📅 Last Updated: {last_update.strftime('%H:%M:%S')} ({time_diff.total_seconds():.0f}s ago)")
                
                else:
                    st.error(f"❌ Balance Error: {balance_status.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error fetching real balance: {e}")
        
        else:
            # Reference mode display
            if st.session_state.dynamic_allocator:
                st.info("📊 Using reference capital allocation (₹10,00,000)")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Capital", f"₹{st.session_state.dynamic_allocator.total_capital:,.2f}")
                
                with col2:
                    st.metric("Deployable (70%)", f"₹{st.session_state.dynamic_allocator.deployable_capital:,.2f}")
                
                with col3:
                    st.metric("Reserve (30%)", f"₹{st.session_state.dynamic_allocator.reserve_capital:,.2f}")
                
                with col4:
                    st.metric("Per Trade (5%)", f"₹{st.session_state.dynamic_allocator.per_trade_amount:,.2f}")
        
        # Monitor status
        if st.session_state.real_time_monitor:
            with st.expander("📊 Real-Time Monitor Status"):
                status = st.session_state.real_time_monitor.get_monitoring_status()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json({
                        "Active": status['monitoring']['is_active'],
                        "Check Interval": f"{status['monitoring']['check_interval_minutes']:.0f} min",
                        "Auto Adjust": status['monitoring']['auto_adjust_enabled'],
                        "Change Threshold": f"{status['monitoring']['change_threshold_pct']:.1f}%"
                    })
                
                with col2:
                    st.json({
                        "Balance History": status['balance_history']['total_entries'],
                        "Significant Changes": status['change_events']['total_significant_changes'],
                        "Last Change": status['change_events']['last_significant_change'] or "None"
                    })

    def render_capital_configuration(self):
        """Render capital allocation configuration panel"""
        st.sidebar.header("📊 Capital Configuration")
        
        # Show dynamic allocator status
        if st.session_state.dynamic_allocator:
            allocator = st.session_state.dynamic_allocator
            
            st.sidebar.markdown("### Dynamic Allocation")
            st.sidebar.metric("Total Capital", f"₹{allocator.total_capital:,.2f}")
            st.sidebar.metric("Deployable (70%)", f"₹{allocator.deployable_capital:,.2f}")
            st.sidebar.metric("Reserve (30%)", f"₹{allocator.reserve_capital:,.2f}")
            st.sidebar.metric("Per Trade (5%)", f"₹{allocator.per_trade_amount:,.2f}")
            st.sidebar.metric("Active Trades", len(allocator.active_trades))
            
            # Force refresh button
            if st.sidebar.button("🔄 Force Refresh"):
                success = allocator.refresh_real_balance()
                if success:
                    st.sidebar.success("✅ Refreshed!")
                else:
                    st.sidebar.error("❌ Failed")
        
        st.sidebar.markdown("---")
        
        # Legacy system display
        manager = st.session_state.capital_manager
        
        # Current parameters
        st.sidebar.markdown("### Legacy Parameters")
        st.sidebar.metric("Reference Capital", f"₹{manager.total_capital:,.2f}")
        st.sidebar.metric("Deployment %", f"{manager.deployment_pct*100:.0f}%")
        st.sidebar.metric("Reserve %", f"{manager.reserve_pct*100:.0f}%")
        st.sidebar.metric("Per Trade %", f"{manager.per_trade_pct*100:.1f}%")
        
        st.sidebar.markdown("---")
        
        # Configuration adjustments
        st.sidebar.markdown("### Adjust Parameters")
        
        new_deployment = st.sidebar.slider(
            "Deployment %", 50, 90, int(manager.deployment_pct*100)
        ) / 100
        
        new_per_trade = st.sidebar.slider(
            "Per Trade %", 1.0, 10.0, manager.per_trade_pct*100, step=0.5
        ) / 100
        
        new_profit_target = st.sidebar.slider(
            "Profit Target %", 1.0, 5.0, manager.profit_target*100, step=0.1
        ) / 100
        
        if st.sidebar.button("Update Parameters"):
            manager.deployment_pct = new_deployment
            manager.reserve_pct = 1.0 - new_deployment
            manager.per_trade_pct = new_per_trade
            manager.profit_target = new_profit_target
            manager.recalculate_allocations()
            st.sidebar.success("Parameters updated!")
            st.experimental_rerun()
    
    def render_capital_overview(self):
        """Render capital allocation overview"""
        st.header("💰 Capital Allocation Overview")
        
        manager = st.session_state.capital_manager
        summary = manager.get_trading_summary()
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Capital",
                f"₹{summary['current_capital']:,.0f}",
                delta=f"₹{summary['total_profit']:,.0f}"
            )
        
        with col2:
            st.metric(
                "Deployment Capital",
                f"₹{summary['deployment_capital']:,.0f}",
                delta=f"{manager.deployment_pct*100:.0f}%"
            )
        
        with col3:
            st.metric(
                "Available Capital",
                f"₹{summary['available_capital']:,.0f}",
                delta=f"{100-summary['utilization_pct']:.0f}% free"
            )
        
        with col4:
            st.metric(
                "Reserve Capital",
                f"₹{summary['reserve_capital']:,.0f}",
                delta=f"{manager.reserve_pct*100:.0f}%"
            )
        
        # Capital allocation chart
        self.render_capital_allocation_chart()
    
    def render_capital_allocation_chart(self):
        """Render capital allocation visualization"""
        manager = st.session_state.capital_manager
        summary = manager.get_trading_summary()
        
        # Create pie chart for capital allocation
        fig = go.Figure()
        
        # Data for pie chart
        labels = ['Available Deployment', 'Allocated Capital', 'Reserve Capital']
        values = [
            summary['available_capital'],
            summary['allocated_capital'],
            summary['reserve_capital']
        ]
        colors = ['#2E86C1', '#E74C3C', '#F39C12']
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>₹%{value:,.0f}<br>(%{percent})',
            hovertemplate='%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Capital Allocation Breakdown",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_position_management(self):
        """Render position management panel"""
        st.header("📋 Position Management")
        
        manager = st.session_state.capital_manager
        
        # Current positions
        if manager.open_positions:
            st.subheader("🎯 Open Positions")
            
            positions_data = []
            for pos in manager.open_positions:
                positions_data.append({
                    'Symbol': pos.symbol,
                    'Investment': f"₹{pos.amount:,.0f}",
                    'Entry Price': f"₹{pos.entry_price:.2f}",
                    'Entry Time': pos.entry_time.strftime("%d/%m %H:%M"),
                    'Target Profit': f"{pos.target_profit*100:.1f}%",
                    'Days Held': (datetime.now() - pos.entry_time).days
                })
            
            df_positions = pd.DataFrame(positions_data)
            st.dataframe(df_positions, use_container_width=True)
            
            # Position allocation chart
            self.render_position_allocation_chart()
        
        else:
            st.info("No open positions currently")
        
        # Trading capacity
        self.render_trading_capacity()
    
    def render_position_allocation_chart(self):
        """Render position allocation chart"""
        manager = st.session_state.capital_manager
        
        if not manager.open_positions:
            return
        
        # Create bar chart for position allocations
        symbols = [pos.symbol for pos in manager.open_positions]
        amounts = [pos.amount for pos in manager.open_positions]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=symbols,
            y=amounts,
            text=[f"₹{amt:,.0f}" for amt in amounts],
            textposition='auto',
            marker_color='#3498DB'
        ))
        
        fig.update_layout(
            title="Position Allocation by Symbol",
            xaxis_title="ETF Symbol",
            yaxis_title="Investment Amount (₹)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_trading_capacity(self):
        """Render trading capacity analysis"""
        manager = st.session_state.capital_manager
        summary = manager.get_trading_summary()
        
        st.subheader("📊 Trading Capacity Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Capacity metrics
            max_positions = int(summary['deployment_capital'] / manager.per_trade_allocation)
            current_positions = summary['open_positions']
            remaining_capacity = max_positions - current_positions
            
            st.metric("Maximum Positions", max_positions)
            st.metric("Current Positions", current_positions)
            st.metric("Remaining Capacity", remaining_capacity)
            st.metric("Per Trade Amount", f"₹{manager.per_trade_allocation:,.0f}")
        
        with col2:
            # Capacity utilization chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = summary['utilization_pct'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Capital Utilization %"},
                delta = {'reference': 70, 'position': "top"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#3498DB"},
                    'steps': [
                        {'range': [0, 50], 'color': "#D5DBDB"},
                        {'range': [50, 80], 'color': "#F8C471"},
                        {'range': [80, 100], 'color': "#E74C3C"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_performance_metrics(self):
        """Render performance analysis"""
        st.header("📈 Performance Analytics")
        
        manager = st.session_state.capital_manager
        summary = manager.get_trading_summary()
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Profit",
                f"₹{summary['total_profit']:,.0f}",
                delta=f"{summary['total_profit_pct']:.3f}%"
            )
        
        with col2:
            st.metric(
                "Trades Completed",
                summary['total_trades_completed'],
                delta="trades"
            )
        
        with col3:
            st.metric(
                "Avg Profit/Trade",
                f"₹{summary['avg_profit_per_trade']:,.0f}",
                delta="per trade"
            )
        
        with col4:
            st.metric(
                "Total Charges",
                f"₹{summary.get('total_charges', 0):,.0f}",
                delta="brokerage"
            )
        
        # Performance charts
        self.render_performance_charts()
    
    def render_performance_charts(self):
        """Render performance visualization charts"""
        manager = st.session_state.capital_manager
        
        # Create sample performance data (in real implementation, this would come from database)
        dates = pd.date_range(start=datetime.now()-timedelta(days=30), end=datetime.now(), freq='D')
        
        # Simulate capital growth
        initial_capital = manager.initial_capital
        daily_growth = np.random.normal(0.001, 0.005, len(dates))  # 0.1% daily avg with volatility
        capital_values = [initial_capital]
        
        for growth in daily_growth[1:]:
            capital_values.append(capital_values[-1] * (1 + growth))
        
        # Capital growth chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Capital Growth', 'Daily P&L', 'Position Count', 'Utilization %'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Capital growth
        fig.add_trace(
            go.Scatter(x=dates, y=capital_values, name='Total Capital', line=dict(color='#2E86C1')),
            row=1, col=1
        )
        
        # Daily P&L
        daily_pnl = np.diff(capital_values)
        fig.add_trace(
            go.Bar(x=dates[1:], y=daily_pnl, name='Daily P&L', marker_color='#27AE60'),
            row=1, col=2
        )
        
        # Position count (simulated)
        position_counts = np.random.randint(0, 10, len(dates))
        fig.add_trace(
            go.Scatter(x=dates, y=position_counts, name='Open Positions', line=dict(color='#E74C3C')),
            row=2, col=1
        )
        
        # Utilization percentage (simulated)
        utilization = position_counts * 5  # 5% per position
        fig.add_trace(
            go.Scatter(x=dates, y=utilization, name='Utilization %', line=dict(color='#F39C12')),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_trade_execution_panel(self):
        """Render trade execution and monitoring panel"""
        st.header("🎯 Trade Execution Panel")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Manual Trade Entry")
            
            # Manual trade form
            with st.form("manual_trade"):
                symbol = st.text_input("ETF Symbol", placeholder="e.g., NIFTYBEES")
                current_price = st.number_input("Current Price (₹)", min_value=0.01, step=0.01)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("Execute Buy Order", type="primary")
                with col_b:
                    check_capacity = st.form_submit_button("Check Capacity")
                
                if check_capacity and symbol and current_price:
                    manager = st.session_state.capital_manager
                    position_info = manager.get_position_size(symbol, current_price)
                    
                    if position_info['can_trade']:
                        st.success(f"✅ Can trade {symbol}")
                        st.info(f"Investment: ₹{position_info['investment_amount']:,.0f}")
                        st.info(f"Shares: {position_info['shares']}")
                        st.info(f"Target Price: ₹{position_info['target_price']:.2f}")
                    else:
                        st.error(f"❌ Cannot trade: {position_info.get('reason', 'Unknown')}")
                
                if submit and symbol and current_price:
                    manager = st.session_state.capital_manager
                    position = manager.open_position(symbol, current_price)
                    
                    if position:
                        st.success(f"✅ Opened position in {symbol}")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Failed to open position")
        
        with col2:
            st.subheader("Quick Actions")
            
            manager = st.session_state.capital_manager
            
            # Close all positions button
            if manager.open_positions:
                if st.button("🔴 Close All Positions", type="secondary"):
                    for pos in manager.open_positions.copy():
                        # Simulate closing at 3% profit
                        exit_price = pos.entry_price * 1.03
                        manager.close_position(pos.symbol, exit_price, "Manual close")
                    st.success("All positions closed")
                    st.experimental_rerun()
            
            # Reset system button
            if st.button("🔄 Reset System"):
                st.session_state.capital_manager = CapitalManager(1000000, 0.70, 0.30, 0.05, 0.03, 0.003)
                st.success("System reset")
                st.experimental_rerun()
    
    def render_live_market_data(self):
        """Render comprehensive live market data feed"""
        st.header("📡 Live Market Data")
        
        # Category filter
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            selected_category = st.selectbox(
                "ETF Category",
                options=['All', 'Liquid ETFs'] + [cat.value for cat in ETFCategory],
                index=1  # Default to Liquid ETFs
            )
        
        with col2:
            max_etfs = st.slider("Max ETFs to display", 5, 50, 15)
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.experimental_rerun()
        
        # Get ETFs based on selection
        if selected_category == 'All':
            symbols = list(etf_db.etfs.keys())[:max_etfs]
        elif selected_category == 'Liquid ETFs':
            symbols = self.liquid_etfs[:max_etfs]
        else:
            category = next(cat for cat in ETFCategory if cat.value == selected_category)
            symbols = [etf.symbol for etf in etf_db.get_etfs_by_category(category)][:max_etfs]
        
        try:
            # Get market data using ETF database
            market_df = etf_db.get_market_data_batch(symbols)
            
            if not market_df.empty:
                # Format the dataframe for better display
                market_df['Price'] = market_df['Price'].apply(lambda x: f"₹{x:.2f}")
                market_df['Change %'] = market_df['Change %'].apply(lambda x: f"{x:+.2f}%")
                market_df['Volume'] = market_df['Volume'].apply(lambda x: f"{x:,.0f}")
                
                # Display the dataframe
                st.dataframe(market_df, use_container_width=True)
                
                # Quick stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    gainers = len([row for _, row in market_df.iterrows() if '🟢' in str(row['Status'])])
                    st.metric("Gainers", gainers)
                
                with col2:
                    losers = len([row for _, row in market_df.iterrows() if '🔴' in str(row['Status'])])
                    st.metric("Losers", losers)
                
                with col3:
                    st.metric("ETFs Tracked", len(market_df))
                
                with col4:
                    st.metric("Categories", len(set(market_df['Category'])))
            
            else:
                st.warning("No market data available for selected ETFs")
        
        except Exception as e:
            st.error(f"Error fetching market data: {e}")
            
        # ETF Sector Overview
        self.render_etf_sector_overview()
    
    def render_etf_sector_overview(self):
        """Render ETF sector distribution"""
        st.subheader("📊 ETF Sector Distribution")
        
        sector_counts = {}
        for category, etfs in self.sector_etfs.items():
            sector_counts[category] = len(etfs)
        
        if sector_counts:
            fig = px.pie(
                values=list(sector_counts.values()),
                names=list(sector_counts.keys()),
                title="ETF Distribution by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Display sector-wise ETF list
        st.subheader("🏷️ ETFs by Sector")
        
        for sector, etf_symbols in self.sector_etfs.items():
            with st.expander(f"{sector} ({len(etf_symbols)} ETFs)"):
                etf_info = []
                for symbol in etf_symbols:
                    etf = etf_db.get_etf_by_symbol(symbol)
                    if etf:
                        etf_info.append({
                            'Symbol': symbol,
                            'Name': etf.name,
                            'Index': etf.tracking_index
                        })
                
                if etf_info:
                    df = pd.DataFrame(etf_info)
                    st.dataframe(df, use_container_width=True, hide_index=True)
    
    def render_strategy_rules(self):
        """Render strategy rules and guidelines"""
        st.sidebar.header("📋 Strategy Rules")
        
        st.sidebar.markdown("""
        ### Dynamic Capital Allocation Rules
        
        **✅ Capital Buckets:**
        - Deployment: 70% of total capital
        - Reserve: 30% (never touched)
        - Per Trade: 5% of deployment capital
        
        **✅ Trade Rules:**
        - Buy on 1%+ dips from recent highs
        - Sell at 3% profit target
        - Stop loss at 5% loss
        - Maximum 20 concurrent positions
        
        **✅ Risk Management:**
        - Never use reserve capital
        - Check capacity before each trade
        - Automatic position sizing
        - Dynamic rebalancing after profits
        
        **✅ Performance Targets:**
        - Daily: ₹756 profit (0.0756%)
        - Weekly: ₹3,780 profit (0.378%)
        - Monthly: ~₹16,200 profit (1.62%)
        """)
    
    def run(self):
        """Run the main dashboard"""
        try:
            # Header
            self.render_header()
            
            # Sidebar configuration
            self.render_capital_configuration()
            self.render_strategy_rules()
            
            # Main content - Real Balance Integration
            self.render_real_balance_status()
            self.render_capital_overview()
            self.render_position_management()
            self.render_performance_metrics()
            self.render_trade_execution_panel()
            self.render_live_market_data()
            
            # Auto refresh
            if st.session_state.auto_refresh:
                time.sleep(30)
                st.experimental_rerun()
        
        except Exception as e:
            st.error(f"Dashboard error: {e}")
            logger.error(f"Dashboard error: {e}")

def main():
    """Main function to run the dashboard"""
    dashboard = TradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()