"""
🔑 MANUAL ACCESS TOKEN GENERATOR
===============================

Simple script to help you manually generate Kite access tokens.
This will open a browser window for you to authorize and get the token.
"""

import webbrowser
from urllib.parse import urlparse, parse_qs
import configparser
import os

def generate_access_token():
    """Generate access token manually"""
    
    # Read config to get API key
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_key = config.get('KITE_API', 'api_key')
    print(f"📋 Using API Key: {api_key}")
    
    # Step 1: Open authorization URL
    auth_url = f"https://kite.zerodha.com/connect/login?api_key={api_key}&v=3"
    
    print("\n🔗 Step 1: Opening authorization URL...")
    print(f"URL: {auth_url}")
    
    # Try to open in browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("📋 Please manually copy and open this URL in your browser:")
        print(auth_url)
    
    print("\n📋 Step 2: Follow these steps:")
    print("1. Login with your Zerodha credentials in the opened browser")
    print("2. Authorize the application") 
    print("3. You will be redirected to a URL that looks like:")
    print("   http://127.0.0.1:8080/?request_token=XXXXXX&action=login&status=success")
    print("4. Copy the ENTIRE redirect URL from your browser address bar")
    
    # Step 3: Get the redirect URL from user
    print("\n🔗 Step 3: Enter the redirect URL")
    redirect_url = input("Paste the complete redirect URL here: ").strip()
    
    # Step 4: Extract request token
    try:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'request_token' in query_params:
            request_token = query_params['request_token'][0]
            print(f"\n✅ Request Token extracted: {request_token}")
            
            # Step 5: Update config.ini
            print("\n💾 Step 4: Updating config.ini...")
            config.set('KITE_API', 'access_token', request_token)
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
            print("✅ config.ini updated successfully!")
            print(f"🔑 Your access token: {request_token}")
            
            print("\n🚀 Next Steps:")
            print("1. Run your trading dashboard:")
            print("   streamlit run simple_trading_dashboard.py")
            print("2. The token should now work for today's trading session")
            print("3. Remember: Access tokens expire daily and need regeneration")
            
            return request_token
            
        else:
            print("❌ Error: request_token not found in URL")
            print("Make sure you copied the complete redirect URL")
            return None
            
    except Exception as e:
        print(f"❌ Error processing URL: {e}")
        return None

def verify_token():
    """Verify if the current token works"""
    try:
        from kite_api_client import KiteAPIClient
        
        print("\n🧪 Testing token...")
        client = KiteAPIClient()
        kite = client.get_kite_client()
        
        if kite:
            profile = kite.profile()
            print(f"✅ Token is valid! Connected as: {profile.get('user_name', 'Unknown')}")
            return True
        else:
            print("❌ Token is invalid or expired")
            return False
            
    except Exception as e:
        print(f"❌ Token test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔑 Manual Access Token Generator")
    print("=" * 50)
    
    # Check if config.ini exists
    if not os.path.exists('config.ini'):
        print("❌ config.ini not found!")
        print("Please make sure you have a config.ini file with your API credentials")
        return
    
    # Check current token
    print("\n🔍 Checking current token...")
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    current_token = config.get('KITE_API', 'access_token', fallback='')
    
    if current_token and current_token != 'YOUR_ACTUAL_TOKEN_FROM_STEP_1':
        print(f"Current token: {current_token[:10]}...")
        
        # Test current token
        if verify_token():
            print("✅ Current token is working!")
            
            choice = input("\nDo you want to generate a new token? (y/N): ").lower()
            if choice != 'y':
                print("👍 Using existing token")
                return
        else:
            print("❌ Current token is not working, generating new one...")
    else:
        print("⚠️ No valid token found, generating new one...")
    
    # Generate new token
    token = generate_access_token()
    
    if token:
        print("\n🎉 Token generation completed successfully!")
        
        # Final verification
        if verify_token():
            print("🚀 Ready to trade! You can now run your dashboard.")
        else:
            print("⚠️ Token generated but verification failed. Please try again.")
    else:
        print("\n❌ Token generation failed. Please try again.")

if __name__ == "__main__":
    main()