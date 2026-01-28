from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
import json
from datetime import datetime

with app.app_context():
    # 1. Reset everything just in case
    print("Resetting simulation data...")
    Order.query.update({Order.status: OrderStatus.PENDING, Order.route_id: None})
    Vehicle.query.update({Vehicle.status: VehicleStatus.AVAILABLE})
    Route.query.delete()
    db.session.commit()

    # 2. Get a vehicle and some orders
    v = Vehicle.query.first()
    orders = Order.query.limit(3).all()

    if v and orders:
        print(f"Forcing Route Assignment for vehicle {v.vehicle_id}...")
        
        # Create a mock route structure
        route_steps = []
        for o in orders:
            route_steps.append({
                "order_id": o.order_id,
                "latitude": o.latitude,
                "longitude": o.longitude
            })

        # Create the route
        route = Route(
            route_id=f"RT-DEMO-{v.vehicle_id}",
            vehicle_id=v.id,
            total_distance_m=5000,
            status="Active",  # Set to ACTIVE immediately
            route_json=json.dumps(route_steps)
        )
        db.session.add(route)
        
        # Update statuses
        v.status = VehicleStatus.ON_ROUTE
        for o in orders:
            o.status = OrderStatus.IN_TRANSIT
            o.route_id = route.id
            
        db.session.commit()
        print("Done! Check your dashboard map now. The truck should start moving.")
    else:
        print("Error: Could not find vehicles or orders in the database.")
