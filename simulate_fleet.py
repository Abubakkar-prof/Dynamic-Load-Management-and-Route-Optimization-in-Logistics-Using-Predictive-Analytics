import time
import json
import random
import math
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.persistence.models import db, Vehicle, Route, Order, OrderStatus, VehicleStatus

# Configuration
DB_URL = "sqlite:///instance/logistics.db"
API_URL = "http://localhost:5000/api/update_location"  # Or use SocketIO client
SOCKET_EMIT_URL = (
    "http://localhost:5000/tracking/api/broadcast"  # Custom endpoint for simulation
)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)


def haversine(pos1, pos2):
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    R = 6371  # Radius of earth in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def move_towards(current, target, speed_kmh, interval_sec):
    dist = haversine(current, target)
    if dist < 0.1:  # Within 100m
        return target, True

    # Calculate distance to move in this interval
    move_dist = (speed_kmh / 3600) * interval_sec
    fraction = move_dist / dist
    if fraction >= 1.0:
        return target, True

    # Interpolate
    new_lat = current[0] + (target[0] - current[0]) * fraction
    new_lon = current[1] + (target[1] - current[1]) * fraction
    return (new_lat, new_lon), False


def run_simulation():
    print("🚀 Logistics AI - Fleet Simulation Engine Started")
    session = Session()

    while True:
        try:
            # 1. Find active routes
            active_routes = session.query(Route).filter(Route.status == "Active").all()

            if not active_routes:
                print("No active routes found. Waiting...")
                time.sleep(5)
                session.commit()  # Refresh
                continue

            for route in active_routes:
                vehicle = session.query(Vehicle).get(route.vehicle_id)
                if not vehicle:
                    continue

                steps = json.loads(route.route_json)
                if not steps:
                    continue

                # Determine current target stop
                current_stop_idx = getattr(vehicle, "_sim_stop_idx", 0)
                if current_stop_idx >= len(steps):
                    print(f"Vehicle {vehicle.vehicle_id} completed its route.")
                    route.status = "Completed"
                    vehicle.status = VehicleStatus.AVAILABLE
                    session.commit()
                    continue

                target_stop = steps[current_stop_idx]
                target_pos = (target_stop["latitude"], target_stop["longitude"])
                current_pos = (
                    vehicle.current_location_lat or 31.5204,
                    vehicle.current_location_lon or 74.3587,
                )

                # Move vehicle
                new_pos, reached = move_towards(
                    current_pos, target_pos, speed_kmh=60, interval_sec=5
                )

                vehicle.current_location_lat = new_pos[0]
                vehicle.current_location_lon = new_pos[1]
                print(f"Vehicle {vehicle.vehicle_id} moved to: {new_pos}")

                if reached:
                    print(
                        f"Vehicle {vehicle.vehicle_id} reached stop: {target_stop['order_id']}"
                    )
                    setattr(vehicle, "_sim_stop_idx", current_stop_idx + 1)

                    # Update Order status
                    order = (
                        session.query(Order)
                        .filter_by(order_id=target_stop["order_id"])
                        .first()
                    )
                    if order:
                        order.status = OrderStatus.DELIVERED
                        order.actual_delivery_time = datetime.utcnow()

                # Push update via SocketIO
                try:
                    update_payload = {
                        "vehicle_id": vehicle.vehicle_id,
                        "lat": vehicle.current_location_lat,
                        "lng": vehicle.current_location_lon,
                        "status": (
                            vehicle.status.value
                            if hasattr(vehicle.status, "value")
                            else vehicle.status
                        ),
                    }
                    requests.post(
                        "http://localhost:5000/api/broadcast_location",
                        json=update_payload,
                        timeout=1,
                    )
                except Exception as e:
                    print(f"Broadcast failed: {e}")
                    pass

            session.commit()
            time.sleep(2)  # Simulation tick rate

        except Exception as e:
            print(f"Simulation Error: {e}")
            session.rollback()
            time.sleep(5)


if __name__ == "__main__":
    from datetime import datetime

    run_simulation()
