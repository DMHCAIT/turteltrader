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
            # Broad Market ETFs
            'NIFTYBEES': ETFInfo(
                "Nippon India ETF Nifty 50 BeES", "NIFTYBEES", "Nifty 50",
                ETFCategory.BROAD_MARKET, priority=1
            ),
            'UTISENSETF': ETFInfo(
                "UTI S&P BSE Sensex ETF", "UTISENSETF", "S&P BSE Sensex",
                ETFCategory.BROAD_MARKET, priority=2
            ),
            'INDA': ETFInfo(
                "iShares MSCI India ETF", "INDA", "MSCI India Index",
                ETFCategory.INTERNATIONAL, priority=3
            ),
            'MOM150ETF': ETFInfo(
                "Motilal Oswal Nifty Midcap 150 ETF", "MOM150ETF", "Nifty Midcap 150",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'MOM250ETF': ETFInfo(
                "Motilal Oswal Nifty Smallcap 250 ETF", "MOM250ETF", "Nifty Smallcap 250",
                ETFCategory.BROAD_MARKET, priority=4
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
            'MOMMICROETF': ETFInfo(
                "Motilal Oswal Nifty Microcap 250 ETF", "MOMMICROETF", "Nifty Microcap 250",
                ETFCategory.BROAD_MARKET, priority=5
            ),
            
            # Sectoral ETFs
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
            'INFRAETF': ETFInfo(
                "Nippon India ETF Nifty Infra", "INFRAETF", "Nifty Infrastructure",
                ETFCategory.SECTORAL, priority=4
            ),
            'AUTOETF': ETFInfo(
                "Nippon India ETF Nifty Auto", "AUTOETF", "Nifty Auto",
                ETFCategory.SECTORAL, priority=3
            ),
            'REALTYETF': ETFInfo(
                "Nippon India ETF Nifty Realty", "REALTYETF", "Nifty Realty",
                ETFCategory.SECTORAL, priority=4
            ),
            'MEDIAETF': ETFInfo(
                "Nippon India ETF Nifty Media", "MEDIAETF", "Nifty Media",
                ETFCategory.SECTORAL, priority=4
            ),
            'PRBANKETF': ETFInfo(
                "Nippon India ETF Nifty Private Bank", "PRBANKETF", "Nifty Private Bank",
                ETFCategory.SECTORAL, priority=3
            ),
            'METALETF': ETFInfo(
                "Nippon India ETF Nifty Metal", "METALETF", "Nifty Metal",
                ETFCategory.SECTORAL, priority=3
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
            
            # Thematic & Strategy ETFs
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
            
            # Fixed Income ETFs
            'GS813ETF': ETFInfo(
                "Bharat Bond ETF April 2030", "GS813ETF", "Nifty 8-13 yr G-Sec Index",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'GS5YEARETF': ETFInfo(
                "SBI ETF 10 Year Gilt", "GS5YEARETF", "Nifty 10 yr Benchmark G-Sec Index",
                ETFCategory.FIXED_INCOME, priority=4
            ),
            'CPSEETF': ETFInfo(
                "Nippon India ETF Nifty CPSE", "CPSEETF", "Nifty CPSE",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIB22': ETFInfo(
                "ICICI Prudential Bharat 22 ETF", "ICICIB22", "Bharat 22 Index",
                ETFCategory.THEMATIC, priority=3
            ),
            
            # International & Motilal Oswal ETFs
            'MON100ETF': ETFInfo(
                "Motilal Oswal Nifty 100 ETF", "MON100ETF", "Nifty 100",
                ETFCategory.BROAD_MARKET, priority=3
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
            
            # Bond ETFs
            'BHARATBONDETFAPR30': ETFInfo(
                "Bharat Bond ETF April 2030", "BHARATBONDETFAPR30", "Nifty Bharat Bond Index April 2030",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'BHARATBONDETFAPR25': ETFInfo(
                "Bharat Bond ETF April 2025", "BHARATBONDETFAPR25", "Nifty Bharat Bond Index April 2025",
                ETFCategory.FIXED_INCOME, priority=3
            ),
            'LIQUIDBEES': ETFInfo(
                "Nippon India ETF Nifty 1D Rate Liquid BeES", "LIQUIDBEES", "Nifty 1D Rate Index",
                ETFCategory.FIXED_INCOME, priority=2
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
            'SILVERBEES': ETFInfo(
                "Nippon India ETF Silver BeES", "SILVERBEES", "Silver Price",
                ETFCategory.COMMODITY, priority=3
            ),
            'GOLDBEES': ETFInfo(
                "Nippon India ETF Gold BeES", "GOLDBEES", "Gold Price",
                ETFCategory.COMMODITY, priority=2
            ),
            
            # ICICI Prudential ETFs
            'ICICINXT50': ETFInfo(
                "ICICI Prudential Nifty Next 50 ETF", "ICICINXT50", "Nifty Next 50",
                ETFCategory.BROAD_MARKET, priority=3
            ),
            'ICICIESGETF': ETFInfo(
                "ICICI Prudential ESG ETF", "ICICIESGETF", "Nifty100 ESG Index",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIMID50': ETFInfo(
                "ICICI Prudential Nifty Midcap 150 ETF", "ICICIMID50", "Nifty Midcap 150",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'ICICISMALL100': ETFInfo(
                "ICICI Prudential Nifty Smallcap 250 ETF", "ICICISMALL100", "Nifty Smallcap 250",
                ETFCategory.BROAD_MARKET, priority=4
            ),
            'ICICIHDIV': ETFInfo(
                "ICICI Prudential Nifty Dividend Opportunities 50 ETF", "ICICIHDIV", "Nifty Dividend Opportunities 50",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIFINSERV': ETFInfo(
                "ICICI Prudential Nifty Financial Services ETF", "ICICIFINSERV", "Nifty Financial Services",
                ETFCategory.SECTORAL, priority=3
            ),
            'ICICIHEALTH': ETFInfo(
                "ICICI Prudential Nifty Healthcare ETF", "ICICIHEALTH", "Nifty Healthcare Index",
                ETFCategory.SECTORAL, priority=4
            ),
            'ICICIDIGITAL': ETFInfo(
                "ICICI Prudential Nifty India Digital ETF", "ICICIDIGITAL", "Nifty India Digital Index",
                ETFCategory.THEMATIC, priority=4
            ),
            'ICICIMANUF': ETFInfo(
                "ICICI Prudential Nifty India Manufacturing ETF", "ICICIMANUF", "Nifty India Manufacturing Index",
                ETFCategory.THEMATIC, priority=4
            ),
            
            # Edelweiss ETFs
                        # Edelweiss ETFs
            'EDELMOM30': ETFInfo(
                "Edelweiss ETF Nifty Momentum 30", "EDELMOM30", "Nifty200 Momentum 30",
                ETFCategory.FACTOR_BASED, priority=4
            )
            
        }
        
        return etf_data
            
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
    
    def get_liquid_etfs(self, liquidity_level: str = 'HIGH_MEDIUM') -> List[str]:
        """Get ETFs filtered by liquidity level for active trading
        
        Args:
            liquidity_level: 'HIGH', 'MEDIUM', 'LOW', 'HIGH_MEDIUM', or 'ALL' 
        """
        # Import our comprehensive universe
        try:
            from etf_universe_config import ETF_UNIVERSE
            
            if liquidity_level == 'ALL':
                # Return all ETFs from our universe that exist in database
                return [symbol for symbol in ETF_UNIVERSE.keys() if symbol in self.etfs]
            elif liquidity_level == 'HIGH_MEDIUM':
                # Default: Return high and medium liquidity ETFs (best for trading)
                high_etfs = [
                    symbol for symbol, config in ETF_UNIVERSE.items() 
                    if config.get('liquidity') == 'HIGH' and symbol in self.etfs
                ]
                medium_etfs = [
                    symbol for symbol, config in ETF_UNIVERSE.items() 
                    if config.get('liquidity') == 'MEDIUM' and symbol in self.etfs
                ]
                return high_etfs + medium_etfs
            else:
                # Filter by specific liquidity level
                filtered_etfs = [
                    symbol for symbol, config in ETF_UNIVERSE.items() 
                    if config.get('liquidity') == liquidity_level and symbol in self.etfs
                ]
                return filtered_etfs
                
        except ImportError:
            # Fallback to original hardcoded list if config not available
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
            # Get high and medium liquidity ETFs for better coverage
            high_liquid = self.get_liquid_etfs('HIGH')
            medium_liquid = self.get_liquid_etfs('MEDIUM')
            symbols = high_liquid + medium_liquid
        
        yahoo_symbols = []
        etf_names = []
        categories = []
        
        for symbol in symbols:
            etf = self.get_etf_by_symbol(symbol)
            if etf and etf.is_active:
                yahoo_symbols.append(etf.yahoo_symbol)
                etf_names.append(etf.name)
                categories.append(etf.category.value)
        
        # Return empty DataFrame - market data should be fetched via Kite API
        market_data = []
        
        # Create placeholder data for the requested symbols
        for i, symbol in enumerate(symbols):
            market_data.append({
                'Symbol': symbol,
                'Name': etf_names[i] if i < len(etf_names) else symbol,
                'Category': categories[i] if i < len(categories) else 'Unknown',
                'Price': 0.0,
                'Change %': 0.0,
                'Volume': 0,
                'Status': '⚪'
            })
        
        return pd.DataFrame(market_data)
    
    def print_database_summary(self):
        """Print summary of ETF database"""
        print(f"🏦 INDIAN ETF DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total ETFs: {len(self.etfs)}")
        
        for category, symbols in self.categories.items():
            print(f"{category.value}: {len(symbols)} ETFs")
            
        print(f"\nHigh Liquidity ETFs for Active Trading:")
        high_liquid = self.get_liquid_etfs('HIGH')
        for symbol in high_liquid:
            if symbol in self.etfs:
                etf = self.etfs[symbol]
                print(f"  {symbol}: {etf.name}")
        
        print(f"\nMedium Liquidity ETFs (Total: {len(self.get_liquid_etfs('MEDIUM'))}):")
        medium_liquid = self.get_liquid_etfs('MEDIUM')
        for symbol in medium_liquid[:15]:  # Show first 15 medium liquidity ETFs
            if symbol in self.etfs:
                etf = self.etfs[symbol]
                print(f"  {symbol}: {etf.name}")
        if len(medium_liquid) > 15:
            print(f"  ... and {len(medium_liquid) - 15} more medium liquidity ETFs")
        
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