"""
Turtle Trader - Advanced Risk Management Module
Comprehensive risk management with real-time monitoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
from scipy import stats
from loguru import logger

from core.config import config, Constants, Utils
from core.api_client import api_client, Position

@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    var_1day: float
    var_5day: float
    cvar_1day: float
    cvar_5day: float
    max_drawdown: float
    current_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    volatility: float
    correlation_risk: float

@dataclass
class PositionRisk:
    """Individual position risk metrics"""
    symbol: str
    position_size: float
    market_value: float
    portfolio_weight: float
    var_contribution: float
    beta: float
    volatility: float
    concentration_risk: float

class VaRCalculator:
    """Value at Risk calculator with multiple methods"""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        
    def parametric_var(self, returns: pd.Series, time_horizon: int = 1) -> float:
        """Calculate parametric VaR (assumes normal distribution)"""
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Z-score for confidence level
        z_score = stats.norm.ppf(self.alpha)
        
        # VaR calculation
        var = -(mean_return + z_score * std_return) * np.sqrt(time_horizon)
        return var
    
    def historical_var(self, returns: pd.Series, time_horizon: int = 1) -> float:
        """Calculate historical VaR using empirical distribution"""
        if len(returns) < 100:
            logger.warning("Insufficient data for reliable historical VaR")
            return self.parametric_var(returns, time_horizon)
        
        # Scale returns for time horizon
        scaled_returns = returns * np.sqrt(time_horizon)
        
        # Calculate VaR as percentile
        var = -np.percentile(scaled_returns, self.alpha * 100)
        return var
    
    def monte_carlo_var(self, returns: pd.Series, time_horizon: int = 1, 
                       num_simulations: int = 10000) -> float:
        """Calculate Monte Carlo VaR"""
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Generate random scenarios
        random_returns = np.random.normal(mean_return, std_return, num_simulations)
        scaled_returns = random_returns * np.sqrt(time_horizon)
        
        # Calculate VaR
        var = -np.percentile(scaled_returns, self.alpha * 100)
        return var
    
    def conditional_var(self, returns: pd.Series, time_horizon: int = 1) -> float:
        """Calculate Conditional VaR (Expected Shortfall)"""
        var = self.historical_var(returns, time_horizon)
        
        # Scale returns for time horizon
        scaled_returns = returns * np.sqrt(time_horizon)
        
        # Calculate CVaR as average of losses beyond VaR
        tail_losses = scaled_returns[scaled_returns <= -var]
        if len(tail_losses) > 0:
            cvar = -tail_losses.mean()
        else:
            cvar = var
        
        return cvar

class PortfolioRiskManager:
    """Comprehensive portfolio risk management"""
    
    def __init__(self):
        self.var_calculator = VaRCalculator()
        self.position_limits = {}
        self.sector_limits = {}
        self.correlation_threshold = config.getfloat("RISK_MANAGEMENT", "MAX_CORRELATION", 0.7)
        self.max_portfolio_var = config.getfloat("RISK_MANAGEMENT", "MAX_PORTFOLIO_VAR", 0.05)
        self.max_position_weight = config.getfloat("RISK_MANAGEMENT", "POSITION_CONCENTRATION_LIMIT", 10.0) / 100
        
    def calculate_portfolio_metrics(self, positions: List[Position], 
                                  returns_data: Dict[str, pd.Series]) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        
        if not positions:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(positions, returns_data)
        
        if portfolio_returns.empty:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Calculate VaR metrics
        var_1day = self.var_calculator.historical_var(portfolio_returns, 1)
        var_5day = self.var_calculator.historical_var(portfolio_returns, 5)
        cvar_1day = self.var_calculator.conditional_var(portfolio_returns, 1)
        cvar_5day = self.var_calculator.conditional_var(portfolio_returns, 5)
        
        # Calculate drawdown metrics
        max_dd, current_dd = self._calculate_drawdown_metrics(portfolio_returns)
        
        # Calculate risk-return metrics
        sharpe = self._calculate_sharpe_ratio(portfolio_returns)
        sortino = self._calculate_sortino_ratio(portfolio_returns)
        
        # Calculate beta and volatility (assuming market index)
        beta = self._calculate_portfolio_beta(portfolio_returns, returns_data)
        volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Calculate correlation risk
        correlation_risk = self._calculate_correlation_risk(positions, returns_data)
        
        return RiskMetrics(
            var_1day=var_1day,
            var_5day=var_5day,
            cvar_1day=cvar_1day,
            cvar_5day=cvar_5day,
            max_drawdown=max_dd,
            current_drawdown=current_dd,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            beta=beta,
            volatility=volatility,
            correlation_risk=correlation_risk
        )
    
    def calculate_position_risks(self, positions: List[Position], 
                               returns_data: Dict[str, pd.Series]) -> List[PositionRisk]:
        """Calculate individual position risk metrics"""
        position_risks = []
        total_portfolio_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        
        for position in positions:
            symbol = position.symbol
            market_value = abs(position.quantity * position.current_price)
            portfolio_weight = market_value / total_portfolio_value if total_portfolio_value > 0 else 0
            
            if symbol in returns_data and len(returns_data[symbol]) > 20:
                returns = returns_data[symbol]
                
                # Calculate position-specific metrics
                var_contribution = self._calculate_var_contribution(position, returns, total_portfolio_value)
                beta = self._calculate_asset_beta(returns, returns_data.get('NIFTY', returns))
                volatility = returns.std() * np.sqrt(252)
                concentration_risk = self._calculate_concentration_risk(portfolio_weight)
                
                position_risk = PositionRisk(
                    symbol=symbol,
                    position_size=position.quantity,
                    market_value=market_value,
                    portfolio_weight=portfolio_weight,
                    var_contribution=var_contribution,
                    beta=beta,
                    volatility=volatility,
                    concentration_risk=concentration_risk
                )
                position_risks.append(position_risk)
        
        return position_risks
    
    def validate_new_position(self, symbol: str, quantity: int, price: float,
                            current_positions: List[Position], 
                            returns_data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Validate if new position meets risk criteria"""
        validation_result = {
            'approved': True,
            'warnings': [],
            'errors': [],
            'risk_metrics': {}
        }
        
        # Calculate new position value
        position_value = abs(quantity * price)
        current_portfolio_value = sum(abs(pos.quantity * pos.current_price) for pos in current_positions)
        new_portfolio_value = current_portfolio_value + position_value
        
        # Check concentration limits
        new_weight = position_value / new_portfolio_value
        if new_weight > self.max_position_weight:
            validation_result['errors'].append(
                f"Position weight {new_weight:.2%} exceeds limit {self.max_position_weight:.2%}"
            )
            validation_result['approved'] = False
        
        # Check if position already exists
        existing_position = next((pos for pos in current_positions if pos.symbol == symbol), None)
        if existing_position:
            combined_value = abs(existing_position.quantity * existing_position.current_price) + position_value
            combined_weight = combined_value / new_portfolio_value
            if combined_weight > self.max_position_weight:
                validation_result['errors'].append(
                    f"Combined position weight {combined_weight:.2%} exceeds limit"
                )
                validation_result['approved'] = False
        
        # Check correlation with existing positions
        if symbol in returns_data:
            high_correlations = self._check_correlation_limits(symbol, returns_data, current_positions)
            if high_correlations:
                validation_result['warnings'].extend(
                    [f"High correlation with {corr_symbol}: {corr:.2f}" 
                     for corr_symbol, corr in high_correlations]
                )
        
        # Estimate impact on portfolio VaR
        if returns_data and symbol in returns_data:
            var_impact = self._estimate_var_impact(symbol, quantity, price, current_positions, returns_data)
            validation_result['risk_metrics']['var_impact'] = var_impact
            
            if var_impact > self.max_portfolio_var:
                validation_result['errors'].append(
                    f"Position would increase portfolio VaR to {var_impact:.2%}"
                )
                validation_result['approved'] = False
        
        return validation_result
    
    def get_position_size_recommendation(self, symbol: str, entry_price: float,
                                       stop_loss_price: float, available_capital: float,
                                       returns_data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Recommend optimal position size based on risk management"""
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        # Maximum risk per trade (from config)
        max_risk_per_trade = config.getfloat("TRADING", "MAX_RISK_PER_TRADE", 1.0) / 100
        max_risk_amount = available_capital * max_risk_per_trade
        
        # Basic position sizing
        basic_position_size = int(max_risk_amount / risk_per_unit)
        basic_position_value = basic_position_size * entry_price
        
        # Adjust for volatility
        volatility_adjustment = 1.0
        if symbol in returns_data and len(returns_data[symbol]) > 20:
            volatility = returns_data[symbol].std() * np.sqrt(252)
            # Reduce position size for highly volatile assets
            volatility_adjustment = max(0.5, 1 - (volatility - 0.2) * 2)
        
        # Adjust for concentration
        concentration_adjustment = 1.0
        portfolio_weight = basic_position_value / available_capital
        if portfolio_weight > self.max_position_weight:
            concentration_adjustment = self.max_position_weight / portfolio_weight
        
        # Final recommendation
        recommended_size = int(basic_position_size * volatility_adjustment * concentration_adjustment)
        recommended_value = recommended_size * entry_price
        
        return {
            'recommended_quantity': recommended_size,
            'recommended_value': recommended_value,
            'portfolio_weight': recommended_value / available_capital,
            'risk_amount': recommended_size * risk_per_unit,
            'risk_percent': (recommended_size * risk_per_unit) / available_capital,
            'volatility_adjustment': volatility_adjustment,
            'concentration_adjustment': concentration_adjustment
        }
    
    def _calculate_portfolio_returns(self, positions: List[Position], 
                                   returns_data: Dict[str, pd.Series]) -> pd.Series:
        """Calculate portfolio returns from position weights and asset returns"""
        if not positions or not returns_data:
            return pd.Series(dtype=float)
        
        # Calculate position weights
        total_value = sum(abs(pos.quantity * pos.current_price) for pos in positions)
        if total_value == 0:
            return pd.Series(dtype=float)
        
        weights = {}
        for pos in positions:
            if pos.symbol in returns_data:
                weight = (pos.quantity * pos.current_price) / total_value
                weights[pos.symbol] = weight
        
        if not weights:
            return pd.Series(dtype=float)
        
        # Align all return series
        common_dates = None
        for symbol in weights.keys():
            if common_dates is None:
                common_dates = returns_data[symbol].index
            else:
                common_dates = common_dates.intersection(returns_data[symbol].index)
        
        if common_dates.empty:
            return pd.Series(dtype=float)
        
        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=common_dates)
        for symbol, weight in weights.items():
            portfolio_returns += weight * returns_data[symbol].reindex(common_dates, fill_value=0)
        
        return portfolio_returns
    
    def _calculate_drawdown_metrics(self, returns: pd.Series) -> Tuple[float, float]:
        """Calculate maximum and current drawdown"""
        if returns.empty:
            return 0.0, 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1]
        
        return max_drawdown, current_drawdown
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe ratio"""
        if returns.empty or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.05) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if returns.empty:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = downside_returns.std()
        if downside_deviation == 0:
            return 0.0
        
        return (excess_returns.mean() / downside_deviation) * np.sqrt(252)
    
    def _calculate_portfolio_beta(self, portfolio_returns: pd.Series, 
                                returns_data: Dict[str, pd.Series]) -> float:
        """Calculate portfolio beta against market"""
        market_returns = returns_data.get('NIFTY', pd.Series(dtype=float))
        if market_returns.empty or portfolio_returns.empty:
            return 1.0
        
        # Align series
        common_dates = portfolio_returns.index.intersection(market_returns.index)
        if common_dates.empty:
            return 1.0
        
        port_aligned = portfolio_returns.reindex(common_dates)
        market_aligned = market_returns.reindex(common_dates)
        
        covariance = np.cov(port_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        return covariance / market_variance if market_variance != 0 else 1.0
    
    def _calculate_asset_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate asset beta against market"""
        if asset_returns.empty or market_returns.empty:
            return 1.0
        
        common_dates = asset_returns.index.intersection(market_returns.index)
        if len(common_dates) < 20:
            return 1.0
        
        asset_aligned = asset_returns.reindex(common_dates)
        market_aligned = market_returns.reindex(common_dates)
        
        covariance = np.cov(asset_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        return covariance / market_variance if market_variance != 0 else 1.0
    
    def _calculate_correlation_risk(self, positions: List[Position], 
                                  returns_data: Dict[str, pd.Series]) -> float:
        """Calculate overall portfolio correlation risk"""
        if len(positions) < 2:
            return 0.0
        
        symbols = [pos.symbol for pos in positions if pos.symbol in returns_data]
        if len(symbols) < 2:
            return 0.0
        
        # Calculate correlation matrix
        returns_df = pd.DataFrame({symbol: returns_data[symbol] for symbol in symbols})
        correlation_matrix = returns_df.corr()
        
        # Calculate average absolute correlation (excluding diagonal)
        n = len(correlation_matrix)
        total_correlations = 0
        count = 0
        
        for i in range(n):
            for j in range(i+1, n):
                total_correlations += abs(correlation_matrix.iloc[i, j])
                count += 1
        
        return total_correlations / count if count > 0 else 0.0
    
    def _calculate_var_contribution(self, position: Position, returns: pd.Series, 
                                  portfolio_value: float) -> float:
        """Calculate position's contribution to portfolio VaR"""
        position_weight = abs(position.quantity * position.current_price) / portfolio_value
        position_var = self.var_calculator.historical_var(returns)
        
        return position_weight * position_var
    
    def _calculate_concentration_risk(self, portfolio_weight: float) -> float:
        """Calculate concentration risk score"""
        if portfolio_weight <= 0.05:  # 5%
            return 0.0
        elif portfolio_weight <= 0.10:  # 10%
            return 0.25
        elif portfolio_weight <= 0.15:  # 15%
            return 0.5
        elif portfolio_weight <= 0.20:  # 20%
            return 0.75
        else:
            return 1.0
    
    def _check_correlation_limits(self, symbol: str, returns_data: Dict[str, pd.Series],
                                current_positions: List[Position]) -> List[Tuple[str, float]]:
        """Check correlation limits with existing positions"""
        high_correlations = []
        
        if symbol not in returns_data:
            return high_correlations
        
        new_asset_returns = returns_data[symbol]
        
        for position in current_positions:
            if position.symbol in returns_data and position.symbol != symbol:
                existing_returns = returns_data[position.symbol]
                
                # Calculate correlation
                common_dates = new_asset_returns.index.intersection(existing_returns.index)
                if len(common_dates) >= 20:
                    correlation = new_asset_returns.reindex(common_dates).corr(
                        existing_returns.reindex(common_dates)
                    )
                    
                    if abs(correlation) > self.correlation_threshold:
                        high_correlations.append((position.symbol, correlation))
        
        return high_correlations
    
    def _estimate_var_impact(self, symbol: str, quantity: int, price: float,
                           current_positions: List[Position], 
                           returns_data: Dict[str, pd.Series]) -> float:
        """Estimate impact of new position on portfolio VaR"""
        # Create simulated new portfolio
        new_positions = current_positions.copy()
        
        # Add new position
        from core.api_client import Position
        new_position = Position(
            symbol=symbol,
            exchange="NSE",
            product_type="cash",
            quantity=quantity,
            average_price=price,
            current_price=price,
            pnl=0,
            unrealized_pnl=0
        )
        new_positions.append(new_position)
        
        # Calculate new portfolio returns
        new_portfolio_returns = self._calculate_portfolio_returns(new_positions, returns_data)
        
        if new_portfolio_returns.empty:
            return 0.0
        
        # Calculate new VaR
        new_var = self.var_calculator.historical_var(new_portfolio_returns)
        return new_var

class RealTimeRiskMonitor:
    """Real-time risk monitoring and alerting"""
    
    def __init__(self):
        self.risk_manager = PortfolioRiskManager()
        self.alert_thresholds = {
            'var_breach': 0.05,
            'drawdown_limit': 0.10,
            'concentration_limit': 0.15,
            'correlation_limit': 0.80
        }
        self.alerts = []
        
    def monitor_portfolio(self, positions: List[Position], 
                         returns_data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Monitor portfolio risk in real-time"""
        
        # Calculate current risk metrics
        risk_metrics = self.risk_manager.calculate_portfolio_metrics(positions, returns_data)
        position_risks = self.risk_manager.calculate_position_risks(positions, returns_data)
        
        # Check for risk breaches
        alerts = self._check_risk_breaches(risk_metrics, position_risks)
        
        # Update alert history
        self.alerts.extend(alerts)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert['timestamp'] > cutoff_time]
        
        return {
            'risk_metrics': risk_metrics,
            'position_risks': position_risks,
            'alerts': alerts,
            'risk_score': self._calculate_overall_risk_score(risk_metrics, position_risks)
        }
    
    def _check_risk_breaches(self, risk_metrics: RiskMetrics, 
                           position_risks: List[PositionRisk]) -> List[Dict[str, Any]]:
        """Check for risk threshold breaches"""
        alerts = []
        current_time = datetime.now()
        
        # VaR breach
        if risk_metrics.var_1day > self.alert_thresholds['var_breach']:
            alerts.append({
                'type': 'VAR_BREACH',
                'severity': 'HIGH',
                'message': f"Portfolio VaR ({risk_metrics.var_1day:.2%}) exceeds limit ({self.alert_thresholds['var_breach']:.2%})",
                'timestamp': current_time,
                'value': risk_metrics.var_1day
            })
        
        # Drawdown breach
        if abs(risk_metrics.current_drawdown) > self.alert_thresholds['drawdown_limit']:
            alerts.append({
                'type': 'DRAWDOWN_BREACH',
                'severity': 'HIGH',
                'message': f"Current drawdown ({risk_metrics.current_drawdown:.2%}) exceeds limit",
                'timestamp': current_time,
                'value': risk_metrics.current_drawdown
            })
        
        # Concentration risk
        for pos_risk in position_risks:
            if pos_risk.portfolio_weight > self.alert_thresholds['concentration_limit']:
                alerts.append({
                    'type': 'CONCENTRATION_RISK',
                    'severity': 'MEDIUM',
                    'message': f"{pos_risk.symbol} weight ({pos_risk.portfolio_weight:.2%}) exceeds concentration limit",
                    'timestamp': current_time,
                    'symbol': pos_risk.symbol,
                    'value': pos_risk.portfolio_weight
                })
        
        # Correlation risk
        if risk_metrics.correlation_risk > self.alert_thresholds['correlation_limit']:
            alerts.append({
                'type': 'CORRELATION_RISK',
                'severity': 'MEDIUM',
                'message': f"Portfolio correlation risk ({risk_metrics.correlation_risk:.2%}) is high",
                'timestamp': current_time,
                'value': risk_metrics.correlation_risk
            })
        
        return alerts
    
    def _calculate_overall_risk_score(self, risk_metrics: RiskMetrics, 
                                    position_risks: List[PositionRisk]) -> float:
        """Calculate overall portfolio risk score (0-100)"""
        score_components = []
        
        # VaR component (0-25 points)
        var_score = min(25, (risk_metrics.var_1day / 0.10) * 25)
        score_components.append(var_score)
        
        # Drawdown component (0-25 points)
        dd_score = min(25, (abs(risk_metrics.current_drawdown) / 0.20) * 25)
        score_components.append(dd_score)
        
        # Concentration component (0-25 points)
        max_concentration = max([pos.portfolio_weight for pos in position_risks], default=0)
        conc_score = min(25, (max_concentration / 0.30) * 25)
        score_components.append(conc_score)
        
        # Correlation component (0-25 points)
        corr_score = min(25, (risk_metrics.correlation_risk / 1.0) * 25)
        score_components.append(corr_score)
        
        return sum(score_components)

# Global risk monitor
risk_monitor = RealTimeRiskMonitor()

# Export main classes
__all__ = [
    'RiskMetrics',
    'PositionRisk', 
    'VaRCalculator',
    'PortfolioRiskManager',
    'RealTimeRiskMonitor',
    'risk_monitor'
]
