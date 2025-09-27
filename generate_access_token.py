#!/usr/bin/env python3
"""
🔑 KITE API ACCESS TOKEN GENERATOR
=======================================

This script helps you generate an access token for your Kite API credentials.
Run this once to get your access token, then copy it to config.ini
"""

import webbrowser
from urllib.parse import urlparse, parse_qs
from kiteconnect import KiteConnect
import configparser

def generate_access_token():
    """Generate access token for Kite API"""
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_key = config.get('KITE_API', 'api_key')
    api_secret = config.get('KITE_API', 'api_secret')
    
    if not api_key or api_key == 'your_kite_api_key_here':
        print("❌ Please configure your API key in config.ini first!")
        return
        
    if not api_secret or api_secret == 'your_kite_api_secret_here':
        print("❌ Please configure your API secret in config.ini first!")
        return
    
    print(f"🔑 Generating access token for API Key: {api_key}")
    print("=" * 50)
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"🌐 Opening login URL: {login_url}")
    
    # Open browser automatically
    webbrowser.open(login_url)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. A browser window will open with Zerodha login")
    print("2. Login with your Zerodha credentials")
    print("3. After login, you'll be redirected to a URL")
    print("4. Copy the FULL redirect URL and paste it below")
    print("\nThe URL will look like:")
    print("http://127.0.0.1:8080/callback?request_token=ABC123&action=login&status=success")
    print()
    
    # Get request token from user
    redirect_url = input("📎 Paste the full redirect URL here: ").strip()
    
    try:
        # Parse the URL to extract request token
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        request_token = query_params.get('request_token', [None])[0]
        
        if not request_token:
            print("❌ Could not find request_token in the URL!")
            return
            
        print(f"✅ Request token extracted: {request_token[:10]}...")
        
        # Generate access token
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print(f"\n🎉 SUCCESS! Access token generated: {access_token}")
        
        # Update config file
        config.set('KITE_API', 'access_token', access_token)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
        print("✅ Access token saved to config.ini")
        print("\n🚀 You can now run your trading system!")
        print("   Run: python test_kite_integration.py")
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you copied the COMPLETE URL")
        print("2. Check your API key and secret are correct")
        print("3. Make sure you completed the login process")

if __name__ == "__main__":
    generate_access_token()