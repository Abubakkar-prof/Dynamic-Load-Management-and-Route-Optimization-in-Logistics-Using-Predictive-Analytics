from django.core.management.base import BaseCommand
from logistics.models import Vehicle, Order, Route
from core.models import User
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create sample vehicles
        vehicle_types = ['Van', 'Truck', 'Pickup', 'Semi-Trailer']
        statuses = ['Available', 'On Route', 'Maintenance']
        
        vehicles_data = [
            {'vehicle_id': 'VAN-001', 'type': 'Van', 'capacity_kg': 1500, 'capacity_vol': 10},
            {'vehicle_id': 'VAN-002', 'type': 'Van', 'capacity_kg': 1500, 'capacity_vol': 10},
            {'vehicle_id': 'TRK-001', 'type': 'Truck', 'capacity_kg': 5000, 'capacity_vol': 30},
            {'vehicle_id': 'TRK-002', 'type': 'Truck', 'capacity_kg': 5000, 'capacity_vol': 30},
            {'vehicle_id': 'TRK-003', 'type': 'Truck', 'capacity_kg': 5000, 'capacity_vol': 30},
            {'vehicle_id': 'PKP-001', 'type': 'Pickup', 'capacity_kg': 2000, 'capacity_vol': 15},
            {'vehicle_id': 'PKP-002', 'type': 'Pickup', 'capacity_kg': 2000, 'capacity_vol': 15},
            {'vehicle_id': 'SMI-001', 'type': 'Semi-Trailer', 'capacity_kg': 20000, 'capacity_vol': 80},
        ]
        
        for v_data in vehicles_data:
            Vehicle.objects.get_or_create(
                vehicle_id=v_data['vehicle_id'],
                defaults={
                    'type': v_data['type'],
                    'capacity_kg': v_data['capacity_kg'],
                    'capacity_vol': v_data['capacity_vol'],
                    'status': random.choice(statuses),
                    'current_location_lat': 31.5204 + random.uniform(-0.1, 0.1),
                    'current_location_lon': 74.3587 + random.uniform(-0.1, 0.1),
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(vehicles_data)} vehicles'))
        
        # Create sample orders
        customers = [
            'ABC Corporation', 'XYZ Logistics', 'Global Traders Inc', 
            'Metro Supplies', 'Prime Distributors', 'Elite Commerce',
            'Urban Retail Co', 'Coastal Imports', 'Summit Exports',
            'Valley Wholesale', 'Peak Trading', 'Horizon Goods'
        ]
        
        addresses = [
            'Gulberg, Lahore', 'DHA Phase 5, Karachi', 'F-7, Islamabad',
            'Johar Town, Lahore', 'Clifton, Karachi', 'Bahria Town, Rawalpindi',
            'Model Town, Lahore', 'PECHS, Karachi', 'G-11, Islamabad',
            'Cantt, Lahore', 'Saddar, Karachi', 'Blue Area, Islamabad'
        ]
        
        order_statuses = ['Pending', 'Assigned', 'In Transit', 'Delivered']
        
        for i in range(50):
            Order.objects.get_or_create(
                order_id=f'ORD-{2000+i}',
                defaults={
                    'customer_name': random.choice(customers),
                    'delivery_address': random.choice(addresses),
                    'latitude': 31.5204 + random.uniform(-0.5, 0.5),
                    'longitude': 74.3587 + random.uniform(-0.5, 0.5),
                    'weight_kg': random.randint(10, 500),
                    'volume_m3': round(random.uniform(0.5, 10), 2),
                    'status': random.choice(order_statuses),
                    'time_window_start': random.randint(8, 14),
                    'time_window_end': random.randint(15, 20),
                    'service_time': random.randint(10, 30),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created 50 sample orders'))
        self.stdout.write(self.style.SUCCESS('Sample data creation complete!'))
