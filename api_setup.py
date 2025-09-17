"""
Turtle Trader - API Setup Helper
Script to test ICICI Breeze API connection and generate session tokens
"""

from breeze_connect import BreezeConnect
import sys

def test_api_connection():
    """Test API connection with credentials"""
    
    print("=" * 60)
    print("TURTLE TRADER - API SETUP HELPER")
    print("=" * 60)
    
    # Get credentials from user
    api_key = input("Enter your API Key: ").strip()
    api_secret = input("Enter your API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("❌ API Key and Secret are required!")
        return False
    
    try:
        # Initialize Breeze Connect
        breeze = BreezeConnect(api_key=api_key)
        
        print("\n🔄 Attempting to generate session...")
        
        # Generate session - this will open a browser window for login
        session = breeze.generate_session(api_secret=api_secret, 
                                        source="WEB")
        
        if session and 'Success' in session:
            print("✅ Session generated successfully!")
            print(f"📄 Session Details: {session}")
            
            # Test API call
            print("\n🔄 Testing API connection...")
            profile = breeze.get_customer_details()
            
            if profile and 'Success' in profile:
                print("✅ API connection successful!")
                print(f"👤 Customer Details: {profile}")
                
                # Extract session token
                if 'session_token' in session:
                    session_token = session['session_token']
                    print(f"\n🔑 Your Session Token: {session_token}")
                    
                    # Update config file
                    update_config_file(api_key, api_secret, session_token)
                    
                return True
            else:
                print(f"❌ API test failed: {profile}")
                return False
        else:
            print(f"❌ Session generation failed: {session}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_config_file(api_key, api_secret, session_token):
    """Update config.ini with API credentials"""
    
    config_path = "config.ini"
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace("API_KEY = your_api_key_here", f"API_KEY = {api_key}")
        content = content.replace("API_SECRET = your_api_secret_here", f"API_SECRET = {api_secret}")
        content = content.replace("SESSION_TOKEN = your_session_token_here", f"SESSION_TOKEN = {session_token}")
        
        # Write updated config
        with open(config_path, 'w') as f:
            f.write(content)
        
        print(f"\n✅ Configuration updated successfully in {config_path}")
        print("🚀 You can now start the trading system with: python main.py start")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        print("\n📝 Please manually update config.ini with these values:")
        print(f"API_KEY = {api_key}")
        print(f"API_SECRET = {api_secret}")
        print(f"SESSION_TOKEN = {session_token}")

def show_instructions():
    """Show detailed setup instructions"""
    
    print("\n" + "=" * 60)
    print("📋 SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("""
🔐 Your ICICI Direct Login Credentials:
   - Login ID: 8089000967
   - Password: Turtletrader@1

📋 Steps to Get API Credentials:

1. 🌐 Go to: https://secure.icicidirect.com/
2. 🔑 Login with your credentials above
3. 🛠️  Navigate to Settings → API or Developer Console
4. ➕ Create new API application
5. 📝 Note down API Key and API Secret
6. ▶️  Run this script again with those credentials

⚠️  IMPORTANT NOTES:
   - API credentials are different from login credentials
   - Session tokens expire (usually 24 hours)
   - Keep your credentials secure
   - Test in paper trading mode first

💡 For detailed API documentation:
   https://api.icicidirect.com/breezeapi/documents/index.html
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "instructions":
        show_instructions()
    else:
        print("Choose an option:")
        print("1. Test API connection with credentials")
        print("2. Show setup instructions")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            if test_api_connection():
                print("\n🎉 Setup complete! Your trading system is ready.")
            else:
                print("\n⚠️  Setup failed. Please check your credentials and try again.")
                show_instructions()
        elif choice == "2":
            show_instructions()
        else:
            print("Invalid choice. Run: python api_setup.py instructions")
