# Kite API Client Wrapper

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kite_api_client import get_kite_client
    api_client = get_kite_client()
except ImportError:
    api_client = None

__all__ = ["api_client"]
