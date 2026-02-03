from app import app
from src.persistence.models import db, Order, OrderStatus
import random

with app.app_context():
    print("Deleting old LIVE orders...")
    Order.query.filter(Order.order_id.like("LIVE%")).delete(synchronize_session=False)
    
    print("Creating new mock orders...")
    for i in range(5):
        o = Order(
            order_id=f"LIVE-ORD-{random.randint(100, 999)}",
            customer_name="Demo Customer",
            delivery_address="Somewhere in Lahore",
            weight_kg=random.uniform(5, 20),
            volume_m3=random.uniform(0.1, 0.5),
            latitude=31.5204 + random.uniform(-0.02, 0.02),
            longitude=74.3587 + random.uniform(-0.02, 0.02),
            status=OrderStatus.PENDING # This should map to "Pending"
        )
        db.session.add(o)
    db.session.commit()
    print("Successfully created orders.")
