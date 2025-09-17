"""
🐢 TURTLE TRADER - MAIN APPLICATION
===================================

Main entry point for Streamlit Cloud deployment
"""

import streamlit as st
from trading_dashboard import TradingDashboard

def main():
    """Main application entry point"""
    
    # Set page config
    st.set_page_config(
        page_title="Turtle Trader - Live Trading System",
        page_icon="🐢", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize and run dashboard
    try:
        dashboard = TradingDashboard()
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Application Error: {e}")
        st.info("Please check your API configuration and try again.")


if __name__ == "__main__":
    main()
