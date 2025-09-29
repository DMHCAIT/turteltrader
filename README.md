# ETF Trading Dashboard

A Flask-based ETF trading dashboard that can be deployed on Vercel. This application provides real-time ETF monitoring, account balance tracking, and manual access token management.

## Features

- 🚀 **Flask Web Application** - No Streamlit dependency
- 📊 **Real-time ETF Monitoring** - Track multiple ETF symbols
- 💰 **Account Balance Integration** - View live Kite account balance
- 🔧 **Manual Token Management** - Simple web interface for daily tokens
- 📱 **Mobile Responsive** - Bootstrap-based modern UI
- ☁️ **Vercel Ready** - Optimized for cloud deployment

## Quick Start

### 1. Configure API Credentials

Update your `config.ini` file:
```ini
[KITE_API]
api_key = your_api_key
api_secret = your_api_secret
access_token = your_daily_access_token
```

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python flask_app.py
```

Visit: `http://localhost:5001`

### 3. Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/DMHCAIT/turteltrader)

Or manually:
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Import your GitHub repository
3. Deploy automatically

## Project Structure

```
├── flask_app.py              # Main Flask application
├── index.py                  # Vercel entry point
├── vercel.json              # Vercel deployment config
├── requirements.txt         # Python dependencies
├── config.ini               # API configuration
├── templates/               # HTML templates
│   ├── dashboard.html       # Main dashboard
│   └── config.html          # Token configuration
├── kite_api_client.py       # Kite API integration
├── etf_database.py          # ETF data management
├── dynamic_capital_allocator.py  # Trading logic
└── real_account_balance.py  # Balance management
```

## API Endpoints

- `GET /` - Main trading dashboard
- `GET /config` - Token management interface
- `GET /api/status` - API connection status
- `GET /api/balance` - Account balance data
- `GET /api/etfs` - ETF information
- `POST /api/update-token` - Update access token

## Daily Workflow

1. **Generate Access Token**: Visit `/config` page and update your daily token
2. **Monitor Markets**: Use the main dashboard to track ETFs
3. **Execute Trades**: Manual trade execution through the interface
4. **Review Performance**: Check account balance and trade history

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Charts**: Plotly.js
- **Deployment**: Vercel
- **Trading API**: Kite Connect

## License

MIT License - See LICENSE file for details