from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from core.models import User

def landing_page(request):
    """Redirect authenticated users to dashboard, others to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        role = request.POST.get('role', 'Manager')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        
        # Auto-login after registration
        login(request, user)
        messages.success(request, f'Welcome to LogisticsOS, {username}!')
        return redirect('dashboard')
    
    return render(request, 'auth/register.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'segment': 'dashboard'
    })

@login_required
def logistics_map(request):
    return render(request, 'map.html', {
        'segment': 'map'
    })

# Frontend Views for API Consumers
@login_required
def order_list_view(request):
    return render(request, 'orders/order_list.html', {'segment': 'orders'})

@login_required
def order_create_view(request):
    return render(request, 'orders/order_create.html', {'segment': 'orders'})

@login_required
def vehicle_list_view(request):
    return render(request, 'vehicles/vehicle_list.html', {'segment': 'vehicles'})

@login_required
def vehicle_create_view(request):
    return render(request, 'vehicles/vehicle_create.html', {'segment': 'vehicles'})

@login_required
def prediction_view(request):
    return render(request, 'prediction/delivery_prediction.html', {'segment': 'prediction'})

@login_required
def bin_packing_view(request):
    return render(request, 'optimization/bin_packing.html', {'segment': 'bin_packing'})

@login_required
def telemetry_view(request):
    return render(request, 'telemetry/tracking.html', {'segment': 'telemetry'})

@login_required
def ml_model_comparison_view(request):
    from optimization.ml_services.model_comparison import MLModelComparison
    
    comparer = MLModelComparison()
    results = comparer.run_comparison()
    best_model = comparer.get_best_model()
    
    return render(request, 'ml/model_comparison.html', {
        'segment': 'ml_comparison',
        'results': results,
        'best_model': best_model
    })

@login_required
def multi_depot_view(request):
    from logistics.models import Order, Vehicle, Depot
    from optimization.multi_depot_optimizer import MultiDepotOptimizer
    
    depots = Depot.objects.all()
    results = []
    
    if request.method == 'POST':
        orders = Order.objects.filter(status='Pending')
        vehicles = Vehicle.objects.all()
        
        optimizer = MultiDepotOptimizer(orders, vehicles, depots)
        results = optimizer.optimize()
        
    return render(request, 'optimization/multi_depot.html', {
        'segment': 'multi_depot',
        'depots': depots,
        'results': results
    })
