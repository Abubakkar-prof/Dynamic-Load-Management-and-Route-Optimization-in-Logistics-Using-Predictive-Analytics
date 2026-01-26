"""
Email and SMS Notification Service
Sends notifications for order updates, delivery status, etc.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class NotificationService:
    """
    Handles all notification sending (Email and SMS)
    """
    
    @staticmethod
    def send_order_created_notification(order):
        """Send notification when order is created"""
        subject = f'Order Confirmation - {order.order_id}'
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #3b82f6;">Order Confirmed!</h2>
            <p>Dear {order.customer_name},</p>
            <p>Your order has been successfully created and is being processed.</p>
            
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Order Details:</h3>
                <p><strong>Order ID:</strong> {order.order_id}</p>
                <p><strong>Delivery Address:</strong> {order.delivery_address}</p>
                <p><strong>Weight:</strong> {order.weight_kg} kg</p>
                <p><strong>Status:</strong> {order.status}</p>
            </div>
            
            <p>You will receive updates as your order progresses.</p>
            <p style="color: #6b7280; font-size: 12px;">This is an automated message from LogisticsOS</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer_email] if hasattr(order, 'customer_email') else [],
                html_message=html_message,
                fail_silently=True,
            )
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    @staticmethod
    def send_status_update_notification(order, old_status, new_status):
        """Send notification when order status changes"""
        subject = f'Order Update - {order.order_id}'
        
        status_messages = {
            'Pending': 'Your order is pending assignment.',
            'Assigned': 'Your order has been assigned to a driver.',
            'In Transit': 'Your order is on the way!',
            'Delivered': 'Your order has been delivered successfully!',
            'Failed': 'There was an issue with your delivery. We will contact you shortly.'
        }
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #3b82f6;">Order Status Update</h2>
            <p>Dear {order.customer_name},</p>
            
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Status Changed:</h3>
                <p><strong>Order ID:</strong> {order.order_id}</p>
                <p><strong>Previous Status:</strong> <span style="color: #6b7280;">{old_status}</span></p>
                <p><strong>Current Status:</strong> <span style="color: #10b981; font-weight: bold;">{new_status}</span></p>
            </div>
            
            <p>{status_messages.get(new_status, 'Your order status has been updated.')}</p>
            
            <p style="color: #6b7280; font-size: 12px;">Track your order at: http://localhost:8000/orders/</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer_email] if hasattr(order, 'customer_email') else [],
                html_message=html_message,
                fail_silently=True,
            )
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    @staticmethod
    def send_delivery_notification(order, driver_name=None):
        """Send notification when order is delivered"""
        subject = f'Delivery Confirmation - {order.order_id}'
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #10b981;">✓ Delivered Successfully!</h2>
            <p>Dear {order.customer_name},</p>
            <p>Your order has been delivered successfully.</p>
            
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Delivery Details:</h3>
                <p><strong>Order ID:</strong> {order.order_id}</p>
                <p><strong>Delivered To:</strong> {order.delivery_address}</p>
                {f'<p><strong>Driver:</strong> {driver_name}</p>' if driver_name else ''}
            </div>
            
            <p>Thank you for choosing LogisticsOS!</p>
            <p style="color: #6b7280; font-size: 12px;">For any queries, please contact our support team.</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer_email] if hasattr(order, 'customer_email') else [],
                html_message=html_message,
                fail_silently=True,
            )
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    @staticmethod
    def send_route_assignment_notification(driver_email, route_details):
        """Send notification to driver when route is assigned"""
        subject = f'New Route Assignment - {route_details.get("vehicle_id", "N/A")}'
        
        orders_list = '\n'.join([
            f'<li>{order["order_id"]} - {order["address"]}</li>'
            for order in route_details.get('orders', [])
        ])
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #3b82f6;">New Route Assignment</h2>
            <p>You have been assigned a new delivery route.</p>
            
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Route Details:</h3>
                <p><strong>Vehicle:</strong> {route_details.get('vehicle_id', 'N/A')}</p>
                <p><strong>Total Orders:</strong> {len(route_details.get('orders', []))}</p>
                <p><strong>Total Distance:</strong> {route_details.get('total_distance', 0)} km</p>
                
                <h4>Delivery Stops:</h4>
                <ol style="padding-left: 20px;">
                    {orders_list}
                </ol>
            </div>
            
            <p>Please check the dashboard for detailed route information.</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[driver_email],
                html_message=html_message,
                fail_silently=True,
            )
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False


# SMS Service (Optional - requires Twilio)
class SMSService:
    """
    SMS notification service using Twilio
    """
    
    @staticmethod
    def send_sms(phone_number, message):
        """
        Send SMS notification
        Requires: pip install twilio
        """
        try:
            from twilio.rest import Client
            
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            from_number = settings.TWILIO_PHONE_NUMBER
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            
            return True
        except ImportError:
            print("Twilio not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            print(f"SMS failed: {e}")
            return False
    
    @staticmethod
    def send_delivery_sms(order):
        """Send SMS for delivery update"""
        message = f"LogisticsOS: Your order {order.order_id} status: {order.status}. Track at: http://localhost:8000/orders/"
        
        if hasattr(order, 'customer_phone'):
            return SMSService.send_sms(order.customer_phone, message)
        return False
