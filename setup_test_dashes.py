import sqlite3
import json
from datetime import datetime

DB_PATH = "instance/logistics.db"

def setup_dashes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Setting up dashes route...")
    
    # Get V001 ID
    cursor.execute("SELECT id FROM vehicles WHERE vehicle_id = 'V001'")
    row = cursor.fetchone()
    if not row:
        print("V001 not found")
        return
    vid = row[0]
    
    # Cancel old active routes for this vehicle
    cursor.execute("UPDATE routes SET status = 'Cancelled' WHERE vehicle_id = ? AND status = 'Active'", (vid,))
    
    # Create 3 distant locations
    steps = [
        {"order_id": "ORD-N1", "latitude": 31.55, "longitude": 74.39},
        {"order_id": "ORD-N2", "latitude": 31.57, "longitude": 74.41},
        {"order_id": "ORD-N3", "latitude": 31.59, "longitude": 74.43}
    ]
    
    rid = f"RT-NEON-{datetime.now().strftime('%H%M%S')}"
    cursor.execute("""
        INSERT INTO routes (route_id, vehicle_id, status, route_json, date)
        VALUES (?, ?, 'Active', ?, ?)
    """, (rid, vid, json.dumps(steps), datetime.now().strftime('%Y-%m-%d')))
    
    # Reset vehicle location to depot
    cursor.execute("UPDATE vehicles SET current_location_lat = 31.5204, current_location_lon = 74.3587, status = 'On Route' WHERE id = ?", (vid,))
    
    conn.commit()
    conn.close()
    print(f"Created Route {rid} with distinct steps.")

if __name__ == "__main__":
    setup_dashes()
