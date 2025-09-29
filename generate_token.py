#!/usr/bin/env python3
"""
🔑 QUICK ACCESS TOKEN GENERATOR
================================

This script helps you generate a valid Kite access token quickly.
Run this before deploying to Streamlit Cloud.
"""

import sys
from kiteconnect import KiteConnect

def generate_access_token():
    """Generate access token interactively"""
    
    print("🔑 KITE ACCESS TOKEN GENERATOR")
    print("=" * 40)
    
    # API credentials
    api_key = "i0bd6xlyqau3ivqe"
    api_secret = "s2x3rpgijq921qmjgcerzqj3x6tkge6p"
    
    print(f"✅ API Key: {api_key}")
    
    # Step 1: Generate login URL
    login_url = f"https://kite.zerodha.com/connect/login?api_key={api_key}&v=3"
    
    print(f"\n📋 Step 1: Open this URL in your browser:")
    print(f"🔗 {login_url}")
    print(f"\n📋 Step 2: Login with your Zerodha credentials")
    print(f"📋 Step 3: After authorization, you'll be redirected to a URL like:")
    print(f"   https://127.0.0.1:8080/?request_token=XXXXXX&action=login&status=success")
    print(f"📋 Step 4: Copy the request_token value (the XXXXXX part)")
    
    # Get request token from user
    request_token = input(f"\n🎯 Enter your request_token here: ").strip()
    
    if not request_token:
        print("❌ No request token provided!")
        return None
    
    try:
        print(f"\n🔄 Generating access token...")
        
        # Initialize Kite Connect
        kite = KiteConnect(api_key=api_key)
        
        # Generate session
        data = kite.generate_session(request_token, api_secret=api_secret)
        
        access_token = data['access_token']
        
        print(f"\n✅ SUCCESS! Access token generated:")
        print(f"🔑 {access_token}")
        
        # Save to config.ini
        config_path = "config.ini"
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Replace the placeholder token
            updated_content = config_content.replace(
                "access_token = YOUR_ACTUAL_TOKEN_FROM_STEP_1",
                f"access_token = {access_token}"
            )
            
            with open(config_path, 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated config.ini with new access token")
            
        except Exception as e:
            print(f"⚠️ Could not update config.ini: {e}")
            print(f"📝 Manually update config.ini with:")
            print(f"   access_token = {access_token}")
        
        print(f"\n🎯 For Streamlit Cloud, add this to secrets:")
        print(f"   access_token = \"{access_token}\"")
        
        print(f"\n🚀 You can now run:")
        print(f"   streamlit run trading_dashboard.py --server.port 8052")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        print(f"💡 Make sure:")
        print(f"   1. Request token is correct")
        print(f"   2. Token hasn't expired (generate new one)")
        print(f"   3. Your Zerodha account is active")
        return None

if __name__ == "__main__":
    generate_access_token()