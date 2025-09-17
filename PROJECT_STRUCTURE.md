"""
🐢 TURTLE TRADER - CLEAN PROJECT STRUCTURE
==========================================

📁 PROJECT ORGANIZATION:

🔧 CORE SYSTEM:
├── app.py                      # Main Streamlit entry point
├── main.py                     # Trading engine orchestrator  
├── trading_dashboard.py        # Main dashboard interface
├── config.ini                  # Your API configuration
├── config_template.ini         # Template for new setups
└── requirements.txt            # All dependencies

🏗️ CORE MODULES:
├── core/                       # Core configuration & API
├── data/                       # Market data storage
├── logs/                       # System logs
├── strategies/                 # Trading strategies
├── ml_models/                  # AI/ML models
├── risk_management/            # Risk controls
└── models/                     # Data models

📊 DATA & TRADING:
├── data_manager.py             # Market data management
├── enhanced_data_manager.py    # Yahoo Finance integration
├── etf_database.py            # ETF information database
├── etf_manager.py             # ETF order management
├── etf_strategies.py          # ETF-specific strategies
└── custom_strategy.py         # Your custom strategies

💰 PORTFOLIO & BALANCE:
├── portfolio_manager.py       # Position tracking
├── real_account_balance.py    # Live balance integration
├── dynamic_capital_allocator.py # Smart capital allocation
└── real_time_monitor.py       # Balance monitoring

🔐 API & CONNECTION:
├── breeze_api_client.py       # Original API client
├── fixed_breeze_api_client.py # Enhanced API client
├── smart_session_manager.py   # Auto session management
└── auto_session_manager.py    # Session automation

🔴 LIVE TRADING:
├── live_order_executor.py     # Real order placement
├── trading_mode_controller.py # Demo/Live mode switching
└── notification_system.py    # Alerts & notifications

🤖 AI & PREDICTION:
└── ai_predictor.py           # AI-powered predictions

📚 DOCUMENTATION:
├── README.md                 # Main documentation
├── QUICK_START_GUIDE.md     # Quick setup guide
└── .streamlit/              # Streamlit configuration

🧹 CLEANED UP:
❌ Removed 25+ duplicate/outdated files
❌ Removed old test files and simulations  
❌ Removed redundant documentation files
❌ Removed deprecated implementations

✅ PRODUCTION-READY STRUCTURE!
"""