import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../models')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_demand_model():
    print("Loading data...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'historical_demand.csv'))
    
    # Feature Engineering
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    
    # Encoding Region
    df = pd.get_dummies(df, columns=['region'], prefix='region')
    
    # Prepare X and y
    feature_cols = [c for c in df.columns if c not in ['date', 'order_volume']]
    X = df[feature_cols]
    y = df['order_volume']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Training
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"Model Training Complete. MAE: {mae:.2f}")
    
    # Save Model and Columns
    joblib.dump(model, os.path.join(MODEL_DIR, 'demand_model.pkl'))
    with open(os.path.join(MODEL_DIR, 'model_columns.json'), 'w') as f:
        json.dump(feature_cols, f)
        
    print("Model saved to models/demand_model.pkl")

    # Generate Forecast for Next 7 Days (Demo)
    print("Generating Forecast...")
    forecast_data = []
    regions = ['North', 'South', 'East', 'West', 'Central']
    last_date = df['date'].max()
    
    for i in range(1, 8):
        future_date = last_date + pd.Timedelta(days=i)
        for region in regions:
            row = {
                'day_of_week': future_date.dayofweek,
                'month': future_date.month,
                'day_of_month': future_date.day
            }
            # Add region dummies
            for r in regions:
                row[f'region_{r}'] = 1 if r == region else 0
            
            # Ensure all columns are present
            feature_row = []
            for col in feature_cols:
                if col in row:
                    feature_row.append(row[col])
                else:
                    feature_row.append(0) # Should not happen with this logic but safe fallback
            
            pred = model.predict([feature_row])[0]
            forecast_data.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'region': region,
                'predicted_volume': int(pred)
            })
            
    df_forecast = pd.DataFrame(forecast_data)
    df_forecast.to_csv(os.path.join(DATA_DIR, 'forecast.csv'), index=False)
    print("Forecast saved to data/forecast.csv")

if __name__ == "__main__":
    train_demand_model()
