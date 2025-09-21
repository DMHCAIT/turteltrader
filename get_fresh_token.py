#!/usr/bin/env python3
"""
🚀 AUTOMATED BREEZE TOKEN GENERATOR & VALIDATOR
=============================================

Complete solution to get fresh session token and validate API connection.
"""

import webbrowser
import time
from datetime import datetime, timedelta
import configparser
from breeze_connect import BreezeConnect

def get_and_validate_token():
    """Complete token generation and validation process"""
    
    print("🔑 BREEZE API TOKEN GENERATOR & VALIDATOR")
    print("=" * 55)
    
    # Your credentials
    api_key = "3K8G69248187o756165f6_602IdJ2m80"
    api_secret = "8sq5o9660813T8)n4LC&nl09x75t9412"
    
    print("📋 STEP 1: Get Fresh Session Token")
    print("-" * 40)
    
    # Generate login URL
    login_url = f"https://api.icicidirect.com/apiuser/login?api_key={api_key}"
    
    print("🌐 Instructions:")
    print("1. Browser will open ICICI login page")
    print("2. Login with:")
    print("   👤 Username: 8089000967")
    print("   🔐 Password: Turtletrader@1")
    print("3. After login, copy the token from URL")
    print("   Example: http://127.0.0.1:8080/?apisession=YOUR_TOKEN")
    print("4. Paste the token here")
    print()
    
    input("Press ENTER to open login page...")
    
    # Open browser
    print("🌐 Opening ICICI login page...")
    webbrowser.open(login_url)
    time.sleep(2)
    
    print()
    print("⏰ Complete login and return here...")
    print("   (Ignore 'site can't be reached' - just copy the token from URL)")
    print()
    
    # Get token from user
    while True:
        token = input("🔑 Paste your session token: ").strip()
        
        if token and len(token) > 6 and token.isdigit():
            break
        else:
            print("❌ Invalid token format. Should be 8+ digits. Try again.")
    
    print()
    print("📋 STEP 2: Validate Token")
    print("-" * 40)
    
    # Test the token
    try:
        print("🧪 Testing new session token...")
        
        # Initialize Breeze with new token
        breeze = BreezeConnect(api_key=api_key)
        breeze.generate_session(api_secret=api_secret, session_token=token)
        
        # Test API calls
        print("   🔍 Testing customer details...")
        profile = breeze.get_customer_details()
        
        if 'Error' not in str(profile) or profile.get('Status') == 200:
            print("   ✅ API connection successful!")
            
            # Update config file
            print("📋 STEP 3: Update Configuration")
            print("-" * 40)
            
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            old_token = config.get('BREEZE_API', 'SESSION_TOKEN', fallback='')
            config.set('BREEZE_API', 'SESSION_TOKEN', token)
            
            with open('config.ini', 'w') as f:
                config.write(f)
            
            print("✅ Configuration updated successfully!")
            print(f"   Old token: {old_token}")
            print(f"   New token: {token}")
            print(f"   Valid until: {(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Final validation
            print()
            print("📋 STEP 4: Final System Test")
            print("-" * 40)
            
            # Test key functions
            try:
                funds = breeze.get_funds()
                print("   💰 Funds access: ✅")
            except:
                print("   💰 Funds access: ⚠️ (may need account setup)")
            
            try:
                holdings = breeze.get_portfolio_holdings()
                print("   📊 Portfolio access: ✅")
            except:
                print("   📊 Portfolio access: ⚠️ (may be empty)")
            
            print()
            print("🎉 SUCCESS! YOUR SYSTEM IS READY FOR LIVE TRADING!")
            print("=" * 55)
            print("🚀 Next steps:")
            print("   1. Run: streamlit run app.py")
            print("   2. Start live trading!")
            print("   3. Monitor your positions and performance")
            
            return True
            
        else:
            print(f"   ❌ Token validation failed: {profile}")
            print("   🔧 Try generating a new token")
            return False
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        print("🔧 Please try generating a new session token")
        return False

if __name__ == "__main__":
    success = get_and_validate_token()
    
    if not success:
        print()
        print("⚠️ If token generation fails repeatedly:")
        print("   1. Check ICICI Direct account is active")
        print("   2. Verify API access is enabled") 
        print("   3. Contact ICICI support if needed")