from django.db import models
from django.conf import settings
from core.models import User

class Depot(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Available"
        ON_ROUTE = "On Route"
        MAINTENANCE = "Maintenance"
        INACTIVE = "Inactive"

    vehicle_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50)
    capacity_kg = models.FloatField()
    capacity_vol = models.FloatField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    current_location_lat = models.FloatField(null=True, blank=True)
    current_location_lon = models.FloatField(null=True, blank=True)
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    
    def __str__(self):
        return self.vehicle_id

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    current_status = models.CharField(max_length=20, default='Available')
    
    def __str__(self):
        return self.license_number

class Route(models.Model):
    route_id = models.CharField(max_length=50, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    total_distance_km = models.FloatField(default=0)
    route_json = models.TextField(help_text="JSON payload of the route path")
    
    def __str__(self):
        return self.route_id

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        ASSIGNED = "Assigned"
        DELIVERED = "Delivered"
        CANCELLED = "Cancelled"

    order_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    delivery_address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    weight_kg = models.FloatField()
    volume_m3 = models.FloatField()
    
    # Time Windows (New Enterprise Feature)
    time_window_start = models.IntegerField(default=9, help_text="Start hour (0-23)")
    time_window_end = models.IntegerField(default=17, help_text="End hour (0-23)")
    service_time = models.IntegerField(default=15, help_text="Minutes to unload")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    def __str__(self):
        return self.order_id
