"""
🐢 Turtle Trader - Live ETF Trading System
Enhanced with ICICI Breeze API integration for your custom strategy
"""

import time
import threading
from datetime import datetime, timedelta
import pandas as pd
import configparser
from loguru import logger
import schedule

from breeze_api_client import BreezeAPIClient
from custom_strategy import CustomETFStrategy

class TurtleTraderEngine:
    """Main trading engine for live ETF trading"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Initialize components
        self.api_client = BreezeAPIClient()
        self.custom_strategy = CustomETFStrategy()
        
        # Trading state
        self.is_running = False
        self.positions = {}
        self.pending_orders = {}
        self.daily_pnl = 0.0
        
        # Configuration
        self.etf_symbols = self.config.get('TRADING', 'SYMBOLS', fallback='GOLDBEES,NIFTYBEES,BANKBEES').split(',')
        self.buy_dip_percent = float(self.config.get('TRADING', 'BUY_DIP_PERCENT', fallback=1.0))
        self.sell_target_percent = float(self.config.get('TRADING', 'SELL_TARGET_PERCENT', fallback=3.0))
        self.loss_alert_percent = float(self.config.get('TRADING', 'LOSS_ALERT_PERCENT', fallback=5.0))
        self.mtf_priority = self.config.getboolean('TRADING', 'MTF_FIRST_PRIORITY', fallback=True)
        
        logger.info("🐢 Turtle Trader Engine initialized")
    
    def start_trading(self):
        """Start the trading engine"""
        
        print("🚀 STARTING TURTLE TRADER ENGINE")
        print("=" * 50)
        
        # Test API connection first
        if not self.api_client.test_connection():
            print("❌ Cannot start trading - API connection failed")
            print("📖 Run: python test_breeze_api.py to diagnose")
            return False
        
        print("✅ API connection verified")
        print(f"🎯 Strategy: Buy {self.buy_dip_percent}% dip, Sell {self.sell_target_percent}% profit")
        print(f"📊 ETFs: {', '.join(self.etf_symbols)}")
        print(f"🔄 Order Priority: {'MTF → CNC' if self.mtf_priority else 'CNC only'}")
        
        # Start trading loop
        self.is_running = True
        
        # Schedule market checks
        schedule.every(30).seconds.do(self.market_scan)
        schedule.every(1).minutes.do(self.position_monitor)
        schedule.every(5).minutes.do(self.update_portfolio)
        
        print("\n🎯 Trading engine started - monitoring market...")
        
        # Main loop
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping trading engine...")
            self.stop_trading()
        
        return True
    
    def market_scan(self):
        """Scan market for trading opportunities"""
        
        try:
            logger.info("📊 Scanning market for opportunities...")
            
            for etf_symbol in self.etf_symbols:
                # Skip if we already have position
                if etf_symbol in self.positions:
                    continue
                
                # Get current quote
                quote = self.api_client.get_quote(etf_symbol)
                if not quote:
                    continue
                
                current_price = float(quote.get('ltp', 0))
                if current_price == 0:
                    continue
                
                # Get yesterday's close (simplified - you can enhance this)
                # For now, using change % to estimate yesterday close
                change_pct = float(quote.get('change_percentage', 0))
                yesterday_close = current_price / (1 + change_pct/100)
                
                # Check for dip opportunity
                dip_percent = ((yesterday_close - current_price) / yesterday_close) * 100
                
                if dip_percent >= self.buy_dip_percent:
                    print(f"\n🎯 BUY OPPORTUNITY DETECTED!")
                    print(f"📈 {etf_symbol}: {dip_percent:.2f}% dip")
                    print(f"💰 Current Price: ₹{current_price:.2f}")
                    
                    # Calculate position size (simplified)
                    quantity = self._calculate_position_size(current_price)
                    
                    # Place buy order
                    order_id = self._place_buy_order(etf_symbol, current_price, quantity)
                    
                    if order_id:
                        # Track position
                        self.positions[etf_symbol] = {
                            'order_id': order_id,
                            'entry_price': current_price,
                            'quantity': quantity,
                            'target_price': current_price * (1 + self.sell_target_percent/100),
                            'stop_loss': current_price * (1 - self.loss_alert_percent/100),
                            'timestamp': datetime.now()
                        }
                        
                        print(f"✅ Position opened for {etf_symbol}")
                        print(f"🎯 Target: ₹{self.positions[etf_symbol]['target_price']:.2f}")
                        print(f"⚠️ Alert at: ₹{self.positions[etf_symbol]['stop_loss']:.2f}")
        
        except Exception as e:
            logger.error(f"Market scan error: {e}")
    
    def position_monitor(self):
        """Monitor existing positions for exit signals"""
        
        try:
            if not self.positions:
                return
            
            logger.info(f"📋 Monitoring {len(self.positions)} positions...")
            
            for etf_symbol, position in list(self.positions.items()):
                # Get current quote
                quote = self.api_client.get_quote(etf_symbol)
                if not quote:
                    continue
                
                current_price = float(quote.get('ltp', 0))
                entry_price = position['entry_price']
                target_price = position['target_price']
                stop_loss = position['stop_loss']
                
                # Calculate P&L
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                pnl_amount = (current_price - entry_price) * position['quantity']
                
                print(f"\n📊 {etf_symbol} Position Status:")
                print(f"   Entry: ₹{entry_price:.2f} → Current: ₹{current_price:.2f}")
                print(f"   P&L: {pnl_percent:+.2f}% (₹{pnl_amount:+.2f})")
                
                # Check exit conditions
                if current_price >= target_price:
                    print(f"🎉 TARGET HIT! Selling {etf_symbol}")
                    self._place_sell_order(etf_symbol, current_price, position['quantity'])
                    del self.positions[etf_symbol]
                    
                elif current_price <= stop_loss:
                    print(f"⚠️ LOSS ALERT! {etf_symbol} hit {self.loss_alert_percent}% loss")
                    print(f"   Consider reviewing position...")
                    # Note: Not auto-selling at loss, just alerting as per your strategy
        
        except Exception as e:
            logger.error(f"Position monitoring error: {e}")
    
    def update_portfolio(self):
        """Update portfolio and P&L information"""
        
        try:
            # Get account funds
            funds = self.api_client.get_account_funds()
            if funds:
                available_cash = funds.get('available_cash', 0)
                print(f"\n💰 Available Cash: ₹{available_cash:,.2f}")
            
            # Calculate total P&L
            total_pnl = 0
            for etf_symbol, position in self.positions.items():
                quote = self.api_client.get_quote(etf_symbol)
                if quote:
                    current_price = float(quote.get('ltp', 0))
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    total_pnl += pnl
            
            self.daily_pnl = total_pnl
            print(f"📊 Total P&L: ₹{total_pnl:+.2f}")
            
        except Exception as e:
            logger.error(f"Portfolio update error: {e}")
    
    def _calculate_position_size(self, price):
        """Calculate position size based on risk management"""
        
        # Get available funds
        funds = self.api_client.get_account_funds()
        if not funds:
            return 1  # Minimum quantity
        
        available_cash = float(funds.get('available_cash', 100000))
        position_size_percent = float(self.config.get('TRADING', 'POSITION_SIZE_PERCENT', fallback=3.0))
        
        # Calculate quantity (3% of available cash by default)
        position_value = available_cash * (position_size_percent / 100)
        quantity = int(position_value / price)
        
        return max(1, quantity)  # At least 1 share
    
    def _place_buy_order(self, symbol, price, quantity):
        """Place buy order with MTF/CNC priority"""
        
        try:
            # Try MTF first if enabled
            if self.mtf_priority:
                print(f"🔄 Attempting MTF order for {symbol}...")
                
                order_id = self.api_client.place_order(
                    stock_code=symbol,
                    exchange_code="NSE",
                    product="MTF",  # Margin Trading Facility
                    action="BUY",
                    order_type="MARKET",
                    stoploss="",
                    quantity=quantity,
                    price="0",  # Market order
                    validity="DAY",
                    user_remark="TurtleTrader-MTF"
                )
                
                if order_id:
                    print(f"✅ MTF order placed: {order_id}")
                    return order_id
                else:
                    print("❌ MTF order failed, trying CNC...")
            
            # Fallback to CNC
            print(f"🔄 Placing CNC order for {symbol}...")
            
            order_id = self.api_client.place_order(
                stock_code=symbol,
                exchange_code="NSE",
                product="CNC",  # Cash and Carry
                action="BUY",
                order_type="MARKET",
                stoploss="",
                quantity=quantity,
                price="0",  # Market order
                validity="DAY",
                user_remark="TurtleTrader-CNC"
            )
            
            if order_id:
                print(f"✅ CNC order placed: {order_id}")
                return order_id
            else:
                print("❌ Both MTF and CNC orders failed")
                return None
        
        except Exception as e:
            logger.error(f"Buy order error: {e}")
            return None
    
    def _place_sell_order(self, symbol, price, quantity):
        """Place sell order"""
        
        try:
            order_id = self.api_client.place_order(
                stock_code=symbol,
                exchange_code="NSE",
                product="CNC",  # Use CNC for selling
                action="SELL",
                order_type="MARKET",
                stoploss="",
                quantity=quantity,
                price="0",  # Market order
                validity="DAY",
                user_remark="TurtleTrader-SELL"
            )
            
            if order_id:
                print(f"✅ Sell order placed: {order_id}")
                return order_id
            else:
                print("❌ Sell order failed")
                return None
        
        except Exception as e:
            logger.error(f"Sell order error: {e}")
            return None
    
    def stop_trading(self):
        """Stop the trading engine"""
        self.is_running = False
        print("⏹️ Trading engine stopped")
    
    def get_status(self):
        """Get current trading status"""
        
        status = {
            'running': self.is_running,
            'positions': len(self.positions),
            'daily_pnl': self.daily_pnl,
            'etf_symbols': self.etf_symbols
        }
        
        return status

def main():
    """Main entry point"""
    
    print("🐢 TURTLE TRADER - LIVE ETF TRADING SYSTEM")
    print("=" * 60)
    print("📊 Custom Strategy: 1% Dip Buy → 3% Target Sell")
    print("⚡ Order Priority: MTF → CNC fallback")
    print("⚠️ Loss Alert: 5% (manual review)")
    print("=" * 60)
    
    # Initialize trading engine
    engine = TurtleTraderEngine()
    
    # Interactive menu
    while True:
        print("\n📋 TURTLE TRADER MENU:")
        print("1. 🚀 Start Live Trading")
        print("2. 📊 Check Status") 
        print("3. 🧪 Test API Connection")
        print("4. 📈 View Dashboard")
        print("5. ⏹️ Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            engine.start_trading()
            
        elif choice == '2':
            status = engine.get_status()
            print(f"\n📊 TRADING STATUS:")
            print(f"   Running: {'✅ Yes' if status['running'] else '❌ No'}")
            print(f"   Positions: {status['positions']}")
            print(f"   Daily P&L: ₹{status['daily_pnl']:+.2f}")
            print(f"   ETFs: {', '.join(status['etf_symbols'])}")
            
        elif choice == '3':
            print("🧪 Testing API connection...")
            if engine.api_client.test_connection():
                print("✅ API connection working!")
            else:
                print("❌ API connection failed!")
                print("📖 Run: python test_breeze_api.py for diagnostics")
            
        elif choice == '4':
            print("📈 Starting dashboard...")
            print("Run in another terminal: streamlit run simple_dashboard.py")
            
        elif choice == '5':
            if engine.is_running:
                engine.stop_trading()
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
