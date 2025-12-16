# 🚀 Quick Start Guide - Logistics AI Platform

## ⚡ Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Setup
```bash
python setup.py
```

This command will:
- ✅ Generate sample data (fleet, orders, demand history)
- ✅ Train the ML forecasting model
- ✅ Initialize database with seed data
- ✅ Create default user accounts

### Step 3: Start the Application
```bash
python app.py
```

### Step 4: Open in Browser
Visit: **http://localhost:5000**

### Step 5: Login
Use the default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🎯 What Can You Do?

### 1. View Dashboard
- See real-time statistics
- View demand forecasts
- Monitor fleet status

### 2. Manage Orders
- Navigate to **Orders** → **New Order**
- Fill in order details (customer, location, weight)
- Click "Create Order"

### 3. Run Route Optimization
- Go to **Routes** page
- Click "Generate New Routes"
- View optimized delivery routes on the map

### 4. Track Fleet
- Navigate to **Fleet** page
- View all vehicles and their status
- Monitor driver assignments

---

## 🛠️ Troubleshooting

### Issue: Module not found error
**Solution**: Make sure virtual environment is activated
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Issue: Database error
**Solution**: Delete database and re-run setup
```bash
# Delete existing database
rm logistics.db

# Re-run setup
python setup.py
```

### Issue: Port 5000 already in use
**Solution**: Change port in app.py
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change to 8000
```

---

## 📚 Next Steps

1. **Explore the Dashboard** - Check out real-time analytics
2. **Create Orders** - Add some test orders
3. **Optimize Routes** - Generate delivery routes
4. **View Documentation** - Read README.md for details
5. **Customize** - Modify templates and add features

---

## 💡 Pro Tips

- **Use Filters**: Filter orders by status, region, or search
- **Check Forecast**: ML model predicts demand for next 7 days
- **Monitor Utilization**: Routes show vehicle capacity utilization
- **Track Performance**: View historical metrics and trends

---

## 🔑 All Default Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| **Admin** | admin | admin123 | Full System Access |
| Manager | manager | manager123 | Fleet & Route Management |
| Dispatcher | dispatcher | dispatch123 | Order Dispatching |
| Driver | driver1 | driver123 | View Assigned Routes |

---

## 📞 Need Help?

- Check **README.md** for detailed documentation
- Review code comments for implementation details
- Open an issue on GitHub for bugs

---

**🎉 Enjoy your Advanced Logistics Platform!**
