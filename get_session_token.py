#!/usr/bin/env python3
"""
🔑 Breeze API Session Token Generator
==================================

Simple script to get a fresh session token for live trading.
"""

import webbrowser
import time
from datetime import datetime, timedelta

def get_fresh_session_token():
    """Generate a fresh session token"""
    
    print("🔑 BREEZE API SESSION TOKEN GENERATOR")
    print("=" * 50)
    print()
    
    # Your API credentials
    api_key = "3K8G69248187o756165f6_602IdJ2m80"
    
    # Generate login URL
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={api_key}"
    
    print("📋 STEP-BY-STEP PROCESS:")
    print()
    print("1️⃣ This will open your browser to the ICICI login page")
    print("2️⃣ Login with your ICICI Direct credentials:")
    print("    Username: 8089000967")
    print("    Password: Turtletrader@1")
    print()
    print("3️⃣ After login, you'll be redirected to a URL like:")
    print("    http://127.0.0.1:8080/?apisession=YOUR_NEW_TOKEN")
    print()
    print("4️⃣ Copy the token from 'apisession=' part")
    print("5️⃣ Come back here and enter it")
    print()
    
    input("Press ENTER to open login page...")
    
    # Open login page
    print("🌐 Opening login page...")
    webbrowser.open(login_url)
    
    print()
    print("⏰ Waiting for you to complete login...")
    print("   (The page might show 'This site can't be reached' - that's normal)")
    print("   Just copy the token from the URL!")
    print()
    
    # Get token from user
    while True:
        token = input("🔑 Enter your session token: ").strip()
        
        if token and len(token) > 5:
            break
        else:
            print("❌ Invalid token. Please try again.")
    
    # Save token to config
    try:
        # Update config.ini
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        old_token = config.get('BREEZE_API', 'SESSION_TOKEN', fallback='')
        config.set('BREEZE_API', 'SESSION_TOKEN', token)
        
        with open('config.ini', 'w') as f:
            config.write(f)
        
        print()
        print("✅ SUCCESS! Session token updated!")
        print(f"   Old token: {old_token}")
        print(f"   New token: {token}")
        print(f"   Valid until: {(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("🚀 Your system is now ready for live trading!")
        return token
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        print(f"💡 Manually update SESSION_TOKEN = {token} in config.ini")
        return token

if __name__ == "__main__":
    get_fresh_session_token()