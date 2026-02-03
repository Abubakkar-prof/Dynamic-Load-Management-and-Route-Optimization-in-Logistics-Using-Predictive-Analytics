from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required
from src.persistence.models import (
    db,
    Vehicle,
    Driver,
    Route,
    VehicleStatus,
    DriverStatus,
)
from src.forms import VehicleForm, DriverForm

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")
drivers_bp = Blueprint("drivers", __name__, url_prefix="/drivers")

# === VEHICLE ROUTES ===


@vehicles_bp.route("/")
@login_required
def list_vehicles():
    """List all vehicles"""
    vehicles = Vehicle.query.all()
    return render_template("vehicles/list.html", vehicles=vehicles)


@vehicles_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_vehicle():
    """Create new vehicle"""
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(
            vehicle_id=form.vehicle_id.data,
            type=form.type.data,
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            license_plate=form.license_plate.data,
            capacity_kg=form.capacity_kg.data,
            capacity_vol=form.capacity_vol.data,
            fuel_type=form.fuel_type.data,
            status=VehicleStatus.AVAILABLE,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash(f"Vehicle {vehicle.vehicle_id} created successfully!", "success")
        return redirect(url_for("vehicles.list_vehicles"))
    return render_template("vehicles/create.html", form=form)


@vehicles_bp.route("/<int:vehicle_id>")
@login_required
def view_vehicle(vehicle_id):
    """View vehicle details"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    routes = Route.query.filter_by(vehicle_id=vehicle_id).limit(10).all()
    return render_template("vehicles/view.html", vehicle=vehicle, routes=routes)


@vehicles_bp.route("/api/vehicles")
@login_required
def api_vehicles():
    """Get vehicles as JSON"""
    vehicles = Vehicle.query.all()
    data = []
    for v in vehicles:
        active_route = Route.query.filter_by(vehicle_id=v.id, status="Active").first()
        data.append({
            "id": v.id,
            "vehicle_id": v.vehicle_id,
            "type": v.type,
            "capacity_kg": v.capacity_kg,
            "capacity_vol": v.capacity_vol,
            "status": (
                v.status.value if hasattr(v.status, "value") else str(v.status)
            ),
            "current_location_lat": v.current_location_lat,
            "current_location_lon": v.current_location_lon,
            "active_route": active_route.route_id if active_route else None
        })
    return jsonify(data)


# === DRIVER ROUTES ===


@drivers_bp.route("/")
@login_required
def list_drivers():
    """List all drivers"""
    drivers = Driver.query.all()
    return render_template("drivers/list.html", drivers=drivers)


@drivers_bp.route("/<int:driver_id>")
@login_required
def view_driver(driver_id):
    """View driver details"""
    driver = Driver.query.get_or_404(driver_id)
    routes = Route.query.filter_by(driver_id=driver_id).limit(10).all()
    return render_template("drivers/view.html", driver=driver, routes=routes)


@drivers_bp.route("/api/drivers")
@login_required
def api_drivers():
    """Get drivers as JSON"""
    drivers = Driver.query.all()
    return jsonify(
        [
            {
                "id": d.id,
                "name": d.user.full_name if d.user else "N/A",
                "license_number": d.license_number,
                "status": (
                    d.status.value if hasattr(d.status, "value") else str(d.status)
                ),
                "rating": d.rating,
                "total_deliveries": d.total_deliveries,
                "vehicle_id": d.vehicle_id,
            }
            for d in drivers
        ]
    )
