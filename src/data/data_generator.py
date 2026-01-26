import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
NUM_ORDERS_DAILY = 50
NUM_DAYS_HISTORY = 180
REGIONS = ["North", "South", "East", "West", "Central"]
FLEET_SIZE = 10

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
os.makedirs(DATA_DIR, exist_ok=True)


def generate_fleet_data():
    fleet = []
    vehicle_types = [
        {"type": "Van", "capacity_kg": 800, "capacity_vol": 5.0, "speed_kmh": 60},
        {"type": "Truck", "capacity_kg": 2000, "capacity_vol": 12.0, "speed_kmh": 50},
    ]

    for i in range(1, FLEET_SIZE + 1):
        v_type = random.choice(vehicle_types)
        fleet.append(
            {
                "vehicle_id": f"V{i:03d}",
                "type": v_type["type"],
                "capacity_kg": v_type["capacity_kg"],
                "capacity_vol": v_type["capacity_vol"],
                "start_location": "Warehouse_Main",
            }
        )

    df_fleet = pd.DataFrame(fleet)
    df_fleet.to_csv(os.path.join(DATA_DIR, "fleet_info.csv"), index=False)
    print(f"Generated {len(df_fleet)} vehicles in fleet_info.csv")


def generate_historical_demand():
    data = []
    start_date = datetime.now() - timedelta(days=NUM_DAYS_HISTORY)

    for day in range(NUM_DAYS_HISTORY):
        current_date = start_date + timedelta(days=day)
        # Seasonal factor (higher on weekends)
        is_weekend = current_date.weekday() >= 5
        base_demand = NUM_ORDERS_DAILY * (1.2 if is_weekend else 1.0)

        daily_volume = int(np.random.normal(base_demand, base_demand * 0.1))

        for _ in range(daily_volume):
            region = random.choices(REGIONS, weights=[0.2, 0.2, 0.2, 0.2, 0.2])[0]
            data.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "region": region,
                    "order_volume": 1,  # Each row is one order for simplicity, or we aggregate later
                }
            )

    df_demand = pd.DataFrame(data)
    # Aggregate to get daily volume per region
    df_agg = df_demand.groupby(["date", "region"]).count().reset_index()
    df_agg.to_csv(os.path.join(DATA_DIR, "historical_demand.csv"), index=False)
    print(f"Generated {NUM_DAYS_HISTORY} days of history in historical_demand.csv")


def generate_todays_orders():
    orders = []
    # Generate random locations around a central point (roughly)
    # Lat/Lon for a fictional city center (e.g., Lahore/Karachi approx)
    BASE_LAT = 31.5204
    BASE_LON = 74.3587

    for i in range(1, NUM_ORDERS_DAILY + 1):
        # Random offset for location
        lat_offset = random.uniform(-0.1, 0.1)
        lon_offset = random.uniform(-0.1, 0.1)

        orders.append(
            {
                "order_id": f'ORD-{datetime.now().strftime("%Y%m%d")}-{i:03d}',
                "weight_kg": round(random.uniform(5, 50), 2),
                "volume_m3": round(random.uniform(0.05, 0.5), 3),
                "latitude": BASE_LAT + lat_offset,
                "longitude": BASE_LON + lon_offset,
                "deadline_hour": random.randint(
                    10, 18
                ),  # Delivery deadline between 10am and 6pm
                "region": random.choice(REGIONS),
            }
        )

    df_orders = pd.DataFrame(orders)
    df_orders.to_csv(os.path.join(DATA_DIR, "orders.csv"), index=False)
    print(f"Generated {NUM_ORDERS_DAILY} orders for today in orders.csv")


if __name__ == "__main__":
    print("Generating Synthetic Data...")
    generate_fleet_data()
    generate_historical_demand()
    generate_todays_orders()
    print("Data Generation Complete.")
