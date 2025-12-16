# 🚚 Logistics AI – Advanced Full-Stack Route Optimization Platform

An enterprise-grade logistics management system with **AI-powered demand forecasting** and **intelligent route optimization** using **Google OR-Tools**.

---

## 🌟 Features

### Core Functionality

* **🤖 AI-Powered Demand Forecasting** – Machine learning models (RandomForest, XGBoost, Prophet)
* **🗺️ Intelligent Route Optimization** – Google OR-Tools CVRP solver
* **📊 Real-time Dashboard** – Live analytics with interactive charts and maps
* **📦 Order Management** – Full CRUD with status tracking
* **🚛 Fleet Management** – Vehicle tracking, maintenance, and utilization metrics
* **👤 Driver Management** – Driver profiles, ratings, and assignment tracking
* **📈 Performance Analytics** – Historical metrics and reports
* **🔔 Notification System** – Real-time alerts and updates

### Technical Features

* **🔐 Authentication & Authorization** – Role-based access (Admin, Manager, Dispatcher, Driver)
* **🗄️ Advanced Database Models** – SQLAlchemy ORM with relationships
* **🎨 Modern UI/UX** – Responsive dark-themed UI with Bootstrap 5
* **📱 RESTful API** – Structured API endpoints
* **🧪 Testing Suite** – Pytest-based tests
* **⚙️ Configuration Management** – Environment-based configs

---

## 🛠️ Technology Stack

### Backend

* Flask
* SQLAlchemy
* Flask-Login
* Flask-WTF

### Machine Learning & Optimization

* scikit-learn
* XGBoost
* Prophet
* Google OR-Tools

### Frontend

* Bootstrap 5
* Chart.js
* Leaflet.js
* Font Awesome

### Database

* SQLite (Development)
* PostgreSQL (Production)

---

## 📋 Prerequisites

* Python 3.8+
* pip
* Git

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Abubakkar-prof/Dynamic-Load-Management-and-Route-Optimization-in-Logistics-Using-Predictive-Analytics.git
cd SK
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

Edit `.env` with your configuration.

### 5️⃣ Run Setup Script

```bash
python setup.py
```

This will:

* Generate synthetic data
* Train ML demand forecasting models
* Initialize the database
* Create default user accounts

### 6️⃣ Start the Application

```bash
python app.py
```

Visit **[http://localhost:5000](http://localhost:5000)**

---

## 👥 Default Login Credentials

| Role       | Username   | Password    |
| ---------- | ---------- | ----------- |
| Admin      | admin      | admin123    |
| Manager    | manager    | manager123  |
| Dispatcher | dispatcher | dispatch123 |
| Driver     | driver1    | driver123   |

---

## 📁 Project Structure

```text
SK/
│── app.py
│── config.py
│── setup.py
│── requirements.txt
│
├── src/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── main_routes.py
│   │   ├── orders_routes.py
│   │   ├── fleet_routes.py
│   │   └── optimization_routes.py
│   │
│   ├── models/
│   │   └── demand_predictor.py
│   │
│   ├── optimization/
│   │   └── optimizer.py
│   │
│   ├── persistence/
│   │   ├── models.py
│   │   └── db_init.py
│   │
│   ├── data/
│   │   └── data_generator.py
│   │
│   └── forms.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   └── orders/
│       └── list.html
│
├── static/
│   ├── css/
│   └── js/
│
├── data/
│   ├── fleet_info.csv
│   ├── historical_demand.csv
│   ├── orders.csv
│   └── forecast.csv
│
├── models/
│   ├── demand_model.pkl
│   └── model_columns.json
│
└── tests/
    └── test_core.py
```

---

## 🎯 Key Components

### Route Optimization

* Solves Capacitated Vehicle Routing Problem (CVRP)
* Minimizes total distance
* Enforces vehicle capacity constraints
* Optimized delivery sequencing

### Demand Forecasting

* Historical demand analysis
* Feature engineering (seasonality, weekdays)
* Model comparison and selection
* Rolling 7-day forecasts

### Database Architecture

* Role-based user management
* Fleet and driver tracking
* Order lifecycle management
* Performance metrics storage

---

## 📊 API Endpoints

### Authentication

* `POST /auth/login`
* `POST /auth/register`
* `GET /auth/logout`

### Dashboard

* `GET /api/stats`
* `GET /api/forecast_chart`
* `GET /api/notifications`

### Orders

* `GET /orders`
* `POST /orders/create`
* `PUT /orders/<id>/status`
* `GET /api/orders`

### Fleet

* `GET /vehicles`
* `GET /drivers`
* `GET /api/vehicles`
* `GET /api/drivers`

### Optimization

* `POST /optimization/api/optimize`
* `GET /optimization/routes`

---

## 🧪 Running Tests

```bash
pytest
pytest --cov=src tests/
pytest tests/test_core.py
```

---

## 🔧 Configuration

Configure via `config.py` or `.env`:

* Database URL
* Secret key
* Mail settings
* API keys
* Upload limits

---

## 📦 Deployment

### Production Setup

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/logistics_db
```

### Run with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Nginx Reverse Proxy

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

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

* Google OR-Tools
* scikit-learn
* Flask
* Bootstrap

---

**Built with ❤️ for Advanced Logistics Management**
