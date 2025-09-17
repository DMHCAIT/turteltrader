"""
🎫 Session Token Generator
Get your session token for ICICI Breeze API
"""

import webbrowser
import configparser

def generate_session_token():
    print("🎫 ICICI BREEZE API - SESSION TOKEN GENERATOR")
    print("=" * 60)
    
    # Read current config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_key = config.get('BREEZE_API', 'API_KEY')
    
    if api_key and api_key != 'your_api_key_here':
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Generate login URL
        login_url = f"https://api.icicidirect.com/apiuser/login?api_key={api_key}"
        
        print(f"\n🌐 Opening login URL in your browser...")
        print(f"URL: {login_url}")
        
        # Open in browser
        try:
            webbrowser.open(login_url)
            print("✅ Browser opened successfully!")
        except:
            print("❌ Could not open browser automatically")
            print(f"📋 Please copy and paste this URL: {login_url}")
        
        print("\n📋 INSTRUCTIONS:")
        print("1. Login with your ICICI credentials:")
        print("   Username: 8089000967")
        print("   Password: Turtletrader@1")
        print()
        print("2. After login, you'll be redirected to:")
        print("   http://localhost:8080/callback?session_token=XXXXX")
        print()
        print("3. Copy the session_token value from the URL")
        print("4. Paste it below:")
        print()
        
        # Get session token from user
        session_token = input("🔑 Enter your session token: ").strip()
        
        if session_token:
            # Update config.ini
            config.set('BREEZE_API', 'SESSION_TOKEN', session_token)
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            print(f"✅ Session token saved!")
            print(f"🎯 Token: {session_token[:20]}...")
            
            print("\n🧪 Testing API connection...")
            
            # Test the connection
            try:
                from breeze_api_client import BreezeAPIClient
                
                client = BreezeAPIClient()
                if client.test_connection():
                    print("🎉 SUCCESS! API connection working!")
                    print("\n🚀 YOU'RE READY FOR LIVE TRADING!")
                    print("   Run: python main_live.py")
                else:
                    print("❌ API test failed - please check credentials")
                    
            except Exception as e:
                print(f"❌ Test error: {e}")
        
        else:
            print("❌ No session token entered")
    
    else:
        print("❌ API Key not configured!")
        print("📖 Please run QUICK_START.py first")

if __name__ == "__main__":
    generate_session_token()
