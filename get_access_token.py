#!/usr/bin/env python3
"""
🔐 KITE ACCESS TOKEN GENERATOR
============================

This script helps you generate a valid access token for your Kite API.
Run this script and follow the instructions to get your daily access token.
"""

import configparser
import webbrowser
from urllib.parse import parse_qs, urlparse

def generate_access_token():
    """Generate access token for Kite API"""
    
    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_key = config.get('KITE_API', 'api_key')
    api_secret = config.get('KITE_API', 'api_secret')
    
    print("🔐 KITE ACCESS TOKEN GENERATOR")
    print("=" * 40)
    print(f"📱 API Key: {api_key}")
    print(f"🔑 API Secret: {api_secret[:8]}...")
    print()
    
    # Generate login URL
    login_url = f"https://kite.zerodha.com/connect/login?api_key={api_key}&v=3"
    
    print("📋 STEP 1: Get Request Token")
    print("-" * 30)
    print("1. Click the URL below (or copy-paste in browser):")
    print(f"   {login_url}")
    print()
    print("2. Login to your Zerodha account")
    print("3. Click 'Authorize' when prompted")
    print("4. Copy the FULL redirect URL from browser address bar")
    print("   (It will look like: http://127.0.0.1:8080/?request_token=abc123&action=login&status=success)")
    print()
    
    # Try to open browser automatically
    try:
        webbrowser.open(login_url)
        print("✅ Browser opened automatically!")
    except:
        print("⚠️  Please manually open the URL above")
    
    print()
    print("🔗 Waiting for redirect URL...")
    redirect_url = input("📋 Paste the full redirect URL here: ").strip()
    
    # Extract request token
    try:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'request_token' in query_params:
            request_token = query_params['request_token'][0]
            print(f"✅ Request Token: {request_token}")
            
            # Generate session
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=api_key)
            
            print("\n🔄 Generating access token...")
            data = kite.generate_session(request_token, api_secret=api_secret)
            access_token = data["access_token"]
            
            print(f"✅ Access Token: {access_token}")
            
            # Update config file
            config.set('KITE_API', 'access_token', access_token)
            with open('config.ini', 'w') as f:
                config.write(f)
            
            print("\n✅ SUCCESS!")
            print("=" * 40)
            print("✅ config.ini updated with valid access token")
            print("✅ You can now run the trading dashboard")
            print("\n🚀 Next Steps:")
            print("   streamlit run trading_dashboard.py --server.port 8060")
            
            return access_token
            
        else:
            print("❌ Error: No request_token found in URL")
            print("   Make sure you copied the complete redirect URL")
            return None
            
    except Exception as e:
        print(f"❌ Error processing URL: {e}")
        return None

if __name__ == "__main__":
    generate_access_token()