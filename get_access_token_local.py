#!/usr/bin/env python3
"""
🔑 LOCAL ACCESS TOKEN GENERATOR
=============================

Simple HTTP server to handle Kite Connect OAuth flow locally.
This avoids HTTPS issues with Streamlit and generates access tokens properly.
"""

import os
import sys
import webbrowser
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from configparser import ConfigParser
import json
from kiteconnect import KiteConnect

class TokenHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Kite"""
    
    def do_GET(self):
        """Handle GET request with authorization code"""
        try:
            # Parse URL and extract request_token
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'request_token' in query_params:
                request_token = query_params['request_token'][0]
                print(f"\n✅ Received request_token: {request_token}")
                
                # Store the token for processing
                self.server.request_token = request_token
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Token Received Successfully</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
                        .success { color: #28a745; font-size: 24px; }
                        .token { background: #f8f9fa; padding: 20px; margin: 20px; border-radius: 8px; }
                    </style>
                </head>
                <body>
                    <div class="success">✅ Authorization Successful!</div>
                    <div class="token">
                        <h3>Request Token Received:</h3>
                        <code>{}</code>
                    </div>
                    <p>You can close this window now. Check your terminal for the access token.</p>
                </body>
                </html>
                """.format(request_token)
                
                self.wfile.write(success_html.encode())
                
            else:
                # Handle error or missing token
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Token Generation Error</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
                        .error { color: #dc3545; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <div class="error">❌ No request token found!</div>
                    <p>Please try the authorization process again.</p>
                </body>
                </html>
                """
                
                self.wfile.write(error_html.encode())
                
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def generate_access_token():
    """Generate access token using local HTTP server"""
    
    print("🔑 KITE CONNECT ACCESS TOKEN GENERATOR")
    print("=" * 50)
    
    # Load configuration
    config = ConfigParser()
    config_path = "/Users/rubeenakhan/Downloads/Turtel trader/config.ini"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    config.read(config_path)
    
    # Get API credentials
    api_key = config.get('KITE_API', 'api_key')
    api_secret = config.get('KITE_API', 'api_secret')
    
    print(f"📋 API Key: {api_key}")
    print(f"🔐 API Secret: {'*' * len(api_secret)}")
    
    # Start local HTTP server
    port = 8080
    server = HTTPServer(('localhost', port), TokenHandler)
    server.request_token = None
    
    # Create redirect URL
    redirect_url = f"http://localhost:{port}"
    
    # Create Kite Connect instance
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    
    print(f"\n🌐 Starting local server on port {port}...")
    print(f"🔗 Redirect URL: {redirect_url}")
    print(f"\n📱 Opening browser for Kite login...")
    print(f"🔗 Login URL: {login_url}")
    
    # Open browser for login
    webbrowser.open(login_url)
    
    print(f"\n⏳ Waiting for authorization callback...")
    print(f"💡 After logging in, you'll be redirected to localhost:{port}")
    print(f"🔄 Server will automatically capture the request token...")
    
    # Handle one request (the callback)
    try:
        server.handle_request()
        
        if server.request_token:
            print(f"\n🔄 Processing request token...")
            
            # Generate access token
            data = kite.generate_session(server.request_token, api_secret=api_secret)
            access_token = data["access_token"]
            
            print(f"\n🎉 SUCCESS! Access token generated:")
            print(f"🔑 Access Token: {access_token}")
            
            # Update config file
            config.set('KITE_API', 'access_token', access_token)
            
            with open(config_path, 'w') as f:
                config.write(f)
            
            print(f"\n💾 Updated config.ini with new access token")
            print(f"✅ Your trading system is now ready to go live!")
            
            # Test the connection
            print(f"\n🧪 Testing API connection...")
            kite.set_access_token(access_token)
            
            try:
                profile = kite.profile()
                print(f"👤 Connected as: {profile['user_name']} ({profile['email']})")
                
                margins = kite.margins()
                available_cash = margins['equity']['available']['cash']
                print(f"💰 Available Cash: ₹{available_cash:,.2f}")
                
                print(f"\n🚀 System is ready for live trading!")
                return True
                
            except Exception as e:
                print(f"⚠️  Token generated but connection test failed: {e}")
                print(f"💡 Token might still be valid - try running the dashboard")
                return True
                
        else:
            print(f"❌ No request token received. Please try again.")
            return False
            
    except KeyboardInterrupt:
        print(f"\n🛑 Process interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
    finally:
        server.server_close()

if __name__ == "__main__":
    success = generate_access_token()
    
    if success:
        print(f"\n" + "="*50)
        print(f"🎯 NEXT STEPS:")
        print(f"1. Run: streamlit run trading_dashboard.py --server.port 8052")
        print(f"2. Open: http://localhost:8052")
        print(f"3. Start trading with live data!")
        print(f"="*50)
    else:
        print(f"\n❌ Token generation failed. Please check your credentials and try again.")
    
    input("\nPress Enter to exit...")