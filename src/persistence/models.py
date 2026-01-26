from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()


# Enums for status tracking
class OrderStatus(enum.Enum):
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    FAILED = "Failed"


class VehicleStatus(enum.Enum):
    AVAILABLE = "Available"
    ON_ROUTE = "On Route"
    MAINTENANCE = "Maintenance"
    INACTIVE = "Inactive"


class DriverStatus(enum.Enum):
    AVAILABLE = "Available"
    ON_DUTY = "On Duty"
    OFF_DUTY = "Off Duty"
    ON_LEAVE = "On Leave"


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    DRIVER = "driver"
    DISPATCHER = "dispatcher"


# User Model
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.DRIVER, nullable=False)
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    driver_profile = db.relationship("Driver", backref="user", uselist=False, lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# Driver Model
class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_expiry = db.Column(db.Date)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    status = db.Column(db.Enum(DriverStatus), default=DriverStatus.AVAILABLE)
    rating = db.Column(db.Float, default=5.0)
    total_deliveries = db.Column(db.Integer, default=0)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    routes = db.relationship("Route", backref="driver", lazy=True)

    def __repr__(self):
        return f"<Driver {self.license_number}>"


# Vehicle Model
class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    license_plate = db.Column(db.String(20), unique=True)
    capacity_kg = db.Column(db.Float, nullable=False)
    capacity_vol = db.Column(db.Float, nullable=False)
    fuel_type = db.Column(db.String(20))
    status = db.Column(db.Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    current_location_lat = db.Column(db.Float)
    current_location_lon = db.Column(db.Float)
    last_maintenance = db.Column(db.Date)
    next_maintenance = db.Column(db.Date)
    mileage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    drivers = db.relationship("Driver", backref="vehicle", lazy=True)
    routes = db.relationship("Route", backref="vehicle", lazy=True)
    maintenance_records = db.relationship(
        "MaintenanceRecord", backref="vehicle", lazy=True
    )

    def __repr__(self):
        return f"<Vehicle {self.vehicle_id}>"


# Order Model
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    pickup_address = db.Column(db.Text)
    delivery_address = db.Column(db.Text, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    volume_m3 = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    deadline_hour = db.Column(db.Integer)
    deadline_date = db.Column(db.Date)
    region = db.Column(db.String(50))
    priority = db.Column(db.Integer, default=1)  # 1=Low, 2=Medium, 3=High, 4=Urgent
    # Time Window Constraints (CVRPTW)
    time_window_start = db.Column(db.Integer, default=9)  # Start Hour (e.g. 9 for 9 AM)
    time_window_end = db.Column(db.Integer, default=17)  # End Hour (e.g. 17 for 5 PM)
    service_time = db.Column(db.Integer, default=15)  # Service duration in minutes
    status = db.Column(
        db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"))
    delivery_notes = db.Column(db.Text)
    actual_delivery_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    tracking_updates = db.relationship(
        "TrackingUpdate", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.order_id}>"


# Route Model
class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    total_distance_m = db.Column(db.Float)
    total_distance_km = db.Column(db.Float)
    total_duration_min = db.Column(db.Float)
    total_load_kg = db.Column(db.Float)
    capacity_kg = db.Column(db.Float)
    utilization_pct = db.Column(db.Float)
    route_json = db.Column(db.Text)  # JSON string of route steps
    status = db.Column(
        db.String(20), default="Planned"
    )  # Planned, Active, Completed, Cancelled
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    orders = db.relationship("Order", backref="route", lazy=True)

    def __repr__(self):
        return f"<Route {self.route_id}>"


# Tracking Update Model
class TrackingUpdate(db.Model):
    __tablename__ = "tracking_updates"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    location_lat = db.Column(db.Float)
    location_lon = db.Column(db.Float)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"<TrackingUpdate {self.id} - {self.status}>"


# Maintenance Record Model
class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    maintenance_type = db.Column(
        db.String(100), nullable=False
    )  # Oil Change, Tire Rotation, etc.
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    performed_by = db.Column(db.String(100))
    mileage_at_service = db.Column(db.Float)
    maintenance_date = db.Column(db.Date, nullable=False)
    next_service_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MaintenanceRecord {self.id} - {self.maintenance_type}>"


# Notification Model
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # info, warning, error, success
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref="notifications", lazy=True)

    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"


# Analytics/Performance Metrics Model
class PerformanceMetric(db.Model):
    __tablename__ = "performance_metrics"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    metric_type = db.Column(
        db.String(50), nullable=False
    )  # daily_orders, delivery_rate, etc.
    metric_value = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(50))
    additional_data = db.Column(db.Text)  # JSON for flexible storage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PerformanceMetric {self.date} - {self.metric_type}>"
