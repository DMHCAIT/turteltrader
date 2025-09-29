""""""

🎯 FLASK TRADING DASHBOARD - Vercel Deployment Ready🐢 TURTLE TRADER - MAIN APPLICATION

=====================================================================================



Web-based trading dashboard using Flask that can be deployed on Vercel.Main entry point for Streamlit Cloud deployment

Supports manual token configuration and live trading.Enhanced with cloud deployment fixes

""""""



from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, sessionimport streamlit as st

import jsonimport sys

import osimport traceback

from datetime import datetime, timedelta

import configparserdef main():

from werkzeug.security import generate_password_hash, check_password_hash    """Main application entry point with enhanced error handling"""

import pandas as pd    

import plotly    # Apply cloud deployment fixes first

import plotly.graph_objects as go    try:

import plotly.express as px        from streamlit_cloud_fixes import fix_streamlit_cloud_issues, create_fallback_dashboard

from plotly.utils import PlotlyJSONEncoder        

        if not fix_streamlit_cloud_issues():

# Import your trading modules            create_fallback_dashboard()

try:            return

    from kite_api_client import KiteAPIClient            

    from dynamic_capital_allocator import DynamicCapitalAllocator    except ImportError:

    from etf_database import etf_db, ETFCategory, ETFInfo        # Fallback if cloud fixes not available

    from real_account_balance import RealAccountBalanceManager        st.set_page_config(

    TRADING_MODULES_AVAILABLE = True            page_title="Turtle Trader - Live Trading System",

except ImportError as e:            page_icon="🐢", 

    print(f"Warning: Trading modules not available - {e}")            layout="wide",

    TRADING_MODULES_AVAILABLE = False            initial_sidebar_state="expanded"

        )

app = Flask(__name__)    

app.secret_key = 'your-secret-key-change-this-in-production'    # Initialize and run dashboard

    try:

# Global variables for trading system        from trading_dashboard import TradingDashboard

trading_system = None        dashboard = TradingDashboard()

balance_manager = None        dashboard.run()

capital_allocator = None        

    except ImportError as e:

def initialize_trading_system():        st.error(f"❌ Import Error: {e}")

    """Initialize trading system components"""        st.info("🔧 **Solutions:**")

    global trading_system, balance_manager, capital_allocator        st.code("""

    # Run locally instead:

    if not TRADING_MODULES_AVAILABLE:cd "/Users/rubeenakhan/Downloads/Turtel trader"

        return False, "Trading modules not available"source turtle_env/bin/activate

    streamlit run app.py --server.port 8502

    try:        """)

        # Initialize API client        

        api_client = KiteAPIClient()    except Exception as e:

        kite = api_client.get_kite_client()        st.error(f"❌ Application Error: {type(e).__name__}: {e}")

                

        if not kite:        with st.expander("🔍 Detailed Error Information"):

            return False, "Invalid API credentials or token"            st.code(traceback.format_exc())

                

        # Initialize other components        st.info("""

        balance_manager = RealAccountBalanceManager()        🛠️ **Troubleshooting Steps:**

        capital_allocator = DynamicCapitalAllocator(use_real_balance=True)        

                1. **Try Local Version**: More reliable than cloud

        return True, "Trading system initialized successfully"        2. **Check Dependencies**: All packages installed?

                3. **Refresh Browser**: Clear cache (Ctrl+F5)

    except Exception as e:        4. **Check Logs**: Review Streamlit Cloud deployment logs

        return False, f"Initialization error: {str(e)}"        """)

        

@app.route('/')        # Show fallback options

def index():        if st.button("🔄 Switch to Fallback Mode"):

    """Main dashboard page"""            try:

    return render_template('dashboard.html')                from streamlit_cloud_fixes import create_fallback_dashboard

                create_fallback_dashboard()

@app.route('/api/status')            except ImportError:

def api_status():                st.error("Fallback mode not available. Use local version.")

    """Get API connection status"""

    if not TRADING_MODULES_AVAILABLE:

        return jsonify({if __name__ == "__main__":

            'connected': False,    main()

            'message': 'Trading modules not available',
            'user': None
        })
    
    try:
        client = KiteAPIClient()
        kite = client.get_kite_client()
        
        if kite:
            profile = kite.profile()
            return jsonify({
                'connected': True,
                'message': 'API connected successfully',
                'user': profile.get('user_name', 'Unknown'),
                'user_id': profile.get('user_id', 'Unknown')
            })
        else:
            return jsonify({
                'connected': False,
                'message': 'Invalid credentials or expired token',
                'user': None
            })
    except Exception as e:
        return jsonify({
            'connected': False,
            'message': f'Connection error: {str(e)}',
            'user': None
        })

@app.route('/api/balance')
def get_balance():
    """Get account balance information"""
    if not balance_manager:
        success, message = initialize_trading_system()
        if not success:
            return jsonify({'error': message})
    
    try:
        balance_data = balance_manager.get_current_balance()
        return jsonify({
            'success': True,
            'data': balance_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/etfs')
def get_etfs():
    """Get ETF information"""
    try:
        if TRADING_MODULES_AVAILABLE:
            liquid_etfs = etf_db.get_liquid_etfs()
            etf_data = []
            
            for etf in liquid_etfs[:20]:  # Limit to 20 for performance
                etf_data.append({
                    'symbol': etf.symbol,
                    'name': etf.name,
                    'category': etf.category.name if etf.category else 'Unknown',
                    'volume': etf.avg_volume,
                    'status': 'Active'
                })
            
            return jsonify({
                'success': True,
                'data': etf_data
            })
        else:
            # Mock data for demo
            return jsonify({
                'success': True,
                'data': [
                    {'symbol': 'NIFTYBEES', 'name': 'Nippon India ETF Nifty BeES', 'category': 'Broad Market', 'volume': 1000000, 'status': 'Active'},
                    {'symbol': 'BANKBEES', 'name': 'Nippon India ETF Bank BeES', 'category': 'Sectoral', 'volume': 500000, 'status': 'Active'},
                    {'symbol': 'ITBEES', 'name': 'Nippon India ETF IT BeES', 'category': 'Sectoral', 'volume': 300000, 'status': 'Active'}
                ]
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        config_data = {
            'api_key': config.get('KITE_API', 'api_key', fallback='')[:10] + '...' if config.get('KITE_API', 'api_key', fallback='') else 'Not set',
            'api_secret': 'Set' if config.get('KITE_API', 'api_secret', fallback='') else 'Not set',
            'access_token': 'Set' if config.get('KITE_API', 'access_token', fallback='') and config.get('KITE_API', 'access_token', fallback='') != 'YOUR_ACTUAL_TOKEN_FROM_STEP_1' else 'Not set'
        }
        
        return jsonify({
            'success': True,
            'data': config_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/update-token', methods=['POST'])
def update_token():
    """Update access token"""
    try:
        data = request.get_json()
        access_token = data.get('access_token', '').strip()
        
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'Access token is required'
            })
        
        # Update config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        if not config.has_section('KITE_API'):
            config.add_section('KITE_API')
        
        config.set('KITE_API', 'access_token', access_token)
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        
        # Test the token
        if TRADING_MODULES_AVAILABLE:
            try:
                client = KiteAPIClient()
                kite = client.get_kite_client()
                if kite:
                    profile = kite.profile()
                    return jsonify({
                        'success': True,
                        'message': f'Token updated and verified for user: {profile.get("user_name", "Unknown")}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Token updated but verification failed'
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Token updated but verification failed: {str(e)}'
                })
        else:
            return jsonify({
                'success': True,
                'message': 'Token updated successfully (verification skipped - modules not available)'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/config')
def config_page():
    """Configuration page"""
    return render_template('config.html')

@app.route('/api/chart-data')
def get_chart_data():
    """Get chart data for dashboard"""
    try:
        # Generate sample chart data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        prices = 100 + (dates.day_of_year * 0.1) + (pd.Series(range(len(dates))).apply(lambda x: x % 10))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#00D4AA', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Performance',
            xaxis_title='Date',
            yaxis_title='Value (₹)',
            template='plotly_dark',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return jsonify({'chart': graphJSON})
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)