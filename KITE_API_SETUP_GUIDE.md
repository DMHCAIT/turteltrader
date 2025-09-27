# 🚀 KITE API SETUP GUIDE - ZERODHA INTEGRATION
=========================================

## 📋 OVERVIEW
Your Turtle Trader now uses **Kite Connect API** from Zerodha for:
- ✅ Real-time market data
- ✅ Live portfolio tracking  
- ✅ Automated order execution
- ✅ Account balance monitoring

## 🔑 STEP 1: GET KITE CONNECT CREDENTIALS

### 1.1 Create Zerodha Account
- Open account at: https://zerodha.com/
- Complete KYC and account activation
- Note your User ID and Password

### 1.2 Get API Credentials
1. **Login to Kite Connect Console**: https://developers.kite.trade/
2. **Create New App**:
   - App Type: `Connect`
   - App Name: `Turtle Trader Bot`
   - Redirect URL: `http://127.0.0.1:8080/callback`
3. **Get Credentials**:
   - `API Key`: Copy from console
   - `API Secret`: Copy from console

## 🔧 STEP 2: UPDATE CONFIGURATION

### 2.1 Edit config.ini
```ini
[KITE_API]
api_key = your_api_key_here
api_secret = your_api_secret_here  
access_token = 
base_url = https://api.kite.trade
```

### 2.2 Configuration Details
- **api_key**: Your Kite Connect API key
- **api_secret**: Your Kite Connect API secret
- **access_token**: Leave empty (will be generated)
- **base_url**: Kite API endpoint (don't change)

## 🔐 STEP 3: AUTHENTICATION PROCESS

### 3.1 First-Time Login
```python
# Run this to get your access token
from kite_api_client import KiteAPIClient

client = KiteAPIClient()

# This will open browser for login
login_url = f"https://kite.trade/connect/login?api_key={client.api_key}&v=3"
print(f"1. Open: {login_url}")
print("2. Login with your Zerodha credentials")
print("3. Copy 'request_token' from redirect URL")

request_token = input("Enter request token: ")
access_token = client.generate_session(request_token)
print(f"✅ Access token saved: {access_token}")
```

### 3.2 Redirect URL Format
After login, you'll be redirected to:
```
http://127.0.0.1:8080/callback?request_token=YOUR_TOKEN&action=login&status=success
```
Copy the `request_token` value.

## 🎯 STEP 4: VERIFY CONNECTION

### 4.1 Test API Connection
```python
from kite_api_client import KiteAPIClient

client = KiteAPIClient()
if client.test_connection():
    print("✅ Kite API connected successfully!")
    
    # Test basic functions
    profile = client.get_profile()
    funds = client.get_funds()
    print(f"User: {profile['user_id']}")
    print(f"Available: ₹{funds['available']['cash']:,.2f}")
else:
    print("❌ Connection failed - check credentials")
```

### 4.2 Test Market Data
```python
# Get live quotes
quotes = client.get_ltp(["NSE:NIFTYBEES", "NSE:BANKBEES"])
print("Live quotes:", quotes)

# Get historical data  
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# You'll need instrument tokens (get from instruments list)
data = client.get_historical_data(
    instrument_token=1234567,  # NIFTYBEES token
    from_date=start_date,
    to_date=end_date,
    interval="day"
)
```

## 📊 STEP 5: INSTRUMENT TOKENS

### 5.1 Get Instrument List
```python
# Download instruments
instruments = client.get_instruments("NSE")
etf_instruments = instruments[instruments['segment'] == 'NFO-OPT']

# Find your ETF tokens
niftybees = instruments[instruments['tradingsymbol'] == 'NIFTYBEES']
print(f"NIFTYBEES token: {niftybees['instrument_token'].iloc[0]}")
```

### 5.2 Common ETF Tokens (Update as needed)
```
NIFTYBEES: 1234567
BANKBEES: 2345678  
GOLDBEES: 3456789
JUNIORBEES: 4567890
```

## ⚠️ IMPORTANT NOTES

### 5.1 Session Management
- **Access tokens expire daily** at 6 AM
- **Auto-refresh not supported** - manual re-login required
- **Rate limits**: 3 requests/second, 1000 requests/minute

### 5.2 Trading Permissions
- Ensure your Zerodha account has **API trading enabled**
- Check **DDPI authorization** for automated orders
- Verify **sufficient margin** for ETF trading

### 5.3 Market Hours
- **Trading**: 9:15 AM - 3:30 PM (Mon-Fri)
- **Historical data**: Available 24/7
- **Live data**: Only during market hours

## 🚀 STEP 6: START LIVE TRADING

### 6.1 Launch Dashboard
```bash
cd "Turtle Trader"
source turtle_env/bin/activate
streamlit run app.py
```

### 6.2 Monitor System
- Dashboard shows **real Zerodha account balance**
- **Live ETF prices** from Kite API
- **Automated trading signals** based on turtle strategy
- **Real order execution** on Zerodha platform

## 🔧 TROUBLESHOOTING

### Common Issues:
1. **"Token expired"**: Re-run authentication process
2. **"Invalid API key"**: Check console credentials
3. **"Insufficient funds"**: Add money to Zerodha account
4. **"Order rejected"**: Check ETF availability and limits

### Support:
- **Kite Connect Docs**: https://kite.trade/docs/
- **Zerodha Support**: https://support.zerodha.com/
- **API Status**: https://status.zerodha.com/

---
**🎉 Your Turtle Trader is now powered by Zerodha Kite Connect API!**