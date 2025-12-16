from flask import Flask, redirect, url_for
from flask_login import LoginManager
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
# Temporarily disabled due to OR-Tools DLL issue on Windows
# from src.routes.optimization_routes import optimization_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(drivers_bp)
    # Temporarily disabled due to OR-Tools DLL issue
    # app.register_blueprint(optimization_bp)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    
    # Root redirect
    @app.route('/')
    def root():
        return redirect(url_for('main.dashboard'))
    
    return app

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Initialize database with seed data
        from src.persistence.db_init import init_db
        try:
            init_db(app, db)
        except Exception as e:
            print(f"Database already initialized or error: {e}")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
