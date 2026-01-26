"""
PDF Report Generator
Generates professional PDF reports for routes, orders, and analytics
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import io

class PDFReportGenerator:
    """
    Generates various PDF reports for the logistics system
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=12,
            spaceAfter=6
        )
    
    def generate_route_report(self, route_data, filename='route_report.pdf'):
        """
        Generate PDF report for a specific route
        
        Args:
            route_data: Dict containing route information
            filename: Output PDF filename
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title
        title = Paragraph(f"Route Report - {route_data.get('vehicle_id', 'N/A')}", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Report metadata
        metadata = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Route ID:', route_data.get('route_id', 'N/A')],
            ['Vehicle ID:', route_data.get('vehicle_id', 'N/A')],
            ['Driver:', route_data.get('driver_name', 'Not Assigned')],
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 20))
        
        # Route Summary
        summary_heading = Paragraph("Route Summary", self.heading_style)
        elements.append(summary_heading)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Distance', f"{route_data.get('total_distance_m', 0) / 1000:.2f} km"],
            ['Total Load', f"{route_data.get('total_load_kg', 0)} kg"],
            ['Capacity Utilization', f"{route_data.get('utilization_pct', 0)}%"],
            ['Number of Stops', str(len(route_data.get('route', [])))],
            ['Estimated Duration', f"{route_data.get('estimated_duration', 0)} minutes"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Delivery Stops
        stops_heading = Paragraph("Delivery Stops", self.heading_style)
        elements.append(stops_heading)
        
        stops_data = [['Stop #', 'Order ID', 'Address', 'Coordinates']]
        
        for idx, stop in enumerate(route_data.get('route', []), 1):
            stops_data.append([
                str(idx),
                stop.get('order_id', 'N/A'),
                stop.get('address', 'N/A')[:40],  # Truncate long addresses
                f"{stop.get('lat', 0):.4f}, {stop.get('lon', 0):.4f}"
            ])
        
        stops_table = Table(stops_data, colWidths=[0.7*inch, 1.5*inch, 3*inch, 1.3*inch])
        stops_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(stops_table)
        elements.append(Spacer(1, 20))
        
        # Footer
        footer_text = Paragraph(
            "<i>Generated by LogisticsOS - Advanced Route Optimization Platform</i>",
            ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(Spacer(1, 30))
        elements.append(footer_text)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(pdf)
        
        return filename
    
    def generate_orders_report(self, orders, filename='orders_report.pdf'):
        """
        Generate PDF report for multiple orders
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        elements = []
        
        # Title
        title = Paragraph("Orders Report", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Summary
        summary_heading = Paragraph(f"Total Orders: {len(orders)}", self.heading_style)
        elements.append(summary_heading)
        elements.append(Spacer(1, 12))
        
        # Orders table
        table_data = [['Order ID', 'Customer', 'Address', 'Weight (kg)', 'Status']]
        
        for order in orders:
            table_data.append([
                order.order_id,
                order.customer_name[:20],  # Truncate
                order.delivery_address[:30],
                str(order.weight_kg),
                order.status
            ])
        
        orders_table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 2.2*inch, 0.9*inch, 1*inch])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(orders_table)
        
        # Build PDF
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        with open(filename, 'wb') as f:
            f.write(pdf)
        
        return filename
    
    def generate_analytics_report(self, analytics_data, filename='analytics_report.pdf'):
        """
        Generate PDF report for analytics and performance metrics
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        elements = []
        
        # Title
        title = Paragraph("Logistics Performance Analytics", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Period
        period = Paragraph(
            f"Report Period: {analytics_data.get('start_date', 'N/A')} to {analytics_data.get('end_date', 'N/A')}",
            self.styles['Normal']
        )
        elements.append(period)
        elements.append(Spacer(1, 20))
        
        # KPIs
        kpi_heading = Paragraph("Key Performance Indicators", self.heading_style)
        elements.append(kpi_heading)
        
        kpi_data = [
            ['Metric', 'Value', 'Change'],
            ['Total Orders', str(analytics_data.get('total_orders', 0)), '+12%'],
            ['Delivered Orders', str(analytics_data.get('delivered_orders', 0)), '+8%'],
            ['Total Distance (km)', f"{analytics_data.get('total_distance', 0):.2f}", '-5%'],
            ['Avg Delivery Time (hrs)', f"{analytics_data.get('avg_delivery_time', 0):.1f}", '-3%'],
            ['Fleet Utilization', f"{analytics_data.get('fleet_utilization', 0)}%", '+7%'],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(kpi_table)
        
        # Build PDF
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        with open(filename, 'wb') as f:
            f.write(pdf)
        
        return filename
