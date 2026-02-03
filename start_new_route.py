from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
import json
from datetime import datetime

with app.app_context():
    print("Assigning a new route for demonstration...")
    # Get a vehicle
    print(f"Vehicle search: V001")
    v = Vehicle.query.filter_by(vehicle_id="V001").first()
    print(f"Vehicle found: {v}")
    if not v:
        v = Vehicle.query.first()
        print(f"Fallback vehicle found: {v}")
        
    # Get 3 pending orders
    orders = Order.query.filter_by(status=OrderStatus.PENDING).limit(3).all()
    print(f"Orders found: {len(orders)}")
    
    try:
        if v and len(orders) > 0:
            # Reset vehicle if it was in another state
            v.status = VehicleStatus.ON_ROUTE
            
            # Create route steps
            steps = []
            for o in orders:
                steps.append({
                    "order_id": o.order_id,
                    "latitude": o.latitude,
                    "longitude": o.longitude
                })
                
            # Create the route record
            new_route = Route(
                route_id=f"RT-LIVE-{v.vehicle_id}-{datetime.now().strftime('%M%S')}",
                vehicle_id=v.id,
                status="Active",
                route_json=json.dumps(steps)
            )
            db.session.add(new_route)
            
            # Assign orders to this route
            for o in orders:
                o.status = OrderStatus.IN_TRANSIT
                o.route_id = new_route.id
                
            db.session.commit()
            print(f"Successfully started Route: {new_route.route_id} for Vehicle: {v.vehicle_id}")
        else:
            print("Required data (Vehicle or Pending Orders) not found.")
    except Exception as e:
        db.session.rollback()
        with open("error_log.txt", "w") as f:
            f.write(str(e))
        print(f"Error starting route: {e}")
