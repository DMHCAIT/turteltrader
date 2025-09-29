# 🔑 GET KITE ACCESS TOKEN - STEP BY STEP

## **Method 1: Manual Token Generation (Recommended for Daily Use)**

### Step 1: Visit Kite Connect Login URL
Open this URL in your browser:
```
https://kite.zerodha.com/connect/login?api_key=i0bd6xlyqau3ivqe&v=3
```

### Step 2: Login to Zerodha
- Enter your Zerodha User ID and Password
- Complete 2FA (TOTP/PIN)
- Click "Authorize" when prompted

### Step 3: Extract Request Token
After authorization, you'll be redirected to a URL like:
```
https://127.0.0.1:8080/?request_token=XXXXXX&action=login&status=success
```

**Copy the `request_token` value (the XXXXXX part)**

### Step 4: Generate Access Token
Run this command in terminal:

```python
from kiteconnect import KiteConnect

api_key = "i0bd6xlyqau3ivqe"
api_secret = "s2x3rpgijq921qmjgcerzqj3x6tkge6p"
request_token = "PASTE_YOUR_REQUEST_TOKEN_HERE"

kite = KiteConnect(api_key=api_key)
data = kite.generate_session(request_token, api_secret=api_secret)
print(f"Access Token: {data['access_token']}")
```

### Step 5: Update Config
Copy the access token and update `config.ini`:
```ini
access_token = YOUR_GENERATED_ACCESS_TOKEN
```

---

## **Method 2: Use the Dashboard Token Manager**
1. Run the dashboard locally first: `streamlit run trading_dashboard.py`
2. Go to "Access Token Manager" tab
3. Follow the guided process
4. Copy the generated token to `config.ini`

---

## **For Streamlit Cloud Deployment:**
You'll need to set these as **Secrets** in Streamlit Cloud:

```toml
[KITE_API]
api_key = "i0bd6xlyqau3ivqe"
api_secret = "s2x3rpgijq921qmjgcerzqj3x6tkge6p"
access_token = "YOUR_GENERATED_ACCESS_TOKEN"
```

⚠️ **Important:** Access tokens expire daily and need to be regenerated!