"""
🔑 SIMPLE ACCESS TOKEN GUIDE
============================

Step-by-step guide to manually get your Kite access token.
"""

def show_token_instructions():
    """Show manual token generation instructions"""
    
    print("🔑 MANUAL KITE ACCESS TOKEN GENERATION")
    print("=" * 50)
    
    print("\n📋 Step 1: Visit the Authorization URL")
    print("Copy this URL and open it in your browser:")
    print("https://kite.zerodha.com/connect/login?api_key=i0bd6xlyqau3ivqe&v=3")
    
    print("\n📋 Step 2: Login and Authorize")
    print("1. Login with your Zerodha credentials")
    print("2. Click 'Authorize' to grant access to the app")
    
    print("\n📋 Step 3: Extract Request Token")
    print("After authorization, you'll be redirected to a URL that contains")
    print("a 'request_token' parameter. It looks like:")
    print("http://127.0.0.1:8080/?request_token=h06I6Ydv95y23D2Dp7GbigFjKweGwRP7&action=login&status=success")
    
    print("\n📋 Step 4: Copy the Request Token")
    print("From the redirect URL, copy ONLY the request_token value")
    print("(the long string after 'request_token=')")
    
    print("\n📋 Step 5: Update Your Config")
    print("Replace this line in your config.ini:")
    print("access_token = YOUR_ACTUAL_TOKEN_FROM_STEP_1")
    print("With:")
    print("access_token = [paste your request token here]")
    
    print("\n🚀 Step 6: Test Your Setup")
    print("Run this command to test:")
    print("streamlit run simple_trading_dashboard.py")
    
    print("\n⚠️ Important Notes:")
    print("- Access tokens expire daily and need to be regenerated")
    print("- The request_token IS your access_token for Kite API")
    print("- Keep your token secure and don't share it")
    
    return "https://kite.zerodha.com/connect/login?api_key=i0bd6xlyqau3ivqe&v=3"

def update_config_with_token():
    """Helper to update config with manual token input"""
    import configparser
    import os
    
    if not os.path.exists('config.ini'):
        print("❌ config.ini not found!")
        return
    
    print("\n🔧 Manual Token Update")
    print("If you have your request_token, I can update config.ini for you")
    
    token = input("\nEnter your request_token (or press Enter to skip): ").strip()
    
    if token:
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            config.set('KITE_API', 'access_token', token)
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            print(f"✅ Token updated in config.ini: {token[:10]}...")
            print("\n🚀 Now you can run: streamlit run simple_trading_dashboard.py")
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
    else:
        print("👍 Skipping automatic update. Update config.ini manually.")

if __name__ == "__main__":
    auth_url = show_token_instructions()
    
    # Ask if user wants to open browser
    choice = input("\n🌐 Open authorization URL in browser? (Y/n): ").lower()
    if choice != 'n':
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("✅ Browser opened")
        except:
            print("❌ Could not open browser")
    
    # Offer to help update config
    update_config_with_token()