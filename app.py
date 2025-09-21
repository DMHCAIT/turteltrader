"""
🐢 TURTLE TRADER - MAIN APPLICATION
===================================

Main entry point for Streamlit Cloud deployment
Enhanced with cloud deployment fixes
"""

import streamlit as st
import sys
import traceback

def main():
    """Main application entry point with enhanced error handling"""
    
    # Apply cloud deployment fixes first
    try:
        from streamlit_cloud_fixes import fix_streamlit_cloud_issues, create_fallback_dashboard
        
        if not fix_streamlit_cloud_issues():
            create_fallback_dashboard()
            return
            
    except ImportError:
        # Fallback if cloud fixes not available
        st.set_page_config(
            page_title="Turtle Trader - Live Trading System",
            page_icon="🐢", 
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    # Initialize and run dashboard
    try:
        from trading_dashboard import TradingDashboard
        dashboard = TradingDashboard()
        dashboard.run()
        
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.info("🔧 **Solutions:**")
        st.code("""
# Run locally instead:
cd "/Users/rubeenakhan/Downloads/Turtel trader"
source turtle_env/bin/activate
streamlit run app.py --server.port 8502
        """)
        
    except Exception as e:
        st.error(f"❌ Application Error: {type(e).__name__}: {e}")
        
        with st.expander("🔍 Detailed Error Information"):
            st.code(traceback.format_exc())
        
        st.info("""
        🛠️ **Troubleshooting Steps:**
        
        1. **Try Local Version**: More reliable than cloud
        2. **Check Dependencies**: All packages installed?
        3. **Refresh Browser**: Clear cache (Ctrl+F5)
        4. **Check Logs**: Review Streamlit Cloud deployment logs
        """)
        
        # Show fallback options
        if st.button("🔄 Switch to Fallback Mode"):
            try:
                from streamlit_cloud_fixes import create_fallback_dashboard
                create_fallback_dashboard()
            except ImportError:
                st.error("Fallback mode not available. Use local version.")


if __name__ == "__main__":
    main()
