import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
import json
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_delivery_time_model():
    """
    Train a model to predict delivery times based on various factors
    """
    print("Loading delivery data...")

    # For demo purposes, we'll generate synthetic data
    # In a real scenario, this would come from your database
    np.random.seed(42)
    n_samples = 1000

    # Generate synthetic delivery data
    data = []
    regions = ["North", "South", "East", "West", "Central"]
    vehicle_types = ["Van", "Truck"]

    for i in range(n_samples):
        # Random features
        distance_km = np.random.uniform(5, 100)
        weight_kg = np.random.uniform(0.5, 50)
        volume_m3 = np.random.uniform(0.01, 2)
        priority = np.random.randint(1, 5)
        region = np.random.choice(regions)
        vehicle_type = np.random.choice(vehicle_types)
        hour_of_day = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)

        # Base delivery time calculation with some randomness
        base_time = (
            distance_km * 2  # 2 minutes per km
            + weight_kg * 0.5  # 0.5 minutes per kg
            + volume_m3 * 3  # 3 minutes per m3
            + (4 - priority) * 15  # Higher priority gets faster delivery
        )

        # Adjust for time of day (traffic effects)
        if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
            base_time *= 1.3  # Rush hour penalty

        # Adjust for day of week
        if day_of_week >= 5:  # Weekend
            base_time *= 0.9  # Less traffic

        # Add some noise
        actual_delivery_time = base_time + np.random.normal(0, 10)
        actual_delivery_time = max(actual_delivery_time, 5)  # Minimum 5 minutes

        data.append(
            {
                "distance_km": distance_km,
                "weight_kg": weight_kg,
                "volume_m3": volume_m3,
                "priority": priority,
                "region": region,
                "vehicle_type": vehicle_type,
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "actual_delivery_time_min": actual_delivery_time,
            }
        )

    df = pd.DataFrame(data)

    # Feature Engineering
    df = pd.get_dummies(
        df, columns=["region", "vehicle_type"], prefix=["region", "vehicle"]
    )

    # Prepare X and y
    feature_cols = [c for c in df.columns if c not in ["actual_delivery_time_min"]]
    X = df[feature_cols]
    y = df["actual_delivery_time_min"]

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Model Training
    print("Training Delivery Time Prediction Model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluation
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Model Training Complete.")
    print(f"MAE: {mae:.2f} minutes")
    print(f"RMSE: {rmse:.2f} minutes")

    # Save Model and Columns
    joblib.dump(model, os.path.join(MODEL_DIR, "delivery_time_model.pkl"))
    with open(os.path.join(MODEL_DIR, "delivery_time_model_columns.json"), "w") as f:
        json.dump(feature_cols, f)

    print("Delivery time model saved to models/delivery_time_model.pkl")

    # Generate sample predictions for demo
    print("Generating sample predictions...")
    sample_predictions = []

    # Create sample orders for prediction
    for i in range(10):
        distance = np.random.uniform(10, 50)
        weight = np.random.uniform(1, 20)
        volume = np.random.uniform(0.1, 1)
        priority = np.random.randint(1, 5)
        region = np.random.choice(regions)
        vehicle_type = np.random.choice(vehicle_types)
        hour = np.random.randint(0, 24)
        day = np.random.randint(0, 7)

        # Create feature vector for prediction
        feature_dict = {
            "distance_km": distance,
            "weight_kg": weight,
            "volume_m3": volume,
            "priority": priority,
            "hour_of_day": hour,
            "day_of_week": day,
        }

        # Add dummy variables
        for r in regions:
            feature_dict[f"region_{r}"] = 1 if r == region else 0
        for v in vehicle_types:
            feature_dict[f"vehicle_{v}"] = 1 if v == vehicle_type else 0

        # Ensure all columns are present
        feature_row = []
        for col in feature_cols:
            if col in feature_dict:
                feature_row.append(feature_dict[col])
            else:
                feature_row.append(0)

        predicted_time = model.predict([feature_row])[0]

        sample_predictions.append(
            {
                "order_id": f"ORD-{1000+i}",
                "distance_km": round(distance, 2),
                "weight_kg": round(weight, 2),
                "predicted_delivery_time_min": round(predicted_time, 1),
                "priority": priority,
                "region": region,
            }
        )

    df_sample = pd.DataFrame(sample_predictions)
    df_sample.to_csv(
        os.path.join(DATA_DIR, "sample_delivery_predictions.csv"), index=False
    )
    print("Sample predictions saved to data/sample_delivery_predictions.csv")


def predict_delivery_time(
    distance_km,
    weight_kg,
    volume_m3,
    priority,
    region,
    vehicle_type,
    hour_of_day,
    day_of_week,
):
    """
    Predict delivery time for a given order
    """
    # Load model and columns
    model_path = os.path.join(MODEL_DIR, "delivery_time_model.pkl")
    columns_path = os.path.join(MODEL_DIR, "delivery_time_model_columns.json")

    if not os.path.exists(model_path) or not os.path.exists(columns_path):
        raise FileNotFoundError(
            "Delivery time model not found. Please train the model first."
        )

    model = joblib.load(model_path)
    with open(columns_path, "r") as f:
        feature_cols = json.load(f)

    # Create feature vector
    feature_dict = {
        "distance_km": distance_km,
        "weight_kg": weight_kg,
        "volume_m3": volume_m3,
        "priority": priority,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
    }

    # Add dummy variables for categorical features
    regions = ["North", "South", "East", "West", "Central"]
    vehicle_types = ["Van", "Truck"]

    for r in regions:
        feature_dict[f"region_{r}"] = 1 if r == region else 0
    for v in vehicle_types:
        feature_dict[f"vehicle_{v}"] = 1 if v == vehicle_type else 0

    # Ensure all columns are present
    feature_row = []
    for col in feature_cols:
        if col in feature_dict:
            feature_row.append(feature_dict[col])
        else:
            feature_row.append(0)

    # Make prediction
    predicted_time = model.predict([feature_row])[0]
    return predicted_time


if __name__ == "__main__":
    train_delivery_time_model()
