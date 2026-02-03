from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
import json
from datetime import datetime
import sys

with app.app_context():
    print("DEMO START SCRIPT")
    try:
        v = Vehicle.query.filter_by(vehicle_id="V001").first()
        if not v:
            v = Vehicle.query.first()
            
        orders = Order.query.filter_by(status=OrderStatus.PENDING).limit(5).all()
        
        if v and orders:
            v.status = VehicleStatus.ON_ROUTE
            
            steps = []
            for o in orders:
                steps.append({
                    "order_id": o.order_id,
                    "latitude": o.latitude,
                    "longitude": o.longitude
                })
                
            rid = f"RT-AUTO-{datetime.now().strftime('%H%M%S')}"
            new_route = Route(
                route_id=rid,
                vehicle_id=v.id,
                status="Active",
                route_json=json.dumps(steps)
            )
            db.session.add(new_route)
            db.session.flush() # Get ID
            
            for o in orders:
                o.status = OrderStatus.IN_TRANSIT
                o.route_id = new_route.id
                
            db.session.commit()
            print(f"CREATED ROUTE {rid} for {v.vehicle_id}")
        else:
            print("DATA MISSING")
    except Exception as e:
        db.session.rollback()
        print(f"FATAL ERROR: {e}")
        sys.exit(1)
