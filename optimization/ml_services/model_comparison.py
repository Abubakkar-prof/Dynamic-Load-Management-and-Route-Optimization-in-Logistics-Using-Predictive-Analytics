"""
ML Model Comparison Service
Compares performance of multiple machine learning models for demand forecasting.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import joblib
import os

class MLModelComparison:
    """
    Service to train and compare multiple ML models for forecasting.
    """
    
    def __init__(self, data=None):
        self.models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'LightGBM': LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
        }
        self.data = data
        self.results = {}
        
    def prepare_data(self):
        """
        Prepare synthetic data for demo if no data provided.
        In a real scenario, this would load from the database.
        """
        if self.data is None:
            # Generate synthetic time-series data
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
            n = len(dates)
            
            # Trend + Seasonality + Noise
            trend = np.linspace(100, 200, n)
            seasonality = 50 * np.sin(2 * np.pi * dates.dayofyear / 365)
            noise = np.random.normal(0, 10, n)
            
            y = trend + seasonality + noise
            
            df = pd.DataFrame({'ds': dates, 'y': y})
            df['day_of_week'] = df['ds'].dt.dayofweek
            df['month'] = df['ds'].dt.month
            df['day_of_year'] = df['ds'].dt.dayofyear
            
            # Lag features
            df['lag_1'] = df['y'].shift(1)
            df['lag_7'] = df['y'].shift(7)
            df = df.dropna()
            
            self.data = df
            
        X = self.data[['day_of_week', 'month', 'day_of_year', 'lag_1', 'lag_7']]
        y = self.data['y']
        
        return train_test_split(X, y, test_size=0.2, shuffle=False)
        
    def run_comparison(self):
        """
        Train all models and calculate performance metrics.
        """
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            
            self.results[name] = {
                'MAE': float(mean_absolute_error(y_test, predictions)),
                'RMSE': float(np.sqrt(mean_squared_error(y_test, predictions))),
                'R2': float(r2_score(y_test, predictions)),
                'predictions': predictions.tolist(),
                'y_test': y_test.tolist()
            }
            
        return self.results

    def get_best_model(self):
        """Returns the model name with the lowest MAE."""
        if not self.results:
            self.run_comparison()
        return min(self.results.items(), key=lambda x: x[1]['MAE'])[0]
