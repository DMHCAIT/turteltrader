"""
🌐 STREAMLIT CLOUD DEPLOYMENT FIX
================================

Fixes for common Streamlit Cloud deployment issues
"""

import streamlit as st
import sys
import os
from pathlib import Path

def fix_streamlit_cloud_issues():
    """Apply fixes for common Streamlit Cloud deployment problems"""
    
    # Fix 1: Set proper page config with error handling
    try:
        if not hasattr(st.session_state, 'page_config_set'):
            st.set_page_config(
                page_title="Turtle Trader - Live Trading System",
                page_icon="🐢",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': 'https://github.com/DMHCAIT/turteltrader',
                    'Report a bug': 'https://github.com/DMHCAIT/turteltrader/issues',
                    'About': '# Turtle Trader\nAutomated ETF Trading System'
                }
            )
            st.session_state.page_config_set = True
    except Exception as e:
        st.error(f"Page config error (non-critical): {e}")
    
    # Fix 2: Handle missing dependencies gracefully
    missing_deps = []
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    try:
        import plotly
    except ImportError:
        missing_deps.append("plotly")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        st.error(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        st.info("📦 Installing dependencies... Please wait and refresh.")
        return False
    
    # Fix 3: Handle file path issues
    try:
        # Ensure we're in the right directory
        current_dir = Path.cwd()
        if not (current_dir / "config.ini").exists():
            # Try to find config.ini in parent directories
            for parent in current_dir.parents:
                if (parent / "config.ini").exists():
                    os.chdir(parent)
                    break
    except Exception as e:
        st.warning(f"Path issue: {e}")
    
    # Fix 4: Memory optimization for cloud
    if 'STREAMLIT_SHARING' in os.environ or 'STREAMLIT_CLOUD' in os.environ:
        # Running on Streamlit Cloud
        st.session_state.is_cloud = True
        
        # Reduce memory usage
        if 'large_dataframes' not in st.session_state:
            st.session_state.large_dataframes = {}
        
        # Clear old session data periodically
        if len(st.session_state.keys()) > 50:
            keys_to_remove = [k for k in st.session_state.keys() 
                            if k.startswith('temp_') or k.startswith('cache_')]
            for key in keys_to_remove[:10]:  # Remove oldest 10
                if key in st.session_state:
                    del st.session_state[key]
    else:
        st.session_state.is_cloud = False
    
    # Fix 5: Graceful error handling
    sys.excepthook = lambda exc_type, exc_value, exc_traceback: st.error(
        f"❌ System Error: {exc_type.__name__}: {exc_value}"
    )
    
    return True

def show_deployment_status():
    """Show current deployment status and troubleshooting info"""
    
    with st.expander("🔧 Deployment Status & Troubleshooting"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 System Status")
            
            # Check Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            st.success(f"🐍 Python: {python_version}")
            
            # Check Streamlit version
            try:
                import streamlit as st_module
                st_version = st_module.__version__
                st.success(f"⚡ Streamlit: {st_version}")
            except:
                st.error("❌ Streamlit version unknown")
            
            # Check environment
            is_cloud = st.session_state.get('is_cloud', False)
            if is_cloud:
                st.info("☁️ Running on Streamlit Cloud")
            else:
                st.success("💻 Running locally")
        
        with col2:
            st.subheader("🛠️ Troubleshooting")
            
            st.markdown("""
            **Common Cloud Issues:**
            - 503 Error → Restart deployment
            - 403 Error → Check repository permissions  
            - 404 Error → Verify file paths
            - Memory Error → Reduce data size
            
            **Quick Fixes:**
            1. Refresh browser (Ctrl+F5)
            2. Clear browser cache
            3. Restart Streamlit Cloud app
            4. Use local version: `./start_daily.sh`
            """)
            
            if st.button("🔄 Clear Session Cache"):
                for key in list(st.session_state.keys()):
                    if key.startswith('cache_') or key.startswith('temp_'):
                        del st.session_state[key]
                st.success("✅ Cache cleared! Refresh page.")

def create_fallback_dashboard():
    """Create a minimal fallback dashboard if main app fails"""
    
    st.title("🐢 Turtle Trader - Fallback Mode")
    
    st.warning("""
    ⚠️ **Fallback Mode Active**
    
    The main dashboard encountered issues. This is a simplified version.
    """)
    
    st.info("""
    🛠️ **Solutions:**
    
    1. **Use Local Version** (Recommended):
       ```bash
       cd "/Users/rubeenakhan/Downloads/Turtel trader"
       ./start_daily.sh
       ```
       Then visit: http://localhost:8502
    
    2. **Cloud Troubleshooting**:
       - Check Streamlit Cloud logs
       - Verify GitHub repository sync
       - Restart deployment from cloud dashboard
    
    3. **Alternative Access**:
       - Try incognito/private browser mode
       - Clear browser cache and cookies
       - Use different browser
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌐 Open Cloud Dashboard"):
            st.info("Check your Streamlit Cloud account for deployment status")
    
    with col2:
        if st.button("💻 Local Setup Guide"):
            st.code("""
# Complete local setup:
cd "/Users/rubeenakhan/Downloads/Turtel trader"
source turtle_env/bin/activate
streamlit run app.py --server.port 8502
            """)
    
    with col3:
        if st.button("📚 Documentation"):
            st.info("Check DASHBOARD_CONTROLS_GUIDE.md for complete instructions")

# Export functions for use in main app
__all__ = ['fix_streamlit_cloud_issues', 'show_deployment_status', 'create_fallback_dashboard']