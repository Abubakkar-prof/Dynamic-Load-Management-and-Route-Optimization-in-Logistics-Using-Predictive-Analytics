from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.persistence.models import db, Vehicle, Driver, Order, TrackingUpdate
from datetime import datetime
import json

tracking_bp = Blueprint("tracking", __name__, url_prefix="/tracking")


@tracking_bp.route("/vehicles")
@login_required
def vehicle_tracking():
    """Get real-time vehicle locations"""
    vehicles = Vehicle.query.filter(Vehicle.status.in_(["Available", "On Route"])).all()
    vehicle_data = []

    for vehicle in vehicles:
        # Get current driver if assigned
        driver_name = None
        if vehicle.drivers:
            driver = vehicle.drivers[0]
            if driver.user:
                driver_name = driver.user.full_name or driver.user.username

        # Get active route if any
        active_route = next((r.route_id for r in vehicle.routes if r.status == "Active"), None)

        vehicle_data.append(
            {
                "id": vehicle.id,
                "vehicle_id": vehicle.vehicle_id,
                "lat": vehicle.current_location_lat,
                "lon": vehicle.current_location_lon,
                "status": vehicle.status.value,
                "driver": driver_name,
                "active_route": active_route,
                "make": vehicle.make,
                "model": vehicle.model,
            }
        )

    return jsonify({"vehicles": vehicle_data})


@tracking_bp.route("/orders")
@login_required
def order_tracking():
    """Get real-time order statuses"""
    orders = Order.query.filter(Order.status.in_(["Assigned", "In Transit"])).all()
    order_data = []

    for order in orders:
        # Get latest tracking update
        latest_update = (
            TrackingUpdate.query.filter_by(order_id=order.id)
            .order_by(TrackingUpdate.timestamp.desc())
            .first()
        )

        order_data.append(
            {
                "id": order.id,
                "order_id": order.order_id,
                "customer": order.customer_name,
                "lat": order.latitude,
                "lon": order.longitude,
                "status": order.status.value,
                "last_update": (
                    latest_update.timestamp.isoformat() if latest_update else None
                ),
                "last_location": (
                    {
                        "lat": latest_update.location_lat if latest_update else None,
                        "lon": latest_update.location_lon if latest_update else None,
                    }
                    if latest_update
                    else None
                ),
            }
        )

    return jsonify({"orders": order_data})


@tracking_bp.route("/update_location", methods=["POST"])
@login_required
def update_location():
    """Update vehicle or driver location"""
    data = request.get_json()

    vehicle_id = data.get("vehicle_id")
    lat = data.get("lat")
    lon = data.get("lon")

    if not vehicle_id or lat is None or lon is None:
        return jsonify({"error": "Missing required fields"}), 400

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Update vehicle location
    vehicle.current_location_lat = lat
    vehicle.current_location_lon = lon
    vehicle.updated_at = datetime.utcnow()

    db.session.commit()

    # Emit location update via SocketIO
    from app import app

    app.socketio.emit(
        "location_update",
        {
            "vehicle_id": vehicle_id,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    return jsonify({"message": "Location updated successfully"})


@tracking_bp.route("/driver_performance")
@login_required
def driver_performance():
    """Get driver performance metrics"""
    drivers = Driver.query.all()
    performance_data = []

    for driver in drivers:
        # Calculate recent performance metrics
        total_deliveries = driver.total_deliveries
        rating = driver.rating

        # Get recent orders for this driver
        recent_orders = (
            Order.query.join("route")
            .filter(Order.route.has(driver_id=driver.id))
            .order_by(Order.created_at.desc())
            .limit(10)
            .all()
        )

        on_time_deliveries = sum(
            1
            for order in recent_orders
            if order.actual_delivery_time
            and order.deadline_date
            and order.actual_delivery_time.date() <= order.deadline_date
        )

        performance_data.append(
            {
                "driver_id": driver.id,
                "name": driver.user.full_name if driver.user else "Unknown",
                "license": driver.license_number,
                "rating": rating,
                "total_deliveries": total_deliveries,
                "on_time_rate": (
                    (on_time_deliveries / len(recent_orders) * 100)
                    if recent_orders
                    else 0
                ),
                "status": driver.status.value,
            }
        )

    return jsonify({"drivers": performance_data})
