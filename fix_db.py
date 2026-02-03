from app import app
from src.persistence.models import db, Vehicle, VehicleStatus, Route
import sys

with app.app_context():
    print("Fixing database state...")
    try:
        # Finish all active routes to start fresh
        active = Route.query.filter_by(status="Active").all()
        for r in active:
            r.status = "Cancelled"
            
        # Reset vehicles
        for v in Vehicle.query.all():
            v.status = VehicleStatus.AVAILABLE
            
        db.session.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
