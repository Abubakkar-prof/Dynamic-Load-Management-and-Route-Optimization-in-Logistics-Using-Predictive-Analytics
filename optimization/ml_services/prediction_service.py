import pandas as pd
import numpy as np
import joblib
import os
import json
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

class DeliveryPredictor:
    def __init__(self):
        self.model_dir = os.path.join(settings.BASE_DIR, 'models_data')
        self.model_path = os.path.join(self.model_dir, "delivery_time_model.pkl")
        self.columns_path = os.path.join(self.model_dir, "delivery_time_model_columns.json")
        os.makedirs(self.model_dir, exist_ok=True)

    def train_model(self):
        """Train a synthetic model for demonstration."""
        np.random.seed(42)
        n_samples = 1000
        regions = ["North", "South", "East", "West", "Central"]
        vehicle_types = ["Van", "Truck"]
        data = []

        for _ in range(n_samples):
            distance_km = np.random.uniform(5, 100)
            weight_kg = np.random.uniform(0.5, 50)
            volume_m3 = np.random.uniform(0.01, 2)
            priority = np.random.randint(1, 5)
            region = np.random.choice(regions)
            vehicle_type = np.random.choice(vehicle_types)
            hour_of_day = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)

            base_time = (distance_km * 2 + weight_kg * 0.5 + volume_m3 * 3 + (4 - priority) * 15)
            
            if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                base_time *= 1.3
            if day_of_week >= 5:
                base_time *= 0.9

            actual_time = max(base_time + np.random.normal(0, 10), 5)

            data.append({
                "distance_km": distance_km,
                "weight_kg": weight_kg,
                "volume_m3": volume_m3,
                "priority": priority,
                "region": region,
                "vehicle_type": vehicle_type,
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "actual_delivery_time_min": actual_time,
            })

        df = pd.DataFrame(data)
        df = pd.get_dummies(df, columns=["region", "vehicle_type"], prefix=["region", "vehicle"])
        
        feature_cols = [c for c in df.columns if c != "actual_delivery_time_min"]
        X = df[feature_cols]
        y = df["actual_delivery_time_min"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluation
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)

        joblib.dump(model, self.model_path)
        with open(self.columns_path, "w") as f:
            json.dump(feature_cols, f)

        return {"mae": mae, "status": "trained"}

    def predict(self, data):
        """Predict delivery time for a single delivery."""
        if not os.path.exists(self.model_path):
            return None

        model = joblib.load(self.model_path)
        with open(self.columns_path, "r") as f:
            feature_cols = json.load(f)

        feature_dict = {
            "distance_km": data.get('distance_km', 0),
            "weight_kg": data.get('weight_kg', 0),
            "volume_m3": data.get('volume_m3', 0),
            "priority": data.get('priority', 1),
            "hour_of_day": data.get('hour_of_day', 12),
            "day_of_week": data.get('day_of_week', 0),
        }

        regions = ["North", "South", "East", "West", "Central"]
        vehicle_types = ["Van", "Truck"]

        region = data.get('region', 'Central')
        v_type = data.get('vehicle_type', 'Van')

        for r in regions:
            feature_dict[f"region_{r}"] = 1 if r == region else 0
        for v in vehicle_types:
            feature_dict[f"vehicle_{v}"] = 1 if v == v_type else 0

        feature_row = [feature_dict.get(col, 0) for col in feature_cols]
        
        predicted_time = model.predict([feature_row])[0]
        return predicted_time
