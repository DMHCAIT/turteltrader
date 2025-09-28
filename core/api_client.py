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

# Lazy-loaded API client - only initialize when actually used
_api_client = None

def get_api_client():
    global _api_client
    if _api_client is None:
        _api_client = get_kite_client()
    return _api_client

# Create a proxy object that lazy-loads the API client
class APIClientProxy:
    def __getattr__(self, name):
        return getattr(get_api_client(), name)

# For backward compatibility - this won't initialize until used
api_client = APIClientProxy()

__all__ = ["api_client", "get_api_client", "get_kite_client", "Position", "Order", "KiteAPIClient"]
