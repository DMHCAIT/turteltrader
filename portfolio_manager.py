"""
Turtle Trader - Portfolio Management Module
Advanced portfolio management with performance tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from loguru import logger

from core.config import config, Constants, Utils
from core.api_client import api_client, Position

@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    cash_balance: float
    invested_amount: float
    unrealized_pnl: float
    realized_pnl: float
    total_return: float
    daily_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float

class PortfolioManager:
    """Comprehensive portfolio management system"""
    
    def __init__(self):
        self.initial_capital = config.getfloat("TRADING", "CAPITAL", 1000000)
        self.max_positions = config.getint("TRADING", "MAX_POSITIONS", 10)
        self.position_size_percent = config.getfloat("TRADING", "POSITION_SIZE_PERCENT", 2.0)
        
        # Performance tracking
        self.trade_history = []
        self.daily_returns = []
        self.equity_curve = []
        
        # Risk management
        self.max_portfolio_risk = 0.05  # 5% VaR limit
        self.max_position_size = 0.20   # 20% max per position
        
        logger.info("Portfolio Manager initialized")
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            # Get current positions and funds
            positions = api_client.get_positions()
            funds = api_client.get_funds()
            
            # Calculate portfolio metrics
            metrics = self._calculate_portfolio_metrics(positions, funds)
            
            # Get position breakdown
            position_breakdown = self._get_position_breakdown(positions)
            
            # Get sector allocation
            sector_allocation = self._get_sector_allocation(positions)
            
            return {
                'metrics': metrics,
                'positions': position_breakdown,
                'sectors': sector_allocation,
                'cash_available': self.get_available_capital(),
                'margin_utilization': self._calculate_margin_utilization(funds),
                'risk_metrics': self._calculate_risk_metrics(positions)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def get_available_capital(self) -> float:
        """Get available capital for new positions"""
        try:
            funds = api_client.get_funds()
            
            # Calculate available cash
            if 'bank_balance' in funds:
                total_balance = float(funds['bank_balance'])
                allocated_equity = float(funds.get('allocated_equity', 0))
                blocked_equity = float(funds.get('block_by_trade_equity', 0))
                
                available_capital = allocated_equity - blocked_equity
                return max(0, available_capital)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting available capital: {e}")
            return 0.0
    
    def calculate_optimal_position_size(self, symbol: str, entry_price: float,
                                      stop_loss_price: float, 
                                      risk_per_trade: float = None) -> int:
        """Calculate optimal position size using Kelly Criterion and risk management"""
        
        if risk_per_trade is None:
            risk_per_trade = config.getfloat("TRADING", "MAX_RISK_PER_TRADE", 1.0) / 100
        
        available_capital = self.get_available_capital()
        
        # Risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        # Maximum risk amount
        max_risk_amount = available_capital * risk_per_trade
        
        # Basic position size
        basic_position_size = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
        
        # Apply Kelly Criterion if we have historical data
        kelly_multiplier = self._calculate_kelly_multiplier(symbol)
        adjusted_position_size = int(basic_position_size * kelly_multiplier)
        
        # Apply concentration limits
        max_position_value = available_capital * self.max_position_size
        max_shares = int(max_position_value / entry_price)
        
        final_position_size = min(adjusted_position_size, max_shares)
        
        return max(0, final_position_size)
    
    def record_trade(self, symbol: str, action: str, quantity: int, 
                    entry_price: float, exit_price: float = None,
                    strategy: str = "", timestamp: datetime = None):
        """Record a completed trade"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        trade = {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'strategy': strategy,
            'timestamp': timestamp,
            'pnl': 0.0,
            'return_pct': 0.0,
            'holding_period': 0
        }
        
        # Calculate P&L if trade is closed
        if exit_price is not None:
            if action.upper() == 'BUY':
                trade['pnl'] = (exit_price - entry_price) * quantity
            else:  # SELL
                trade['pnl'] = (entry_price - exit_price) * quantity
            
            trade['return_pct'] = trade['pnl'] / (entry_price * quantity) * 100
        
        self.trade_history.append(trade)
        logger.info(f"Recorded trade: {symbol} {action} {quantity} @ {entry_price}")
    
    def get_performance_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed performance analytics"""
        
        try:
            # Filter recent trades
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_trades = [
                trade for trade in self.trade_history 
                if trade['timestamp'] > cutoff_date and trade['exit_price'] is not None
            ]
            
            if not recent_trades:
                return {'error': 'No completed trades in the specified period'}
            
            # Calculate metrics
            returns = [trade['return_pct'] for trade in recent_trades]
            pnls = [trade['pnl'] for trade in recent_trades]
            
            # Basic metrics
            total_trades = len(recent_trades)
            winning_trades = len([r for r in returns if r > 0])
            losing_trades = len([r for r in returns if r < 0])
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            avg_return = np.mean(returns) if returns else 0
            total_pnl = sum(pnls)
            
            # Risk metrics
            return_std = np.std(returns) if len(returns) > 1 else 0
            sharpe_ratio = avg_return / return_std if return_std > 0 else 0
            
            # Profit factor
            gross_profit = sum([pnl for pnl in pnls if pnl > 0])
            gross_loss = abs(sum([pnl for pnl in pnls if pnl < 0]))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Strategy breakdown
            strategy_performance = self._analyze_strategy_performance(recent_trades)
            
            # Monthly performance
            monthly_performance = self._calculate_monthly_performance(recent_trades)
            
            return {
                'period_days': days,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'avg_return_pct': avg_return,
                'total_pnl': total_pnl,
                'sharpe_ratio': sharpe_ratio,
                'profit_factor': profit_factor,
                'max_win': max(pnls) if pnls else 0,
                'max_loss': min(pnls) if pnls else 0,
                'strategy_performance': strategy_performance,
                'monthly_performance': monthly_performance
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance analytics: {e}")
            return {'error': str(e)}
    
    def rebalance_portfolio(self, target_allocation: Dict[str, float]) -> List[Dict]:
        """Rebalance portfolio to target allocation"""
        
        rebalance_orders = []
        
        try:
            # Get current positions
            positions = api_client.get_positions()
            current_allocation = self._calculate_current_allocation(positions)
            
            total_portfolio_value = sum(
                abs(pos.quantity * pos.current_price) for pos in positions
            )
            
            if total_portfolio_value == 0:
                logger.warning("No portfolio value to rebalance")
                return rebalance_orders
            
            # Calculate required trades
            for symbol, target_weight in target_allocation.items():
                current_weight = current_allocation.get(symbol, 0)
                weight_diff = target_weight - current_weight
                
                if abs(weight_diff) > 0.01:  # 1% threshold
                    # Calculate required position change
                    target_value = total_portfolio_value * target_weight
                    current_position = next(
                        (pos for pos in positions if pos.symbol == symbol), None
                    )
                    
                    if current_position:
                        current_value = current_position.quantity * current_position.current_price
                        value_diff = target_value - current_value
                        quantity_diff = int(value_diff / current_position.current_price)
                        
                        if quantity_diff != 0:
                            order = {
                                'symbol': symbol,
                                'action': 'BUY' if quantity_diff > 0 else 'SELL',
                                'quantity': abs(quantity_diff),
                                'order_type': 'MARKET',
                                'reason': 'REBALANCE'
                            }
                            rebalance_orders.append(order)
            
            logger.info(f"Generated {len(rebalance_orders)} rebalancing orders")
            return rebalance_orders
            
        except Exception as e:
            logger.error(f"Error in portfolio rebalancing: {e}")
            return rebalance_orders
    
    def _calculate_portfolio_metrics(self, positions: List[Position], 
                                   funds: Dict) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        
        # Basic values
        total_invested = sum(abs(pos.quantity * pos.average_price) for pos in positions)
        current_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        # Cash balance
        cash_balance = float(funds.get('allocated_equity', 0)) - float(funds.get('block_by_trade_equity', 0))
        total_value = current_value + cash_balance
        
        # Returns
        total_return = (total_value - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        
        # Calculate other metrics (simplified)
        return PortfolioMetrics(
            total_value=total_value,
            cash_balance=cash_balance,
            invested_amount=total_invested,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=sum(trade.get('pnl', 0) for trade in self.trade_history),
            total_return=total_return,
            daily_return=0.0,  # Would need historical data
            sharpe_ratio=0.0,  # Would need historical returns
            max_drawdown=0.0,  # Would need historical equity curve
            win_rate=self._calculate_win_rate(),
            profit_factor=self._calculate_profit_factor()
        )
    
    def _get_position_breakdown(self, positions: List[Position]) -> List[Dict]:
        """Get detailed position breakdown"""
        breakdown = []
        
        total_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        
        for pos in positions:
            if pos.quantity != 0:
                position_value = abs(pos.quantity * pos.current_price)
                weight = position_value / total_value if total_value > 0 else 0
                
                breakdown.append({
                    'symbol': pos.symbol,
                    'quantity': pos.quantity,
                    'avg_price': pos.average_price,
                    'current_price': pos.current_price,
                    'market_value': position_value,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'weight': weight,
                    'return_pct': ((pos.current_price - pos.average_price) / pos.average_price * 100) if pos.average_price > 0 else 0
                })
        
        # Sort by market value
        breakdown.sort(key=lambda x: x['market_value'], reverse=True)
        return breakdown
    
    def _get_sector_allocation(self, positions: List[Position]) -> Dict[str, float]:
        """Get sector-wise allocation"""
        # This would typically use a sector mapping database
        # For now, return a simplified allocation
        sector_map = {
            'RELIND': 'Energy',
            'TCS': 'Technology',
            'INFY': 'Technology',
            'HINDUNILVR': 'Consumer Goods',
            'ITC': 'Consumer Goods',
            'SBIN': 'Banking',
            'KOTAKBANK': 'Banking',
            'HDFCBANK': 'Banking',
            'AXISBANK': 'Banking',
            'BAJFINANCE': 'Financial Services'
        }
        
        sector_allocation = {}
        total_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        
        for pos in positions:
            if pos.quantity != 0:
                sector = sector_map.get(pos.symbol, 'Others')
                position_value = abs(pos.quantity * pos.current_price)
                weight = position_value / total_value if total_value > 0 else 0
                
                sector_allocation[sector] = sector_allocation.get(sector, 0) + weight
        
        return sector_allocation
    
    def _calculate_margin_utilization(self, funds: Dict) -> float:
        """Calculate margin utilization percentage"""
        try:
            allocated = float(funds.get('allocated_equity', 0))
            blocked = float(funds.get('block_by_trade_equity', 0))
            
            return (blocked / allocated * 100) if allocated > 0 else 0
        except:
            return 0.0
    
    def _calculate_risk_metrics(self, positions: List[Position]) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        # Simplified risk metrics
        total_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        
        if total_value == 0:
            return {'concentration_risk': 0, 'sector_concentration': 0}
        
        # Concentration risk (largest position weight)
        max_position_weight = 0
        if positions:
            max_position = max(positions, key=lambda p: abs(p.quantity * p.current_price))
            max_position_weight = abs(max_position.quantity * max_position.current_price) / total_value
        
        return {
            'concentration_risk': max_position_weight,
            'sector_concentration': 0.0,  # Would need sector mapping
            'var_1day': 0.0,  # Would need returns data
            'beta': 1.0  # Would need market data
        }
    
    def _calculate_kelly_multiplier(self, symbol: str) -> float:
        """Calculate Kelly Criterion multiplier for position sizing"""
        # Get historical trades for this symbol
        symbol_trades = [
            trade for trade in self.trade_history 
            if trade['symbol'] == symbol and trade['exit_price'] is not None
        ]
        
        if len(symbol_trades) < 10:  # Need sufficient history
            return 0.5  # Conservative default
        
        returns = [trade['return_pct'] / 100 for trade in symbol_trades]
        
        if not returns:
            return 0.5
        
        # Calculate win rate and average win/loss
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]
        
        if not wins or not losses:
            return 0.5
        
        win_rate = len(wins) / len(returns)
        avg_win = np.mean(wins)
        avg_loss = abs(np.mean(losses))
        
        # Kelly formula: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
        if avg_loss > 0:
            b = avg_win / avg_loss
            kelly_fraction = (b * win_rate - (1 - win_rate)) / b
            
            # Apply conservative cap (max 25% Kelly)
            return max(0.1, min(0.25, kelly_fraction))
        
        return 0.5
    
    def _calculate_win_rate(self) -> float:
        """Calculate overall win rate"""
        completed_trades = [
            trade for trade in self.trade_history 
            if trade['exit_price'] is not None
        ]
        
        if not completed_trades:
            return 0.0
        
        winning_trades = len([trade for trade in completed_trades if trade['pnl'] > 0])
        return winning_trades / len(completed_trades)
    
    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor"""
        completed_trades = [
            trade for trade in self.trade_history 
            if trade['exit_price'] is not None
        ]
        
        if not completed_trades:
            return 0.0
        
        gross_profit = sum(trade['pnl'] for trade in completed_trades if trade['pnl'] > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in completed_trades if trade['pnl'] < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    def _analyze_strategy_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by strategy"""
        strategy_stats = {}
        
        for trade in trades:
            strategy = trade.get('strategy', 'Unknown')
            
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'trades': 0,
                    'wins': 0,
                    'total_pnl': 0,
                    'returns': []
                }
            
            strategy_stats[strategy]['trades'] += 1
            strategy_stats[strategy]['total_pnl'] += trade['pnl']
            strategy_stats[strategy]['returns'].append(trade['return_pct'])
            
            if trade['pnl'] > 0:
                strategy_stats[strategy]['wins'] += 1
        
        # Calculate win rates and averages
        for strategy, stats in strategy_stats.items():
            stats['win_rate'] = stats['wins'] / stats['trades'] if stats['trades'] > 0 else 0
            stats['avg_return'] = np.mean(stats['returns']) if stats['returns'] else 0
        
        return strategy_stats
    
    def _calculate_monthly_performance(self, trades: List[Dict]) -> Dict[str, float]:
        """Calculate monthly performance breakdown"""
        monthly_pnl = {}
        
        for trade in trades:
            month_key = trade['timestamp'].strftime('%Y-%m')
            monthly_pnl[month_key] = monthly_pnl.get(month_key, 0) + trade['pnl']
        
        return monthly_pnl
    
    def _calculate_current_allocation(self, positions: List[Position]) -> Dict[str, float]:
        """Calculate current portfolio allocation"""
        allocation = {}
        total_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        
        if total_value == 0:
            return allocation
        
        for pos in positions:
            if pos.quantity != 0:
                weight = abs(pos.quantity * pos.current_price) / total_value
                allocation[pos.symbol] = weight
        
        return allocation

# Export main class
__all__ = ['PortfolioManager', 'PortfolioMetrics']
