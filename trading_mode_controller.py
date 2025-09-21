"""
🔄 LIVE/DEMO MODE CONTROLLER
===========================

Controls switching between demo and live trading modes
"""

import streamlit as st
from typing import Dict, Any
import json
import os

class TradingModeController:
    """Manage demo vs live trading modes"""
    
    def __init__(self):
        self.mode_file = '.trading_mode.json'
        self.current_mode = self.load_mode()
    
    def load_mode(self) -> str:
        """Load current trading mode"""
        try:
            if os.path.exists(self.mode_file):
                with open(self.mode_file, 'r') as f:
                    data = json.load(f)
                return data.get('mode', 'LIVE')
        except Exception:
            pass
        return 'LIVE'
    
    def save_mode(self, mode: str):
        """Save trading mode"""
        try:
            with open(self.mode_file, 'w') as f:
                json.dump({
                    'mode': mode,
                    'timestamp': str(st.session_state.get('timestamp', '')),
                    'user_confirmed': True
                }, f, indent=2)
            self.current_mode = mode
        except Exception as e:
            st.error(f"Error saving mode: {e}")
    
    def render_mode_selector(self):
        """Render mode selection interface"""
        st.sidebar.markdown("---")
        st.sidebar.header("🎯 Trading Mode")
        
        # Current mode display
        if self.current_mode == 'LIVE':
            st.sidebar.success("🔴 **LIVE TRADING ACTIVE**")
            st.sidebar.warning("⚠️ Real money at risk!")
        else:
            st.sidebar.info("🧪 **DEMO MODE ACTIVE**")
            st.sidebar.info("💡 No real trades placed")
        
        # Mode switcher
        new_mode = st.sidebar.selectbox(
            "Select Mode:",
            options=['DEMO', 'LIVE'],
            index=0 if self.current_mode == 'DEMO' else 1,
            key="trading_mode_select"
        )
        
        # Confirmation for live mode
        if new_mode == 'LIVE' and self.current_mode != 'LIVE':
            st.sidebar.markdown("### ⚠️ **LIVE MODE CONFIRMATION**")
            st.sidebar.error("**WARNING: You are switching to LIVE trading!**")
            st.sidebar.warning("Real money will be used for trades.")
            
            # Checklist
            st.sidebar.markdown("**Confirm all requirements:**")
            api_ready = st.sidebar.checkbox("✅ API credentials configured", key="api_check")
            balance_ready = st.sidebar.checkbox("✅ Sufficient account balance", key="balance_check")
            strategy_ready = st.sidebar.checkbox("✅ Strategy parameters verified", key="strategy_check")
            risk_ready = st.sidebar.checkbox("✅ Risk limits understood", key="risk_check")
            
            all_ready = api_ready and balance_ready and strategy_ready and risk_ready
            
            if all_ready:
                if st.sidebar.button("🔴 **ACTIVATE LIVE TRADING**", key="activate_live"):
                    self.save_mode('LIVE')
                    st.sidebar.success("✅ Live trading activated!")
                    st.rerun()
            else:
                st.sidebar.info("Complete all checks to enable live trading")
        
        elif new_mode == 'DEMO' and self.current_mode == 'LIVE':
            if st.sidebar.button("🧪 Switch to Demo Mode", key="switch_demo"):
                self.save_mode('DEMO')
                st.sidebar.success("✅ Switched to demo mode")
                st.rerun()
        
        return self.current_mode
    
    def is_live_mode(self) -> bool:
        """Check if currently in live trading mode"""
        return self.current_mode == 'LIVE'
    
    def get_mode_config(self) -> Dict[str, Any]:
        """Get mode-specific configuration"""
        if self.is_live_mode():
            return {
                'execute_orders': True,
                'use_real_balance': True,
                'send_notifications': True,
                'logging_level': 'INFO',
                'safety_checks': True
            }
        else:
            return {
                'execute_orders': False,
                'use_real_balance': False,
                'send_notifications': False,
                'logging_level': 'DEBUG',
                'safety_checks': False
            }

# Global instance
mode_controller = TradingModeController()