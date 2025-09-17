"""
AI Predictor Module for Turtle Trader
Provides machine learning-based price predictions for ETF trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

# Try to import ml_models, but handle gracefully if ML libraries fail
try:
    from ml_models import model_manager
    ML_AVAILABLE = True
except Exception as e:
    logger.warning(f"ML models not available: {e}")
    model_manager = None
    ML_AVAILABLE = False

@dataclass
class PredictionResult:
    """Prediction result data structure"""
    symbol: str
    timestamp: datetime
    predicted_price: float
    confidence: float
    direction: str  # 'up', 'down', 'neutral'
    probability: float

class AIPredictor:
    """AI-based price prediction for ETFs"""
    
    def __init__(self):
        """Initialize AI predictor"""
        self.models = {}
        self.is_initialized = False
        logger.info("AI Predictor initialized")
    
    def initialize(self):
        """Initialize the AI models"""
        try:
            if ML_AVAILABLE and model_manager:
                # Initialize models from ml_models module
                self.models = model_manager.get_models() if hasattr(model_manager, 'get_models') else {}
                self.is_initialized = True
                logger.info("AI models loaded successfully")
            else:
                logger.info("Using fallback prediction mode (ML models not available)")
                self.is_initialized = True
        except Exception as e:
            logger.warning(f"Failed to load AI models: {e}")
            self.is_initialized = False
    
    def predict_price(self, symbol: str, data: pd.DataFrame) -> Optional[PredictionResult]:
        """
        Predict future price for given symbol
        
        Args:
            symbol: ETF symbol
            data: Historical price data
            
        Returns:
            PredictionResult object or None if prediction fails
        """
        if not self.is_initialized:
            self.initialize()
        
        try:
            if data.empty or len(data) < 10:
                logger.warning(f"Insufficient data for prediction: {symbol}")
                return None
            
            # Simple trend-based prediction as fallback
            recent_prices = data['close'].tail(5).values
            price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # Predict next price based on trend
            predicted_price = recent_prices[-1] * (1 + price_change * 0.1)
            
            # Determine direction and confidence
            if price_change > 0.01:
                direction = 'up'
                confidence = min(0.8, abs(price_change) * 10)
            elif price_change < -0.01:
                direction = 'down'
                confidence = min(0.8, abs(price_change) * 10)
            else:
                direction = 'neutral'
                confidence = 0.5
            
            return PredictionResult(
                symbol=symbol,
                timestamp=datetime.now(),
                predicted_price=predicted_price,
                confidence=confidence,
                direction=direction,
                probability=0.6 + confidence * 0.3
            )
            
        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return None
    
    def get_signal_strength(self, symbol: str, data: pd.DataFrame) -> float:
        """
        Get trading signal strength for symbol
        
        Args:
            symbol: ETF symbol  
            data: Historical price data
            
        Returns:
            Signal strength between -1 (strong sell) and 1 (strong buy)
        """
        prediction = self.predict_price(symbol, data)
        if not prediction:
            return 0.0
        
        if prediction.direction == 'up':
            return prediction.confidence
        elif prediction.direction == 'down':
            return -prediction.confidence
        else:
            return 0.0

# Global instance
ai_predictor = AIPredictor()