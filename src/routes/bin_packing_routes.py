from flask import Blueprint, jsonify, request
from flask_login import login_required
from src.optimization.bin_packing import optimize_loading, generate_sample_data
import pandas as pd

bin_packing_bp = Blueprint("bin_packing", __name__, url_prefix="/api/bin_packing")


@bin_packing_bp.route("/optimize", methods=["POST"])
@login_required
def optimize_loading_api():
    """
    Optimize loading of orders into vehicles using 3D bin packing
    """
    try:
        data = request.get_json()

        # Extract fleet and orders data
        fleet = data.get("fleet", [])
        orders = data.get("orders", [])

        # Validate inputs
        if not fleet or not orders:
            return (
                jsonify({"error": "Missing required parameters: fleet and orders"}),
                400,
            )

        # Optimize loading
        results = optimize_loading(fleet, orders)

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"error": f"Bin packing optimization failed: {str(e)}"}), 500


@bin_packing_bp.route("/scenario/generate", methods=["POST"])
@login_required
def generate_packing_scenario():
    """
    Generate a sample bin packing scenario for testing
    """
    try:
        fleet, orders = generate_sample_data()

        return jsonify({"fleet": fleet, "orders": orders})

    except Exception as e:
        return jsonify({"error": f"Failed to generate scenario: {str(e)}"}), 500


@bin_packing_bp.route("/analyze", methods=["POST"])
@login_required
def analyze_packing_results():
    """
    Analyze bin packing results and provide recommendations
    """
    try:
        data = request.get_json()
        results = data.get("results", {})

        if not results:
            return jsonify({"error": "No results provided for analysis"}), 400

        # Extract statistics
        stats = results.get("statistics", {})
        packing_results = results.get("packing_results", [])

        # Generate recommendations
        recommendations = []

        # Check packing efficiency
        efficiency = stats.get("packing_efficiency", 0)
        if efficiency < 80:
            recommendations.append(
                f"Packing efficiency is {efficiency:.1f}%. Consider using larger vehicles or optimizing package sizes."
            )
        elif efficiency > 95:
            recommendations.append("Excellent packing efficiency achieved!")

        # Check vehicle utilization
        for bin_result in packing_results:
            bin_info = bin_result["bin"]
            vol_util = bin_info.get("volume_utilization", 0)
            weight_util = bin_info.get("weight_utilization", 0)

            if vol_util < 30 and weight_util < 30:
                recommendations.append(
                    f"Vehicle {bin_info['bin_id']} is underutilized. Consider consolidating loads."
                )
            elif vol_util > 90 or weight_util > 90:
                recommendations.append(
                    f"Vehicle {bin_info['bin_id']} is heavily loaded. Ensure secure loading procedures."
                )

        # Check for unpacked items
        unpacked = stats.get("unpacked_items", 0)
        if unpacked > 0:
            recommendations.append(
                f"{unpacked} items could not be packed. Consider adding more vehicles or adjusting package sizes."
            )

        # Calculate additional metrics
        total_bins = len(packing_results)
        total_items = stats.get("total_items", 0)
        packed_items = stats.get("packed_items", 0)

        analysis = {
            "summary": {
                "total_vehicles": total_bins,
                "total_items": total_items,
                "packed_items": packed_items,
                "unpacked_items": unpacked,
                "packing_efficiency": efficiency,
                "average_volume_utilization": stats.get(
                    "average_volume_utilization", 0
                ),
                "average_weight_utilization": stats.get(
                    "average_weight_utilization", 0
                ),
            },
            "recommendations": recommendations,
        }

        return jsonify(analysis)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@bin_packing_bp.route("/vehicle_types")
@login_required
def get_vehicle_types():
    """
    Get standard vehicle types and their dimensions
    """
    vehicle_types = [
        {
            "type": "Motorcycle",
            "width": 0.8,
            "height": 1.2,
            "depth": 1.5,
            "capacity_kg": 50,
            "description": "Small packages, urban deliveries",
        },
        {
            "type": "Van",
            "width": 2.0,
            "height": 1.8,
            "depth": 3.0,
            "capacity_kg": 1000,
            "description": "Standard delivery vehicle",
        },
        {
            "type": "Pickup Truck",
            "width": 2.2,
            "height": 2.0,
            "depth": 3.5,
            "capacity_kg": 1500,
            "description": "Medium capacity, versatile",
        },
        {
            "type": "Box Truck",
            "width": 2.5,
            "height": 2.0,
            "depth": 4.0,
            "capacity_kg": 3000,
            "description": "Large capacity, long-distance",
        },
        {
            "type": "Semi-Trailer",
            "width": 2.5,
            "height": 2.7,
            "depth": 13.0,
            "capacity_kg": 20000,
            "description": "Heavy freight, bulk shipments",
        },
    ]

    return jsonify({"vehicle_types": vehicle_types})
