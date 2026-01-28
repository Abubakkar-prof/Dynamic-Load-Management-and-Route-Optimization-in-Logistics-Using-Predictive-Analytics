from app import app
from src.persistence.models import db, Route, Vehicle, Order

with app.app_context():
    print(f"{'Route ID':<20} | {'Status':<10} | {'Vehicle':<10}")
    print("-" * 45)
    routes = Route.query.all()
    for r in routes:
        vehicle = Vehicle.query.get(r.vehicle_id)
        v_id = vehicle.vehicle_id if vehicle else "None"
        print(f"{r.route_id:<20} | {r.status:<10} | {v_id:<10}")
