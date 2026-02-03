from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
import json
from datetime import datetime

with app.app_context():
    print("Creating distinct test route...")
    
    # 1. Clear existing active routes for V001 to avoid confusion
    v = Vehicle.query.filter_by(vehicle_id="V001").first()
    if not v:
        print("V001 not found")
        exit()
        
    ActiveRoutes = Route.query.filter_by(vehicle_id=v.id, status="Active").all()
    for r in ActiveRoutes:
        r.status = "Cancelled"
    
    # 2. Create 3 distinct orders far from depot
    # Depot is at 31.5204, 74.3587
    locations = [
        (31.54, 74.38, "Upper Mall"),
        (31.56, 74.40, "Gulberg"),
        (31.58, 74.42, "DHA")
    ]
    
    demo_orders = []
    for i, (lat, lon, addr) in enumerate(locations):
        oid = f"ORD-DASH-{i}-{datetime.now().strftime('%M%S')}"
        order = Order(
            order_id=oid,
            customer_name=f"Demo Customer {i}",
            delivery_address=addr,
            latitude=lat,
            longitude=lon,
            weight_kg=10.0,
            volume_m3=0.1,
            status=OrderStatus.PENDING
        )
        db.session.add(order)
        demo_orders.append(order)
    
    db.session.flush()
    
    # 3. Create route
    steps = []
    for o in demo_orders:
        steps.append({
            "order_id": o.order_id,
            "latitude": o.latitude,
            "longitude": o.longitude,
            "customer_name": o.customer_name
        })
        
    new_route = Route(
        route_id=f"RT-DASHES-{datetime.now().strftime('%H%M%S')}",
        vehicle_id=v.id,
        status="Active",
        route_json=json.dumps(steps)
    )
    db.session.add(new_route)
    db.session.flush()
    
    for o in demo_orders:
        o.status = OrderStatus.IN_TRANSIT
        o.route_id = new_route.id
        
    v.status = VehicleStatus.ON_ROUTE
    # Set current location to depot to make sure it has far to travel
    v.current_location_lat = 31.5204
    v.current_location_lon = 74.3587
    
    db.session.commit()
    print(f"Created Route {new_route.route_id}. V001 is now starting at Depot.")
