# 🐢 TURTLE TRADER - COMPLETE ETF TRADING SYSTEM

## 🎯 What You Built

A **professional-grade ETF trading system** with custom AI/ML strategy implementation and web dashboard interface.

### � Your Exact Requirements Implemented:

1. **✅ MTF First Preference, CNC Fallback**
   - System checks MTF margin availability first
   - Automatically falls back to CNC if MTF not available
   
2. **✅ 1% Dip Buy Strategy**  
   - Buys ETFs when price drops 1% from yesterday's close
   - Smart entry point detection
   
3. **✅ 3% Profit Target**
   - Automatically sells when position reaches 3% profit
   - Profit maximization with disciplined exit
   
4. **✅ 5% Loss Alert System**
   - Sends alerts when loss reaches 5%
   - Risk management with early warning
   
5. **✅ One Position Per ETF Rule**
   - Prevents multiple positions in same ETF
   - Portfolio diversification enforcement

## 🚀 Launch Your System

### Option 1: Quick Start (Recommended)
```bash
python launcher.py
```

### Option 2: Direct Launch
```bash
# Web Dashboard
streamlit run dashboard.py

# Command Line System  
python main.py start
```

## 📊 System Components

### 🧠 Core Trading Engine
- **`main.py`** - Main trading system with real-time monitoring
- **`custom_strategy.py`** - Your custom ETF strategy implementation
- **`etf_manager.py`** - ETF portfolio and order management

### 🌐 Web Dashboard  
- **`dashboard.py`** - Professional web interface
- **Real-time charts** - Live ETF price monitoring
- **Position tracking** - Current holdings and P&L
- **Strategy controls** - Modify settings on-the-fly

### 📋 Configuration
- **`config.ini`** - All strategy parameters and API settings
- **`etf_symbols.txt`** - ETF symbols to trade
- **`logs/`** - Trading logs and performance data

## 📋 Prerequisites

- Python 3.8 or higher
- ICICI Breeze API credentials
- Windows/Linux/macOS

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Turtel trader"
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv turtle_env
   
   # Windows
   turtle_env\Scripts\activate
   
   # Linux/macOS
   source turtle_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install TA-Lib** (required for technical analysis):
   
   **Windows**:
   - Download TA-Lib from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   - Install: `pip install TA_Lib-0.4.28-cp38-cp38-win_amd64.whl` (adjust for your Python version)
   
   **Linux**:
   ```bash
   sudo apt-get install ta-lib-dev
   pip install TA-Lib
   ```
   
   **macOS**:
   ```bash
   brew install ta-lib
   pip install TA-Lib
   ```

## ⚙️ Configuration

1. **Copy and edit configuration**:
   ```bash
   cp config.ini.example config.ini
   ```

2. **Update `config.ini` with your settings**:
   ```ini
   [API]
   APP_KEY = your_breeze_app_key
   SECRET_KEY = your_breeze_secret_key
   SESSION_TOKEN = your_session_token
   
   [TRADING]
   CAPITAL = 1000000
   MAX_POSITIONS = 10
   MAX_RISK_PER_TRADE = 1.0
   SYMBOLS = RELIND,TCS,INFY,HINDUNILVR,ITC
   
   [NOTIFICATIONS]
   EMAIL_FROM = your_email@gmail.com
   EMAIL_PASSWORD = your_app_password
   EMAIL_RECIPIENTS = recipient@email.com
   TELEGRAM_BOT_TOKEN = your_bot_token
   TELEGRAM_CHAT_IDS = your_chat_id
   ```

## 🏃‍♂️ Usage

### Basic Usage

1. **Start the trading system**:
   ```bash
   python main.py
   ```

2. **View real-time logs**:
   The system will display real-time trading activities, signals, and portfolio updates.

### Advanced Usage

1. **Test individual components**:
   ```python
   # Test API connection
   from core.api_client import api_client
   profile = api_client.get_customer_details()
   print(profile)
   
   # Test notifications
   from notification_system import notification_manager
   notification_manager.test_notifications()
   
   # Test ML models
   from ml_models import ModelManager
   model_manager = ModelManager()
   predictions = model_manager.get_predictions(['RELIND'])
   ```

2. **Backtesting** (implement your backtesting logic):
   ```python
   from strategies import StrategyManager
   from data_manager import DataManager
   
   # Initialize components
   data_manager = DataManager()
   strategy_manager = StrategyManager()
   
   # Run backtest
   # Your backtesting implementation here
   ```

## 📊 System Architecture

```
Turtle Trader/
├── core/
│   ├── config.py           # Configuration management
│   └── api_client.py      # ICICI Breeze API client
├── ml_models/             # AI/ML models and feature engineering
├── strategies/            # Trading strategies
├── risk_management/       # Risk management systems
├── main.py               # Main trading engine
├── data_manager.py       # Data collection and storage
├── portfolio_manager.py  # Portfolio management
├── notification_system.py # Multi-channel notifications
├── config.ini            # Configuration file
└── requirements.txt      # Python dependencies
```

## 🔧 Key Components

### Trading Engine (`main.py`)
- Orchestrates all system components
- Multi-threaded operation for real-time processing
- Automated order execution and monitoring
- Scheduled tasks and maintenance

### ML Models (`ml_models/`)
- **Feature Engineering**: Technical indicators, market microstructure features
- **Ensemble Models**: XGBoost, LightGBM, CatBoost combination
- **Deep Learning**: LSTM and Transformer networks
- **Model Management**: Training, validation, and deployment pipeline

### Strategies (`strategies/`)
- **Turtle Strategy**: Classic breakout system with modern enhancements
- **Mean Reversion**: Statistical arbitrage with ML validation
- **Momentum Strategy**: Trend following with adaptive parameters
- **AI Enhanced**: Pure ML-driven trading decisions

### Risk Management (`risk_management/`)
- **VaR Calculation**: Parametric, historical, and Monte Carlo methods
- **Portfolio Risk**: Real-time monitoring and alerting
- **Position Sizing**: Kelly Criterion and volatility-based sizing

## 📈 Trading Strategies

### 1. Turtle Strategy
- 20/55-day breakout system
- Dynamic position sizing
- Trend following with momentum confirmation

### 2. Mean Reversion
- Statistical arbitrage opportunities
- Bollinger Bands and RSI-based entries
- ML validation for trade confirmation

### 3. Momentum Strategy
- Multi-timeframe momentum analysis
- Volume confirmation
- Adaptive stop-loss management

### 4. AI Enhanced Strategy
- Pure machine learning predictions
- Ensemble model consensus
- Real-time feature engineering

## 🔔 Notifications

The system supports multiple notification channels:

- **Email**: HTML-formatted alerts with detailed information
- **Telegram**: Real-time messages with emoji indicators
- **Slack**: Rich message formatting with color coding
- **Webhooks**: Custom integrations with external systems

## 📊 Performance Monitoring

### Real-time Metrics
- Portfolio value and P&L
- Individual position performance
- Risk metrics (VaR, drawdown, etc.)
- Strategy performance breakdown

### Analytics
- Win rate and profit factor
- Sharpe ratio and risk-adjusted returns
- Monthly performance breakdown
- Strategy comparison and optimization

## 🛡️ Risk Management

### Position-Level Risk
- Maximum risk per trade (default: 1% of capital)
- Stop-loss automation
- Position sizing based on volatility

### Portfolio-Level Risk
- Maximum portfolio VaR (default: 5%)
- Sector concentration limits
- Correlation monitoring

### System-Level Risk
- API connection monitoring
- Order execution validation
- Real-time balance checks

## 🐛 Troubleshooting

### Common Issues

1. **TA-Lib Installation Error**:
   - Ensure you have the correct version for your Python installation
   - Try installing from pre-compiled wheels

2. **API Connection Issues**:
   - Verify your API credentials in `config.ini`
   - Check if your session token is valid
   - Ensure proper network connectivity

3. **Database Errors**:
   - Check SQLite database permissions
   - Verify disk space availability

4. **Memory Issues**:
   - Reduce the number of symbols if running on limited memory
   - Adjust cache settings in configuration

### Logging
The system uses comprehensive logging. Check the log files for detailed error information:
- Info level: General system operations
- Warning level: Non-critical issues
- Error level: System errors requiring attention

## 📜 License

This project is for educational purposes. Please ensure compliance with your broker's API terms of service and local trading regulations.

## ⚠️ Disclaimer

**Important**: This is an automated trading system that can place real trades. Always:
- Test thoroughly in a paper trading environment first
- Start with small position sizes
- Monitor the system continuously
- Understand the risks involved in algorithmic trading
- Comply with all applicable laws and regulations

Trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log files
3. Create an issue in the repository

---

**Made with ❤️ for algorithmic traders**
