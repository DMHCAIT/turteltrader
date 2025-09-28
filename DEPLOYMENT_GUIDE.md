# Streamlit Cloud Deployment Configuration

## Required Files for Public Hosting

### .streamlit/config.toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

### .streamlit/secrets.toml (For Streamlit Cloud)
[KITE_API]
api_key = "your_kite_api_key_here"
api_secret = "your_kite_api_secret_here"
access_token = "will_be_updated_daily"

[TRADING]
capital = 500000
demo_mode = false
max_positions = 8

### requirements.txt (Already exists - verify these packages)
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
kiteconnect>=4.0.0
loguru>=0.7.0
python-dateutil>=2.8.0

## Deployment Steps:

### 1. GitHub Repository Setup
1. Push your code to GitHub (repository: turteltrader)
2. Ensure all files are committed
3. Make repository public or give Streamlit access

### 2. Streamlit Cloud Deployment
1. Go to https://share.streamlit.io/
2. Connect your GitHub account
3. Deploy from repository: DMHCAIT/turteltrader
4. Set main file: trading_dashboard.py
5. Add environment variables in Streamlit Cloud settings

### 3. Environment Variables (Set in Streamlit Cloud)
KITE_API_KEY = "your_kite_api_key"
KITE_API_SECRET = "your_kite_api_secret"

### 4. Daily Token Update Process
The dashboard will have a dedicated "Token Management" section where you can:
- Generate login URL
- Update access token daily
- Monitor token expiry
- Test API connection

### 5. Alternative Hosting Options:

#### A. Heroku Deployment
- More control over environment
- Can use scheduler for automated tasks
- Supports file storage

#### B. Railway Deployment
- Simple deployment from GitHub
- Auto-deploys on code changes
- Good for long-running apps

#### C. Render Deployment
- Free tier available
- Easy GitHub integration
- Good performance

### 6. Security Considerations:
1. Never commit API secrets to GitHub
2. Use environment variables
3. Regularly rotate access tokens
4. Monitor API usage

### 7. Monitoring and Maintenance:
- Check token expiry daily
- Monitor API rate limits
- Regular system health checks
- Backup important data