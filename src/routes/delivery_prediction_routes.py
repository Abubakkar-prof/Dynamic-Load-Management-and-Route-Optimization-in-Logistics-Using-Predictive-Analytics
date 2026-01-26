from flask import Blueprint, jsonify, request
from flask_login import login_required
from src.models.delivery_time_predictor import predict_delivery_time
import os
import pandas as pd

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/prediction")


@prediction_bp.route("/delivery_time", methods=["POST"])
@login_required
def predict_delivery():
    """
    Predict delivery time for an order
    """
    try:
        data = request.get_json()

        # Extract required parameters
        distance_km = data.get("distance_km", 0)
        weight_kg = data.get("weight_kg", 0)
        volume_m3 = data.get("volume_m3", 0)
        priority = data.get("priority", 1)
        region = data.get("region", "Central")
        vehicle_type = data.get("vehicle_type", "Van")
        hour_of_day = data.get("hour_of_day", 12)
        day_of_week = data.get("day_of_week", 0)

        # Validate inputs
        if distance_km <= 0:
            return jsonify({"error": "Distance must be greater than 0"}), 400

        # Make prediction
        predicted_time = predict_delivery_time(
            distance_km,
            weight_kg,
            volume_m3,
            priority,
            region,
            vehicle_type,
            hour_of_day,
            day_of_week,
        )

        # Convert to hours and minutes for better readability
        hours = int(predicted_time // 60)
        minutes = int(predicted_time % 60)

        return jsonify(
            {
                "predicted_delivery_time_minutes": round(predicted_time, 1),
                "predicted_delivery_time_formatted": f"{hours}h {minutes}m",
                "confidence": "high" if abs(predicted_time) < 120 else "medium",
            }
        )

    except FileNotFoundError as e:
        return (
            jsonify(
                {
                    "error": "Prediction model not trained yet. Please train the model first."
                }
            ),
            400,
        )
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@prediction_bp.route("/delivery_time/sample")
@login_required
def get_sample_predictions():
    """
    Get sample delivery time predictions
    """
    try:
        sample_path = os.path.join(
            os.path.dirname(__file__), "../../data/sample_delivery_predictions.csv"
        )

        if not os.path.exists(sample_path):
            return (
                jsonify(
                    {
                        "error": "Sample predictions not available. Please train the model first."
                    }
                ),
                400,
            )

        df = pd.read_csv(sample_path)
        predictions = df.to_dict("records")

        return jsonify({"predictions": predictions})

    except Exception as e:
        return jsonify({"error": f"Failed to load sample predictions: {str(e)}"}), 500


@prediction_bp.route("/train_delivery_model", methods=["POST"])
@login_required
def train_delivery_model():
    """
    Train the delivery time prediction model
    """
    try:
        from src.models.delivery_time_predictor import train_delivery_time_model

        train_delivery_time_model()
        return jsonify(
            {"message": "Delivery time prediction model trained successfully"}
        )

    except Exception as e:
        return jsonify({"error": f"Failed to train model: {str(e)}"}), 500
