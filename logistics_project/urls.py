from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from logistics.views import VehicleViewSet, DriverViewSet, OrderViewSet, RouteViewSet, StatsView, ForecastChartView
from optimization.views import OptimizeRoutesView, PredictionView, TrainModelView, BinPackingView
from core.views import (
    landing_page, login_view, register_view, logout_view,
    dashboard, order_list_view, order_create_view, 
    vehicle_list_view, vehicle_create_view, prediction_view, 
    bin_packing_view, telemetry_view, ml_model_comparison_view,
    multi_depot_view
)
from core.export_views import (
    export_orders_excel, export_orders_pdf,
    export_vehicles_excel, export_analytics_excel
)

# DRF Router for API endpoints ONLY
router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='api-vehicle')
router.register(r'drivers', DriverViewSet, basename='api-driver')
router.register(r'orders', OrderViewSet, basename='api-order')
router.register(r'routes', RouteViewSet, basename='api-route')

urlpatterns = [
    # Authentication
    path("", landing_page, name='landing'),
    path("login/", login_view, name='login'),
    path("register/", register_view, name='register'),
    path("logout/", logout_view, name='logout'),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # Main App
    path("dashboard/", dashboard, name='dashboard'),
    
    # UI Routes (Protected) - MUST come BEFORE api/ to avoid conflicts
    path("orders/", order_list_view, name='order-list'),
    path("orders/new/", order_create_view, name='order-create'),
    path("vehicles/", vehicle_list_view, name='vehicle-list'),
    path("vehicles/new/", vehicle_create_view, name='vehicle-create'),
    path("forecasting/", prediction_view, name='prediction'),
    path("optimizer/", bin_packing_view, name='bin-packing'),
    path("telemetry/", telemetry_view, name='telemetry'),
    path("ml-comparison/", ml_model_comparison_view, name='ml-comparison'),
    path("multi-depot/", multi_depot_view, name='multi-depot'),

    # API Routes (For AJAX/Fetch calls) - Router includes /api/vehicles/, /api/orders/, etc.
    path("api/stats", StatsView.as_view(), name='stats'),
    path("api/forecast_chart", ForecastChartView.as_view(), name='forecast_chart'),
    path("api/predict-delivery/", PredictionView.as_view(), name='predict-delivery'),
    path("api/train-model/", TrainModelView.as_view(), name='train-model'),
    path("api/bin-packing/", BinPackingView.as_view(), name='bin-packing-api'),
    path("api/optimize/", OptimizeRoutesView.as_view(), name='optimize'),
    path("api/", include(router.urls)),  # This creates /api/vehicles/, /api/orders/, etc.
    
    # Export Routes
    path("export/orders/excel/", export_orders_excel, name='export-orders-excel'),
    path("export/orders/pdf/", export_orders_pdf, name='export-orders-pdf'),
    path("export/vehicles/excel/", export_vehicles_excel, name='export-vehicles-excel'),
    path("export/analytics/excel/", export_analytics_excel, name='export-analytics-excel'),
    
    path("api-auth/", include("rest_framework.urls")), # DRF browsable API login
]
