"""
📊 COMPREHENSIVE INDIAN ETF DATABASE
===================================

Complete list of Indian ETFs for the trading system with sector classification
and market data integration capabilities.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from datetime import datetime
import json

class ETFCategory(Enum):
    """ETF categories for better organization"""
    BROAD_MARKET = "Broad Market"
    SECTORAL = "Sectoral"
    THEMATIC = "Thematic"
    FIXED_INCOME = "Fixed Income"
    COMMODITY = "Commodity"
    INTERNATIONAL = "International"
    FACTOR_BASED = "Factor Based"

@dataclass
class ETFInfo:
    """Complete ETF information"""
    name: str
    symbol: str
    tracking_index: str
    category: ETFCategory
    nse_symbol: str = None  # NSE symbol for market data
    priority: int = 5  # Default priority for sorting
    is_active: bool = True
    min_investment: float = 1000.0  # Minimum investment amount
    
    def __post_init__(self):
        """Set NSE symbol if not provided"""
        if self.nse_symbol is None:
            self.nse_symbol = f"{self.symbol}.NS"

class IndianETFDatabase:
    """Comprehensive database of Indian ETFs"""
    
    def __init__(self):
        """Initialize the ETF database"""
        self.etfs = self._load_etf_data()
        self.categories = self._organize_by_category()
    
    def _load_etf_data(self) -> Dict[str, ETFInfo]:
        """Load complete ETF data with all requested symbols"""
        etf_data = {
            # Broad Market ETFs - Priority 1-3 (High Liquidity)
            'NIFTYBEES': ETFInfo(
                "Nippon India ETF Nifty 50 BeES", "NIFTYBEES", "Nifty 50",
                ETFCategory.BROAD_MARKET, priority=1
            ),
            'UTISENSETF': ETFInfo(
                "UTI S&P BSE Sensex ETF", "UTISENSETF", "S&P BSE Sensex",
                ETFCategory.BROAD_MARKET, priority=2
            ),
            'ICICINXT50': ETFInfo(
                "ICICI Prudential Nifty Next 50 ETF", "ICICINXT50", "Nifty Next 50",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'SETFNIF100': ETFInfo(
                "SBI ETF Nifty 100", "SETFNIF100", "Nifty 100",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'KOTAKNIFTY200': ETFInfo(
                "Kotak Nifty 200 ETF", "KOTAKNIFTY200", "Nifty 200",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'ABSLNIFTY500ETF': ETFInfo(
                "Aditya Birla Sun Life Nifty 500 ETF", "ABSLNIFTY500ETF", "Nifty 500",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'MOM150ETF': ETFInfo(
                "Motilal Oswal Nifty Midcap 150 ETF", "MOM150ETF", "Nifty Midcap 150",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'MOM250ETF': ETFInfo(
                "Motilal Oswal Nifty Smallcap 250 ETF", "MOM250ETF", "Nifty Smallcap 250",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'MOMMICROETF': ETFInfo(
                "Motilal Oswal Nifty Microcap 250 ETF", "MOMMICROETF", "Nifty Microcap 250",
                ETFCategory.BROAD_MARKET, priority=5
            ),
            'MON100ETF': ETFInfo(
                "Motilal Oswal Nifty 100 ETF", "MON100ETF", "Nifty 100",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'ICICIMID50': ETFInfo(
                "ICICI Prudential Nifty Midcap 150 ETF", "ICICIMID50", "Nifty Midcap 150",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'ICICISMALL100': ETFInfo(
                "ICICI Prudential Nifty Smallcap 250 ETF", "ICICISMALL100", "Nifty Smallcap 250",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            
            # Sectoral ETFs - Priority 1-4
            'BANKBEES': ETFInfo(
                "Nippon India ETF Nifty Bank BeES", "BANKBEES", "Nifty Bank",
                ETFCategory.SECTORAL, priority=1
            ),
            'ITBEES': ETFInfo(
                "Nippon India ETF Nifty IT", "ITBEES", "Nifty IT",
                ETFCategory.SECTORAL, priority=2
            ),
            'PSUBANKBEES': ETFInfo(
                "Nippon India ETF Nifty PSU Bank", "PSUBANKBEES", "Nifty PSU Bank",
                ETFCategory.SECTORAL, priority=3
            ),
            'PHARMABEES': ETFInfo(
                "Nippon India ETF Nifty Pharma", "PHARMABEES", "Nifty Pharma",
                ETFCategory.SECTORAL, priority=3
            ),
            'FMCGBEES': ETFInfo(
                "Nippon India ETF Nifty FMCG", "FMCGBEES", "Nifty FMCG",
                ETFCategory.SECTORAL, priority=3
            ),
            'ENERGYBEES': ETFInfo(
                "Nippon India ETF Nifty Energy", "ENERGYBEES", "Nifty Energy",
                ETFCategory.SECTORAL, priority=3
            ),
            'AUTOETF': ETFInfo(
                "Nippon India ETF Nifty Auto", "AUTOETF", "Nifty Auto",
                ETFCategory.SECTORAL, priority=3
            ),
            'PRBANKETF': ETFInfo(
                "Nippon India ETF Nifty Private Bank", "PRBANKETF", "Nifty Private Bank",
                ETFCategory.SECTORAL, priority=3
            ),
            'METALETF': ETFInfo(
                "Nippon India ETF Nifty Metal", "METALETF", "Nifty Metal",
                ETFCategory.SECTORAL, priority=3
            ),
            'INFRAETF': ETFInfo(
                "Nippon India ETF Nifty Infra", "INFRAETF", "Nifty Infrastructure",
                ETFCategory.SECTORAL, priority=4
            ),
            'REALTYETF': ETFInfo(
                "Nippon India ETF Nifty Realty", "REALTYETF", "Nifty Realty",
                ETFCategory.SECTORAL, priority=4
            ),
            'MEDIAETF': ETFInfo(
                "Nippon India ETF Nifty Media", "MEDIAETF", "Nifty Media",
                ETFCategory.SECTORAL, priority=4
            ),
            'COMMODETF': ETFInfo(
                "Nippon India ETF Nifty Commodities", "COMMODETF", "Nifty Commodities",
                ETFCategory.SECTORAL, priority=4
            ),
            'SERVICESETF': ETFInfo(
                "Nippon India ETF Nifty Services Sector", "SERVICESETF", "Nifty Services Sector",
                ETFCategory.SECTORAL, priority=4
            ),
            'CONSUMETF': ETFInfo(
                "Nippon India ETF Nifty Consumption", "CONSUMETF", "Nifty Consumption",
                ETFCategory.SECTORAL, priority=4
            ),
            'ICICIFINSERV': ETFInfo(
                "ICICI Prudential Nifty Financial Services ETF", "ICICIFINSERV", "Nifty Financial Services",
                ETFCategory.SECTORAL, priority=3
            ),
            'ICICIHEALTH': ETFInfo(
                "ICICI Prudential Nifty Healthcare ETF", "ICICIHEALTH", "Nifty Healthcare Index",
                ETFCategory.SECTORAL, priority=4
            ),
            
            # Thematic ETFs
            'DIVOPPBEES': ETFInfo(
                "Nippon India ETF Nifty Dividend Opportunities 50", "DIVOPPBEES", "Nifty Dividend Opportunities 50",
                ETFCategory.THEMATIC, priority=3
            ),
            'GROWTHETF': ETFInfo(
                "Nippon India ETF Nifty Growth Sectors 15", "GROWTHETF", "Nifty Growth Sectors 15",
                ETFCategory.THEMATIC, priority=4
            ),
            'MNCETF': ETFInfo(
                "Nippon India ETF Nifty MNC", "MNCETF", "Nifty MNC",
                ETFCategory.THEMATIC, priority=4
            ),
            'CPSEETF': ETFInfo(
                "Nippon India ETF Nifty CPSE", "CPSEETF", "Nifty CPSE",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIB22': ETFInfo(
                "ICICI Prudential Bharat 22 ETF", "ICICIB22", "Bharat 22 Index",
                ETFCategory.THEMATIC, priority=3
            ),
            'ICICIESGETF': ETFInfo(
                "ICICI Prudential ESG ETF", "ICICIESGETF", "Nifty100 ESG Index",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIDIGITAL': ETFInfo(
                "ICICI Prudential Nifty India Digital ETF", "ICICIDIGITAL", "Nifty India Digital Index",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIMANUF': ETFInfo(
                "ICICI Prudential Nifty India Manufacturing ETF", "ICICIMANUF", "Nifty India Manufacturing Index",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIHDIV': ETFInfo(
                "ICICI Prudential Nifty Dividend Opportunities 50 ETF", "ICICIHDIV", "Nifty Dividend Opportunities 50",
                ETFCategory.THEMATIC, priority=4
            ),
            
            # Factor Based ETFs
            'ALPHALVETF': ETFInfo(
                "Nippon India ETF Nifty Alpha Low-Volatility 30", "ALPHALVETF", "Nifty Alpha Low-Volatility 30",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'QUALITYETF': ETFInfo(
                "Nippon India ETF Nifty200 Quality 30", "QUALITYETF", "Nifty200 Quality 30",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'VALUEETF': ETFInfo(
                "Nippon India ETF Nifty200 Value 30", "VALUEETF", "Nifty200 Value 30",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'LOWVOLETF': ETFInfo(
                "Nippon India ETF Nifty100 Low Volatility 30", "LOWVOLETF", "Nifty100 Low Volatility 30",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'EQUALWEIGHTETF': ETFInfo(
                "Nippon India ETF Nifty100 Equal Weight", "EQUALWEIGHTETF", "Nifty100 Equal Weight",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'EDELMOM30': ETFInfo(
                "Edelweiss ETF Nifty Momentum 30", "EDELMOM30", "Nifty200 Momentum 30",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            'ALPHA50ETF': ETFInfo(
                "Edelweiss ETF Nifty Alpha 50", "ALPHA50ETF", "Nifty Alpha 50",
                ETFCategory.FACTOR_BASED, priority=4
            ),
            
            # Fixed Income ETFs
            'LIQUIDBEES': ETFInfo(
                "Nippon India ETF Nifty 1D Rate Liquid BeES", "LIQUIDBEES", "Nifty 1D Rate Index",
                ETFCategory.FIXED_INCOME, priority=2
            ),
            'GS813ETF': ETFInfo(
                "Nippon India ETF Nifty 8-13 Years G-Sec", "GS813ETF", "Nifty 8-13 Years G-Sec Index",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'GS5YEARETF': ETFInfo(
                "SBI ETF 10 Year Gilt", "GS5YEARETF", "Nifty 10 yr Benchmark G-Sec Index",
                ETFCategory.FIXED_INCOME, priority=4
            ),
            'BHARATBONDETFAPR30': ETFInfo(
                "Bharat Bond ETF April 2030", "BHARATBONDETFAPR30", "Nifty Bharat Bond Index April 2030",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'BHARATBONDETFAPR25': ETFInfo(
                "Bharat Bond ETF April 2025", "BHARATBONDETFAPR25", "Nifty Bharat Bond Index April 2025",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'EDEL1DRATEETF': ETFInfo(
                "Edelweiss ETF Nifty 1D Rate", "EDEL1DRATEETF", "Nifty 1D Rate Index", 
                ETFCategory.FIXED_INCOME, priority=4
            ),
            'SBISDL26ETF': ETFInfo(
                "SBI ETF SDL 2026", "SBISDL26ETF", "Nifty SDL Index 2026",
                ETFCategory.FIXED_INCOME, priority=4
            ),
            'ICICISDL27ETF': ETFInfo(
                "ICICI Prudential ETF SDL 2027", "ICICISDL27ETF", "Nifty SDL Index 2027",
                ETFCategory.FIXED_INCOME, priority=4
            ),
            'HDFCGSEC30ETF': ETFInfo(
                "HDFC ETF G-Sec Long Term", "HDFCGSEC30ETF", "Nifty 15 Yr and above G-Sec Index",
                ETFCategory.FIXED_INCOME, priority=4
            ),
            
            # Commodity ETFs
            'GOLDBEES': ETFInfo(
                "Nippon India ETF Gold BeES", "GOLDBEES", "Gold Price",
                ETFCategory.COMMODITY, priority=2
            ),
            'SILVERBEES': ETFInfo(
                "Nippon India ETF Silver BeES", "SILVERBEES", "Silver Price",
                ETFCategory.COMMODITY, priority=3
            ),
            
            # International ETFs
            'INDA': ETFInfo(
                "iShares MSCI India ETF", "INDA", "MSCI India Index",
                ETFCategory.INTERNATIONAL, priority=3
            ),
            'MOSP500ETF': ETFInfo(
                "Motilal Oswal S&P 500 Index Fund", "MOSP500ETF", "S&P 500 Index",
                ETFCategory.INTERNATIONAL, priority=3
            ),
            'MOEAFEETF': ETFInfo(
                "Motilal Oswal MSCI EAFE Index Fund", "MOEAFEETF", "MSCI EAFE Index",
                ETFCategory.INTERNATIONAL, priority=4
            ),
            'MOEMETF': ETFInfo(
                "Motilal Oswal MSCI Emerging Markets ETF", "MOEMETF", "MSCI Emerging Markets Index",
                ETFCategory.INTERNATIONAL, priority=4
            )
        }
        
        return etf_data
    
    def _organize_by_category(self) -> Dict[ETFCategory, List[str]]:
        """Organize ETFs by category"""
        categories = {}
        for symbol, etf_info in self.etfs.items():
            category = etf_info.category
            if category not in categories:
                categories[category] = []
            categories[category].append(symbol)
        return categories
    
    def get_etf_by_symbol(self, symbol: str) -> Optional[ETFInfo]:
        """Get ETF information by symbol"""
        return self.etfs.get(symbol.upper())
    
    def get_all_symbols(self) -> List[str]:
        """Get all ETF symbols"""
        return list(self.etfs.keys())
    
    def get_symbols_by_category(self, category: ETFCategory) -> List[str]:
        """Get ETF symbols by category"""
        return self.categories.get(category, [])
    
    def get_high_priority_etfs(self, max_priority: int = 3) -> List[str]:
        """Get high priority ETFs for active trading"""
        high_priority = []
        for symbol, etf_info in self.etfs.items():
            if etf_info.priority <= max_priority and etf_info.is_active:
                high_priority.append(symbol)
        # Sort by priority
        high_priority.sort(key=lambda s: self.etfs[s].priority)
        return high_priority
    
    def get_liquid_etfs(self, liquidity_level: str = 'HIGH') -> List[str]:
        """Get ETFs by liquidity level"""
        if liquidity_level == 'HIGH':
            return self.get_high_priority_etfs(2)  # Priority 1-2
        elif liquidity_level == 'MEDIUM':
            return self.get_high_priority_etfs(4)  # Priority 1-4
        else:
            return self.get_all_symbols()
    
    def get_sector_etfs(self) -> Dict[str, List[str]]:
        """Get ETFs organized by sector"""
        return {
            'Banking': ['BANKBEES', 'PSUBANKBEES', 'PRBANKETF', 'ICICIFINSERV'],
            'Technology': ['ITBEES', 'ICICIDIGITAL'],
            'Healthcare': ['PHARMABEES', 'ICICIHEALTH'],
            'FMCG': ['FMCGBEES'],
            'Energy': ['ENERGYBEES'],
            'Auto': ['AUTOETF'],
            'Metal': ['METALETF'],
            'Realty': ['REALTYETF'],
            'Media': ['MEDIAETF'],
            'Infrastructure': ['INFRAETF'],
            'Manufacturing': ['ICICIMANUF'],
            'Services': ['SERVICESETF'],
            'Consumption': ['CONSUMETF'],
            'Commodities': ['COMMODETF']
        }
    
    def search_etfs(self, query: str) -> List[str]:
        """Search ETFs by name or symbol"""
        results = []
        query_lower = query.lower()
        
        for symbol, etf_info in self.etfs.items():
            if (query_lower in symbol.lower() or 
                query_lower in etf_info.name.lower() or
                query_lower in etf_info.tracking_index.lower()):
                results.append(symbol)
        
        return results
    
    def export_to_json(self, filename: str = "indian_etf_database.json") -> str:
        """Export ETF database to JSON"""
        export_data = {}
        for symbol, etf_info in self.etfs.items():
            export_data[symbol] = {
                'name': etf_info.name,
                'symbol': etf_info.symbol,
                'tracking_index': etf_info.tracking_index,
                'category': etf_info.category.value,
                'nse_symbol': etf_info.nse_symbol,
                'priority': etf_info.priority,
                'is_active': etf_info.is_active,
                'min_investment': etf_info.min_investment
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"ETF database exported to {filename}")
        return filename
    
    def get_market_data_batch(self, symbols: List[str] = None) -> pd.DataFrame:
        """Get market data for multiple ETFs (placeholder for Kite API integration)"""
        if symbols is None:
            # Get high and medium liquidity ETFs for better coverage
            high_liquid = self.get_liquid_etfs('HIGH')
            medium_liquid = self.get_liquid_etfs('MEDIUM')
            symbols = high_liquid + medium_liquid
        
        market_data = []
        
        # Create placeholder data for the requested symbols
        for symbol in symbols:
            etf = self.get_etf_by_symbol(symbol)
            if etf and etf.is_active:
                market_data.append({
                    'Symbol': symbol,
                    'Name': etf.name,
                    'Category': etf.category.value,
                    'NSE_Symbol': etf.nse_symbol,
                    'Priority': etf.priority,
                    'Price': 0.0,  # To be filled by Kite API
                    'Change %': 0.0,  # To be filled by Kite API
                    'Volume': 0,  # To be filled by Kite API
                    'Status': '⚪'  # To be updated based on data availability
                })
        
        return pd.DataFrame(market_data)
    
    def print_database_summary(self):
        """Print summary of ETF database"""
        print(f"🏦 INDIAN ETF DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total ETFs: {len(self.etfs)}")
        
        for category, symbols in self.categories.items():
            print(f"{category.value}: {len(symbols)} ETFs")
            
        print(f"\n📈 High Priority ETFs for Active Trading:")
        high_liquid = self.get_liquid_etfs('HIGH')
        for symbol in high_liquid:
            if symbol in self.etfs:
                etf = self.etfs[symbol]
                print(f"  {symbol}: {etf.name} (Priority: {etf.priority})")
        
        print(f"\n📊 Medium Priority ETFs (Total: {len(self.get_liquid_etfs('MEDIUM'))}):")
        medium_liquid = self.get_liquid_etfs('MEDIUM')
        for symbol in medium_liquid[:10]:  # Show first 10
            if symbol in self.etfs:
                etf = self.etfs[symbol]
                print(f"  {symbol}: {etf.name} (Priority: {etf.priority})")
        if len(medium_liquid) > 10:
            print(f"  ... and {len(medium_liquid) - 10} more medium priority ETFs")
        
        print(f"\n🏭 Sector Distribution:")
        sectors = self.get_sector_etfs()
        for sector, symbols in sectors.items():
            print(f"  {sector}: {len(symbols)} ETFs")

# Create global instance
etf_db = IndianETFDatabase()

if __name__ == "__main__":
    print("🏦 INDIAN ETF DATABASE")
    print("=" * 40)
    
    # Print summary
    etf_db.print_database_summary()
    
    print(f"\n📊 Sample Market Data Structure:")
    market_df = etf_db.get_market_data_batch(etf_db.get_liquid_etfs('HIGH')[:5])
    if not market_df.empty:
        print(market_df.to_string(index=False))
    
    # Export database
    etf_db.export_to_json()
    
    print(f"\n✅ Database ready with {len(etf_db.etfs)} ETFs across {len(etf_db.categories)} categories")
    print(f"📋 All symbols: {', '.join(etf_db.get_all_symbols())}")