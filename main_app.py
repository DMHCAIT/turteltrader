"""
🐢 TURTLE TRADER - CLOUD DEPLOYMENT FIX
======================================

This file handles both local and cloud deployment
"""

import streamlit as st
import os

# Check if running in cloud
def is_cloud_environment():
    return "STREAMLIT_SHARING" in os.environ or "STREAMLIT_CLOUD" in os.environ or hasattr(st, 'secrets')

def main():
    """Main application entry point"""
    
    st.set_page_config(
        page_title="🐢 Turtle Trader",
        page_icon="🐢",
        layout="wide"
    )
    
    if is_cloud_environment():
        # Cloud deployment - use demo mode
        st.title("🐢 Turtle Trader Dashboard - Cloud Demo")
        st.warning("🌩️ This is a demo version. For live trading, deploy locally.")
        
        # Import and run cloud-compatible version
        try:
            import streamlit_app as cloud_app
            cloud_app.main()
        except ImportError:
            st.error("Demo mode not available. Please check deployment configuration.")
    
    else:
        # Local deployment - full functionality
        try:
            from trading_dashboard import TradingDashboard
            dashboard = TradingDashboard()
            dashboard.run()
        except Exception as e:
            st.error(f"❌ Local dashboard failed: {str(e)}")
            st.info("💡 Falling back to demo mode...")
            import streamlit_app as cloud_app
            cloud_app.main()

if __name__ == "__main__":
    main()