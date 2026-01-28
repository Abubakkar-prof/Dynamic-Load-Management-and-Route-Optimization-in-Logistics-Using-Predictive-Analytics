from app import app
from src.persistence.models import db, Route, Vehicle, Order, OrderStatus, VehicleStatus
from src.optimization.optimizer import LogisticsOptimizer
import pandas as pd
import json

with app.app_context():
    print("Finding pending orders and available vehicles...")
    orders_db = Order.query.filter_by(status=OrderStatus.PENDING).all()
    vehicles_db = Vehicle.query.filter_by(status=VehicleStatus.AVAILABLE).all()
    
    if not orders_db:
        print("No pending orders found.")
    elif not vehicles_db:
        print("No available vehicles found.")
    else:
        print(f"Optimizing {len(orders_db)} orders with {len(vehicles_db)} vehicles...")
        orders_data = pd.DataFrame([{
            "order_id": o.order_id,
            "weight_kg": o.weight_kg,
            "volume_m3": o.volume_m3,
            "latitude": o.latitude,
            "longitude": o.longitude,
            "deadline_hour": o.deadline_hour or 18,
            "region": o.region,
        } for o in orders_db])
        
        fleet_data = [{
            "vehicle_id": v.vehicle_id,
            "capacity_kg": v.capacity_kg,
            "capacity_vol": v.capacity_vol,
        } for v in vehicles_db]
        
        optimizer = LogisticsOptimizer(fleet_data, orders_data)
        routes = optimizer.optimize_routes()
        
        if routes:
            print(f"Generated {len(routes)} routes. Saving and activating...")
            for route_data in routes:
                vehicle = Vehicle.query.filter_by(vehicle_id=route_data["vehicle_id"]).first()
                route = Route(
                    route_id=f"RT-ACT-{route_data['vehicle_id']}",
                    vehicle_id=vehicle.id,
                    total_distance_m=route_data["total_distance_m"],
                    total_load_kg=route_data["total_load_kg"],
                    capacity_kg=route_data["capacity_kg"],
                    utilization_pct=route_data["utilization_pct"],
                    route_json=json.dumps(route_data["route"]),
                    status="Active"
                )
                db.session.add(route)
                
                # Update vehicle and orders
                vehicle.status = VehicleStatus.ON_ROUTE
                for step in route_data["route"]:
                    order = Order.query.filter_by(order_id=step["order_id"]).first()
                    if order:
                        order.status = OrderStatus.IN_TRANSIT
                        order.route_id = route.id
            
            db.session.commit()
            print("Successfully optimized and activated routes!")
        else:
            print("Optimizer could not find valid routes.")
