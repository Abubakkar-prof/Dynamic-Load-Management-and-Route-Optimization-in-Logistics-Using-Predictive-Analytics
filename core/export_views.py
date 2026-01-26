"""
Export Views
Handles PDF and Excel export functionality
"""
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from logistics.models import Order, Vehicle
from core.pdf_generator import PDFReportGenerator
from core.excel_exporter import ExcelExporter
import os
from datetime import datetime

@login_required
def export_orders_excel(request):
    """Export all orders to Excel"""
    try:
        orders = Order.objects.all()
        exporter = ExcelExporter()
        
        filename = f'orders_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = exporter.export_orders(orders, filename)
        
        with open(filepath, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clean up file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return response
    except Exception as e:
        return HttpResponse(f"Error exporting orders: {str(e)}", status=500)

@login_required
def export_orders_pdf(request):
    """Export all orders to PDF"""
    try:
        orders = Order.objects.all()
        generator = PDFReportGenerator()
        
        filename = f'orders_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        filepath = generator.generate_orders_report(orders, filename)
        
        response = FileResponse(
            open(filepath, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

@login_required
def export_vehicles_excel(request):
    """Export all vehicles to Excel"""
    try:
        vehicles = Vehicle.objects.all()
        exporter = ExcelExporter()
        
        filename = f'vehicles_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = exporter.export_vehicles(vehicles, filename)
        
        with open(filepath, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return response
    except Exception as e:
        return HttpResponse(f"Error exporting vehicles: {str(e)}", status=500)

@login_required
def export_analytics_excel(request):
    """Export analytics to Excel"""
    try:
        # Gather analytics data
        from logistics.models import Order, Vehicle
        
        analytics_data = {
            'total_orders': Order.objects.count(),
            'delivered_orders': Order.objects.filter(status='Delivered').count(),
            'pending_orders': Order.objects.filter(status='Pending').count(),
            'total_vehicles': Vehicle.objects.count(),
            'active_vehicles': Vehicle.objects.filter(status='On Route').count(),
            'total_distance': 0,  # Calculate from routes
            'avg_delivery_time': 0,  # Calculate from completed orders
            'fleet_utilization': 0,  # Calculate from vehicle usage
        }
        
        exporter = ExcelExporter()
        filename = f'analytics_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = exporter.export_analytics(analytics_data, filename)
        
        with open(filepath, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return response
    except Exception as e:
        return HttpResponse(f"Error exporting analytics: {str(e)}", status=500)
