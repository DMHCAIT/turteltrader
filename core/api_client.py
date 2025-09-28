"""
🔌 CORE API CLIENT WRAPPER
==========================

Clean wrapper for Kite API client - Real data only
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kite_api_client import get_kite_client, Position, Order, KiteAPIClient

# Initialize the API client
api_client = get_kite_client()

__all__ = ["api_client", "get_kite_client", "Position", "Order", "KiteAPIClient"]
