import pandas as pd
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from faker import Faker
import random

fake = Faker()

def init_db(app, db):
    """Initialize database with tables and seed data"""
    from src.persistence.models import (
        User, Driver, Vehicle, Order, Route, 
        MaintenanceRecord, Notification, PerformanceMetric,
        UserRole, VehicleStatus, DriverStatus, OrderStatus
    )
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
    
    with app.app_context():
        print("Creating Database Tables...")
        db.create_all()
        
        # === USERS ===
        if User.query.count() == 0:
            print("Creating default users...")
            users = [
                User(
                    username='admin',
                    email='admin@logistics.com',
                    password=generate_password_hash('admin123'),
                    role=UserRole.ADMIN,
                    full_name='System Administrator',
                    phone='+92-300-1234567',
                    is_active=True
                ),
                User(
                    username='manager',
                    email='manager@logistics.com',
                    password=generate_password_hash('manager123'),
                    role=UserRole.MANAGER,
                    full_name='Fleet Manager',
                    phone='+92-300-2345678',
                    is_active=True
                ),
                User(
                    username='dispatcher',
                    email='dispatcher@logistics.com',
                    password=generate_password_hash('dispatch123'),
                    role=UserRole.DISPATCHER,
                    full_name='Route Dispatcher',
                    phone='+92-300-3456789',
                    is_active=True
                )
            ]
            
            # Create driver users
            for i in range(1, 11):
                users.append(User(
                    username=f'driver{i}',
                    email=f'driver{i}@logistics.com',
                    password=generate_password_hash('driver123'),
                    role=UserRole.DRIVER,
                    full_name=fake.name(),
                    phone=fake.phone_number()[:15],
                    is_active=True
                ))
            
            db.session.add_all(users)
            db.session.commit()
            print(f"Created {len(users)} users")
        
        # === VEHICLES ===
        if Vehicle.query.count() == 0:
            print("Importing Fleet from CSV...")
            fleet_path = os.path.join(DATA_DIR, 'fleet_info.csv')
            
            if os.path.exists(fleet_path):
                df_fleet = pd.read_csv(fleet_path)
                for idx, row in df_fleet.iterrows():
                    v = Vehicle(
                        vehicle_id=row['vehicle_id'],
                        type=row['type'],
                        make='Toyota' if row['type'] == 'Van' else 'Isuzu',
                        model='Hiace' if row['type'] == 'Van' else 'NPR',
                        year=random.randint(2018, 2023),
                        license_plate=f'LHR-{random.randint(1000, 9999)}',
                        capacity_kg=row['capacity_kg'],
                        capacity_vol=row['capacity_vol'],
                        fuel_type='Diesel',
                        status=VehicleStatus.AVAILABLE,
                        current_location_lat=31.5204,
                        current_location_lon=74.3587,
                        last_maintenance=date.today() - timedelta(days=random.randint(10, 90)),
                        next_maintenance=date.today() + timedelta(days=random.randint(30, 90)),
                        mileage=random.uniform(5000, 50000)
                    )
                    db.session.add(v)
                db.session.commit()
                print(f"Imported {len(df_fleet)} vehicles")
        
        # === DRIVERS ===
        if Driver.query.count() == 0:
            print("Creating driver profiles...")
            driver_users = User.query.filter_by(role=UserRole.DRIVER).all()
            vehicles = Vehicle.query.all()
            
            for idx, user in enumerate(driver_users):
                driver = Driver(
                    user_id=user.id,
                    license_number=f'DL-{random.randint(100000, 999999)}',
                    license_expiry=date.today() + timedelta(days=random.randint(365, 1825)),
                    vehicle_id=vehicles[idx].id if idx < len(vehicles) else None,
                    status=DriverStatus.AVAILABLE,
                    rating=round(random.uniform(4.0, 5.0), 1),
                    total_deliveries=random.randint(50, 500),
                    address=fake.address()[:100],
                    emergency_contact=fake.phone_number()[:15],
                    hire_date=date.today() - timedelta(days=random.randint(365, 1825))
                )
                db.session.add(driver)
            db.session.commit()
            print(f"Created {len(driver_users)} driver profiles")
        
        # === ORDERS ===
        if Order.query.count() == 0:
            print("Importing Orders from CSV...")
            orders_path = os.path.join(DATA_DIR, 'orders.csv')
            
            if os.path.exists(orders_path):
                df_orders = pd.read_csv(orders_path)
                for _, row in df_orders.iterrows():
                    o = Order(
                        order_id=row['order_id'],
                        customer_name=fake.name(),
                        customer_phone=fake.phone_number()[:15],
                        customer_email=fake.email(),
                        pickup_address='Main Warehouse, Lahore',
                        delivery_address=fake.address()[:150],
                        weight_kg=row['weight_kg'],
                        volume_m3=row['volume_m3'],
                        latitude=row['latitude'],
                        longitude=row['longitude'],
                        deadline_hour=row['deadline_hour'],
                        deadline_date=date.today(),
                        region=row['region'],
                        priority=random.randint(1, 4),
                        status=OrderStatus.PENDING
                    )
                    db.session.add(o)
                db.session.commit()
                print(f"Imported {len(df_orders)} orders")
        
        # === NOTIFICATIONS ===
        if Notification.query.count() == 0:
            print("Creating sample notifications...")
            admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
            if admin_user:
                notifications = [
                    Notification(
                        user_id=admin_user.id,
                        title='System Initialized',
                        message='Logistics Management System has been successfully initialized.',
                        type='success',
                        is_read=False
                    ),
                    Notification(
                        user_id=admin_user.id,
                        title='High Demand Alert',
                        message='Predicted 20% increase in demand for North region tomorrow.',
                        type='warning',
                        is_read=False
                    )
                ]
                db.session.add_all(notifications)
                db.session.commit()
        
        # === PERFORMANCE METRICS ===
        if PerformanceMetric.query.count() == 0:
            print("Creating performance metrics...")
            regions = ['North', 'South', 'East', 'West', 'Central']
            for i in range(30):
                metric_date = date.today() - timedelta(days=i)
                for region in regions:
                    metric = PerformanceMetric(
                        date=metric_date,
                        metric_type='daily_orders',
                        metric_value=random.randint(30, 80),
                        region=region
                    )
                    db.session.add(metric)
            db.session.commit()
            print("Created performance metrics for last 30 days")
        
        print("\n✅ Database Initialized Successfully!")
        print("\nDefault Login Credentials:")
        print("Admin: username='admin', password='admin123'")
        print("Manager: username='manager', password='manager123'")
        print("Dispatcher: username='dispatcher', password='dispatch123'")
        print("Driver: username='driver1', password='driver123'")

if __name__ == "__main__":
    from app import app, db
    init_db(app, db)
