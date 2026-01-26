from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.optimization.multi_depot_optimizer import MultiDepotOptimizer
import pandas as pd
import os

multi_depot_bp = Blueprint("multi_depot", __name__, url_prefix="/api/multi_depot")


@multi_depot_bp.route("/optimize", methods=["POST"])
@login_required
def optimize_multi_depot():
    """
    Optimize routes for multiple depots
    """
    try:
        data = request.get_json()

        # Extract parameters
        depots = data.get("depots", [])
        fleet = data.get("fleet", [])
        orders = data.get("orders", [])

        # Validate inputs
        if not depots or not fleet or not orders:
            return (
                jsonify(
                    {"error": "Missing required parameters: depots, fleet, and orders"}
                ),
                400,
            )

        # Convert orders to DataFrame
        orders_df = pd.DataFrame(orders)

        # Create optimizer
        optimizer = MultiDepotOptimizer(depots, fleet, orders_df)

        # Optimize routes
        results = optimizer.optimize_multi_depot_routes()

        return jsonify(
            {
                "success": True,
                "routes": results,
                "total_depots": len(depots),
                "total_vehicles_used": len(results),
                "total_orders_served": sum(len(route["route"]) for route in results),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Multi-depot optimization failed: {str(e)}"}), 500


@multi_depot_bp.route("/scenario/generate", methods=["POST"])
@login_required
def generate_scenario():
    """
    Generate a sample multi-depot scenario for testing
    """
    try:
        from src.optimization.multi_depot_optimizer import generate_multi_depot_scenario

        depots, fleet, orders = generate_multi_depot_scenario()

        return jsonify(
            {"depots": depots, "fleet": fleet, "orders": orders.to_dict("records")}
        )

    except Exception as e:
        return jsonify({"error": f"Failed to generate scenario: {str(e)}"}), 500


@multi_depot_bp.route("/depots")
@login_required
def get_sample_depots():
    """
    Get sample depot locations
    """
    # Sample depot locations (major cities in Pakistan)
    depots = [
        {"id": 0, "name": "Karachi Main Depot", "lat": 24.8607, "lon": 67.0011},
        {"id": 1, "name": "Lahore Distribution Center", "lat": 31.5204, "lon": 74.3587},
        {"id": 2, "name": "Islamabad Hub", "lat": 33.6844, "lon": 73.0479},
        {"id": 3, "name": "Rawalpindi Warehouse", "lat": 33.5973, "lon": 73.0479},
        {"id": 4, "name": "Multan Facility", "lat": 30.1956, "lon": 71.4753},
    ]

    return jsonify({"depots": depots})


@multi_depot_bp.route("/analyze", methods=["POST"])
@login_required
def analyze_multi_depot_solution():
    """
    Analyze multi-depot optimization results
    """
    try:
        data = request.get_json()
        routes = data.get("routes", [])

        if not routes:
            return jsonify({"error": "No routes provided for analysis"}), 400

        # Perform analysis
        total_distance = sum(route["total_distance_m"] for route in routes)
        total_load = sum(route["total_load_kg"] for route in routes)
        total_capacity = sum(route["capacity_kg"] for route in routes)

        # Depot utilization
        depot_utilization = {}
        for route in routes:
            depot_id = route["depot_id"]
            if depot_id not in depot_utilization:
                depot_utilization[depot_id] = {
                    "routes": 0,
                    "distance": 0,
                    "load": 0,
                    "capacity": 0,
                }

            depot_utilization[depot_id]["routes"] += 1
            depot_utilization[depot_id]["distance"] += route["total_distance_m"]
            depot_utilization[depot_id]["load"] += route["total_load_kg"]
            depot_utilization[depot_id]["capacity"] += route["capacity_kg"]

        # Calculate metrics
        avg_utilization = (
            (total_load / total_capacity * 100) if total_capacity > 0 else 0
        )
        total_distance_km = total_distance / 1000

        analysis = {
            "summary": {
                "total_routes": len(routes),
                "total_distance_km": round(total_distance_km, 2),
                "total_load_kg": round(total_load, 2),
                "total_capacity_kg": round(total_capacity, 2),
                "average_utilization_pct": round(avg_utilization, 2),
            },
            "depot_analysis": depot_utilization,
            "recommendations": generate_recommendations(routes, depot_utilization),
        }

        return jsonify(analysis)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


def generate_recommendations(routes, depot_utilization):
    """
    Generate recommendations based on the optimization results
    """
    recommendations = []

    # Check for underutilized depots
    for depot_id, util in depot_utilization.items():
        if util["routes"] == 0:
            recommendations.append(
                f"Depot {depot_id} is not being utilized. Consider redistributing orders."
            )
        elif util["load"] / util["capacity"] < 0.3:
            recommendations.append(
                f"Depot {depot_id} is underutilized ({round(util['load']/util['capacity']*100, 1)}% capacity). Consider consolidating with nearby depots."
            )

    # Check for overloaded vehicles
    overloaded_count = sum(1 for route in routes if route["utilization_pct"] > 95)
    if overloaded_count > 0:
        recommendations.append(
            f"{overloaded_count} vehicles are operating near capacity. Consider adding more vehicles or redistributing loads."
        )

    # Efficiency recommendations
    if len(routes) > len(set(route["vehicle_id"] for route in routes)):
        recommendations.append(
            "Some vehicles are making multiple trips. Consider optimizing trip scheduling."
        )

    # If no recommendations, add a positive note
    if not recommendations:
        recommendations.append(
            "Optimization looks balanced. All depots and vehicles are well-utilized."
        )

    return recommendations
