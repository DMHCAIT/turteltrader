"""
Turtle Trader - ETF Order Management
Specialized order handling for ETF trading with MTF and CNC order types
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from core.config import config
from core.api_client import api_client

class ETFOrderType(Enum):
    """ETF-specific order types"""
    CNC = "CNC"  # Cash and Carry - Full payment required
    MTF = "MTF"  # Margin Trading Facility - Leverage trading

class ETFProductType(Enum):
    """ETF product types for different strategies"""
    CASH = "CASH"        # Cash segment
    MARGIN = "MARGIN"    # Margin segment
    INTRADAY = "MIS"     # Margin Intraday Square-off

@dataclass
class ETFOrderRequest:
    """ETF-specific order request structure"""
    symbol: str
    action: str  # BUY/SELL
    quantity: int
    order_type: ETFOrderType
    product_type: ETFProductType
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    validity: str = "DAY"
    disclosed_quantity: int = 0

class ETFOrderManager:
    """Specialized order manager for ETF trading"""
    
    def __init__(self):
        self.default_order_type = ETFOrderType(config.get("TRADING", "DEFAULT_ORDER_TYPE", "CNC"))
        self.mtf_margin_multiplier = config.getfloat("TRADING", "MTF_MARGIN_MULTIPLIER", 4.0)
        self.max_positions = config.getint("TRADING", "MAX_POSITIONS", 8)
        
        # ETF-specific configuration
        self.etf_symbols = self._load_etf_symbols()
        self.etf_lot_sizes = self._get_etf_lot_sizes()
        
        logger.info(f"ETF Order Manager initialized with {len(self.etf_symbols)} ETF symbols")
    
    def _load_etf_symbols(self) -> List[str]:
        """Load ETF symbols from configuration"""
        symbols_str = config.get("TRADING", "SYMBOLS", "GOLDBEES,NIFTYBEES,BANKBEES")
        return [symbol.strip() for symbol in symbols_str.split(",")]
    
    def _get_etf_lot_sizes(self) -> Dict[str, int]:
        """Get lot sizes for different ETFs"""
        # Standard lot sizes for popular ETFs (can be updated from API)
        return {
            "GOLDBEES": 1,      # Gold ETF
            "NIFTYBEES": 1,     # Nifty ETF
            "BANKBEES": 1,      # Bank ETF
            "JUNIORBEES": 1,    # Junior ETF
            "LIQUIDBEES": 1,    # Liquid ETF
            "ITBEES": 1,        # IT ETF
            "PHARMBEES": 1,     # Pharma ETF
            "PSUBANK": 1,       # PSU Bank ETF
            "CPSE": 1,          # CPSE ETF
            "NETF": 1           # Next 50 ETF
        }
    
    def calculate_etf_position_size(self, symbol: str, price: float, 
                                  order_type: ETFOrderType) -> int:
        """Calculate optimal position size for ETF"""
        
        available_capital = self._get_available_capital()
        position_size_percent = config.getfloat("TRADING", "POSITION_SIZE_PERCENT", 3.0) / 100
        
        # Calculate base position size
        base_allocation = available_capital * position_size_percent
        
        # Adjust for order type
        if order_type == ETFOrderType.MTF:
            # MTF allows leverage
            effective_capital = base_allocation * self.mtf_margin_multiplier
        else:
            # CNC requires full payment
            effective_capital = base_allocation
        
        # Calculate quantity
        max_quantity = int(effective_capital / price)
        
        # Apply ETF lot size
        lot_size = self.etf_lot_sizes.get(symbol, 1)
        adjusted_quantity = (max_quantity // lot_size) * lot_size
        
        return max(adjusted_quantity, lot_size)
    
    def place_etf_order(self, order_request: ETFOrderRequest) -> Dict[str, Any]:
        """Place ETF order with proper validation"""
        
        try:
            # Validate ETF symbol
            if order_request.symbol not in self.etf_symbols:
                return {
                    'success': False,
                    'error': f'Symbol {order_request.symbol} not in ETF list'
                }
            
            # Validate order type
            if order_request.order_type not in [ETFOrderType.CNC, ETFOrderType.MTF]:
                return {
                    'success': False,
                    'error': f'Invalid order type for ETF: {order_request.order_type}'
                }
            
            # Prepare order parameters
            order_params = {
                'stock_code': order_request.symbol,
                'exchange_code': 'NSE',  # ETFs primarily on NSE
                'product': order_request.product_type.value,
                'action': order_request.action,
                'order_type': 'MARKET' if order_request.price is None else 'LIMIT',
                'quantity': str(order_request.quantity),
                'validity': order_request.validity,
                'disclosed_quantity': str(order_request.disclosed_quantity)
            }
            
            # Add price for limit orders
            if order_request.price is not None:
                order_params['price'] = str(order_request.price)
            
            # Add stop loss for bracket orders
            if order_request.stop_loss is not None:
                order_params['stoploss'] = str(order_request.stop_loss)
            
            # Place order through API
            response = api_client.place_order(**order_params)
            
            if response and 'Success' in response:
                order_id = response.get('order_id', 'N/A')
                
                logger.info(f"ETF Order placed: {order_request.symbol} {order_request.action} "
                          f"{order_request.quantity} @ {order_request.order_type.value} - "
                          f"Order ID: {order_id}")
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'response': response
                }
            else:
                error_msg = response.get('Error', 'Unknown error') if response else 'No response'
                logger.error(f"ETF Order failed: {order_request.symbol} - {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'response': response
                }
        
        except Exception as e:
            logger.error(f"Exception placing ETF order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_etf_buy_order(self, symbol: str, price: float = None, 
                           order_type: ETFOrderType = None) -> ETFOrderRequest:
        """Create standardized ETF buy order"""
        
        if order_type is None:
            order_type = self.default_order_type
        
        # Calculate position size
        quantity = self.calculate_etf_position_size(symbol, price or 0, order_type)
        
        # Determine product type
        if order_type == ETFOrderType.MTF:
            product_type = ETFProductType.MARGIN
        else:
            product_type = ETFProductType.CASH
        
        return ETFOrderRequest(
            symbol=symbol,
            action="BUY",
            quantity=quantity,
            order_type=order_type,
            product_type=product_type,
            price=price
        )
    
    def create_etf_sell_order(self, symbol: str, quantity: int, 
                            price: float = None) -> ETFOrderRequest:
        """Create standardized ETF sell order"""
        
        return ETFOrderRequest(
            symbol=symbol,
            action="SELL",
            quantity=quantity,
            order_type=ETFOrderType.CNC,  # Usually sell as CNC
            product_type=ETFProductType.CASH,
            price=price
        )
    
    def get_etf_positions(self) -> List[Dict]:
        """Get current ETF positions"""
        
        try:
            positions = api_client.get_positions()
            etf_positions = []
            
            for position in positions:
                if hasattr(position, 'symbol') and position.symbol in self.etf_symbols:
                    etf_positions.append({
                        'symbol': position.symbol,
                        'quantity': position.quantity,
                        'avg_price': position.average_price,
                        'current_price': position.current_price,
                        'pnl': position.unrealized_pnl,
                        'product_type': getattr(position, 'product', 'Unknown')
                    })
            
            return etf_positions
            
        except Exception as e:
            logger.error(f"Error getting ETF positions: {e}")
            return []
    
    def get_etf_market_data(self) -> Dict[str, Dict]:
        """Get real-time market data for all ETFs"""
        
        market_data = {}
        
        for symbol in self.etf_symbols:
            try:
                # Get quotes
                quote = api_client.get_quotes(
                    stock_code=symbol,
                    exchange_code="NSE"
                )
                
                if quote and 'Success' in quote:
                    market_data[symbol] = {
                        'ltp': float(quote.get('ltp', 0)),
                        'open': float(quote.get('open', 0)),
                        'high': float(quote.get('high', 0)),
                        'low': float(quote.get('low', 0)),
                        'volume': int(quote.get('volume', 0)),
                        'change': float(quote.get('change', 0)),
                        'change_percent': float(quote.get('change_percent', 0))
                    }
                
            except Exception as e:
                logger.error(f"Error getting market data for {symbol}: {e}")
                market_data[symbol] = {
                    'ltp': 0, 'open': 0, 'high': 0, 'low': 0, 
                    'volume': 0, 'change': 0, 'change_percent': 0
                }
        
        return market_data
    
    def _check_mtf_margin_available(self, symbol: str) -> bool:
        """
        Check if MTF margin is available for the symbol
        MTF Priority with CNC Fallback logic
        """
        try:
            # Get funds information from API
            funds_response = self.api_client.get_funds()
            
            if funds_response and funds_response.get('Success'):
                funds_data = funds_response.get('Result', {})
                
                # Check available margin
                available_margin = float(funds_data.get('margin_available', 0))
                mtf_limit = float(funds_data.get('mtf_limit', 0))
                
                # MTF is available if we have sufficient margin
                min_required_margin = 10000  # Minimum ₹10,000 margin required
                
                mtf_available = (available_margin >= min_required_margin and 
                               mtf_limit > 0)
                
                logger.info(f"MTF Check for {symbol}: Available=₹{available_margin:.0f}, "
                           f"Limit=₹{mtf_limit:.0f}, Available={mtf_available}")
                
                return mtf_available
            
            else:
                logger.warning("Could not fetch funds data for MTF check")
                return False
                
        except Exception as e:
            logger.error(f"Error checking MTF availability: {e}")
            return False
    
    def determine_optimal_order_type(self, symbol: str) -> ETFOrderType:
        """
        Determine optimal order type: MTF first priority, CNC fallback
        """
        from core.config import config
        
        mtf_priority = config.getboolean('TRADING', 'MTF_FIRST_PRIORITY', fallback=True)
        
        if not mtf_priority:
            return ETFOrderType.CNC
        
        # Check if MTF is available
        if self._check_mtf_margin_available(symbol):
            logger.info(f"Using MTF for {symbol} - margin available")
            return ETFOrderType.MTF
        else:
            logger.info(f"MTF not available for {symbol}, using CNC fallback")
            return ETFOrderType.CNC
    
    def calculate_etf_allocation(self, total_capital: float) -> Dict[str, float]:
        """Calculate optimal ETF allocation across different categories"""
        
        # ETF category allocation strategy
        etf_categories = {
            'BROAD_MARKET': ['NIFTYBEES', 'JUNIORBEES', 'NETF'],  # 40%
            'SECTOR': ['BANKBEES', 'ITBEES', 'PHARMBEES'],        # 30%
            'THEMATIC': ['GOLDBEES', 'LIQUIDBEES'],               # 20%
            'SPECIALTY': ['PSUBANK', 'CPSE']                      # 10%
        }
        
        category_allocation = {
            'BROAD_MARKET': 0.40,
            'SECTOR': 0.30,
            'THEMATIC': 0.20,
            'SPECIALTY': 0.10
        }
        
        allocation = {}
        
        for category, weight in category_allocation.items():
            category_capital = total_capital * weight
            etfs_in_category = etf_categories.get(category, [])
            
            if etfs_in_category:
                per_etf_allocation = category_capital / len(etfs_in_category)
                
                for etf in etfs_in_category:
                    allocation[etf] = per_etf_allocation
        
        return allocation
    
    def _get_available_capital(self) -> float:
        """Get available capital for trading"""
        
        try:
            funds = api_client.get_funds()
            
            if funds and isinstance(funds, dict):
                # Extract available margin/cash
                available = float(funds.get('available_margin', 0))
                if available == 0:
                    available = float(funds.get('available_cash', 0))
                
                return available
            
        except Exception as e:
            logger.error(f"Error getting available capital: {e}")
        
        # Fallback to configured capital
        return config.getfloat("TRADING", "CAPITAL", 1000000)

# Create global ETF order manager instance
etf_order_manager = ETFOrderManager()

# Export classes and instance
__all__ = ['ETFOrderType', 'ETFProductType', 'ETFOrderRequest', 'ETFOrderManager', 'etf_order_manager']
