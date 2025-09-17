"""
Smart Session Token Manager
Automatically manages session tokens with intelligent caching and renewal
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Optional
import requests

class SmartSessionManager:
    """Smart session token manager with auto-renewal and caching"""
    
    def __init__(self):
        self.cache_file = '.session_cache.json'
        self.api_key = "3K8G69248187o756165f6_602IdJ2m80"
        self.api_secret = "8sq5o9660813T8)n4LC&nl09x75t9412"
        
    def get_session_token(self) -> str:
        """Get a valid session token (cached or prompt for new)"""
        
        # Try to load cached token
        cached_token = self._load_cached_token()
        if cached_token and self._is_token_valid(cached_token):
            return cached_token['token']
        
        # Token expired or doesn't exist - need new one
        return self._get_fresh_token()
    
    def _load_cached_token(self) -> Optional[dict]:
        """Load cached token from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def _is_token_valid(self, token_data: dict) -> bool:
        """Check if cached token is still valid"""
        try:
            expiry = datetime.fromisoformat(token_data['expiry'])
            # Add 30 minute buffer before expiry
            return datetime.now() < (expiry - timedelta(minutes=30))
        except Exception:
            return False
    
    def _get_fresh_token(self) -> str:
        """Get fresh session token"""
        
        # In Streamlit app, show user-friendly instructions
        if hasattr(st, 'session_state'):
            return self._streamlit_token_input()
        else:
            return self._console_token_input()
    
    def _streamlit_token_input(self) -> str:
        """Streamlit interface for token input"""
        
        st.warning("🔑 Session Token Required")
        
        # Show instructions
        with st.expander("📋 How to get a new session token", expanded=True):
            st.markdown(f"""
            **Quick Steps:**
            1. 🔗 **Click this link**: [Get Session Token](https://api.icicidirect.com/apiuser/login?api_key={self.api_key})
            2. 🔐 **Login** with your ICICI Direct credentials:
               - Username: `8089000967`
               - Password: `Turtletrader@1`
            3. 📋 **Copy the session token** from the URL after login
            4. ✅ **Paste it below**
            
            **Example URL after login:**
            `http://localhost:8080/callback?apisession=YOUR_TOKEN_HERE`
            """)
        
        # Token input
        new_token = st.text_input(
            "🎫 Enter Session Token:",
            placeholder="e.g., 53038123",
            help="Paste the session token from the callback URL"
        )
        
        if st.button("💾 Save Token", key="save_token_btn"):
            if new_token:
                self._save_token(new_token)
                st.success("✅ Token saved successfully!")
                st.rerun()
            else:
                st.error("❌ Please enter a valid token")
        
        # Return existing token if available, else empty
        cached = self._load_cached_token()
        return cached['token'] if cached else ""
    
    def _console_token_input(self) -> str:
        """Console interface for token input"""
        print(f"\n🔑 Session Token Required")
        print(f"1. Go to: https://api.icicidirect.com/apiuser/login?api_key={self.api_key}")
        print(f"2. Login with: Username=8089000967, Password=Turtletrader@1")
        print(f"3. Copy token from callback URL")
        
        token = input("Enter session token: ").strip()
        if token:
            self._save_token(token)
        return token
    
    def _save_token(self, token: str):
        """Save token with expiry time"""
        token_data = {
            'token': token,
            'created': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(hours=8)).isoformat(),  # 8 hour expiry
            'api_key': self.api_key
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            print(f"✅ Token cached until {token_data['expiry']}")
        except Exception as e:
            print(f"⚠️ Could not cache token: {e}")

class PermanentBreezeClient:
    """Breeze client with permanent session management"""
    
    def __init__(self):
        self.session_manager = SmartSessionManager()
        self.breeze = None
        
    def get_connection(self):
        """Get authenticated Breeze connection"""
        try:
            from breeze_connect import BreezeConnect
            
            # Get valid session token
            session_token = self.session_manager.get_session_token()
            
            if not session_token:
                raise Exception("No valid session token available")
            
            # Create connection
            self.breeze = BreezeConnect(api_key=self.session_manager.api_key)
            self.breeze.generate_session(
                api_secret=self.session_manager.api_secret,
                session_token=session_token
            )
            
            return self.breeze
            
        except Exception as e:
            print(f"Connection error: {e}")
            return None
    
    def get_account_balance(self) -> Optional[float]:
        """Get account balance with automatic session handling"""
        try:
            connection = self.get_connection()
            if connection:
                funds = connection.get_funds()
                if funds and 'Success' in funds:
                    return float(funds['Success'].get('cash_balance', 0))
            return None
        except Exception as e:
            print(f"Balance fetch error: {e}")
            return None

# Global instance for easy use
permanent_client = PermanentBreezeClient()