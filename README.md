# 🚚 Logistics AI - Advanced Full-Stack Route Optimization Platform

An enterprise-grade logistics management system with AI-powered demand forecasting and intelligent route optimization using Google OR-Tools.

## 🌟 Features

### Core Functionality
- **🤖 AI-Powered Demand Forecasting** - Machine Learning models (RandomForest, XGBoost) for accurate demand prediction
- **🗺️ Intelligent Route Optimization** - Google OR-Tools CVRP solver for optimal vehicle routing
- **📊 Real-time Dashboard** - Live analytics with interactive charts and maps
- **📦 Order Management** - Complete CRUD operations with status tracking
- **🚛 Fleet Management** - Vehicle tracking, maintenance records, and utilization metrics
- **👤 Driver Management** - Driver profiles, ratings, and assignment tracking
- **📈 Performance Analytics** - Historical metrics and performance reports
- **🔔 Notification System** - Real-time alerts and updates

### Technical Features
- **🔐 Authentication & Authorization** - Role-based access control (Admin, Manager, Dispatcher, Driver)
- **🗄️ Advanced Database Models** - SQLAlchemy ORM with comprehensive relationships
- **🎨 Modern UI/UX** - Responsive dark-themed interface with Bootstrap 5
- **📱 RESTful API** - Well-structured API endpoints for all operations
- **🧪 Testing Suite** - Comprehensive pytest test coverage
- **⚙️ Configuration Management** - Environment-based config (Development/Production)

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation

### Machine Learning & Optimization
- **scikit-learn** - Machine learning algorithms
- **XGBoost** - Gradient boosting for demand forecasting
- **Prophet** - Time series forecasting
- **Google OR-Tools** - Constraint programming and route optimization

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive data visualization
- **Leaflet.js** - Interactive maps
- **Font Awesome** - Icon library

### Database
- **SQLite** - Default database (Development)
- **PostgreSQL** - Production-ready option

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SK
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/Mac

# Edit .env with your configuration
```

### 5. Run Setup Script
```bash
python setup.py
```

This will:
- Generate synthetic data (fleet, orders, historical demand)
- Train the ML demand forecasting model
- Initialize the database with seed data
- Create default user accounts

### 6. Start the Application
```bash
python app.py
```

Visit: **http://localhost:5000**

## 👥 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Dispatcher | dispatcher | dispatch123 |
| Driver | driver1 | driver123 |

## 📁 Project Structure

```
SK/
│
├── app.py                          # Main application entry point
├── config.py                       # Configuration management
├── setup.py                        # Automated setup script
├── requirements.txt                # Python dependencies
│
├── src/
│   ├── routes/                     # Blueprint routes
│   │   ├── auth_routes.py         # Authentication endpoints
│   │   ├── main_routes.py         # Dashboard & main pages
│   │   ├── orders_routes.py       # Order management
│   │   ├── fleet_routes.py        # Vehicle & driver management
│   │   └── optimization_routes.py # Route optimization
│   │
│   ├── models/
│   │   └── demand_predictor.py    # ML demand forecasting
│   │
│   ├── optimization/
│   │   └── optimizer.py           # OR-Tools route optimizer
│   │
│   ├── persistence/
│   │   ├── models.py              # Database models
│   │   └── db_init.py             # Database initialization
│   │
│   ├── data/
│   │   └── data_generator.py      # Synthetic data generation
│   │
│   └── forms.py                    # WTForms definitions
│
├── templates/                      # Jinja2 templates
│   ├── base.html                  # Base template
│   ├── dashboard.html             # Main dashboard
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   └── orders/                    # Order templates
│       └── list.html              # Orders list
│
├── static/                         # Static assets
│   ├── css/                       # Custom stylesheets
│   └── js/                        # Custom JavaScript
│
├── data/                           # Generated data files
│   ├── fleet_info.csv
│   ├── historical_demand.csv
│   ├── orders.csv
│   └── forecast.csv
│
├── models/                         # Trained ML models
│   ├── demand_model.pkl
│   └── model_columns.json
│
└── tests/                          # Test suite
    └── test_core.py
```

## 🎯 Key Components

### 1. Route Optimization
The system uses Google OR-Tools to solve the Capacitated Vehicle Routing Problem (CVRP):
- Minimizes total distance traveled
- Respects vehicle capacity constraints
- Optimizes delivery sequences
- Provides real-time route visualization

### 2. Demand Forecasting
Machine Learning pipeline for demand prediction:
- Historical data analysis
- Feature engineering (day of week, seasonality)
- Multiple model comparison
- 7-day rolling forecasts

### 3. Database Architecture
Comprehensive relational database with:
- User management with role-based access
- Fleet and driver tracking
- Order lifecycle management
- Route planning and execution
- Performance metrics storage

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Dashboard
- `GET /api/stats` - Get dashboard statistics
- `GET /api/forecast_chart` - Get demand forecast data
- `GET /api/notifications` - Get user notifications

### Orders
- `GET /orders` - List all orders (with filters)
- `GET /orders/<id>` - Get order details
- `POST /orders/create` - Create new order
- `PUT /orders/<id>/status` - Update order status
- `GET /api/orders` - Get orders as JSON

### Fleet
- `GET /vehicles` - List all vehicles
- `GET /api/vehicles` - Get vehicles as JSON
- `GET /drivers` - List all drivers
- `GET /api/drivers` - Get drivers as JSON

### Optimization
- `POST /optimization/api/optimize` - Run route optimization
- `GET /optimization/routes` - List all routes
- `GET /optimization/routes/<id>` - Get route details

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_core.py
```

## 🔧 Configuration

Edit `config.py` or `.env` file to configure:

- **Database URL** - SQLite (default) or PostgreSQL
- **Secret Key** - For session encryption
- **Mail Settings** - For email notifications
- **API Keys** - Google Maps, etc.
- **Upload Settings** - File size limits, allowed extensions

## 📦 Deployment

### Production Setup

1. **Update Configuration**
```python
# Set FLASK_ENV=production in .env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@localhost/logistics_db
```

2. **Use Production Server**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

3. **Setup Nginx** (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google OR-Tools** - Route optimization engine
- **scikit-learn** - Machine learning framework
- **Flask** - Web framework
- **Bootstrap** - UI framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for Advanced Logistics Management**
#   D y n a m i c - L o a d - M a n a g e m e n t - a n d - R o u t e - O p t i m i z a t i o n - i n - L o g i s t i c s - U s i n g - P r e d i c t i v e - A n a l y t i c s  
 