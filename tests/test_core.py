import pytest
import pandas as pd
import os
import joblib
from src.optimization.optimizer import LogisticsOptimizer

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")


def test_data_exists():
    assert os.path.exists(os.path.join(DATA_DIR, "fleet_info.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "orders.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "historical_demand.csv"))


def test_model_exists():
    assert os.path.exists(os.path.join(MODEL_DIR, "demand_model.pkl"))


def test_optimization_logic():
    # Create dummy data
    fleet = [
        {"vehicle_id": "V1", "capacity_kg": 100, "capacity_vol": 10, "speed_kmh": 60}
    ]
    orders = pd.DataFrame(
        [
            {
                "order_id": "O1",
                "weight_kg": 10,
                "volume_m3": 1,
                "latitude": 31.52,
                "longitude": 74.36,
                "deadline_hour": 12,
                "region": "North",
            }
        ]
    )

    optimizer = LogisticsOptimizer(fleet, orders)
    routes = optimizer.optimize_routes()

    assert len(routes) > 0 or len(orders) == 0
    if len(routes) > 0:
        assert "vehicle_id" in routes[0]
        assert "route" in routes[0]
