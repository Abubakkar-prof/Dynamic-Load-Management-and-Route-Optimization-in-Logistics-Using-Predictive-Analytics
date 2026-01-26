try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    pass

from flask import Flask, redirect, url_for, request
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

# Import configuration
from config import config

# Import database models
from src.persistence.models import db, User

# Import blueprints
from src.routes.auth_routes import auth_bp
from src.routes.main_routes import main_bp
from src.routes.orders_routes import orders_bp
from src.routes.fleet_routes import vehicles_bp, drivers_bp
from src.routes.tracking_routes import tracking_bp
from src.routes.delivery_prediction_routes import prediction_bp
from src.routes.bin_packing_routes import bin_packing_bp
from src.routes.scenario_analysis_routes import scenario_bp

# Try importing blueprints that might have external dependencies
try:
    from src.routes.multi_depot_routes import multi_depot_bp
except Exception as e:
    print(f"Warning: Multi-depot routes disabled: {e}")
    multi_depot_bp = None

try:
    from src.routes.optimization_routes import optimization_bp
except Exception as e:
    print(f"Warning: Optimization routes disabled: {e}")
    optimization_bp = None


def create_app(config_name="development"):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    app.socketio = socketio

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Initialize CSRF Protection
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # SocketIO event handlers
    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Client disconnected")

    @socketio.on("update_location")
    def handle_location_update(data):
        # Broadcast location update to all clients
        socketio.emit("location_update", data, broadcast=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(prediction_bp)
    if multi_depot_bp:
        app.register_blueprint(multi_depot_bp)
    app.register_blueprint(bin_packing_bp)
    app.register_blueprint(scenario_bp)
    if optimization_bp:
        app.register_blueprint(optimization_bp)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    @app.context_processor
    def inject_segment():
        endpoint = request.endpoint or ""
        segment = ""
        if endpoint.startswith("main.dashboard"):
            segment = "dashboard"
        elif endpoint.startswith("orders."):
            segment = "orders"
        elif endpoint.startswith("vehicles."):
            segment = "vehicles"
        elif endpoint.startswith("main.tracking"):
            segment = "telemetry"
        elif endpoint.startswith("main.delivery_prediction"):
            segment = "prediction"
        elif endpoint.startswith("main.bin_packing"):
            segment = "bin_packing"
        elif endpoint.startswith("main.multi_depot"):
            segment = "multi_depot"
        elif endpoint.startswith("main.scenario_analysis"):
            segment = "scenario"
        elif endpoint.startswith("main.model_comparison"):
            segment = "ml_comparison"
        return dict(segment=segment)

    # Root redirect
    @app.route("/")
    def root():
        return redirect(url_for("main.dashboard"))

    return app


# Create app instance
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    with app.app_context():
        # Create database tables
        db.create_all()

        # Initialize database with seed data
        from src.persistence.db_init import init_db

        try:
            init_db(app, db)
        except Exception as e:
            print(f"Database already initialized or error: {e}")

    # Run the application with SocketIO
    print("\n🚀 Server is starting...")
    print("📍 URL: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.\n")
    app.socketio.run(app, debug=True, host="0.0.0.0", port=5000, use_reloader=False)
