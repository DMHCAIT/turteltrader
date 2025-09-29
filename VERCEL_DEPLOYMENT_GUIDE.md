# ETF Trading Dashboard - Vercel Deployment Guide

## Overview
This is a Flask-based ETF trading dashboard that can be deployed on Vercel. It removes the Streamlit dependency and provides a web interface for managing your trading system.

## Features
- ✅ **Manual Access Token Management** - No automatic token generation, you manually configure tokens
- ✅ **Real-time ETF Monitoring** - Track multiple ETF symbols and prices
- ✅ **Account Balance Integration** - View real Kite account balance
- ✅ **Clean Web Interface** - Modern Bootstrap-based responsive design
- ✅ **Vercel Ready** - Optimized for Vercel deployment

## Local Development

### 1. Install Dependencies
```bash
pip install Flask pandas plotly werkzeug
```

### 2. Configure Your API Credentials
Update your `config.ini` file:
```ini
[KITE_API]
api_key = i0bd6xlyqau3ivqe
api_secret = s2x3rpgijq921qmjgcerzqj3x6tkge6p
access_token = YOUR_DAILY_ACCESS_TOKEN
```

### 3. Run Locally
```bash
python flask_app.py
```

Visit: `http://localhost:5001`

## How to Get Access Token

### Method 1: Manual Browser Method
1. Visit: `https://kite.zerodha.com/connect/login?api_key=i0bd6xlyqau3ivqe&v=3`
2. Login with your Zerodha credentials
3. Authorize the application
4. From the redirect URL, copy the `request_token` parameter
5. Use the Configuration page in the dashboard to update the token

### Method 2: Use the Dashboard
1. Go to the Configuration page (`/config`)
2. Click "Open Authorization URL"
3. Complete the authorization process
4. Paste the request token in the form
5. Click "Update Token"

## Vercel Deployment

### 1. Prepare Your Repository
Make sure your repository has these files:
- `flask_app.py` (main application)
- `vercel.json` (Vercel configuration)
- `requirements_vercel.txt` (Python dependencies)
- `templates/` folder with HTML templates
- `config.ini` (your API configuration)

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Connect your GitHub repository
4. Vercel will auto-detect it's a Python project
5. Deploy!

### 3. Environment Configuration
After deployment, you'll need to:
1. Visit your deployed app
2. Go to `/config` page
3. Configure your access token using the web interface

## Project Structure

```
├── flask_app.py              # Main Flask application
├── vercel.json              # Vercel deployment config
├── requirements_vercel.txt   # Python dependencies for Vercel
├── config.ini               # API configuration
├── templates/
│   ├── dashboard.html       # Main dashboard
│   ├── config.html          # Configuration page
│   ├── 404.html             # Error pages
│   └── 500.html
├── kite_api_client.py       # Your existing Kite API client
├── etf_database.py          # ETF database
├── dynamic_capital_allocator.py  # Capital management
└── real_account_balance.py  # Balance management
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /config` - Configuration page
- `GET /api/status` - API connection status
- `GET /api/balance` - Account balance
- `GET /api/etfs` - ETF list
- `GET /api/config` - Current configuration
- `POST /api/update-token` - Update access token
- `GET /api/chart-data` - Chart data for dashboard

## Key Differences from Streamlit

1. **No Real-time Auto-refresh** - Dashboard updates when you refresh the page
2. **Manual Token Management** - You configure tokens through web interface
3. **RESTful API Design** - All data comes from API endpoints
4. **Traditional Web App** - Uses forms and AJAX instead of Streamlit widgets
5. **Better Mobile Support** - Responsive Bootstrap design

## Daily Workflow

1. **Morning**: Generate new access token and update via Configuration page
2. **Trading**: Use the dashboard to monitor ETFs and account balance
3. **Evening**: Review trades and performance

## Troubleshooting

### Common Issues

1. **"Trading modules not available"**
   - This is normal if your trading modules aren't uploaded to Vercel
   - The dashboard will work with mock data for demo purposes

2. **"Invalid credentials or expired token"**
   - Access tokens expire daily at 6 AM
   - Generate a new token using the Configuration page

3. **Vercel deployment fails**
   - Check that `requirements_vercel.txt` only has essential packages
   - Make sure `vercel.json` is properly configured

### Production Considerations

1. **Security**: Change the Flask secret key in production
2. **Logging**: Add proper logging for production debugging
3. **Error Handling**: Add more robust error handling for edge cases
4. **Performance**: Consider adding caching for API responses

## Success Indicators

✅ Flask app runs locally on http://localhost:5001  
✅ Configuration page allows token management  
✅ Dashboard shows ETF data and account balance  
✅ Vercel deployment completes successfully  
✅ Production app accessible via Vercel URL  

## Next Steps

1. Test the local Flask app
2. Push code to your GitHub repository
3. Deploy to Vercel
4. Configure your access token via the web interface
5. Start trading with your new web-based dashboard!