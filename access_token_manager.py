"""
Kite Access Token Manager
Handles daily token refresh and management from dashboard
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger
import streamlit as st
from kiteconnect import KiteConnect

from core.config import get_config, config

class AccessTokenManager:
    """Manages Kite API access tokens with dashboard integration"""
    
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.get('KITE_API', 'api_key')
        self.api_secret = self.config.get('KITE_API', 'api_secret')
        self.token_file = "data/access_token.json"
        self.kite = None
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize KiteConnect
        if self.api_key:
            self.kite = KiteConnect(api_key=self.api_key)
    
    def get_login_url(self) -> str:
        """Get Kite login URL for token generation"""
        if not self.kite:
            raise ValueError("KiteConnect not initialized. Check API key.")
        
        login_url = self.kite.login_url()
        logger.info("Generated Kite login URL")
        return login_url
    
    def generate_access_token(self, request_token: str) -> Dict[str, str]:
        """Generate access token from request token"""
        try:
            if not self.kite or not self.api_secret:
                raise ValueError("KiteConnect or API secret not available")
            
            # Generate session
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            
            access_token = data["access_token"]
            user_id = data["user_id"]
            
            # Save token with metadata
            token_data = {
                "access_token": access_token,
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=1)).isoformat(),
                "request_token": request_token
            }
            
            self.save_token_data(token_data)
            self.update_config_token(access_token)
            
            logger.info(f"Access token generated successfully for user {user_id}")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            raise
    
    def save_token_data(self, token_data: Dict) -> None:
        """Save token data to file"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.info("Token data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save token data: {e}")
    
    def load_token_data(self) -> Optional[Dict]:
        """Load token data from file"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load token data: {e}")
        return None
    
    def update_config_token(self, access_token: str) -> None:
        """Update access token in config.ini"""
        try:
            config.set('KITE_API', 'access_token', access_token)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logger.info("Config file updated with new access token")
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
    
    def is_token_valid(self) -> Tuple[bool, Optional[str]]:
        """Check if current token is valid"""
        token_data = self.load_token_data()
        if not token_data:
            return False, "No token data found"
        
        try:
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.now() >= expires_at:
                return False, "Token expired"
            
            # Test token by making a simple API call
            current_token = token_data["access_token"]
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(current_token)
            
            # Try to get user profile
            kite.profile()
            return True, "Token is valid"
            
        except Exception as e:
            return False, f"Token validation failed: {str(e)}"
    
    def get_token_status(self) -> Dict:
        """Get comprehensive token status"""
        token_data = self.load_token_data()
        is_valid, message = self.is_token_valid()
        
        if not token_data:
            return {
                "valid": False,
                "message": "No token found",
                "expires_at": None,
                "user_id": None,
                "generated_at": None
            }
        
        return {
            "valid": is_valid,
            "message": message,
            "expires_at": token_data.get("expires_at"),
            "user_id": token_data.get("user_id"),
            "generated_at": token_data.get("generated_at"),
            "access_token": token_data.get("access_token")[:10] + "..." if token_data.get("access_token") else None
        }
    
    def render_token_dashboard(self) -> None:
        """Render token management UI in Streamlit"""
        st.header("🔐 Access Token Management")
        
        # Get current token status
        status = self.get_token_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Token Status")
            if status["valid"]:
                st.success(f"✅ {status['message']}")
                if status["expires_at"]:
                    expires_at = datetime.fromisoformat(status["expires_at"])
                    time_left = expires_at - datetime.now()
                    st.info(f"⏰ Expires in: {time_left}")
            else:
                st.error(f"❌ {status['message']}")
            
            if status["user_id"]:
                st.info(f"👤 User ID: {status['user_id']}")
            
            if status["generated_at"]:
                generated_at = datetime.fromisoformat(status["generated_at"])
                st.info(f"🕒 Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.subheader("Generate New Token")
            
            if st.button("🔗 Get Login URL", key="get_login_url"):
                try:
                    login_url = self.get_login_url()
                    st.success("✅ Login URL generated!")
                    st.code(login_url)
                    st.markdown(f"[🔗 Click here to login]({login_url})")
                    
                    st.info("📝 Steps:")
                    st.write("1. Click the login URL above")
                    st.write("2. Login to your Kite account")
                    st.write("3. Copy the request_token from the URL")
                    st.write("4. Paste it below and click Generate Token")
                    
                except Exception as e:
                    st.error(f"❌ Failed to generate login URL: {e}")
            
            st.markdown("---")
            
            # Request token input
            request_token = st.text_input(
                "📋 Request Token",
                placeholder="Paste request token from Kite login URL",
                help="After logging in to Kite, copy the 'request_token' parameter from the URL"
            )
            
            if st.button("🎯 Generate Access Token", key="generate_token"):
                if request_token:
                    try:
                        with st.spinner("Generating access token..."):
                            token_data = self.generate_access_token(request_token)
                        
                        st.success("🎉 Access token generated successfully!")
                        st.balloons()
                        
                        # Show token details
                        st.json({
                            "user_id": token_data["user_id"],
                            "generated_at": token_data["generated_at"],
                            "expires_at": token_data["expires_at"]
                        })
                        
                        # Auto-refresh the page to update status
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate token: {e}")
                        st.error("Please check your API credentials and request token")
                else:
                    st.warning("⚠️ Please enter a request token")
        
        st.markdown("---")
        
        # Daily refresh reminder
        st.subheader("📅 Daily Refresh Reminder")
        if status["valid"] and status["expires_at"]:
            expires_at = datetime.fromisoformat(status["expires_at"])
            hours_left = (expires_at - datetime.now()).total_seconds() / 3600
            
            if hours_left < 24:
                if hours_left < 2:
                    st.error(f"🚨 Token expires in {hours_left:.1f} hours! Refresh immediately!")
                elif hours_left < 6:
                    st.warning(f"⚠️ Token expires in {hours_left:.1f} hours. Please refresh soon.")
                else:
                    st.info(f"ℹ️ Token expires in {hours_left:.1f} hours.")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh page every 30 seconds", key="auto_refresh_token")
        if auto_refresh:
            st.experimental_rerun()
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection with current token"""
        try:
            status = self.get_token_status()
            if not status["valid"]:
                return False, status["message"]
            
            # Test with actual API call
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(status["access_token"].replace("...", ""))
            
            profile = kite.profile()
            return True, f"Connected successfully as {profile['user_name']} ({profile['user_id']})"
            
        except Exception as e:
            return False, f"Connection test failed: {e}"

# Create global instance
access_token_manager = AccessTokenManager()

if __name__ == "__main__":
    print("🔐 ACCESS TOKEN MANAGER")
    print("=" * 40)
    
    status = access_token_manager.get_token_status()
    print(f"Token Valid: {status['valid']}")
    print(f"Message: {status['message']}")
    
    if status['valid']:
        is_connected, message = access_token_manager.test_connection()
        print(f"API Connection: {message}")