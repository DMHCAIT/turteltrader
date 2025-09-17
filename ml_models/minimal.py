"""
Turtle Trader - Minimal ML Models (without TensorFlow/PyTorch)
Essential machine learning models for trading predictions
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Core ML libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import optuna
import talib
from loguru import logger

# Optional pandas_ta import
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    logger.warning("pandas_ta not available - some indicators will be disabled")

# Install joblib if missing
try:
    import joblib
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'joblib'])
    import joblib

class FeatureEngineer:
    """Advanced feature engineering for trading signals"""
    
    def __init__(self):
        self.feature_names = []
        logger.info("Feature Engineer initialized")
    
    def create_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive feature set"""
        df = data.copy()
        
        # Technical indicators using TA-Lib
        df = self._add_talib_features(df)
        
        # Price-based features
        df = self._add_price_features(df)
        
        # Volume features
        df = self._add_volume_features(df)
        
        # Time-based features
        df = self._add_time_features(df)
        
        # Market microstructure features
        df = self._add_market_microstructure(df)
        
        # Statistical features
        df = self._add_statistical_features(df)
        
        # Clean data
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method='ffill').fillna(0)
        
        return df
    
    def _add_talib_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add TA-Lib technical indicators"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        volume = df['volume'].values
        
        # Momentum indicators
        df['rsi'] = talib.RSI(close, timeperiod=14)
        df['rsi_30'] = talib.RSI(close, timeperiod=30)
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(close)
        df['cci'] = talib.CCI(high, low, close, timeperiod=14)
        df['williams_r'] = talib.WILLR(high, low, close, timeperiod=14)
        df['roc'] = talib.ROC(close, timeperiod=10)
        df['stoch_k'], df['stoch_d'] = talib.STOCH(high, low, close)
        
        # Trend indicators
        df['sma_5'] = talib.SMA(close, timeperiod=5)
        df['sma_10'] = talib.SMA(close, timeperiod=10)
        df['sma_20'] = talib.SMA(close, timeperiod=20)
        df['sma_50'] = talib.SMA(close, timeperiod=50)
        df['ema_12'] = talib.EMA(close, timeperiod=12)
        df['ema_26'] = talib.EMA(close, timeperiod=26)
        df['adx'] = talib.ADX(high, low, close, timeperiod=14)
        df['aroon_up'], df['aroon_down'] = talib.AROON(high, low, timeperiod=14)
        
        # Volatility indicators
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(close)
        df['atr'] = talib.ATR(high, low, close, timeperiod=14)
        df['natr'] = talib.NATR(high, low, close, timeperiod=14)
        
        # Volume indicators
        df['obv'] = talib.OBV(close, volume)
        df['ad'] = talib.AD(high, low, close, volume)
        df['adosc'] = talib.ADOSC(high, low, close, volume)
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price-based features"""
        
        # Price changes and returns
        for period in [1, 2, 3, 5, 10, 20]:
            df[f'return_{period}d'] = df['close'].pct_change(period)
            df[f'price_change_{period}d'] = df['close'] - df['close'].shift(period)
            df[f'high_low_ratio_{period}d'] = df['high'].rolling(period).max() / df['low'].rolling(period).min()
        
        # Price ratios
        df['hl_ratio'] = df['high'] / df['low']
        df['oc_ratio'] = df['open'] / df['close']
        df['close_sma20_ratio'] = df['close'] / df['sma_20']
        df['close_ema12_ratio'] = df['close'] / df['ema_12']
        
        # Price position in range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        
        # Volume ratios and changes
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        df['volume_change'] = df['volume'].pct_change()
        
        # Price-volume features
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        df['price_volume'] = df['close'] * df['volume']
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        
        if 'datetime' not in df.columns and df.index.name == 'datetime':
            df['datetime'] = df.index
        
        if 'datetime' in df.columns:
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
            df['month'] = df['datetime'].dt.month
            df['quarter'] = df['datetime'].dt.quarter
            
            # Market session features
            df['is_opening'] = (df['hour'] == 9).astype(int)
            df['is_closing'] = (df['hour'] == 15).astype(int)
            df['is_lunch'] = ((df['hour'] >= 12) & (df['hour'] <= 13)).astype(int)
        
        return df
    
    def _add_market_microstructure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        
        # Spread and efficiency measures
        df['spread'] = df['high'] - df['low']
        df['spread_pct'] = df['spread'] / df['close']
        df['efficiency'] = np.abs(df['close'] - df['open']) / df['spread']
        
        # Momentum and mean reversion signals
        df['momentum_1d'] = df['close'] / df['close'].shift(1) - 1
        df['momentum_5d'] = df['close'] / df['close'].shift(5) - 1
        df['mean_reversion_5d'] = (df['close'] - df['close'].rolling(5).mean()) / df['close'].rolling(5).std()
        
        return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features"""
        
        # Rolling statistics
        for window in [5, 10, 20]:
            df[f'volatility_{window}d'] = df['close'].rolling(window).std()
            df[f'skewness_{window}d'] = df['close'].rolling(window).skew()
            df[f'kurtosis_{window}d'] = df['close'].rolling(window).kurt()
            
            # Z-scores
            rolling_mean = df['close'].rolling(window).mean()
            rolling_std = df['close'].rolling(window).std()
            df[f'zscore_{window}d'] = (df['close'] - rolling_mean) / rolling_std
        
        return df

class EnsembleModel:
    """Ensemble model combining XGBoost, LightGBM, and CatBoost"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train ensemble model"""
        
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train individual models
        models_performance = {}
        
        # XGBoost
        self.models['xgboost'] = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.models['xgboost'].fit(X_train, y_train)
        xgb_pred = self.models['xgboost'].predict(X_val)
        models_performance['xgboost'] = mean_squared_error(y_val, xgb_pred)
        
        # LightGBM
        self.models['lightgbm'] = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        self.models['lightgbm'].fit(X_train, y_train)
        lgb_pred = self.models['lightgbm'].predict(X_val)
        models_performance['lightgbm'] = mean_squared_error(y_val, lgb_pred)
        
        # CatBoost
        self.models['catboost'] = cb.CatBoostRegressor(
            iterations=100,
            depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=False
        )
        self.models['catboost'].fit(X_train, y_train)
        cb_pred = self.models['catboost'].predict(X_val)
        models_performance['catboost'] = mean_squared_error(y_val, cb_pred)
        
        # Calculate weights based on performance (inverse of MSE)
        total_inverse_mse = sum(1/mse for mse in models_performance.values())
        self.weights = {
            model: (1/mse) / total_inverse_mse 
            for model, mse in models_performance.items()
        }
        
        self.is_trained = True
        
        logger.info(f"Ensemble model trained with weights: {self.weights}")
        return models_performance
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble prediction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from each model
        predictions = {}
        predictions['xgboost'] = self.models['xgboost'].predict(X_scaled)
        predictions['lightgbm'] = self.models['lightgbm'].predict(X_scaled)
        predictions['catboost'] = self.models['catboost'].predict(X_scaled)
        
        # Weighted average
        ensemble_pred = np.zeros(len(X_scaled))
        for model, pred in predictions.items():
            ensemble_pred += self.weights[model] * pred
        
        return ensemble_pred

class ModelManager:
    """Simplified model manager without deep learning"""
    
    def __init__(self, model_dir: str = "models/"):
        self.model_dir = model_dir
        self.models = {}
        self.feature_engineer = FeatureEngineer()
        
        # Create model directory
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        logger.info("Model Manager initialized (ML models only)")
    
    def train_model(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Train model for a specific symbol"""
        logger.info(f"Training model for {symbol}")
        
        try:
            # Feature engineering
            featured_data = self.feature_engineer.create_all_features(data)
            
            # Prepare target (next period return)
            featured_data['target'] = featured_data['close'].shift(-1) / featured_data['close'] - 1
            featured_data = featured_data.dropna()
            
            if len(featured_data) < 100:
                logger.warning(f"Insufficient data for {symbol}: {len(featured_data)} rows")
                return {'error': 'Insufficient data'}
            
            # Select features (exclude target and price columns)
            feature_cols = [col for col in featured_data.columns 
                          if col not in ['target', 'open', 'high', 'low', 'close', 'volume', 'datetime']]
            
            X = featured_data[feature_cols].values
            y = featured_data['target'].values
            
            # Train ensemble model
            model = EnsembleModel()
            performance = model.train(X, y)
            
            # Save model
            model_path = f"{self.model_dir}/{symbol}_model.pkl"
            joblib.dump(model, model_path)
            
            self.models[symbol] = model
            
            return {
                'symbol': symbol,
                'performance': performance,
                'features': len(feature_cols),
                'samples': len(X),
                'model_path': model_path
            }
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_predictions(self, symbols: List[str], current_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Get predictions for multiple symbols"""
        predictions = {}
        
        for symbol in symbols:
            if symbol not in current_data:
                logger.warning(f"No data available for {symbol}")
                continue
            
            try:
                # Load or use cached model
                if symbol not in self.models:
                    model_path = f"{self.model_dir}/{symbol}_model.pkl"
                    if os.path.exists(model_path):
                        self.models[symbol] = joblib.load(model_path)
                    else:
                        logger.warning(f"No trained model for {symbol}")
                        continue
                
                # Prepare features
                data = current_data[symbol]
                featured_data = self.feature_engineer.create_all_features(data)
                
                # Get latest features
                feature_cols = [col for col in featured_data.columns 
                              if col not in ['open', 'high', 'low', 'close', 'volume', 'datetime']]
                
                latest_features = featured_data[feature_cols].iloc[-1:].values
                
                # Make prediction
                prediction = self.models[symbol].predict(latest_features)[0]
                confidence = min(abs(prediction) * 10, 1.0)  # Simple confidence measure
                
                predictions[symbol] = {
                    'prediction': prediction,
                    'confidence': confidence,
                    'signal': 'BUY' if prediction > 0.01 else 'SELL' if prediction < -0.01 else 'HOLD'
                }
                
            except Exception as e:
                logger.error(f"Error getting prediction for {symbol}: {e}")
                predictions[symbol] = {
                    'prediction': 0.0,
                    'confidence': 0.0,
                    'signal': 'HOLD',
                    'error': str(e)
                }
        
        return predictions

# Create global model manager instance
model_manager = ModelManager()

# Export main classes
__all__ = ['FeatureEngineer', 'EnsembleModel', 'ModelManager', 'model_manager']
