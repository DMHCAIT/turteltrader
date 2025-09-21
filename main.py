"""
Turtle Trader - Main Trading Engine
===================================

Orchestrates the entire trading system with AI/ML integration
Handles data collection, strategy execution, and order management
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from loguru import logger
import schedule
from dataclasses import dataclass

from core.config import config, Constants, Utils
from breeze_api_client import BreezeAPIClient  # Updated API client
from etf_manager import ETFOrderManager
from ai_predictor import AIPredictor
from custom_strategy import CustomETFStrategy, custom_etf_strategy
from strategies import strategy_manager, TradingSignal, SignalType
from ml_models import model_manager
from risk_management import risk_monitor
from data_manager import DataManager
from portfolio_manager import PortfolioManager
from notification_system import NotificationManager

@dataclass
class TradingState:
    """Current trading system state"""
    is_running: bool = False
    is_market_open: bool = False
    last_update: datetime = None
    active_positions: int = 0
    pending_orders: int = 0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    risk_score: float = 0.0

class TradingEngine:
    """Main trading engine orchestrating all components"""
    
    def __init__(self):
        self.state = TradingState()
        self.data_manager = DataManager()
        self.portfolio_manager = PortfolioManager()
        self.notification_manager = NotificationManager()
        
        # Initialize API client
        self.api_client = BreezeAPIClient()
        
        # Trading parameters from config
        self.symbols_to_trade = self._load_trading_universe()
        self.update_frequency = config.getint("MARKET_DATA", "UPDATE_FREQUENCY", 1)
        self.max_positions = config.getint("TRADING", "MAX_POSITIONS", 10)
        self.capital = config.getfloat("TRADING", "CAPITAL", 1000000)
        
        # Internal state
        self.running = False
        self.market_data_cache = {}
        self.last_signals = {}
        self.order_queue = []
        
        # Threading
        self.main_thread = None
        self.data_thread = None
        self.risk_thread = None
        
        logger.info("Trading Engine initialized with API client")
    
    def start(self):
        """Start the trading engine"""
        if self.running:
            logger.warning("Trading engine is already running")
            return
        
        try:
            # Authenticate with Breeze API
            session_token = config.get("BREEZE_API", "SESSION_TOKEN")
            if not session_token:
                raise ValueError("Session token not configured")
            
            self.api_client.authenticate(session_token)
            logger.info("Successfully authenticated with Breeze API")
            
            # Initialize data manager
            self.data_manager.start()
            
            # Start main trading loop
            self.running = True
            self.state.is_running = True
            
            # Start threads
            self.main_thread = threading.Thread(target=self._main_trading_loop, daemon=True)
            self.data_thread = threading.Thread(target=self._data_update_loop, daemon=True)
            self.risk_thread = threading.Thread(target=self._risk_monitoring_loop, daemon=True)
            
            self.main_thread.start()
            self.data_thread.start()
            self.risk_thread.start()
            
            # Schedule periodic tasks
            self._schedule_tasks()
            
            logger.info("Trading Engine started successfully")
            
            # Send startup notification
            self.notification_manager.send_notification(
                "🚀 Trading Engine Started",
                f"System initialized with {len(self.symbols_to_trade)} symbols\n"
                f"Capital: {Utils.format_currency(self.capital)}\n"
                f"Max Positions: {self.max_positions}"
            )
            
        except Exception as e:
            logger.error(f"Failed to start trading engine: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the trading engine"""
        if not self.running:
            return
        
        logger.info("Stopping Trading Engine...")
        
        self.running = False
        self.state.is_running = False
        
        # Close all positions if configured
        if config.getboolean("TRADING", "CLOSE_POSITIONS_ON_STOP", True):
            self._close_all_positions()
        
        # Cancel pending orders
        self._cancel_pending_orders()
        
        # Stop data manager
        self.data_manager.stop()
        
        # Close API connection
        self.api_client.close()
        
        logger.info("Trading Engine stopped")
        
        # Send shutdown notification
        self.notification_manager.send_notification(
            "🛑 Trading Engine Stopped",
            f"System shutdown at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Final P&L: {Utils.format_currency(self.state.total_pnl)}"
        )
    
    def _main_trading_loop(self):
        """Main trading loop"""
        logger.info("Starting main trading loop")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Check if market is open
                self.state.is_market_open = Utils.is_market_open()
                
                if not self.state.is_market_open:
                    logger.debug("Market is closed, waiting...")
                    time.sleep(60)  # Check every minute when market is closed
                    continue
                
                # Update portfolio state
                self._update_portfolio_state()
                
                # Process custom ETF strategy (1% dip buy, 3% sell)
                try:
                    self._process_custom_etf_strategy()
                except Exception as e:
                    logger.error(f"Error in custom ETF strategy: {e}")
                
                # Process each symbol
                for symbol in self.symbols_to_trade:
                    if not self.running:
                        break
                    
                    try:
                        self._process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        continue
                
                # Process order queue
                self._process_order_queue()
                
                # Update state
                self.state.last_update = datetime.now()
                
                # Control loop frequency
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_frequency - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in main trading loop: {e}")
                time.sleep(5)  # Brief pause before retrying
        
        logger.info("Main trading loop stopped")
    
    def _data_update_loop(self):
        """Data update loop running in separate thread"""
        logger.info("Starting data update loop")
        
        while self.running:
            try:
                if self.state.is_market_open:
                    # Update market data for all symbols
                    for symbol in self.symbols_to_trade:
                        if not self.running:
                            break
                        
                        try:
                            # Get latest data
                            data = self.data_manager.get_real_time_data(symbol)
                            if not data.empty:
                                self.market_data_cache[symbol] = data
                        except Exception as e:
                            logger.debug(f"Error updating data for {symbol}: {e}")
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in data update loop: {e}")
                time.sleep(10)
        
        logger.info("Data update loop stopped")
    
    def _risk_monitoring_loop(self):
        """Risk monitoring loop"""
        logger.info("Starting risk monitoring loop")
        
        while self.running:
            try:
                if self.state.is_market_open:
                    # Get current positions
                    positions = self.api_client.get_positions()
                    
                    if positions:
                        # Get returns data for risk calculation
                        returns_data = {}
                        for pos in positions:
                            if pos.symbol in self.market_data_cache:
                                data = self.market_data_cache[pos.symbol]
                                if 'close' in data.columns and len(data) > 1:
                                    returns_data[pos.symbol] = data['close'].pct_change().dropna()
                        
                        # Monitor portfolio risk
                        risk_report = risk_monitor.monitor_portfolio(positions, returns_data)
                        self.state.risk_score = risk_report['risk_score']
                        
                        # Handle risk alerts
                        if risk_report['alerts']:
                            self._handle_risk_alerts(risk_report['alerts'])
                
                time.sleep(30)  # Check risk every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in risk monitoring loop: {e}")
                time.sleep(60)
        
        logger.info("Risk monitoring loop stopped")
    
    def _process_symbol(self, symbol: str):
        """Process a single symbol for trading opportunities"""
        
        # Get latest market data
        if symbol not in self.market_data_cache:
            return
        
        data = self.market_data_cache[symbol]
        if data.empty or len(data) < 50:  # Need sufficient history
            return
        
        # Generate signals from all strategies
        signals = strategy_manager.generate_all_signals(symbol, data)
        
        if not signals:
            return
        
        # Get consensus signal
        consensus_signal = strategy_manager.consensus_signal(signals)
        
        if consensus_signal is None:
            return
        
        # Store signal
        self.last_signals[symbol] = consensus_signal
        
        # Check if we should act on this signal
        current_positions = self.api_client.get_positions()
        
        if not strategy_manager.strategies['Turtle Strategy'].validate_signal(
            consensus_signal, {pos.symbol: pos for pos in current_positions}
        ):
            return
        
        # Check risk management approval
        current_price = data['close'].iloc[-1]
        
        # Calculate position size
        available_capital = self.portfolio_manager.get_available_capital()
        position_size = self._calculate_position_size(consensus_signal, available_capital)
        
        if position_size <= 0:
            return
        
        # Validate with risk management
        returns_data = {}
        for pos in current_positions:
            if pos.symbol in self.market_data_cache:
                pos_data = self.market_data_cache[pos.symbol]
                if 'close' in pos_data.columns and len(pos_data) > 1:
                    returns_data[pos.symbol] = pos_data['close'].pct_change().dropna()
        
        risk_validation = risk_monitor.risk_manager.validate_new_position(
            symbol, position_size, current_price, current_positions, returns_data
        )
        
        if not risk_validation['approved']:
            logger.warning(f"Risk management rejected {symbol} position: {risk_validation['errors']}")
            return
        
        # Create order
        order = self._create_order_from_signal(consensus_signal, position_size)
        if order:
            self.order_queue.append(order)
            logger.info(f"Queued order for {symbol}: {order}")
    
    def _calculate_position_size(self, signal: TradingSignal, available_capital: float) -> int:
        """Calculate appropriate position size for signal"""
        
        # Get strategy-specific position size
        strategy = strategy_manager.strategies.get(signal.strategy)
        if strategy:
            return strategy.calculate_position_size(signal, available_capital)
        
        # Default position sizing (2% of capital)
        position_value = available_capital * 0.02
        return int(position_value / signal.price)
    
    def _create_order_from_signal(self, signal: TradingSignal, quantity: int) -> Optional[Dict]:
        """Create order dictionary from trading signal"""
        
        if quantity <= 0:
            return None
        
        # Determine order action
        if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY]:
            action = Constants.BUY
        elif signal.signal in [SignalType.SELL, SignalType.STRONG_SELL]:
            action = Constants.SELL
        else:
            return None
        
        # Calculate stop loss and take profit
        stop_loss = 0
        if signal.metadata and 'stop_loss' in signal.metadata:
            stop_loss = signal.metadata['stop_loss']
        
        order = {
            'symbol': signal.symbol,
            'exchange': Constants.NSE,
            'product': Constants.CASH,
            'action': action,
            'order_type': Constants.LIMIT,
            'quantity': quantity,
            'price': signal.price,
            'stop_loss': stop_loss,
            'validity': 'day',
            'strategy': signal.strategy,
            'confidence': signal.confidence,
            'timestamp': signal.timestamp
        }
        
        return order
    
    def _process_order_queue(self):
        """Process queued orders"""
        
        if not self.order_queue:
            return
        
        processed_orders = []
        
        for order in self.order_queue:
            try:
                # Place order via API
                order_id = self.api_client.place_order(
                    symbol=order['symbol'],
                    exchange=order['exchange'],
                    product=order['product'],
                    action=order['action'],
                    order_type=order['order_type'],
                    quantity=order['quantity'],
                    price=order['price'],
                    stop_loss=order['stop_loss'],
                    validity=order['validity'],
                    user_remark=f"{order['strategy'][:15]}_{order['confidence']:.2f}"
                )
                
                if order_id:
                    logger.info(f"Order placed successfully: {order_id}")
                    
                    # Send notification
                    self.notification_manager.send_notification(
                        f"📋 Order Placed",
                        f"Symbol: {order['symbol']}\n"
                        f"Action: {order['action'].upper()}\n"
                        f"Quantity: {order['quantity']}\n"
                        f"Price: ₹{order['price']:.2f}\n"
                        f"Strategy: {order['strategy']}\n"
                        f"Confidence: {order['confidence']:.2%}"
                    )
                    
                    processed_orders.append(order)
                
            except Exception as e:
                logger.error(f"Failed to place order for {order['symbol']}: {e}")
                # Keep order in queue for retry
        
        # Remove processed orders
        for order in processed_orders:
            self.order_queue.remove(order)
    
    def _update_portfolio_state(self):
        """Update portfolio state information"""
        try:
            # Get current positions
            positions = self.api_client.get_positions()
            self.state.active_positions = len([p for p in positions if p.quantity != 0])
            
            # Calculate daily P&L
            daily_pnl = sum(p.pnl for p in positions)
            self.state.daily_pnl = daily_pnl
            
            # Update total P&L (this should be tracked more persistently)
            self.state.total_pnl += daily_pnl
            
            # Get pending orders count
            try:
                today = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
                orders = self.api_client.get_order_list(Constants.NSE, today, today)
                self.state.pending_orders = len([o for o in orders if o.get('status') == 'Ordered'])
            except:
                self.state.pending_orders = 0
            
        except Exception as e:
            logger.error(f"Error updating portfolio state: {e}")
    
    def _handle_risk_alerts(self, alerts: List[Dict]):
        """Handle risk management alerts"""
        for alert in alerts:
            logger.warning(f"Risk Alert: {alert['message']}")
            
            # Send notification for high severity alerts
            if alert['severity'] == 'HIGH':
                self.notification_manager.send_notification(
                    f"🚨 {alert['type']} Alert",
                    alert['message'],
                    urgent=True
                )
                
                # Take protective action if needed
                if alert['type'] == 'VAR_BREACH':
                    self._reduce_portfolio_risk()
    
    def _reduce_portfolio_risk(self):
        """Reduce portfolio risk by closing riskiest positions"""
        try:
            positions = self.api_client.get_positions()
            if not positions:
                return
            
            # Get returns data
            returns_data = {}
            for pos in positions:
                if pos.symbol in self.market_data_cache:
                    data = self.market_data_cache[pos.symbol]
                    if 'close' in data.columns and len(data) > 1:
                        returns_data[pos.symbol] = data['close'].pct_change().dropna()
            
            # Calculate position risks
            position_risks = risk_monitor.risk_manager.calculate_position_risks(positions, returns_data)
            
            # Sort by risk contribution
            position_risks.sort(key=lambda x: x.var_contribution, reverse=True)
            
            # Close top 20% of risky positions
            positions_to_close = position_risks[:max(1, len(position_risks) // 5)]
            
            for pos_risk in positions_to_close:
                # Find the position
                position = next((p for p in positions if p.symbol == pos_risk.symbol), None)
                if position and position.quantity != 0:
                    # Square off position
                    action = Constants.SELL if position.quantity > 0 else Constants.BUY
                    
                    self.api_client.square_off_position(
                        symbol=position.symbol,
                        exchange=position.exchange,
                        product=position.product_type,
                        action=action,
                        quantity=abs(position.quantity)
                    )
                    
                    logger.info(f"Emergency square off: {position.symbol}")
            
        except Exception as e:
            logger.error(f"Error reducing portfolio risk: {e}")
    
    def _close_all_positions(self):
        """Close all open positions"""
        try:
            positions = self.api_client.get_positions()
            
            for position in positions:
                if position.quantity != 0:
                    action = Constants.SELL if position.quantity > 0 else Constants.BUY
                    
                    self.api_client.square_off_position(
                        symbol=position.symbol,
                        exchange=position.exchange,
                        product=position.product_type,
                        action=action,
                        quantity=abs(position.quantity)
                    )
                    
                    logger.info(f"Closed position: {position.symbol}")
            
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
    
    def _cancel_pending_orders(self):
        """Cancel all pending orders"""
        try:
            today = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            for exchange in [Constants.NSE, Constants.NFO]:
                try:
                    orders = self.api_client.get_order_list(exchange, today, today)
                    
                    for order in orders:
                        if order.get('status') == 'Ordered':
                            self.api_client.cancel_order(order['order_id'], exchange)
                            logger.info(f"Cancelled order: {order['order_id']}")
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")
    
    def _process_custom_etf_strategy(self):
        """
        Process custom ETF strategy: 1% dip buy, 3% target sell, 5% loss alert
        """
        try:
            # Get market data for all ETFs
            etf_market_data = {}
            
            for symbol in custom_etf_strategy.etf_symbols:
                # Get recent data for the ETF
                data = self.data_manager.get_market_data(symbol, "1D", 5)  # Last 5 days
                
                if data is not None and len(data) >= 2:
                    etf_market_data[symbol] = data
            
            if not etf_market_data:
                logger.debug("No ETF market data available for custom strategy")
                return
            
            # Get signals from custom strategy
            signals = custom_etf_strategy.get_signals(etf_market_data)
            
            if signals:
                logger.info(f"Custom ETF Strategy generated {len(signals)} signals")
                
                # Process signals
                custom_etf_strategy.process_signals(signals)
                
                # Log signal summary
                for signal in signals:
                    logger.info(f"Custom Signal: {signal.action} {signal.symbol} @ "
                               f"₹{signal.current_price:.2f} ({signal.order_type.value})")
            
        except Exception as e:
            logger.error(f"Error in custom ETF strategy processing: {e}")
    
    def _schedule_tasks(self):
        """Schedule periodic tasks"""
        
        # Daily model retraining
        schedule.every().day.at("18:00").do(self._daily_model_retrain)
        
        # Weekly performance report
        schedule.every().sunday.at("20:00").do(self._weekly_performance_report)
        
        # Market open preparation
        schedule.every().day.at("09:00").do(self._market_open_preparation)
        
        # Market close cleanup
        schedule.every().day.at("15:45").do(self._market_close_cleanup)
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _run_scheduler(self):
        """Run scheduled tasks"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _daily_model_retrain(self):
        """Daily model retraining task"""
        logger.info("Starting daily model retraining...")
        
        try:
            for symbol in self.symbols_to_trade:
                # Get historical data
                historical_data = self.data_manager.get_historical_data(
                    symbol=symbol,
                    days=365,
                    interval=Constants.DAY
                )
                
                if not historical_data.empty and len(historical_data) > 100:
                    # Retrain model
                    model_manager.train_model(symbol, historical_data, "ensemble")
                    logger.info(f"Retrained model for {symbol}")
            
            self.notification_manager.send_notification(
                "🤖 Model Retraining Complete",
                f"Successfully retrained models for {len(self.symbols_to_trade)} symbols"
            )
            
        except Exception as e:
            logger.error(f"Error in daily model retraining: {e}")
    
    def _weekly_performance_report(self):
        """Generate weekly performance report"""
        logger.info("Generating weekly performance report...")
        
        try:
            # This would generate a comprehensive performance report
            # For now, just send a simple notification
            self.notification_manager.send_notification(
                "📊 Weekly Performance Report",
                f"Total P&L: {Utils.format_currency(self.state.total_pnl)}\n"
                f"Active Positions: {self.state.active_positions}\n"
                f"Risk Score: {self.state.risk_score:.1f}/100"
            )
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
    
    def _market_open_preparation(self):
        """Prepare for market open"""
        logger.info("Preparing for market open...")
        
        try:
            # Clear old cache
            self.market_data_cache.clear()
            
            # Reset daily state
            self.state.daily_pnl = 0.0
            
            # Pre-load market data
            for symbol in self.symbols_to_trade[:5]:  # Load top 5 symbols
                try:
                    data = self.data_manager.get_historical_data(symbol, days=1, interval=Constants.MINUTE_1)
                    if not data.empty:
                        self.market_data_cache[symbol] = data
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error in market open preparation: {e}")
    
    def _market_close_cleanup(self):
        """Cleanup tasks at market close"""
        logger.info("Performing market close cleanup...")
        
        try:
            # Cancel any remaining day orders
            self._cancel_pending_orders()
            
            # Save daily performance data
            # This would typically save to database
            
            # Send daily summary
            self.notification_manager.send_notification(
                "📈 Daily Summary",
                f"Market Close Summary:\n"
                f"Daily P&L: {Utils.format_currency(self.state.daily_pnl)}\n"
                f"Active Positions: {self.state.active_positions}\n"
                f"Signals Generated: {len(self.last_signals)}"
            )
            
        except Exception as e:
            logger.error(f"Error in market close cleanup: {e}")
    
    def _load_trading_universe(self) -> List[str]:
        """Load the universe of symbols to trade"""
        # This could be loaded from config file or database
        # For now, using a default set of liquid stocks
        return [
            'RELIND', 'TCS', 'INFY', 'HINDUNILVR', 'ITC', 
            'SBIN', 'KOTAKBANK', 'BAJFINANCE', 'BHARTIARTL', 'ASIANPAINT',
            'MARUTI', 'AXISBANK', 'LT', 'HDFCBANK', 'WIPRO',
            'TATASTEEL', 'ONGC', 'POWERGRID', 'NTPC', 'COALINDIA'
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self.state.is_running,
            'market_open': self.state.is_market_open,
            'last_update': self.state.last_update.isoformat() if self.state.last_update else None,
            'active_positions': self.state.active_positions,
            'pending_orders': self.state.pending_orders,
            'daily_pnl': self.state.daily_pnl,
            'total_pnl': self.state.total_pnl,
            'risk_score': self.state.risk_score,
            'symbols_trading': len(self.symbols_to_trade),
            'cached_data': len(self.market_data_cache),
            'queued_orders': len(self.order_queue)
        }

# Global trading engine instance
trading_engine = TradingEngine()

if __name__ == "__main__":
    # Command line interface
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            try:
                trading_engine.start()
                
                # Keep running until interrupted
                while True:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                trading_engine.stop()
                
        elif command == "status":
            status = trading_engine.get_status()
            for key, value in status.items():
                print(f"{key}: {value}")
                
        else:
            print("Usage: python main.py [start|status]")
    else:
        print("Turtle Trader - Advanced AI/ML Trading System")
        print("Usage: python main.py [start|status]")

# Export main class
__all__ = ['TradingEngine', 'trading_engine']
