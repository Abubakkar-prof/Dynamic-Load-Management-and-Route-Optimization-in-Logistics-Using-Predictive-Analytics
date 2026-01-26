from rest_framework import viewsets
from logistics.models import Vehicle, Driver, Order, Route
from logistics.serializers import VehicleSerializer, DriverSerializer, OrderSerializer, RouteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_orders = Order.objects.filter(status='Pending').count()
        total_vehicles = Vehicle.objects.count()
        active_vehicles = Vehicle.objects.filter(status='On Route').count()
        
        return Response({
            'forecast_volume': 1250, # Mocked for demo
            'active_vehicles': active_vehicles,
            'fleet_capacity_kg': sum(v.capacity_kg for v in Vehicle.objects.all()),
            'pending_orders': pending_orders,
            'total_orders_today': Order.objects.count(), # Simplified
            'total_vehicles': total_vehicles
        })

class ForecastChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'values': [65, 59, 80, 81, 56, 55, 40]
        })

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
