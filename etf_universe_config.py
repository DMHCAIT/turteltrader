"""
🏛️ COMPREHENSIVE ETF UNIVERSE CONFIGURATION
=========================================

Complete list of 65 ETFs available in Indian market, organized by categories
for optimal monitoring and trading strategy implementation.
"""

from typing import Dict, List, Tuple
from enum import Enum


class ETFCategory(Enum):
    """ETF categories for strategic allocation"""
    MAJOR_INDEX = "Major Index"
    SECTORAL = "Sectoral"
    STRATEGY_FACTOR = "Strategy & Factor"
    GOVT_BONDS = "Government Securities & Bonds"
    INTERNATIONAL = "International"
    COMMODITY = "Commodity"
    SPECIALTY = "Specialty"


class ETFRiskLevel(Enum):
    """Risk levels for position sizing"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


# Complete ETF Universe with metadata
ETF_UNIVERSE: Dict[str, Dict] = {
    
    # MAJOR INDEX ETFs - Core Indian market exposure
    'NIFTYBEES': {
        'name': 'Nippon India ETF Nifty 50 BeES',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty 50',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'HIGH',
        'priority': 1,  # Highest priority
        'allocation_weight': 1.0
    },
    'UTISENSETF': {
        'name': 'UTI S&P BSE Sensex ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'S&P BSE Sensex',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'HIGH',
        'priority': 1,
        'allocation_weight': 1.0
    },
    'INDA': {
        'name': 'iShares MSCI India ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'MSCI India Index',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'HIGH',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'ICICINXT50': {
        'name': 'ICICI Prudential Nifty Next 50 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Next 50',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'SETFNIF100': {
        'name': 'SBI ETF Nifty 100',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty 100',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'MEDIUM',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'KOTAKNIFTY200': {
        'name': 'Kotak Nifty 200 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty 200',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ABSLNIFTY500ETF': {
        'name': 'Aditya Birla Sun Life Nifty 500 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty 500',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'MOM150ETF': {
        'name': 'Motilal Oswal Nifty Midcap 150 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Midcap 150',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'MOM250ETF': {
        'name': 'Motilal Oswal Nifty Smallcap 250 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Smallcap 250',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'MOMMICROETF': {
        'name': 'Motilal Oswal Nifty Microcap 250 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Microcap 250',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    
    # SECTORAL ETFs - Sector-specific exposure
    'BANKBEES': {
        'name': 'Nippon India ETF Nifty Bank BeES',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Bank',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'HIGH',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'ITBEES': {
        'name': 'Nippon India ETF Nifty IT',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty IT',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'HIGH',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'PSUBANKBEES': {
        'name': 'Nippon India ETF Nifty PSU Bank',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty PSU Bank',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'PHARMABEES': {
        'name': 'Nippon India ETF Nifty Pharma',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Pharma',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'FMCGBEES': {
        'name': 'Nippon India ETF Nifty FMCG',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty FMCG',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ENERGYBEES': {
        'name': 'Nippon India ETF Nifty Energy',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Energy',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'INFRAETF': {
        'name': 'Nippon India ETF Nifty Infra',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Infrastructure',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'AUTOETF': {
        'name': 'Nippon India ETF Nifty Auto',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Auto',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'REALTYETF': {
        'name': 'Nippon India ETF Nifty Realty',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Realty',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'MEDIAETF': {
        'name': 'Nippon India ETF Nifty Media',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Media',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'PRBANKETF': {
        'name': 'Nippon India ETF Nifty Private Bank',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Private Bank',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'METALETF': {
        'name': 'Nippon India ETF Nifty Metal',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Metal',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'COMMODETF': {
        'name': 'Nippon India ETF Nifty Commodities',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Commodities',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'SERVICESETF': {
        'name': 'Nippon India ETF Nifty Services Sector',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Services Sector',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'CONSUMETF': {
        'name': 'Nippon India ETF Nifty Consumption',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Consumption',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    
    # STRATEGY & FACTOR ETFs - Smart beta strategies
    'DIVOPPBEES': {
        'name': 'Nippon India ETF Nifty Dividend Opportunities 50',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Dividend Opportunities 50',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'GROWTHETF': {
        'name': 'Nippon India ETF Nifty Growth Sectors 15',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Growth Sectors 15',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'MNCETF': {
        'name': 'Nippon India ETF Nifty MNC',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty MNC',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'QUALITYETF': {
        'name': 'Nippon India ETF Nifty Quality 30',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Quality 30',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'VALUEETF': {
        'name': 'Nippon India ETF Nifty Value 20',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Value 20',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'LOWVOLETF': {
        'name': 'Nippon India ETF Nifty Low Volatility 50',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Low Volatility 50',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'MEDIUM',
        'priority': 2,
        'allocation_weight': 0.8
    },
    'EQUALWEIGHTETF': {
        'name': 'Nippon India ETF Nifty Equal Weight',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Equal Weight',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'ALPHALVETF': {
        'name': 'Nippon India ETF Nifty Alpha Low Volatility 30',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Alpha Low Volatility 30',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'ALPHA50ETF': {
        'name': 'Nippon India ETF Nifty Alpha 50',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Alpha 50',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'EDELMOM30': {
        'name': 'Edelweiss Nifty Momentum 30 ETF',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty Momentum 30',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    
    # GOVERNMENT SECURITIES & BONDS - Fixed income
    'GS813ETF': {
        'name': 'Nippon India ETF Nifty 8-13 Years G-Sec',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'Nifty 8-13 Years G-Sec',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'GS5YEARETF': {
        'name': 'Nippon India ETF Nifty 5 Year Benchmark G-Sec',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'Nifty 5 Year Benchmark G-Sec',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'BHARATBONDETFAPR30': {
        'name': 'Bharat Bond ETF April 2030',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'PSU bonds maturing April 2030',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'BHARATBONDETFAPR25': {
        'name': 'Bharat Bond ETF April 2025',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'PSU bonds maturing April 2025',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'LIQUIDBEES': {
        'name': 'Nippon India ETF Liquid BeES',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'Overnight money market instruments',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'HIGH',
        'priority': 1,
        'allocation_weight': 1.0
    },
    'EDEL1DRATEETF': {
        'name': 'Edelweiss ETF Nifty 1D Rate',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'Nifty 1D Rate Index',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'SBISDL26ETF': {
        'name': 'SBI ETF Nifty SDL April 2026',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'State Development Loans maturing April 2026',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'ICICISDL27ETF': {
        'name': 'ICICI Prudential Nifty SDL Dec 2027 ETF',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'SDLs maturing Dec 2027',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    'HDFCGSEC30ETF': {
        'name': 'HDFC Nifty G-Sec Dec 2030 Index ETF',
        'category': ETFCategory.GOVT_BONDS,
        'tracking': 'G-Secs maturing Dec 2030',
        'risk_level': ETFRiskLevel.LOW,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    
    # INTERNATIONAL ETFs - Global exposure
    'ICICIB22': {
        'name': 'ICICI Prudential Bharat 22 ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'S&P BSE Bharat 22 Index',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'MON100ETF': {
        'name': 'Motilal Oswal Nasdaq 100 ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'Nasdaq 100',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'MOSP500ETF': {
        'name': 'Motilal Oswal S&P 500 ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'S&P 500',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'MOEAFEETF': {
        'name': 'Motilal Oswal MSCI EAFE Top 100 ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'MSCI EAFE',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'MOEMETF': {
        'name': 'Motilal Oswal MSCI Emerging Markets ETF',
        'category': ETFCategory.INTERNATIONAL,
        'tracking': 'MSCI Emerging Markets',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'LOW',
        'priority': 5,
        'allocation_weight': 0.2
    },
    
    # COMMODITY ETFs - Physical commodities
    'SILVERBEES': {
        'name': 'Nippon India ETF Silver BeES',
        'category': ETFCategory.COMMODITY,
        'tracking': 'Physical Silver',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'GOLDBEES': {
        'name': 'Nippon India ETF Gold BeES',
        'category': ETFCategory.COMMODITY,
        'tracking': 'Physical Gold',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'HIGH',
        'priority': 2,
        'allocation_weight': 0.8
    },
    
    # SPECIALTY ETFs - Thematic and ESG
    'ICICIESGETF': {
        'name': 'ICICI Prudential ESG ETF',
        'category': ETFCategory.SPECIALTY,
        'tracking': 'Nifty 100 ESG Sector Leaders',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'LOW',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'CPSEETF': {
        'name': 'Nippon India ETF CPSE',
        'category': ETFCategory.SPECIALTY,
        'tracking': 'Nifty CPSE Index',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    
    # ICICI SPECIALTY ETFs
    'ICICIMID50': {
        'name': 'ICICI Prudential Nifty Midcap 50 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Midcap 50',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ICICISMALL100': {
        'name': 'ICICI Prudential Nifty Smallcap 100 ETF',
        'category': ETFCategory.MAJOR_INDEX,
        'tracking': 'Nifty Smallcap 100',
        'risk_level': ETFRiskLevel.VERY_HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'ICICIHDIV': {
        'name': 'ICICI Prudential Nifty High Dividend Yield 50 ETF',
        'category': ETFCategory.STRATEGY_FACTOR,
        'tracking': 'Nifty High Dividend Yield 50',
        'risk_level': ETFRiskLevel.MEDIUM,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ICICIFINSERV': {
        'name': 'ICICI Prudential Nifty Financial Services ETF',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Financial Services',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ICICIHEALTH': {
        'name': 'ICICI Prudential Nifty Healthcare ETF',
        'category': ETFCategory.SECTORAL,
        'tracking': 'Nifty Healthcare',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 3,
        'allocation_weight': 0.6
    },
    'ICICIDIGITAL': {
        'name': 'ICICI Prudential Nifty India Digital ETF',
        'category': ETFCategory.SPECIALTY,
        'tracking': 'Nifty India Digital',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    },
    'ICICIMANUF': {
        'name': 'ICICI Prudential Nifty India Manufacturing ETF',
        'category': ETFCategory.SPECIALTY,
        'tracking': 'Nifty India Manufacturing',
        'risk_level': ETFRiskLevel.HIGH,
        'liquidity': 'MEDIUM',
        'priority': 4,
        'allocation_weight': 0.4
    }
}


def get_etf_symbols() -> List[str]:
    """Get list of all ETF symbols"""
    return list(ETF_UNIVERSE.keys())


def get_etfs_by_category(category: ETFCategory) -> List[str]:
    """Get ETF symbols by category"""
    return [symbol for symbol, data in ETF_UNIVERSE.items() 
            if data['category'] == category]


def get_etfs_by_priority(priority: int) -> List[str]:
    """Get ETF symbols by priority level (1=highest, 5=lowest)"""
    return [symbol for symbol, data in ETF_UNIVERSE.items() 
            if data['priority'] == priority]


def get_etfs_by_risk_level(risk_level: ETFRiskLevel) -> List[str]:
    """Get ETF symbols by risk level"""
    return [symbol for symbol, data in ETF_UNIVERSE.items() 
            if data['risk_level'] == risk_level]


def get_high_priority_etfs() -> List[str]:
    """Get high priority ETFs (priority 1-3) for focused monitoring"""
    return [symbol for symbol, data in ETF_UNIVERSE.items() 
            if data['priority'] <= 3]


def get_etf_allocation_weight(symbol: str) -> float:
    """Get allocation weight for ETF (0.2 to 1.0)"""
    return ETF_UNIVERSE.get(symbol, {}).get('allocation_weight', 0.4)


def get_etf_info(symbol: str) -> Dict:
    """Get complete information about an ETF"""
    return ETF_UNIVERSE.get(symbol, {})


def print_etf_universe_summary():
    """Print summary of the ETF universe"""
    print("🏛️ COMPLETE ETF UNIVERSE SUMMARY")
    print("=" * 50)
    
    by_category = {}
    by_priority = {}
    by_risk = {}
    
    for symbol, data in ETF_UNIVERSE.items():
        # Group by category
        category = data['category'].value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(symbol)
        
        # Group by priority
        priority = data['priority']
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(symbol)
        
        # Group by risk
        risk = data['risk_level'].value
        if risk not in by_risk:
            by_risk[risk] = []
        by_risk[risk].append(symbol)
    
    print(f"📊 Total ETFs: {len(ETF_UNIVERSE)}")
    print()
    
    print("🏷️ BY CATEGORY:")
    for category, symbols in by_category.items():
        print(f"   {category}: {len(symbols)} ETFs")
        print(f"      {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    print()
    
    print("🎯 BY PRIORITY:")
    for priority in sorted(by_priority.keys()):
        symbols = by_priority[priority]
        print(f"   Priority {priority}: {len(symbols)} ETFs")
        print(f"      {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    print()
    
    print("⚠️ BY RISK LEVEL:")
    for risk, symbols in by_risk.items():
        print(f"   {risk}: {len(symbols)} ETFs")
        print(f"      {', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''}")


if __name__ == "__main__":
    print_etf_universe_summary()