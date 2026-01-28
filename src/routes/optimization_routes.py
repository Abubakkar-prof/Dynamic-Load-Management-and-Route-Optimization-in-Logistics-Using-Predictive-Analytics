from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from src.persistence.models import db, Vehicle, Order, Route, OrderStatus, VehicleStatus
from src.optimization.optimizer import LogisticsOptimizer
import pandas as pd
import json
from datetime import datetime, date

optimization_bp = Blueprint("optimization", __name__, url_prefix="/optimization")


@optimization_bp.route("/")
@login_required
def index():
    """Optimization dashboard"""
    return render_template("optimization/index.html")


@optimization_bp.route("/api/optimize", methods=["POST"])
@login_required
def run_optimization():
    """Run route optimization"""
    # Load pending orders from DB
    orders_db = Order.query.filter_by(status=OrderStatus.PENDING).all()
    vehicles_db = Vehicle.query.filter_by(status=VehicleStatus.AVAILABLE).all()

    if not orders_db:
        return jsonify({"error": "No pending orders to optimize", "routes": []})

    if not vehicles_db:
        return jsonify({"error": "No available vehicles", "routes": []})

    # Convert to DataFrame for optimizer
    orders_data = pd.DataFrame(
        [
            {
                "order_id": o.order_id,
                "weight_kg": o.weight_kg,
                "volume_m3": o.volume_m3,
                "latitude": o.latitude,
                "longitude": o.longitude,
                "deadline_hour": o.deadline_hour or 18,
                "region": o.region,
            }
            for o in orders_db
        ]
    )

    fleet_data = [
        {
            "vehicle_id": v.vehicle_id,
            "capacity_kg": v.capacity_kg,
            "capacity_vol": v.capacity_vol,
        }
        for v in vehicles_db
    ]

    # Run optimization
    try:
        optimizer = LogisticsOptimizer(fleet_data, orders_data)
        routes = optimizer.optimize_routes()

        # Save routes to database if requested
        if request.json and request.json.get("save_routes", False):
            for route_data in routes:
                # Create route record
                route = Route(
                    route_id=f"RT-{datetime.now().strftime('%Y%m%d')}-{route_data['vehicle_id']}",
                    date=date.today(),
                    vehicle_id=Vehicle.query.filter_by(
                        vehicle_id=route_data["vehicle_id"]
                    )
                    .first()
                    .id,
                    total_distance_m=route_data["total_distance_m"],
                    total_distance_km=route_data["total_distance_m"] / 1000,
                    total_load_kg=route_data["total_load_kg"],
                    capacity_kg=route_data["capacity_kg"],
                    utilization_pct=route_data["utilization_pct"],
                    route_json=json.dumps(route_data["route"]),
                    status="Planned",
                )
                db.session.add(route)

                # Update order status to assigned
                for step in route_data["route"]:
                    order = Order.query.filter_by(order_id=step["order_id"]).first()
                    if order:
                        order.status = OrderStatus.ASSIGNED
                        order.route_id = route.id

            db.session.commit()

        return jsonify({"success": True, "routes": routes})
    except Exception as e:
        return jsonify({"error": str(e), "routes": []}), 500


@optimization_bp.route("/routes")
@login_required
def list_routes():
    """List all routes"""
    routes = Route.query.order_by(Route.created_at.desc()).limit(50).all()
    return render_template("optimization/routes.html", routes=routes)


@optimization_bp.route("/api/activate-route", methods=["POST"])
@login_required
def activate_route():
    """Activate a planned route"""
    data = request.json
    route_id = data.get("route_id")

    if not route_id:
        return jsonify({"success": False, "error": "Missing route ID"}), 400

    route = Route.query.get(route_id)
    if not route:
        return jsonify({"success": False, "error": "Route not found"}), 404

    if route.status != "Planned":
        return jsonify({"success": False, "error": f"Cannot activate route in {route.status} status"}), 400

    try:
        # Update route status
        route.status = "Active"
        route.start_time = datetime.now()

        # Update vehicle status
        vehicle = Vehicle.query.get(route.vehicle_id)
        if vehicle:
            vehicle.status = VehicleStatus.ON_ROUTE

        # Update order statuses
        for order in route.orders:
            order.status = OrderStatus.IN_TRANSIT

        db.session.commit()
        return jsonify({"success": True, "message": "Route activated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@optimization_bp.route("/routes/<int:route_id>")
@login_required
def view_route(route_id):
    """View route details"""
    # Try to find route_detail.html in various locations
    route = Route.query.get_or_404(route_id)
    route_steps = json.loads(route.route_json) if route.route_json else []
    
    # Check if we should use a generic view or if the template exists
    template_path = "optimization/route_detail.html"
    return render_template(template_path, route=route, route_steps=route_steps)
