from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from src.persistence.models import db, Order, OrderStatus, TrackingUpdate
from src.forms import OrderForm
from datetime import datetime, date
from sqlalchemy import or_

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/")
@login_required
def list_orders():
    """List all orders with filtering and pagination"""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    status_filter = request.args.get("status", "")
    region_filter = request.args.get("region", "")
    search = request.args.get("search", "")

    query = Order.query

    # Apply filters
    if status_filter and status_filter != "all":
        try:
            status_enum = OrderStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            pass

    if region_filter and region_filter != "all":
        query = query.filter_by(region=region_filter)

    if search:
        query = query.filter(
            or_(
                Order.order_id.contains(search),
                Order.customer_name.contains(search),
                Order.delivery_address.contains(search),
            )
        )

    # Order by creation date (newest first)
    query = query.order_by(Order.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items

    return render_template(
        "orders/list.html",
        orders=orders,
        pagination=pagination,
        status_filter=status_filter,
        region_filter=region_filter,
        search=search,
    )


@orders_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_order():
    """Create a new order"""
    form = OrderForm()

    if form.validate_on_submit():
        order = Order(
            order_id=form.order_id.data,
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            customer_email=form.customer_email.data,
            delivery_address=form.delivery_address.data,
            weight_kg=form.weight_kg.data,
            volume_m3=form.volume_m3.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            region=form.region.data,
            priority=form.priority.data,
            deadline_hour=form.deadline_hour.data,
            deadline_date=date.today(),
            delivery_notes=form.delivery_notes.data,
            status=OrderStatus.PENDING,
        )

        db.session.add(order)
        db.session.commit()

        flash(f"Order {order.order_id} created successfully!", "success")
        return redirect(url_for("orders.list_orders"))

    return render_template("orders/create.html", form=form)


@orders_bp.route("/<int:order_id>")
@login_required
def view_order(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    tracking = (
        TrackingUpdate.query.filter_by(order_id=order_id)
        .order_by(TrackingUpdate.timestamp.desc())
        .all()
    )

    return render_template("orders/view.html", order=order, tracking=tracking)


@orders_bp.route("/<int:order_id>/edit", methods=["GET", "POST"])
@login_required
def edit_order(order_id):
    """Edit an existing order"""
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)

    if form.validate_on_submit():
        order.customer_name = form.customer_name.data
        order.customer_phone = form.customer_phone.data
        order.customer_email = form.customer_email.data
        order.delivery_address = form.delivery_address.data
        order.weight_kg = form.weight_kg.data
        order.volume_m3 = form.volume_m3.data
        order.latitude = form.latitude.data
        order.longitude = form.longitude.data
        order.region = form.region.data
        order.priority = form.priority.data
        order.deadline_hour = form.deadline_hour.data
        order.delivery_notes = form.delivery_notes.data

        db.session.commit()
        flash(f"Order {order.order_id} updated successfully!", "success")
        return redirect(url_for("orders.view_order", order_id=order_id))

    return render_template("orders/edit.html", form=form, order=order)


@orders_bp.route("/<int:order_id>/delete", methods=["POST"])
@login_required
def delete_order(order_id):
    """Delete an order"""
    order = Order.query.get_or_404(order_id)

    # Only allow deletion of pending orders
    if order.status != OrderStatus.PENDING:
        flash("Only pending orders can be deleted!", "danger")
        return redirect(url_for("orders.view_order", order_id=order_id))

    db.session.delete(order)
    db.session.commit()

    flash(f"Order {order.order_id} deleted successfully!", "success")
    return redirect(url_for("orders.list_orders"))


@orders_bp.route("/<int:order_id>/status", methods=["POST"])
@login_required
def update_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.json.get("status")
    notes = request.json.get("notes", "")

    try:
        status_enum = OrderStatus[new_status.upper().replace(" ", "_")]
        order.status = status_enum

        # Create tracking update
        tracking = TrackingUpdate(
            order_id=order.id,
            status=status_enum.value,
            notes=notes,
            created_by=current_user.id,
        )
        db.session.add(tracking)

        # If delivered, record delivery time
        if status_enum == OrderStatus.DELIVERED:
            order.actual_delivery_time = datetime.utcnow()

        db.session.commit()

        return jsonify({"success": True, "message": "Status updated successfully"})
    except (KeyError, ValueError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


# API Endpoints
@orders_bp.route("/api/orders")
@login_required
def api_orders():
    """Get orders as JSON"""
    status_filter = request.args.get("status", "")

    query = Order.query

    if status_filter:
        try:
            status_enum = OrderStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            pass

    orders = query.all()

    return jsonify(
        [
            {
                "id": o.id,
                "order_id": o.order_id,
                "customer_name": o.customer_name,
                "delivery_address": o.delivery_address,
                "weight_kg": o.weight_kg,
                "volume_m3": o.volume_m3,
                "latitude": o.latitude,
                "longitude": o.longitude,
                "region": o.region,
                "status": (
                    o.status.value if hasattr(o.status, "value") else str(o.status)
                ),
                "priority": o.priority,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for o in orders
        ]
    )
