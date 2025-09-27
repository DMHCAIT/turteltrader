"""
🐢 TURTLE TRADING STRATEGY BACKTESTER
====================================

Historical backtesting system for turtle trading strategy
- Tests on real historical data from Kite API
- Implements original turtle trading rules
- Dynamic position sizing based on account balance
- Comprehensive performance analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger
import json

from kite_api_client import KiteAPIClient
from dynamic_capital_allocator import DynamicCapitalAllocator


@dataclass
class BacktestTrade:
    """Individual trade record for backtesting"""
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: int = 0
    position_size: float = 0.0
    side: str = "LONG"  # LONG or SHORT
    exit_reason: str = ""  # "PROFIT", "STOP_LOSS", "TIMEOUT"
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None


@dataclass
class BacktestMetrics:
    """Performance metrics for backtesting"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0


class TurtleBacktester:
    """
    Turtle Trading Strategy Backtester
    
    Implements the classic turtle trading system:
    1. Donchian Channel Breakouts (20/55 day)
    2. ATR-based position sizing
    3. Pyramid position additions
    4. ATR-based stop losses
    """
    
    def __init__(self, initial_capital: float = None):
        """Initialize backtester with real account balance"""
        self.api_client = KiteAPIClient()
        
        # Use real capital allocator for position sizing
        self.allocator = DynamicCapitalAllocator(use_real_balance=True)
        
        # Turtle trading parameters
        self.donchian_entry_period = 20    # Breakout period for entry
        self.donchian_exit_period = 10     # Breakout period for exit
        self.atr_period = 20               # ATR calculation period
        self.atr_stop_multiplier = 2.0     # Stop loss = 2 x ATR
        self.max_pyramid_units = 4         # Maximum units per position
        self.unit_size_pct = 0.01          # 1% risk per unit (N)
        
        # Backtesting state
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, BacktestTrade] = {}
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        
        logger.info("🐢 Turtle Backtester initialized with real capital allocation")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate turtle trading indicators"""
        data = df.copy()
        
        # Donchian Channels
        data['donchian_high_20'] = data['high'].rolling(window=self.donchian_entry_period).max()
        data['donchian_low_20'] = data['low'].rolling(window=self.donchian_entry_period).min()
        data['donchian_high_10'] = data['high'].rolling(window=self.donchian_exit_period).max()
        data['donchian_low_10'] = data['low'].rolling(window=self.donchian_exit_period).min()
        
        # ATR (Average True Range)
        data['prev_close'] = data['close'].shift(1)
        data['tr1'] = data['high'] - data['low']
        data['tr2'] = abs(data['high'] - data['prev_close'])
        data['tr3'] = abs(data['low'] - data['prev_close'])
        data['true_range'] = data[['tr1', 'tr2', 'tr3']].max(axis=1)
        data['atr'] = data['true_range'].rolling(window=self.atr_period).mean()
        
        # N = Average True Range (volatility measure)
        data['N'] = data['atr']
        
        # Entry and exit signals
        data['long_entry'] = data['close'] > data['donchian_high_20'].shift(1)
        data['long_exit'] = data['close'] < data['donchian_low_10'].shift(1)
        data['short_entry'] = data['close'] < data['donchian_low_20'].shift(1)
        data['short_exit'] = data['close'] > data['donchian_high_10'].shift(1)
        
        return data.dropna()
    
    def calculate_position_size(self, price: float, atr: float, capital: float) -> Tuple[int, float]:
        """
        Calculate turtle position size based on N (ATR)
        
        Formula: Unit Size = (Account Risk) / (N × Shares)
        Where Account Risk = 1% of capital
        """
        if atr <= 0:
            return 0, 0.0
        
        # Account risk (1% of deployable capital per unit)
        account_risk = capital * self.unit_size_pct
        
        # Dollar volatility per share
        dollar_volatility = atr
        
        # Position size in dollars
        position_value = account_risk / dollar_volatility * price
        
        # Number of shares (rounded down to avoid over-allocation)
        shares = int(position_value / price)
        actual_position_size = shares * price
        
        return shares, actual_position_size
    
    def backtest_symbol(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Run backtest for a single symbol"""
        
        logger.info(f"🐢 Backtesting {symbol} from {start_date.date()} to {end_date.date()}")
        
        # Get instruments to find token
        instruments = self.api_client.get_instruments("NSE")
        token = None
        
        for _, instrument in instruments.iterrows():
            if instrument['tradingsymbol'] == symbol:
                token = instrument['instrument_token']
                break
        
        if not token:
            logger.error(f"❌ Token not found for {symbol}")
            return pd.DataFrame()
        
        # Fetch historical data
        historical_data = self.api_client.get_historical_data(
            instrument_token=token,
            from_date=start_date,
            to_date=end_date,
            interval="day"
        )
        
        if historical_data is None or len(historical_data) == 0:
            logger.error(f"❌ No historical data for {symbol}")
            return pd.DataFrame()
        
        # Calculate indicators
        data = self.calculate_indicators(historical_data)
        
        # Initial capital
        current_capital = self.allocator.deployable_capital
        self.equity_curve = [current_capital]
        
        logger.info(f"📊 Starting backtest with ₹{current_capital:,.2f} deployable capital")
        
        # Run simulation
        for i, (date, row) in enumerate(data.iterrows()):
            
            # Check for exits first
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                exit_triggered = False
                
                # Check stop loss (2 * ATR)
                if position.side == "LONG":
                    stop_price = position.entry_price - (2 * row['N'])
                    if row['low'] <= stop_price:
                        exit_price = stop_price
                        exit_reason = "STOP_LOSS"
                        exit_triggered = True
                    elif row['long_exit']:
                        exit_price = row['close']
                        exit_reason = "EXIT_SIGNAL"
                        exit_triggered = True
                
                if exit_triggered:
                    self._close_position(symbol, date, exit_price, exit_reason)
                    current_capital = self._update_capital()
            
            # Check for entries
            if symbol not in self.open_positions:
                if row['long_entry'] and not pd.isna(row['N']):
                    # Calculate position size
                    shares, position_size = self.calculate_position_size(
                        row['close'], row['N'], current_capital
                    )
                    
                    if shares > 0 and position_size <= current_capital * 0.2:  # Max 20% per position
                        trade = BacktestTrade(
                            symbol=symbol,
                            entry_date=date,
                            entry_price=row['close'],
                            quantity=shares,
                            position_size=position_size,
                            side="LONG"
                        )
                        
                        self.open_positions[symbol] = trade
                        self.trades.append(trade)
                        current_capital -= position_size
                        
                        logger.debug(f"📈 LONG entry: {symbol} @ ₹{row['close']:.2f}, Size: ₹{position_size:,.0f}")
            
            # Update equity curve
            total_equity = current_capital + self._calculate_open_pnl(data.loc[date])
            self.equity_curve.append(total_equity)
        
        # Close any remaining positions
        final_date = data.index[-1]
        final_price = data.loc[final_date, 'close']
        
        if symbol in self.open_positions:
            self._close_position(symbol, final_date, final_price, "END_OF_TEST")
        
        logger.info(f"✅ Backtest completed for {symbol}")
        return data
    
    def _close_position(self, symbol: str, exit_date: datetime, exit_price: float, exit_reason: str):
        """Close an open position"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        position.exit_date = exit_date
        position.exit_price = exit_price
        position.exit_reason = exit_reason
        
        # Calculate P&L
        if position.side == "LONG":
            position.pnl = (exit_price - position.entry_price) * position.quantity
        
        position.pnl_pct = (position.pnl / position.position_size) * 100
        
        logger.debug(f"📉 Position closed: {symbol}, P&L: ₹{position.pnl:.0f} ({position.pnl_pct:+.1f}%)")
        
        del self.open_positions[symbol]
    
    def _calculate_open_pnl(self, current_prices: pd.Series) -> float:
        """Calculate unrealized P&L for open positions"""
        total_pnl = 0.0
        
        for symbol, position in self.open_positions.items():
            if 'close' in current_prices:
                current_price = current_prices['close']
                if position.side == "LONG":
                    unrealized_pnl = (current_price - position.entry_price) * position.quantity
                    total_pnl += unrealized_pnl
        
        return total_pnl
    
    def _update_capital(self) -> float:
        """Update available capital after position changes"""
        # Start with deployable capital
        available_capital = self.allocator.deployable_capital
        
        # Add realized P&L
        for trade in self.trades:
            if trade.pnl is not None:
                available_capital += trade.pnl
        
        # Subtract capital tied up in open positions
        for position in self.open_positions.values():
            available_capital -= position.position_size
        
        return available_capital
    
    def calculate_performance_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive performance metrics"""
        
        # Filter completed trades only
        completed_trades = [t for t in self.trades if t.pnl is not None]
        
        if not completed_trades:
            return BacktestMetrics()
        
        # Basic metrics
        total_trades = len(completed_trades)
        winning_trades = len([t for t in completed_trades if t.pnl > 0])
        losing_trades = len([t for t in completed_trades if t.pnl < 0])
        
        # P&L calculations
        total_pnl = sum(t.pnl for t in completed_trades)
        wins = [t.pnl for t in completed_trades if t.pnl > 0]
        losses = [t.pnl for t in completed_trades if t.pnl < 0]
        
        # Performance ratios
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        profit_factor = sum(wins) / abs(sum(losses)) if losses else float('inf')
        
        # Drawdown calculation
        equity_series = pd.Series(self.equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = equity_series - rolling_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / rolling_max.max()) * 100
        
        # Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = pd.Series(self.equity_curve).pct_change().dropna()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_pct=(total_pnl / self.allocator.deployable_capital) * 100,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            largest_win=max(wins) if wins else 0,
            largest_loss=min(losses) if losses else 0
        )
    
    def run_multi_symbol_backtest(self, symbols: List[str], months_back: int = 6) -> Dict:
        """Run backtest across multiple symbols"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        logger.info(f"🐢 Starting multi-symbol backtest: {symbols}")
        logger.info(f"📅 Period: {start_date.date()} to {end_date.date()}")
        
        results = {}
        
        for symbol in symbols:
            try:
                data = self.backtest_symbol(symbol, start_date, end_date)
                if not data.empty:
                    results[symbol] = {
                        'data': data,
                        'completed': True
                    }
                else:
                    results[symbol] = {'completed': False, 'error': 'No data'}
            
            except Exception as e:
                logger.error(f"❌ Error backtesting {symbol}: {e}")
                results[symbol] = {'completed': False, 'error': str(e)}
        
        # Calculate overall metrics
        metrics = self.calculate_performance_metrics()
        
        return {
            'symbols': results,
            'metrics': metrics,
            'trades': [t.__dict__ for t in self.trades],
            'equity_curve': self.equity_curve,
            'initial_capital': self.allocator.deployable_capital
        }
    
    def print_backtest_report(self, results: Dict):
        """Print comprehensive backtest report"""
        
        print("\n🐢 TURTLE TRADING BACKTEST REPORT")
        print("=" * 60)
        
        metrics = results['metrics']
        initial_capital = results['initial_capital']
        
        print(f"\n💼 ACCOUNT SUMMARY:")
        print(f"   Initial Capital: ₹{initial_capital:,.2f}")
        print(f"   Final P&L: ₹{metrics.total_pnl:+,.2f}")
        print(f"   Total Return: {metrics.total_pnl_pct:+.2f}%")
        
        print(f"\n📊 TRADE STATISTICS:")
        print(f"   Total Trades: {metrics.total_trades}")
        print(f"   Winning Trades: {metrics.winning_trades}")
        print(f"   Losing Trades: {metrics.losing_trades}")
        print(f"   Win Rate: {metrics.win_rate:.1f}%")
        
        print(f"\n💰 PROFIT/LOSS ANALYSIS:")
        print(f"   Average Win: ₹{metrics.avg_win:+,.0f}")
        print(f"   Average Loss: ₹{metrics.avg_loss:+,.0f}")
        print(f"   Largest Win: ₹{metrics.largest_win:+,.0f}")
        print(f"   Largest Loss: ₹{metrics.largest_loss:+,.0f}")
        print(f"   Profit Factor: {metrics.profit_factor:.2f}")
        
        print(f"\n📉 RISK METRICS:")
        print(f"   Max Drawdown: ₹{metrics.max_drawdown:+,.0f}")
        print(f"   Max Drawdown %: {metrics.max_drawdown_pct:.2f}%")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        
        print(f"\n🎯 SYMBOL PERFORMANCE:")
        for symbol, result in results['symbols'].items():
            if result.get('completed'):
                symbol_trades = [t for t in self.trades if t['symbol'] == symbol and t['pnl'] is not None]
                if symbol_trades:
                    symbol_pnl = sum(t['pnl'] for t in symbol_trades)
                    print(f"   {symbol:12} → ₹{symbol_pnl:+8,.0f} ({len(symbol_trades)} trades)")
                else:
                    print(f"   {symbol:12} → No completed trades")
            else:
                print(f"   {symbol:12} → Error: {result.get('error', 'Unknown')}")


def run_turtle_backtest_demo():
    """Demo function to run turtle backtest"""
    
    print("🐢 TURTLE TRADING STRATEGY BACKTESTER")
    print("=" * 50)
    
    # ETF symbols for testing
    test_symbols = ['NIFTYBEES', 'BANKBEES', 'GOLDBEES']
    
    # Initialize backtester
    backtester = TurtleBacktester()
    
    # Run backtest
    print(f"\n🚀 Running backtest on symbols: {test_symbols}")
    results = backtester.run_multi_symbol_backtest(test_symbols, months_back=6)
    
    # Print results
    backtester.print_backtest_report(results)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"turtle_backtest_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filename}")
    
    return results


if __name__ == "__main__":
    run_turtle_backtest_demo()