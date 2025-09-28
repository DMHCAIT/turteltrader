"""
ETF Market Data Integration
Fetches live and historical data for all ETFs using Kite API
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from etf_database import etf_db
from kite_api_client import KiteAPIClient
from core.config import get_config

class ETFMarketDataManager:
    """Manages live and historical data for all ETFs"""
    
    def __init__(self):
        self.etf_db = etf_db
        self.kite_client = None
        self._init_kite_client()
        
    def _init_kite_client(self):
        """Initialize Kite API client"""
        try:
            config = get_config()
            api_key = config.get('KITE_API', 'api_key')
            access_token = config.get('KITE_API', 'access_token')
            
            if api_key and access_token:
                self.kite_client = KiteAPIClient(api_key, access_token)
                logger.info("ETF Market Data Manager initialized with Kite API")
            else:
                logger.error("Kite API credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Kite API client: {e}")
    
    def get_live_prices(self, symbols: List[str] = None) -> Dict[str, Dict]:
        """Get live prices for ETFs"""
        if not self.kite_client:
            logger.error("Kite API client not available")
            return {}
            
        if symbols is None:
            # Get high priority ETFs by default
            symbols = self.etf_db.get_high_priority_etfs(3)
        
        try:
            # Get LTP data from Kite API
            ltp_data = self.kite_client.get_ltp(symbols)
            
            result = {}
            for symbol in symbols:
                etf_info = self.etf_db.get_etf_by_symbol(symbol)
                if etf_info and symbol in ltp_data:
                    result[symbol] = {
                        'name': etf_info.name,
                        'category': etf_info.category.value,
                        'price': ltp_data[symbol],
                        'priority': etf_info.priority,
                        'nse_symbol': etf_info.nse_symbol,
                        'tracking_index': etf_info.tracking_index,
                        'status': 'LIVE' if ltp_data[symbol] > 0 else 'NO_DATA'
                    }
                else:
                    result[symbol] = {
                        'name': etf_info.name if etf_info else symbol,
                        'category': etf_info.category.value if etf_info else 'Unknown',
                        'price': 0.0,
                        'priority': etf_info.priority if etf_info else 5,
                        'nse_symbol': f"{symbol}.NS",
                        'tracking_index': etf_info.tracking_index if etf_info else 'Unknown',
                        'status': 'NO_DATA'
                    }
            
            logger.info(f"Fetched live prices for {len(result)} ETFs")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get live prices: {e}")
            return {}
    
    def get_all_etfs_live_data(self) -> pd.DataFrame:
        """Get live data for all ETFs as a DataFrame"""
        all_symbols = self.etf_db.get_all_symbols()
        live_data = self.get_live_prices(all_symbols)
        
        # Convert to DataFrame
        rows = []
        for symbol, data in live_data.items():
            rows.append({
                'Symbol': symbol,
                'Name': data['name'],
                'Category': data['category'],
                'Price': data['price'],
                'Priority': data['priority'],
                'Status': data['status'],
                'NSE_Symbol': data['nse_symbol'],
                'Tracking_Index': data['tracking_index']
            })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            # Sort by priority and then by category
            df = df.sort_values(['Priority', 'Category', 'Symbol'])
        
        return df
    
    def get_high_priority_etfs_live(self) -> pd.DataFrame:
        """Get live data for high priority ETFs only"""
        high_priority = self.etf_db.get_high_priority_etfs(3)
        live_data = self.get_live_prices(high_priority)
        
        # Convert to DataFrame
        rows = []
        for symbol, data in live_data.items():
            rows.append({
                'Symbol': symbol,
                'Name': data['name'],
                'Category': data['category'],
                'Price': data['price'],
                'Priority': data['priority'],
                'Status': data['status']
            })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(['Priority', 'Symbol'])
        
        return df
    
    def get_sector_wise_data(self) -> Dict[str, pd.DataFrame]:
        """Get ETF data organized by sector"""
        sectors = self.etf_db.get_sector_etfs()
        sector_data = {}
        
        for sector, symbols in sectors.items():
            if symbols:  # Only process sectors that have ETFs
                live_data = self.get_live_prices(symbols)
                rows = []
                for symbol, data in live_data.items():
                    rows.append({
                        'Symbol': symbol,
                        'Name': data['name'],
                        'Price': data['price'],
                        'Status': data['status']
                    })
                sector_data[sector] = pd.DataFrame(rows)
        
        return sector_data
    
    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for an ETF"""
        if not self.kite_client:
            logger.error("Kite API client not available")
            return pd.DataFrame()
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format for Kite API
            instrument_token = f"NSE:{symbol}"
            
            # This would need to be implemented based on Kite's historical data API
            # For now, return empty DataFrame as placeholder
            logger.warning(f"Historical data fetch not yet implemented for {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_etf_summary(self) -> Dict:
        """Get summary statistics of all ETFs"""
        try:
            all_data = self.get_all_etfs_live_data()
            
            if all_data.empty:
                return {}
            
            summary = {
                'total_etfs': len(all_data),
                'categories': all_data['Category'].value_counts().to_dict(),
                'live_data_count': len(all_data[all_data['Status'] == 'LIVE']),
                'no_data_count': len(all_data[all_data['Status'] == 'NO_DATA']),
                'high_priority_count': len(all_data[all_data['Priority'] <= 3]),
                'average_price': all_data[all_data['Price'] > 0]['Price'].mean(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate ETF summary: {e}")
            return {}

# Create global instance
etf_market_data = ETFMarketDataManager()

if __name__ == "__main__":
    # Test the market data manager
    print("🏦 ETF MARKET DATA MANAGER")
    print("=" * 40)
    
    # Get summary
    summary = etf_market_data.get_etf_summary()
    if summary:
        print(f"Total ETFs: {summary.get('total_etfs', 0)}")
        print(f"Live Data Available: {summary.get('live_data_count', 0)}")
        print(f"High Priority ETFs: {summary.get('high_priority_count', 0)}")
    
    # Get high priority ETFs
    print("\n📈 High Priority ETFs:")
    high_priority_df = etf_market_data.get_high_priority_etfs_live()
    if not high_priority_df.empty:
        print(high_priority_df.to_string(index=False))
    
    print(f"\n✅ ETF Market Data Manager ready")