
print("Step 1: flask", flush=True)
from flask import Flask, redirect, url_for
print("Step 2: flask_login", flush=True)
from flask_login import LoginManager
print("Step 3: flask_socketio", flush=True)
from flask_socketio import SocketIO
print("Step 4: config", flush=True)
from config import config
print("Step 5: models", flush=True)
from src.persistence.models import db, User
print("Step 6: auth_routes", flush=True)
from src.routes.auth_routes import auth_bp
print("Step 7: main_routes", flush=True)
from src.routes.main_routes import main_bp
print("Step 8: orders_routes", flush=True)
from src.routes.orders_routes import orders_bp
print("Step 9: fleet_routes", flush=True)
from src.routes.fleet_routes import vehicles_bp, drivers_bp
print("Step 10: tracking_routes", flush=True)
from src.routes.tracking_routes import tracking_bp
print("Step 11: delivery_prediction_routes", flush=True)
from src.routes.delivery_prediction_routes import prediction_bp
print("Step 12: multi_depot_routes", flush=True)
from src.routes.multi_depot_routes import multi_depot_bp
print("Step 13: bin_packing_routes", flush=True)
from src.routes.bin_packing_routes import bin_packing_bp
print("Step 14: scenario_analysis_routes", flush=True)
from src.routes.scenario_analysis_routes import scenario_bp
print("Step 15: optimization_routes", flush=True)
try:
    from src.routes.optimization_routes import optimization_bp
except Exception as e:
    print(f"Failed optim: {e}")

print("Done imports", flush=True)
