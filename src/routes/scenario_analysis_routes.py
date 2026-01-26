from flask import Blueprint, jsonify, request
from flask_login import login_required
from src.analysis.scenario_analysis import ScenarioAnalyzer, generate_baseline_data
import pandas as pd

scenario_bp = Blueprint("scenario", __name__, url_prefix="/api/scenario")


@scenario_bp.route("/analyze", methods=["POST"])
@login_required
def run_scenario_analysis():
    """
    Run a what-if scenario analysis
    """
    try:
        data = request.get_json()
        scenario_type = data.get("scenario_type")
        parameters = data.get("parameters", {})
        baseline_data = data.get("baseline_data", {})

        # If no baseline data provided, generate sample data
        if not baseline_data:
            baseline_data = generate_baseline_data()

        # Create analyzer
        analyzer = ScenarioAnalyzer(baseline_data)

        # Run appropriate scenario
        if scenario_type == "vehicle_breakdown":
            result = analyzer.simulate_vehicle_breakdown(
                parameters.get("vehicle_id", "VAN-001"),
                parameters.get("duration_hours", 24),
            )
        elif scenario_type == "demand_spike":
            result = analyzer.simulate_demand_spike(
                parameters.get("spike_percentage", 50),
                parameters.get("duration_days", 7),
            )
        elif scenario_type == "weather_disruption":
            result = analyzer.simulate_weather_disruption(
                parameters.get("severity", "moderate"),
                parameters.get("affected_regions", ["North"]),
                parameters.get("duration_hours", 48),
            )
        elif scenario_type == "driver_shortage":
            result = analyzer.simulate_driver_shortage(
                parameters.get("shortage_percentage", 25),
                parameters.get("duration_days", 14),
            )
        else:
            return jsonify({"error": f"Unknown scenario type: {scenario_type}"}), 400

        return jsonify(
            {"success": True, "scenario_type": scenario_type, "result": result}
        )

    except Exception as e:
        return jsonify({"error": f"Scenario analysis failed: {str(e)}"}), 500


@scenario_bp.route("/compare", methods=["POST"])
@login_required
def compare_scenarios():
    """
    Compare multiple scenarios
    """
    try:
        data = request.get_json()
        scenarios = data.get("scenarios", [])
        baseline_data = data.get("baseline_data", {})

        # If no baseline data provided, generate sample data
        if not baseline_data:
            baseline_data = generate_baseline_data()

        # Create analyzer
        analyzer = ScenarioAnalyzer(baseline_data)

        # Run all scenarios
        results = []
        for scenario in scenarios:
            scenario_type = scenario.get("type")
            parameters = scenario.get("parameters", {})

            # Run scenario and collect result
            if scenario_type == "vehicle_breakdown":
                result = analyzer.simulate_vehicle_breakdown(
                    parameters.get("vehicle_id", "VAN-001"),
                    parameters.get("duration_hours", 24),
                )
            elif scenario_type == "demand_spike":
                result = analyzer.simulate_demand_spike(
                    parameters.get("spike_percentage", 50),
                    parameters.get("duration_days", 7),
                )
            elif scenario_type == "weather_disruption":
                result = analyzer.simulate_weather_disruption(
                    parameters.get("severity", "moderate"),
                    parameters.get("affected_regions", ["North"]),
                    parameters.get("duration_hours", 48),
                )
            elif scenario_type == "driver_shortage":
                result = analyzer.simulate_driver_shortage(
                    parameters.get("shortage_percentage", 25),
                    parameters.get("duration_days", 14),
                )
            else:
                result = {"error": f"Unknown scenario type: {scenario_type}"}

            results.append(
                {
                    "scenario_type": scenario_type,
                    "parameters": parameters,
                    "result": result,
                }
            )

        # Get comparison
        comparison = analyzer.compare_scenarios()

        return jsonify(
            {"success": True, "individual_results": results, "comparison": comparison}
        )

    except Exception as e:
        return jsonify({"error": f"Scenario comparison failed: {str(e)}"}), 500


@scenario_bp.route("/baseline")
@login_required
def get_baseline_data():
    """
    Get current baseline operational data
    """
    try:
        baseline_data = generate_baseline_data()
        return jsonify({"success": True, "baseline_data": baseline_data})

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve baseline data: {str(e)}"}), 500


@scenario_bp.route("/templates")
@login_required
def get_scenario_templates():
    """
    Get predefined scenario templates
    """
    templates = [
        {
            "id": "vehicle_breakdown",
            "name": "Vehicle Breakdown",
            "description": "Analyze the impact of a vehicle becoming unavailable",
            "parameters": [
                {
                    "name": "vehicle_id",
                    "type": "string",
                    "default": "VAN-001",
                    "label": "Vehicle ID",
                },
                {
                    "name": "duration_hours",
                    "type": "number",
                    "default": 24,
                    "label": "Duration (hours)",
                },
            ],
        },
        {
            "id": "demand_spike",
            "name": "Demand Spike",
            "description": "Analyze the impact of sudden increase in order volume",
            "parameters": [
                {
                    "name": "spike_percentage",
                    "type": "number",
                    "default": 50,
                    "label": "Increase (%)",
                },
                {
                    "name": "duration_days",
                    "type": "number",
                    "default": 7,
                    "label": "Duration (days)",
                },
            ],
        },
        {
            "id": "weather_disruption",
            "name": "Weather Disruption",
            "description": "Analyze the impact of weather-related delivery disruptions",
            "parameters": [
                {
                    "name": "severity",
                    "type": "select",
                    "options": ["minor", "moderate", "severe"],
                    "default": "moderate",
                    "label": "Severity",
                },
                {
                    "name": "affected_regions",
                    "type": "multiselect",
                    "options": ["North", "South", "East", "West", "Central"],
                    "default": ["North"],
                    "label": "Affected Regions",
                },
                {
                    "name": "duration_hours",
                    "type": "number",
                    "default": 48,
                    "label": "Duration (hours)",
                },
            ],
        },
        {
            "id": "driver_shortage",
            "name": "Driver Shortage",
            "description": "Analyze the impact of reduced driver availability",
            "parameters": [
                {
                    "name": "shortage_percentage",
                    "type": "number",
                    "default": 25,
                    "label": "Shortage (%)",
                },
                {
                    "name": "duration_days",
                    "type": "number",
                    "default": 14,
                    "label": "Duration (days)",
                },
            ],
        },
    ]

    return jsonify({"templates": templates})


@scenario_bp.route("/recommendations", methods=["POST"])
@login_required
def get_scenario_recommendations():
    """
    Get recommendations based on scenario results
    """
    try:
        data = request.get_json()
        scenario_results = data.get("results", {})

        # Extract key metrics for recommendations
        cost_impact = scenario_results.get("cost_impact", 0)
        affected_orders = scenario_results.get("affected_orders", 0)
        delay_hours = scenario_results.get(
            "estimated_total_delay_hours",
            scenario_results.get("estimated_delay_hours", 0),
        )

        # Generate recommendations based on impact
        recommendations = []

        if cost_impact > 2000:
            recommendations.append(
                "High financial impact detected. Consider immediate executive review."
            )
            recommendations.append("Activate emergency budget allocation procedures.")
        elif cost_impact > 1000:
            recommendations.append(
                "Moderate financial impact. Review operational budgets."
            )

        if affected_orders > 50:
            recommendations.append(
                "Significant order impact. Proactive customer communication essential."
            )
            recommendations.append("Consider temporary staffing or partner solutions.")
        elif affected_orders > 20:
            recommendations.append("Review delivery priorities and adjust accordingly.")

        if delay_hours > 100:
            recommendations.append(
                "Substantial delay impact. Implement customer compensation protocols."
            )
            recommendations.append(
                "Coordinate with customer service for proactive notifications."
            )
        elif delay_hours > 50:
            recommendations.append(
                "Monitor delivery schedule closely and adjust as needed."
            )

        # Add general recommendations
        general_recommendations = scenario_results.get("alternative_solutions", [])
        recommendations.extend(general_recommendations[:3])  # Limit to top 3

        return jsonify({"success": True, "recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500
