"""
📊 COMPREHENSIVE INDIAN ETF DATABASE
===================================

Complete list of Indian ETFs for the trading system with sector classification
and market data integration capabilities.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import yfinance as yf
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
    yahoo_symbol: str  # Symbol with .NS suffix for Yahoo Finance
    is_active: bool = True
    min_investment: float = 1000.0  # Minimum investment amount

class IndianETFDatabase:
    """Comprehensive database of Indian ETFs"""
    
    def __init__(self):
        """Initialize the ETF database"""
        self.etfs = self._load_etf_data()
        self.categories = self._organize_by_category()
    
    def _load_etf_data(self) -> Dict[str, ETFInfo]:
        """Load complete ETF data"""
        etf_data = {
            # Broad Market ETFs
            'NIFTYBEES': ETFInfo(
                "Nippon India ETF Nifty 50 BeES", "NIFTYBEES", "Nifty 50",
                ETFCategory.BROAD_MARKET, "NIFTYBEES.NS"
            ),
            'UTISENSETF': ETFInfo(
                "UTI S&P BSE Sensex ETF", "UTISENSETF", "S&P BSE Sensex",
                ETFCategory.BROAD_MARKET, "UTISENSETF.NS"
            ),
            'MOM150ETF': ETFInfo(
                "Motilal Oswal Nifty Midcap 150 ETF", "MOM150ETF", "Nifty Midcap 150",
                ETFCategory.BROAD_MARKET, "MOM150ETF.NS"
            ),
            'MOM250ETF': ETFInfo(
                "Motilal Oswal Nifty Smallcap 250 ETF", "MOM250ETF", "Nifty Smallcap 250",
                ETFCategory.BROAD_MARKET, "MOM250ETF.NS"
            ),
            'ICICINXT50': ETFInfo(
                "ICICI Prudential Nifty Next 50 ETF", "ICICINXT50", "Nifty Next 50",
                ETFCategory.BROAD_MARKET, "ICICINXT50.NS"
            ),
            'SETFNIF100': ETFInfo(
                "SBI ETF Nifty 100", "SETFNIF100", "Nifty 100",
                ETFCategory.BROAD_MARKET, "SETFNIF100.NS"
            ),
            'KOTAKNIFTY200': ETFInfo(
                "Kotak Nifty 200 ETF", "KOTAKNIFTY200", "Nifty 200",
                ETFCategory.BROAD_MARKET, "KOTAKNIFTY200.NS"
            ),
            'ABSLNIFTY500ETF': ETFInfo(
                "Aditya Birla Sun Life Nifty 500 ETF", "ABSLNIFTY500ETF", "Nifty 500",
                ETFCategory.BROAD_MARKET, "ABSLNIFTY500ETF.NS"
            ),
            'MOMMICROETF': ETFInfo(
                "Motilal Oswal Nifty Microcap 250 ETF", "MOMMICROETF", "Nifty Microcap 250",
                ETFCategory.BROAD_MARKET, "MOMMICROETF.NS"
            ),
            
            # Sectoral ETFs
            'BANKBEES': ETFInfo(
                "Nippon India ETF Nifty Bank BeES", "BANKBEES", "Nifty Bank",
                ETFCategory.SECTORAL, "BANKBEES.NS"
            ),
            'ITBEES': ETFInfo(
                "Nippon India ETF Nifty IT", "ITBEES", "Nifty IT",
                ETFCategory.SECTORAL, "ITBEES.NS"
            ),
            'PSUBANKBEES': ETFInfo(
                "Nippon India ETF Nifty PSU Bank", "PSUBANKBEES", "Nifty PSU Bank",
                ETFCategory.SECTORAL, "PSUBANKBEES.NS"
            ),
            'PHARMABEES': ETFInfo(
                "Nippon India ETF Nifty Pharma", "PHARMABEES", "Nifty Pharma",
                ETFCategory.SECTORAL, "PHARMABEES.NS"
            ),
            'FMCGBEES': ETFInfo(
                "Nippon India ETF Nifty FMCG", "FMCGBEES", "Nifty FMCG",
                ETFCategory.SECTORAL, "FMCGBEES.NS"
            ),
            'ENERGYBEES': ETFInfo(
                "Nippon India ETF Nifty Energy", "ENERGYBEES", "Nifty Energy",
                ETFCategory.SECTORAL, "ENERGYBEES.NS"
            ),
            'INFRAETF': ETFInfo(
                "Nippon India ETF Nifty Infra", "INFRAETF", "Nifty Infrastructure",
                ETFCategory.SECTORAL, "INFRAETF.NS"
            ),
            'AUTOETF': ETFInfo(
                "Nippon India ETF Nifty Auto", "AUTOETF", "Nifty Auto",
                ETFCategory.SECTORAL, "AUTOETF.NS"
            ),
            'REALTYETF': ETFInfo(
                "Nippon India ETF Nifty Realty", "REALTYETF", "Nifty Realty",
                ETFCategory.SECTORAL, "REALTYETF.NS"
            ),
            'MEDIAETF': ETFInfo(
                "Nippon India ETF Nifty Media", "MEDIAETF", "Nifty Media",
                ETFCategory.SECTORAL, "MEDIAETF.NS"
            ),
            'PRBANKETF': ETFInfo(
                "Nippon India ETF Nifty Private Bank", "PRBANKETF", "Nifty Private Bank",
                ETFCategory.SECTORAL, "PRBANKETF.NS"
            ),
            'METALETF': ETFInfo(
                "Nippon India ETF Nifty Metal", "METALETF", "Nifty Metal",
                ETFCategory.SECTORAL, "METALETF.NS"
            ),
            'COMMODETF': ETFInfo(
                "Nippon India ETF Nifty Commodities", "COMMODETF", "Nifty Commodities",
                ETFCategory.SECTORAL, "COMMODETF.NS"
            ),
            'SERVICESETF': ETFInfo(
                "Nippon India ETF Nifty Services Sector", "SERVICESETF", "Nifty Services Sector",
                ETFCategory.SECTORAL, "SERVICESETF.NS"
            ),
            'CONSUMETF': ETFInfo(
                "Nippon India ETF Nifty Consumption", "CONSUMETF", "Nifty Consumption",
                ETFCategory.SECTORAL, "CONSUMETF.NS"
            ),
            'ICICIFINSERV': ETFInfo(
                "ICICI Prudential Nifty Financial Services ETF", "ICICIFINSERV", "Nifty Financial Services",
                ETFCategory.SECTORAL, "ICICIFINSERV.NS"
            ),
            'ICICIHEALTH': ETFInfo(
                "ICICI Prudential Nifty Healthcare ETF", "ICICIHEALTH", "Nifty Healthcare",
                ETFCategory.SECTORAL, "ICICIHEALTH.NS"
            ),
            
            # Thematic ETFs
            'DIVOPPBEES': ETFInfo(
                "Nippon India ETF Nifty Dividend Opportunities 50", "DIVOPPBEES", "Nifty Dividend Opportunities 50",
                ETFCategory.THEMATIC, "DIVOPPBEES.NS"
            ),
            'GROWTHETF': ETFInfo(
                "Nippon India ETF Nifty Growth Sectors 15", "GROWTHETF", "Nifty Growth Sectors 15",
                ETFCategory.THEMATIC, "GROWTHETF.NS"
            ),
            'MNCETF': ETFInfo(
                "Nippon India ETF Nifty MNC", "MNCETF", "Nifty MNC",
                ETFCategory.THEMATIC, "MNCETF.NS"
            ),
            'CPSEETF': ETFInfo(
                "Nippon India ETF CPSE", "CPSEETF", "Nifty CPSE Index",
                ETFCategory.THEMATIC, "CPSEETF.NS"
            ),
            'ICICIB22': ETFInfo(
                "ICICI Prudential Bharat 22 ETF", "ICICIB22", "S&P BSE Bharat 22 Index",
                ETFCategory.THEMATIC, "ICICIB22.NS"
            ),
            'ICICIESGETF': ETFInfo(
                "ICICI Prudential ESG ETF", "ICICIESGETF", "Nifty 100 ESG Sector Leaders",
                ETFCategory.THEMATIC, "ICICIESGETF.NS"
            ),
            'ICICIDIGITAL': ETFInfo(
                "ICICI Prudential Nifty India Digital ETF", "ICICIDIGITAL", "Nifty India Digital",
                ETFCategory.THEMATIC, "ICICIDIGITAL.NS"
            ),
            'ICICIMANUF': ETFInfo(
                "ICICI Prudential Nifty India Manufacturing ETF", "ICICIMANUF", "Nifty India Manufacturing",
                ETFCategory.THEMATIC, "ICICIMANUF.NS"
            ),
            
            # Factor Based ETFs
            'ALPHALVETF': ETFInfo(
                "Nippon India ETF Nifty Alpha Low Volatility 30", "ALPHALVETF", "Nifty Alpha Low Volatility 30",
                ETFCategory.FACTOR_BASED, "ALPHALVETF.NS"
            ),
            'QUALITYETF': ETFInfo(
                "Nippon India ETF Nifty Quality 30", "QUALITYETF", "Nifty Quality 30",
                ETFCategory.FACTOR_BASED, "QUALITYETF.NS"
            ),
            'VALUEETF': ETFInfo(
                "Nippon India ETF Nifty Value 20", "VALUEETF", "Nifty Value 20",
                ETFCategory.FACTOR_BASED, "VALUEETF.NS"
            ),
            'LOWVOLETF': ETFInfo(
                "Nippon India ETF Nifty Low Volatility 50", "LOWVOLETF", "Nifty Low Volatility 50",
                ETFCategory.FACTOR_BASED, "LOWVOLETF.NS"
            ),
            'EQUALWEIGHTETF': ETFInfo(
                "Nippon India ETF Nifty Equal Weight", "EQUALWEIGHTETF", "Nifty Equal Weight",
                ETFCategory.FACTOR_BASED, "EQUALWEIGHTETF.NS"
            ),
            'ALPHA50ETF': ETFInfo(
                "Nippon India ETF Nifty Alpha 50", "ALPHA50ETF", "Nifty Alpha 50",
                ETFCategory.FACTOR_BASED, "ALPHA50ETF.NS"
            ),
            'EDELMOM30': ETFInfo(
                "Edelweiss Nifty Momentum 30 ETF", "EDELMOM30", "Nifty Momentum 30",
                ETFCategory.FACTOR_BASED, "EDELMOM30.NS"
            ),
            'ICICIHDIV': ETFInfo(
                "ICICI Prudential Nifty High Dividend Yield 50 ETF", "ICICIHDIV", "Nifty High Dividend Yield 50",
                ETFCategory.FACTOR_BASED, "ICICIHDIV.NS"
            ),
            
            # Fixed Income ETFs
            'GS813ETF': ETFInfo(
                "Nippon India ETF Nifty 8-13 Years G-Sec", "GS813ETF", "Nifty 8-13 Years G-Sec",
                ETFCategory.FIXED_INCOME, "GS813ETF.NS"
            ),
            'GS5YEARETF': ETFInfo(
                "Nippon India ETF Nifty 5 Year Benchmark G-Sec", "GS5YEARETF", "Nifty 5 Year Benchmark G-Sec",
                ETFCategory.FIXED_INCOME, "GS5YEARETF.NS"
            ),
            'BHARATBONDETFAPR30': ETFInfo(
                "Bharat Bond ETF April 2030", "BHARATBONDETFAPR30", "PSU bonds maturing April 2030",
                ETFCategory.FIXED_INCOME, "BHARATBONDETFAPR30.NS"
            ),
            'BHARATBONDETFAPR25': ETFInfo(
                "Bharat Bond ETF April 2025", "BHARATBONDETFAPR25", "PSU bonds maturing April 2025",
                ETFCategory.FIXED_INCOME, "BHARATBONDETFAPR25.NS"
            ),
            'LIQUIDBEES': ETFInfo(
                "Nippon India ETF Liquid BeES", "LIQUIDBEES", "Overnight money market instruments",
                ETFCategory.FIXED_INCOME, "LIQUIDBEES.NS"
            ),
            'EDEL1DRATEETF': ETFInfo(
                "Edelweiss ETF Nifty 1D Rate", "EDEL1DRATEETF", "Nifty 1D Rate Index",
                ETFCategory.FIXED_INCOME, "EDEL1DRATEETF.NS"
            ),
            'SBISDL26ETF': ETFInfo(
                "SBI ETF Nifty SDL April 2026", "SBISDL26ETF", "State Development Loans maturing April 2026",
                ETFCategory.FIXED_INCOME, "SBISDL26ETF.NS"
            ),
            'ICICISDL27ETF': ETFInfo(
                "ICICI Prudential Nifty SDL Dec 2027 ETF", "ICICISDL27ETF", "SDLs maturing Dec 2027",
                ETFCategory.FIXED_INCOME, "ICICISDL27ETF.NS"
            ),
            'HDFCGSEC30ETF': ETFInfo(
                "HDFC Nifty G-Sec Dec 2030 Index ETF", "HDFCGSEC30ETF", "G-Secs maturing Dec 2030",
                ETFCategory.FIXED_INCOME, "HDFCGSEC30ETF.NS"
            ),
            
            # Commodity ETFs
            'GOLDBEES': ETFInfo(
                "Nippon India ETF Gold BeES", "GOLDBEES", "Physical Gold",
                ETFCategory.COMMODITY, "GOLDBEES.NS"
            ),
            'SILVERBEES': ETFInfo(
                "Nippon India ETF Silver BeES", "SILVERBEES", "Physical Silver",
                ETFCategory.COMMODITY, "SILVERBEES.NS"
            ),
            
            # International ETFs
            'MON100ETF': ETFInfo(
                "Motilal Oswal Nasdaq 100 ETF", "MON100ETF", "Nasdaq 100",
                ETFCategory.INTERNATIONAL, "MON100ETF.NS"
            ),
            'MOSP500ETF': ETFInfo(
                "Motilal Oswal S&P 500 ETF", "MOSP500ETF", "S&P 500",
                ETFCategory.INTERNATIONAL, "MOSP500ETF.NS"
            ),
            'MOEAFEETF': ETFInfo(
                "Motilal Oswal MSCI EAFE Top 100 ETF", "MOEAFEETF", "MSCI EAFE",
                ETFCategory.INTERNATIONAL, "MOEAFEETF.NS"
            ),
            'MOEMETF': ETFInfo(
                "Motilal Oswal MSCI Emerging Markets ETF", "MOEMETF", "MSCI Emerging Markets",
                ETFCategory.INTERNATIONAL, "MOEMETF.NS"
            ),
            
            # Additional Mid/Small Cap ETFs
            'ICICIMID50': ETFInfo(
                "ICICI Prudential Nifty Midcap 50 ETF", "ICICIMID50", "Nifty Midcap 50",
                ETFCategory.BROAD_MARKET, "ICICIMID50.NS"
            ),
            'ICICISMALL100': ETFInfo(
                "ICICI Prudential Nifty Smallcap 100 ETF", "ICICISMALL100", "Nifty Smallcap 100",
                ETFCategory.BROAD_MARKET, "ICICISMALL100.NS"
            )
        }
        
        return etf_data
    
    def _organize_by_category(self) -> Dict[ETFCategory, List[str]]:
        """Organize ETFs by category"""
        categories = {}
        for symbol, etf in self.etfs.items():
            if etf.category not in categories:
                categories[etf.category] = []
            categories[etf.category].append(symbol)
        return categories
    
    def get_etf_by_symbol(self, symbol: str) -> Optional[ETFInfo]:
        """Get ETF information by symbol"""
        return self.etfs.get(symbol.upper())
    
    def get_etfs_by_category(self, category: ETFCategory) -> List[ETFInfo]:
        """Get all ETFs in a specific category"""
        symbols = self.categories.get(category, [])
        return [self.etfs[symbol] for symbol in symbols]
    
    def get_all_yahoo_symbols(self) -> List[str]:
        """Get all Yahoo Finance symbols for data fetching"""
        return [etf.yahoo_symbol for etf in self.etfs.values() if etf.is_active]
    
    def get_liquid_etfs(self) -> List[str]:
        """Get most liquid ETFs for active trading"""
        liquid_etfs = [
            'NIFTYBEES', 'BANKBEES', 'ITBEES', 'GOLDBEES', 'LIQUIDBEES',
            'UTISENSETF', 'PHARMABEES', 'FMCGBEES', 'SETFNIF100', 'ICICINXT50'
        ]
        return [symbol for symbol in liquid_etfs if symbol in self.etfs]
    
    def get_sector_etfs(self) -> Dict[str, List[str]]:
        """Get ETFs organized by sectors"""
        sectors = {
            'Banking & Finance': ['BANKBEES', 'PSUBANKBEES', 'PRBANKETF', 'ICICIFINSERV'],
            'Technology': ['ITBEES', 'ICICIDIGITAL'],
            'Healthcare & Pharma': ['PHARMABEES', 'ICICIHEALTH'],
            'Consumer': ['FMCGBEES', 'CONSUMETF'],
            'Infrastructure': ['ENERGYBEES', 'INFRAETF', 'AUTOETF', 'REALTYETF'],
            'Commodities': ['GOLDBEES', 'SILVERBEES', 'METALETF', 'COMMODETF'],
            'Broad Market': ['NIFTYBEES', 'UTISENSETF', 'SETFNIF100', 'KOTAKNIFTY200']
        }
        
        # Filter out non-existent symbols
        return {
            sector: [symbol for symbol in symbols if symbol in self.etfs]
            for sector, symbols in sectors.items()
        }
    
    def export_to_json(self, filename: str = "etf_database.json"):
        """Export ETF database to JSON"""
        export_data = {}
        for symbol, etf in self.etfs.items():
            export_data[symbol] = {
                'name': etf.name,
                'symbol': etf.symbol,
                'tracking_index': etf.tracking_index,
                'category': etf.category.value,
                'yahoo_symbol': etf.yahoo_symbol,
                'is_active': etf.is_active,
                'min_investment': etf.min_investment
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"ETF database exported to {filename}")
        return filename
    
    def get_market_data_batch(self, symbols: List[str] = None) -> pd.DataFrame:
        """Get market data for multiple ETFs"""
        if symbols is None:
            symbols = self.get_liquid_etfs()[:10]  # Top 10 liquid ETFs
        
        yahoo_symbols = []
        etf_names = []
        categories = []
        
        for symbol in symbols:
            etf = self.get_etf_by_symbol(symbol)
            if etf and etf.is_active:
                yahoo_symbols.append(etf.yahoo_symbol)
                etf_names.append(etf.name)
                categories.append(etf.category.value)
        
        # Fetch market data
        market_data = []
        
        for i, yahoo_symbol in enumerate(yahoo_symbols):
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.history(period='1d', interval='5m')
                
                if not info.empty:
                    current_price = float(info['Close'].iloc[-1])
                    prev_price = float(info['Close'].iloc[-2]) if len(info) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    volume = float(info['Volume'].iloc[-1]) if not pd.isna(info['Volume'].iloc[-1]) else 0
                    
                    market_data.append({
                        'Symbol': symbols[i],
                        'Name': etf_names[i],
                        'Category': categories[i],
                        'Price': current_price,
                        'Change %': change_pct,
                        'Volume': volume,
                        'Status': '🟢' if change_pct >= 0 else '🔴'
                    })
            
            except Exception as e:
                print(f"Error fetching data for {yahoo_symbol}: {e}")
                continue
        
        return pd.DataFrame(market_data)
    
    def print_database_summary(self):
        """Print summary of ETF database"""
        print(f"🏦 INDIAN ETF DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total ETFs: {len(self.etfs)}")
        
        for category, symbols in self.categories.items():
            print(f"{category.value}: {len(symbols)} ETFs")
            
        print(f"\nTop Liquid ETFs for Trading:")
        for symbol in self.get_liquid_etfs()[:10]:
            etf = self.etfs[symbol]
            print(f"  {symbol}: {etf.name}")
        
        print(f"\nSector Distribution:")
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
    
    print(f"\n📊 Sample Market Data:")
    market_df = etf_db.get_market_data_batch()
    if not market_df.empty:
        print(market_df.to_string(index=False))
    
    # Export database
    etf_db.export_to_json()
    
    print(f"\n✅ Database ready with {len(etf_db.etfs)} ETFs across {len(etf_db.categories)} categories")