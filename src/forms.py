"""
Flask-WTF Forms for Logistics AI Platform
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    SelectField,
    TextAreaField,
    DateField,
    PasswordField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)
from src.persistence.models import OrderStatus, VehicleStatus, DriverStatus


class LoginForm(FlaskForm):
    """User login form"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=100)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField("Remember Me")


class RegisterForm(FlaskForm):
    """User registration form"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=100)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    full_name = StringField("Full Name", validators=[Optional(), Length(max=200)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    role = SelectField(
        "Operational Designation",
        choices=[
            ("driver", "Fleet Operator (Driver)"),
            ("dispatcher", "Mission Dispatcher"),
            ("manager", "Logistics Manager"),
        ],
        validators=[DataRequired()],
    )

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError("Passwords must match")


class OrderForm(FlaskForm):
    """Order creation and editing form"""

    order_id = StringField("Order ID", validators=[DataRequired(), Length(max=50)])
    customer_name = StringField(
        "Customer Name", validators=[DataRequired(), Length(max=200)]
    )
    customer_phone = StringField(
        "Customer Phone", validators=[Optional(), Length(max=20)]
    )
    customer_email = StringField(
        "Customer Email", validators=[Optional(), Email(), Length(max=120)]
    )
    delivery_address = TextAreaField("Delivery Address", validators=[DataRequired()])
    weight_kg = FloatField(
        "Weight (kg)", validators=[DataRequired(), NumberRange(min=0.1, max=10000)]
    )
    volume_m3 = FloatField(
        "Volume (m³)", validators=[Optional(), NumberRange(min=0, max=100)]
    )
    latitude = FloatField(
        "Latitude", validators=[Optional(), NumberRange(min=-90, max=90)]
    )
    longitude = FloatField(
        "Longitude", validators=[Optional(), NumberRange(min=-180, max=180)]
    )
    region = SelectField(
        "Region",
        choices=[
            ("North", "North"),
            ("South", "South"),
            ("East", "East"),
            ("West", "West"),
            ("Central", "Central"),
        ],
        validators=[DataRequired()],
    )
    priority = IntegerField(
        "Priority (1-4)", validators=[DataRequired(), NumberRange(min=1, max=4)]
    )
    deadline_hour = IntegerField(
        "Deadline Hour (0-23)", validators=[Optional(), NumberRange(min=0, max=23)]
    )
    delivery_notes = TextAreaField("Delivery Notes", validators=[Optional()])


class VehicleForm(FlaskForm):
    """Vehicle creation and editing form"""

    vehicle_id = StringField("Vehicle ID", validators=[DataRequired(), Length(max=50)])
    type = StringField("Vehicle Type", validators=[DataRequired(), Length(max=50)])
    make = StringField("Make", validators=[Optional(), Length(max=50)])
    model = StringField("Model", validators=[Optional(), Length(max=50)])
    year = IntegerField(
        "Year", validators=[Optional(), NumberRange(min=1900, max=2100)]
    )
    license_plate = StringField(
        "License Plate", validators=[Optional(), Length(max=20)]
    )
    capacity_kg = FloatField(
        "Capacity (kg)", validators=[DataRequired(), NumberRange(min=1, max=50000)]
    )
    capacity_vol = FloatField(
        "Volume Capacity (m³)", validators=[Optional(), NumberRange(min=0, max=200)]
    )
    fuel_type = StringField("Fuel Type", validators=[Optional(), Length(max=50)])


class DriverForm(FlaskForm):
    """Driver creation and editing form"""

    user_id = IntegerField("User ID", validators=[DataRequired()])
    license_number = StringField(
        "License Number", validators=[DataRequired(), Length(max=50)]
    )
    license_expiry = DateField("License Expiry", validators=[Optional()])
    vehicle_id = IntegerField("Assigned Vehicle ID", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional()])
    emergency_contact = StringField(
        "Emergency Contact", validators=[Optional(), Length(max=100)]
    )
