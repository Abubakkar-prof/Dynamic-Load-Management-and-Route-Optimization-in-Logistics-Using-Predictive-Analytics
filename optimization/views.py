from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from logistics.models import Order, Vehicle
from .services import LogisticsOptimizer
from .ml_services.prediction_service import DeliveryPredictor
from .ml_services.bin_packing_service import optimize_loading

class OptimizeRoutesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pending_orders = Order.objects.filter(status='Pending')
        available_vehicles = Vehicle.objects.filter(status='Available')
        
        if not pending_orders.exists():
             return Response({"status": "No pending orders"}, status=400)
             
        optimizer = LogisticsOptimizer(pending_orders, available_vehicles)
        solution = optimizer.optimize_routes()
        
        return Response(solution)

class PredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        predictor = DeliveryPredictor()
        try:
            result = predictor.predict(request.data)
            if result is None:
                return Response({"error": "Model not trained. Please train model first."}, status=400)
            
            hours = int(result // 60)
            minutes = int(result % 60)
            
            return Response({
                "predicted_delivery_time_minutes": round(result, 1),
                "predicted_delivery_time_formatted": f"{hours}h {minutes}m",
                "confidence": "high"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TrainModelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        predictor = DeliveryPredictor()
        try:
            result = predictor.train_model()
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class BinPackingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fleet = request.data.get('fleet', [])
        orders = request.data.get('orders', [])
        
        if not fleet:
            fleet = [
                {"vehicle_id": "TRK-001", "capacity_kg": 5000, "width": 2.5, "height": 2.5, "depth": 6.0},
                {"vehicle_id": "VAN-001", "capacity_kg": 1500, "width": 1.8, "height": 1.5, "depth": 3.0}
            ]
        
        if not orders:
             orders = [{"order_id": f"PKG-{i}", "weight_kg": 50, "package_width": 0.5, "package_height": 0.5, "package_depth": 0.5} for i in range(10)]

        try:
            result = optimize_loading(fleet, orders)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
