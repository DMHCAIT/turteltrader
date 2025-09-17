"""
🔗 BREEZE API CREATION GUIDE
===========================

STEP-BY-STEP BREEZE API SETUP FOR LIVE TRADING

📋 PREREQUISITES:
✅ ICICI Direct trading account (active)
✅ ICICI Direct login credentials  
✅ Valid PAN card
✅ Mobile number registered with ICICI

🌐 STEP 1: ACCESS API PORTAL
============================

1. 🔗 Go to: https://api.icicidirect.com/apiuser/login
2. 📱 Login with your ICICI Direct credentials:
   - User ID: Your ICICI Direct user ID
   - Password: Your ICICI Direct password
   - Mobile OTP: Enter OTP sent to registered mobile

⚙️ STEP 2: CREATE API APPLICATION
=================================

After login, you'll see the API dashboard:

1. 🆕 Click "Create New App" or "Add Application"
2. 📝 Fill application details:
   
   App Name: "TurtleTrader"
   App Description: "Automated ETF Trading System"
   App Category: "Personal Trading"
   
3. 🌐 Network Configuration:
   IP Address: Enter your current IP
   
   🔍 TO GET YOUR IP:
   - Go to: https://whatismyipaddress.com/
   - Copy the IPv4 address shown
   - Example: 152.58.122.38
   
   💡 TIP: For cloud deployment, use: 0.0.0.0/0
   (This allows access from any IP - needed for Streamlit Cloud)

4. 📋 Select Permissions:
   ✅ Market Data
   ✅ Order Placement  
   ✅ Portfolio
   ✅ Funds
   ✅ Historical Data

5. ✅ Submit application

⏳ STEP 3: APPROVAL PROCESS
==========================

📧 After submission:
- Application goes for review (usually instant for existing customers)
- You'll receive email confirmation
- API credentials will be generated

🔑 STEP 4: GET YOUR CREDENTIALS
==============================

Once approved, you'll get:

1. 🗝️ API Key (Example: 3K8G69248187o756165f6_602IdJ2m80)
2. 🔐 API Secret (Example: 8sq5o9660813T8)n4LC&nl09x75t9412)
3. 📱 You'll need to generate session tokens daily (automated by our system)

🛠️ STEP 5: CONFIGURE IN YOUR SYSTEM
===================================

Update your .streamlit/secrets.toml file:

[BREEZE_API]
API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here" 
USERNAME = "your_icici_username"
PASSWORD = "your_icici_password"
BASE_URL = "https://api.icicidirect.com/breezeapi/api/"

🔧 STEP 6: TEST CONNECTION
=========================

1. 🚀 Run your dashboard: streamlit run app.py
2. 🔄 Click "Refresh Session" in sidebar
3. ✅ Verify connection shows "Active"

⚠️ COMMON ISSUES & SOLUTIONS:
============================

❌ Issue: "IP not whitelisted"
✅ Solution: Add your current IP in API portal settings

❌ Issue: "Invalid credentials"  
✅ Solution: Double-check API key and secret

❌ Issue: "Session expired daily"
✅ Solution: Our smart session manager handles this automatically

❌ Issue: "Permission denied for orders"
✅ Solution: Ensure "Order Placement" permission is enabled

🔴 LIVE TRADING ACTIVATION:
==========================

Once API is working:

1. 🧪 Test in DEMO mode first
2. ✅ Verify all functions work
3. 🔴 Switch to LIVE mode in dashboard
4. ⚠️ Start with small amounts
5. 📊 Monitor positions carefully

💡 SUPPORT CONTACTS:
===================

📞 ICICI Direct API Support: 1800-103-5656
📧 Email: api.support@icicidirect.com  
🌐 Documentation: https://api.icicidirect.com/

🚨 SECURITY REMINDERS:
=====================

🔐 Never share API credentials
🌐 Use secure networks only  
📱 Keep mobile number updated
🔄 Monitor API usage regularly
💰 Set appropriate trading limits

✅ YOU'RE READY FOR LIVE TRADING!
"""