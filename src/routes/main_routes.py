from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from src.persistence.models import db, Vehicle, Order, Route, Driver, Notification, PerformanceMetric, VehicleStatus, OrderStatus
from datetime import date, datetime, timedelta
import pandas as pd
import os

main_bp = Blueprint('main', __name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')

@main_bp.route('/')
@login_required
def index():
    return render_template('dashboard.html', user=current_user)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# API Endpoints
@main_bp.route('/api/stats')
@login_required
def get_stats():
    """Get dashboard statistics"""
    # Forecast data (from CSV - ML generated)
    forecast_path = os.path.join(DATA_DIR, 'forecast.csv')
    total_demand_next_week = 0
    
    if os.path.exists(forecast_path):
        df_forecast = pd.read_csv(forecast_path)
        total_demand_next_week = int(df_forecast['predicted_volume'].sum())
    
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
    active_routes = Route.query.filter_by(status='Active').count()
    
    return jsonify({
        'forecast_volume': total_demand_next_week,
        'active_vehicles': active_vehicles,
        'total_vehicles': total_vehicles,
        'fleet_capacity_kg': int(total_capacity),
        'pending_orders': pending_orders,
        'total_orders_today': total_orders_today,
        'active_routes': active_routes
    })

@main_bp.route('/api/forecast_chart')
@login_required
def get_forecast_chart():
    """Get forecast data for chart"""
    forecast_path = os.path.join(DATA_DIR, 'forecast.csv')
    
    if not os.path.exists(forecast_path):
        return jsonify({'labels': [], 'values': []})
    
    df = pd.read_csv(forecast_path)
    daily = df.groupby('date')['predicted_volume'].sum().reset_index()
    
    return jsonify({
        'labels': daily['date'].tolist(),
        'values': daily['predicted_volume'].tolist()
    })

@main_bp.route('/api/notifications')
@login_required
def get_notifications():
    """Get user notifications"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'link': n.link
    } for n in notifications])

@main_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notif_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@main_bp.route('/api/performance_metrics')
@login_required
def get_performance_metrics():
    """Get performance metrics for analytics"""
    # Last 30 days metrics
    start_date = date.today() - timedelta(days=30)
    
    metrics = PerformanceMetric.query.filter(
        PerformanceMetric.date >= start_date,
        PerformanceMetric.metric_type == 'daily_orders'
    ).order_by(PerformanceMetric.date).all()
    
    # Group by date and region
    data_by_date = {}
    regions = set()
    
    for metric in metrics:
        date_str = metric.date.strftime('%Y-%m-%d')
        if date_str not in data_by_date:
            data_by_date[date_str] = {}
        data_by_date[date_str][metric.region] = metric.metric_value
        regions.add(metric.region)
    
    return jsonify({
        'dates': sorted(data_by_date.keys()),
        'regions': sorted(list(regions)),
        'data': data_by_date
    })
