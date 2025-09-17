"""
Automatic Session Token Manager for ICICI Breeze API
Handles automatic login and session token generation
"""

import requests
import time
from datetime import datetime, timedelta
import json
import os
from typing import Optional, Dict, Any

class AutoSessionManager:
    """Manages automatic session token generation for Breeze API"""
    
    def __init__(self, api_key: str, api_secret: str, username: str, password: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.password = password
        self.session_token = None
        self.token_expiry = None
        self.base_url = "https://api.icicidirect.com"
        
    def auto_login(self) -> Optional[str]:
        """
        Automatically login and generate session token
        Returns: session token if successful, None if failed
        """
        try:
            # Step 1: Get login URL
            login_url = f"{self.base_url}/apiuser/login?api_key={self.api_key}"
            
            # Step 2: Prepare login payload
            login_data = {
                'user_id': self.username,
                'password': self.password,
                'api_key': self.api_key
            }
            
            # Step 3: Submit login
            session = requests.Session()
            response = session.post(login_url, data=login_data, allow_redirects=False)
            
            # Step 4: Extract session token from redirect
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if 'apisession=' in redirect_url:
                    self.session_token = redirect_url.split('apisession=')[1].split('&')[0]
                    self.token_expiry = datetime.now() + timedelta(hours=8)  # Tokens usually last 8 hours
                    self.save_session_token()
                    return self.session_token
            
            print(f"Login failed. Status: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Auto login error: {str(e)}")
            return None
    
    def get_valid_session_token(self) -> Optional[str]:
        """
        Get a valid session token (generate new one if expired)
        """
        # Check if we have a saved token that's still valid
        if self.load_session_token():
            if self.token_expiry and datetime.now() < self.token_expiry:
                return self.session_token
        
        # Generate new token
        print("🔄 Generating new session token...")
        return self.auto_login()
    
    def save_session_token(self):
        """Save session token to file"""
        try:
            token_data = {
                'session_token': self.session_token,
                'expiry': self.token_expiry.isoformat() if self.token_expiry else None,
                'generated_at': datetime.now().isoformat()
            }
            
            with open('.session_cache.json', 'w') as f:
                json.dump(token_data, f)
                
        except Exception as e:
            print(f"Error saving session token: {e}")
    
    def load_session_token(self) -> bool:
        """Load session token from file"""
        try:
            if os.path.exists('.session_cache.json'):
                with open('.session_cache.json', 'r') as f:
                    token_data = json.load(f)
                
                self.session_token = token_data.get('session_token')
                expiry_str = token_data.get('expiry')
                
                if expiry_str:
                    self.token_expiry = datetime.fromisoformat(expiry_str)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error loading session token: {e}")
            return False

class PermanentBreezeConnection:
    """Permanent Breeze API connection with auto-renewal"""
    
    def __init__(self, api_key: str, api_secret: str, username: str, password: str):
        self.session_manager = AutoSessionManager(api_key, api_secret, username, password)
        self.breeze = None
        
    def get_connection(self):
        """Get a valid Breeze connection (auto-renew if needed)"""
        try:
            from breeze_connect import BreezeConnect
            
            # Get valid session token
            session_token = self.session_manager.get_valid_session_token()
            
            if not session_token:
                raise Exception("Could not obtain valid session token")
            
            # Create connection
            self.breeze = BreezeConnect(api_key=self.session_manager.api_key)
            self.breeze.generate_session(
                api_secret=self.session_manager.api_secret, 
                session_token=session_token
            )
            
            return self.breeze
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            connection = self.get_connection()
            if connection:
                # Try a simple API call
                result = connection.get_customer_detail()
                return result is not None
            return False
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Usage Example
if __name__ == "__main__":
    # Your credentials
    API_KEY = "3K8G69248187o756165f6_602IdJ2m80"
    API_SECRET = "8sq5o9660813T8)n4LC&nl09x75t9412"
    USERNAME = "your_icici_username"  # Your ICICI login username
    PASSWORD = "your_icici_password"  # Your ICICI login password
    
    # Create permanent connection
    perm_connection = PermanentBreezeConnection(API_KEY, API_SECRET, USERNAME, PASSWORD)
    
    # Test connection
    if perm_connection.test_connection():
        print("✅ Permanent connection established successfully!")
    else:
        print("❌ Failed to establish permanent connection")