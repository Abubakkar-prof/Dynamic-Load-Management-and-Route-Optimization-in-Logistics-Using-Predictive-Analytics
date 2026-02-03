from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from src.persistence.models import (
    db,
    Vehicle,
    Order,
    Route,
    Driver,
    Notification,
    PerformanceMetric,
    VehicleStatus,
    OrderStatus,
)
from datetime import date, datetime, timedelta
import pandas as pd
import os

main_bp = Blueprint("main", __name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")


@main_bp.route("/")
@login_required
def index():
    return render_template("dashboard.html", user=current_user)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@main_bp.route("/tracking")
@login_required
def tracking():
    """Real-time tracking dashboard"""
    return render_template("telemetry/tracking.html")


@main_bp.route("/delivery_prediction")
@login_required
def delivery_prediction():
    """Delivery time prediction dashboard"""
    return render_template("prediction/delivery_prediction.html")


@main_bp.route("/multi_depot", methods=["GET", "POST"])
@login_required
def multi_depot():
    """Multi-depot optimization dashboard"""
    depots = [
        {"name": "Central Hub", "address": "123 Main St, Lahore", "latitude": 31.5204, "longitude": 74.3587},
        {"name": "North Annex", "address": "456 North Rd, Lahore", "latitude": 31.5584, "longitude": 74.3436}
    ]
    results = []
    if request.method == "POST":
        # Mocking some optimization results for demonstration when the button is clicked
        results = [
            {"vehicle_id": "TRK-772", "depot_name": "Central Hub", "total_distance_m": 12500, "utilization_pct": 88, "route": []},
            {"vehicle_id": "VAN-104", "depot_name": "North Annex", "total_distance_m": 8400, "utilization_pct": 92, "route": []}
        ]
    return render_template("optimization/multi_depot.html", depots=depots, results=results)


@main_bp.route("/scenario_analysis")
@login_required
def scenario_analysis():
    """Scenario analysis dashboard"""
    return render_template("scenario_analysis.html")


@main_bp.route("/bin_packing")
@login_required
def bin_packing():
    """3D bin packing optimization dashboard"""
    return render_template("optimization/bin_packing.html")


@main_bp.route("/driver/<vehicle_id>")
def driver_portal(vehicle_id):
    """Driver mobile portal view"""
    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first_or_404()
    active_route = Route.query.filter_by(vehicle_id=vehicle.id, status="Active").first()
    
    current_stop = None
    if active_route:
        # In a real app, we'd track the current stop index in the DB
        # For demo, we find the first non-delivered order
        for order in active_route.orders:
            if order.status != OrderStatus.DELIVERED:
                current_stop = order
                break
                
    return render_template("driver/mobile_view.html", vehicle=vehicle, route=active_route, stop=current_stop)


@main_bp.route("/model_comparison")
@login_required
def model_comparison():
    """ML Model comparison dashboard"""
    # Mock data for model comparison
    results = {
        "RandomForest": {
            "MAE": 12.5,
            "RMSE": 15.2,
            "R2": 0.85,
            "predictions": [100, 110, 105, 115, 120] * 6,
            "y_test": [102, 108, 106, 114, 122] * 6
        },
        "XGBoost": {
            "MAE": 10.2,
            "RMSE": 12.1,
            "R2": 0.92,
            "predictions": [101, 109, 106, 114, 121] * 6
        }
    }
    best_model = "XGBoost"
    return render_template("ml/model_comparison.html", results=results, best_model=best_model)


# API Endpoints
@main_bp.route("/api/stats")
@login_required
def get_stats():
    """Get dashboard statistics"""
    # Forecast data (from CSV - ML generated)
    forecast_path = os.path.join(DATA_DIR, "forecast.csv")
    total_demand_next_week = 0

    if os.path.exists(forecast_path):
        df_forecast = pd.read_csv(forecast_path)
        total_demand_next_week = int(df_forecast["predicted_volume"].sum())

    # Database queries
    active_vehicles = Vehicle.query.filter_by(status=VehicleStatus.AVAILABLE).count()
    total_vehicles = Vehicle.query.count()

    total_capacity = db.session.query(db.func.sum(Vehicle.capacity_kg)).scalar() or 0

    # Orders stats
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    total_orders_today = Order.query.filter(
        db.func.date(Order.created_at) == date.today()
    ).count()

    # Routes stats
    active_routes = Route.query.filter_by(status="Active").count()
    
    # ROI & Sustainability Calculations
    completed_routes = Route.query.filter_by(status="Completed").all()
    total_km_done = sum(r.total_distance_km or 0 for r in completed_routes)
    
    # Assumptions: 
    # 1. Manual routes are 30% longer than AI optimized routes
    # 2. Avg fuel efficiency is 8 km/L
    # 3. Fuel price is 270 PKR/L
    # 4. 1L Diesel = 2.68 kg CO2
    
    km_saved = total_km_done * 0.3
    fuel_saved_l = km_saved / 8
    pkr_saved = fuel_saved_l * 270
    co2_saved_kg = fuel_saved_l * 2.68

    return jsonify(
        {
            "forecast_volume": total_demand_next_week,
            "active_vehicles": active_vehicles,
            "total_vehicles": total_vehicles,
            "fleet_capacity_kg": int(total_capacity),
            "pending_orders": pending_orders,
            "total_orders_today": total_orders_today,
            "active_routes": active_routes,
            "pkr_saved": round(pkr_saved, 2),
            "co2_saved": round(co2_saved_kg, 2),
            "total_km_optimized": round(total_km_done, 2)
        }
    )


@main_bp.route("/api/forecast_chart")
@login_required
def get_forecast_chart():
    """Get forecast data for chart"""
    forecast_path = os.path.join(DATA_DIR, "forecast.csv")

    if not os.path.exists(forecast_path):
        return jsonify({"labels": [], "values": []})

    df = pd.read_csv(forecast_path)
    daily = df.groupby("date")["predicted_volume"].sum().reset_index()

    return jsonify(
        {"labels": daily["date"].tolist(), "values": daily["predicted_volume"].tolist()}
    )


@main_bp.route("/api/notifications")
@login_required
def get_notifications():
    """Get user notifications"""
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    return jsonify(
        [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "link": n.link,
            }
            for n in notifications
        ]
    )


@main_bp.route("/api/notifications/<int:notif_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notif_id)

    if notification.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({"success": True})


@main_bp.route("/api/performance_metrics")
@login_required
def get_performance_metrics():
    """Get performance metrics for analytics"""
    # Last 30 days metrics
    start_date = date.today() - timedelta(days=30)

    metrics = (
        PerformanceMetric.query.filter(
            PerformanceMetric.date >= start_date,
            PerformanceMetric.metric_type == "daily_orders",
        )
        .order_by(PerformanceMetric.date)
        .all()
    )

    # Group by date and region
    data_by_date = {}
    regions = set()

    for metric in metrics:
        date_str = metric.date.strftime("%Y-%m-%d")
        if date_str not in data_by_date:
            data_by_date[date_str] = {}
        data_by_date[date_str][metric.region] = metric.metric_value
        regions.add(metric.region)

    return jsonify(
        {
            "dates": sorted(data_by_date.keys()),
            "regions": sorted(list(regions)),
            "data": data_by_date,
        }
    )


@main_bp.route("/api/broadcast_location", methods=["POST"])
def broadcast_location():
    """Endpoint for simulation engine to broadcast location updates"""
    data = request.json
    # current_app is used to access the socketio instance attached to the app
    from flask import current_app

    current_app.socketio.emit("location_update", data, broadcast=True)
    return jsonify({"success": True})
