from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
from datetime import datetime
import json

with app.app_context():
    print("Initializing professional test data...")
    
    # 1. Update some routes to "Completed" to show ROI
    old_routes = Route.query.limit(2).all()
    for r in old_routes:
        r.status = "Completed"
        r.total_distance_km = 45.5 # Mock distance
        
    # 2. Ensure at least one vehicle has an active route for the Driver Portal demo
    v = Vehicle.query.filter_by(vehicle_id="V001").first()
    if v:
        # Create a live route if none exists
        active = Route.query.filter_by(vehicle_id=v.id, status="Active").first()
        if not active:
             new_r = Route(
                 route_id=f"RT-DEMO-{v.vehicle_id}",
                 vehicle_id=v.id,
                 status="Active",
                 route_json=json.dumps([{"order_id": "ORD-1", "latitude": 31.5, "longitude": 74.3}])
             )
             db.session.add(new_r)
             v.status = VehicleStatus.ON_ROUTE
             
    db.session.commit()
    print("Test data ready. You can now demo ROI and Driver Portal.")
