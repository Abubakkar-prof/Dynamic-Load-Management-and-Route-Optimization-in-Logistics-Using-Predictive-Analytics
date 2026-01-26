import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta


class ScenarioAnalyzer:
    """
    Performs what-if scenario analysis for logistics operations
    """

    def __init__(self, baseline_data: Dict):
        """
        Initialize with baseline operational data

        Args:
            baseline_data: Dictionary containing current operational metrics
        """
        self.baseline_data = baseline_data
        self.scenarios = []

    def simulate_vehicle_breakdown(
        self, vehicle_id: str, duration_hours: int = 24
    ) -> Dict:
        """
        Simulate the impact of a vehicle breakdown

        Args:
            vehicle_id: ID of the vehicle that breaks down
            duration_hours: Duration of breakdown in hours

        Returns:
            Dictionary with impact analysis
        """
        # Get baseline metrics
        baseline_routes = self.baseline_data.get("routes", [])
        baseline_vehicles = self.baseline_data.get("vehicles", [])
        baseline_orders = self.baseline_data.get("orders", [])

        # Find affected vehicle
        affected_vehicle = None
        for vehicle in baseline_vehicles:
            if vehicle.get("vehicle_id") == vehicle_id:
                affected_vehicle = vehicle
                break

        if not affected_vehicle:
            return {"error": f"Vehicle {vehicle_id} not found"}

        # Find routes assigned to this vehicle
        affected_routes = [
            r for r in baseline_routes if r.get("vehicle_id") == vehicle_id
        ]
        affected_orders = []

        for route in affected_routes:
            affected_orders.extend(route.get("orders", []))

        # Calculate impact
        impact = {
            "scenario": "vehicle_breakdown",
            "vehicle_id": vehicle_id,
            "duration_hours": duration_hours,
            "affected_routes": len(affected_routes),
            "affected_orders": len(affected_orders),
            "estimated_delay_hours": len(affected_orders)
            * 0.5,  # Assumption: 30 mins per order delay
            "cost_impact": len(affected_orders)
            * 50,  # Assumption: $50 per delayed order
            "alternative_solutions": [
                "Reassign orders to other available vehicles",
                "Request temporary vehicle rental",
                "Negotiate delivery time extensions with customers",
                "Prioritize high-priority orders",
            ],
        }

        self.scenarios.append(
            {
                "type": "vehicle_breakdown",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "vehicle_id": vehicle_id,
                    "duration_hours": duration_hours,
                },
                "impact": impact,
            }
        )

        return impact

    def simulate_demand_spike(
        self, spike_percentage: float, duration_days: int = 7
    ) -> Dict:
        """
        Simulate the impact of a sudden demand increase

        Args:
            spike_percentage: Percentage increase in demand (e.g., 50 for 50% increase)
            duration_days: Duration of spike in days

        Returns:
            Dictionary with impact analysis
        """
        # Get baseline metrics
        baseline_orders = self.baseline_data.get("orders", [])
        baseline_vehicles = self.baseline_data.get("vehicles", [])

        # Calculate current capacity
        total_capacity = sum(v.get("capacity_kg", 0) for v in baseline_vehicles)
        current_orders = len(baseline_orders)
        avg_orders_per_day = current_orders / 7  # Assuming weekly data

        # Calculate new demand
        new_orders = current_orders * (1 + spike_percentage / 100)
        new_daily_orders = new_orders / 7

        # Calculate required capacity
        required_capacity = total_capacity * (1 + spike_percentage / 100)
        capacity_shortfall = max(0, required_capacity - total_capacity)

        # Calculate impact
        impact = {
            "scenario": "demand_spike",
            "spike_percentage": spike_percentage,
            "duration_days": duration_days,
            "current_orders": current_orders,
            "new_orders": int(new_orders),
            "additional_orders": int(new_orders - current_orders),
            "current_capacity_kg": total_capacity,
            "required_capacity_kg": required_capacity,
            "capacity_shortfall_kg": capacity_shortfall,
            "estimated_overtime_hours": (spike_percentage / 100)
            * 40,  # Assumption: 40 hours baseline work week
            "cost_impact": (new_orders - current_orders)
            * 20,  # Assumption: $20 additional cost per order
            "alternative_solutions": [
                "Lease additional vehicles",
                "Hire temporary drivers",
                "Extend working hours",
                "Partner with third-party logistics providers",
                "Implement dynamic pricing during peak periods",
            ],
        }

        self.scenarios.append(
            {
                "type": "demand_spike",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "spike_percentage": spike_percentage,
                    "duration_days": duration_days,
                },
                "impact": impact,
            }
        )

        return impact

    def simulate_weather_disruption(
        self, severity: str, affected_regions: List[str], duration_hours: int = 48
    ) -> Dict:
        """
        Simulate the impact of weather disruptions

        Args:
            severity: Severity level ('minor', 'moderate', 'severe')
            affected_regions: List of regions affected
            duration_hours: Duration of disruption in hours

        Returns:
            Dictionary with impact analysis
        """
        # Severity multipliers
        severity_multiplier = {"minor": 0.2, "moderate": 0.5, "severe": 0.8}

        multiplier = severity_multiplier.get(severity, 0.5)

        # Get baseline metrics
        baseline_orders = self.baseline_data.get("orders", [])
        baseline_routes = self.baseline_data.get("routes", [])

        # Filter orders in affected regions
        affected_orders = [
            o for o in baseline_orders if o.get("region") in affected_regions
        ]
        affected_routes = [
            r
            for r in baseline_routes
            if any(o.get("region") in affected_regions for o in r.get("orders", []))
        ]

        # Calculate impact
        delay_factor = multiplier * 2  # Hours delay per order
        total_delay = len(affected_orders) * delay_factor

        impact = {
            "scenario": "weather_disruption",
            "severity": severity,
            "affected_regions": affected_regions,
            "duration_hours": duration_hours,
            "affected_orders": len(affected_orders),
            "affected_routes": len(affected_routes),
            "estimated_total_delay_hours": total_delay,
            "cost_impact": len(affected_orders)
            * 30
            * multiplier,  # Assumption: $30 per delayed order
            "alternative_solutions": [
                "Reschedule deliveries for affected regions",
                "Use alternative routes",
                "Deploy all-weather vehicles where available",
                "Communicate delays to customers proactively",
                "Offer compensation for significant delays",
            ],
        }

        self.scenarios.append(
            {
                "type": "weather_disruption",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "severity": severity,
                    "affected_regions": affected_regions,
                    "duration_hours": duration_hours,
                },
                "impact": impact,
            }
        )

        return impact

    def simulate_driver_shortage(
        self, shortage_percentage: float, duration_days: int = 14
    ) -> Dict:
        """
        Simulate the impact of driver shortage

        Args:
            shortage_percentage: Percentage of drivers unavailable
            duration_days: Duration of shortage in days

        Returns:
            Dictionary with impact analysis
        """
        # Get baseline metrics
        baseline_drivers = self.baseline_data.get("drivers", [])
        baseline_routes = self.baseline_data.get("routes", [])
        baseline_vehicles = self.baseline_data.get("vehicles", [])

        # Calculate affected drivers
        total_drivers = len(baseline_drivers)
        affected_drivers = int(total_drivers * (shortage_percentage / 100))
        remaining_drivers = total_drivers - affected_drivers

        # Calculate impact on operations
        routes_per_driver = (
            len(baseline_routes) / total_drivers if total_drivers > 0 else 0
        )
        affected_routes = int(routes_per_driver * affected_drivers)

        # Calculate vehicle utilization impact
        vehicles_per_driver = (
            len(baseline_vehicles) / total_drivers if total_drivers > 0 else 0
        )
        underutilized_vehicles = int(vehicles_per_driver * affected_drivers)

        impact = {
            "scenario": "driver_shortage",
            "shortage_percentage": shortage_percentage,
            "duration_days": duration_days,
            "total_drivers": total_drivers,
            "affected_drivers": affected_drivers,
            "remaining_drivers": remaining_drivers,
            "affected_routes": affected_routes,
            "underutilized_vehicles": underutilized_vehicles,
            "estimated_productivity_loss": shortage_percentage
            * 0.8,  # Assumption: 80% correlation
            "cost_impact": affected_drivers
            * 200
            * duration_days,  # Assumption: $200/day per driver shortage cost
            "alternative_solutions": [
                "Cross-train staff for driving duties",
                "Offer overtime to existing drivers",
                "Use temporary staffing agencies",
                "Implement route optimization to do more with fewer drivers",
                "Adjust delivery schedules and expectations",
            ],
        }

        self.scenarios.append(
            {
                "type": "driver_shortage",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "shortage_percentage": shortage_percentage,
                    "duration_days": duration_days,
                },
                "impact": impact,
            }
        )

        return impact

    def get_scenario_history(self) -> List[Dict]:
        """
        Get history of all simulated scenarios

        Returns:
            List of scenario simulations
        """
        return self.scenarios

    def compare_scenarios(self) -> Dict:
        """
        Compare all scenarios and provide overall risk assessment

        Returns:
            Dictionary with comparative analysis
        """
        if not self.scenarios:
            return {"error": "No scenarios to compare"}

        # Aggregate impacts
        total_cost_impact = sum(
            s["impact"].get("cost_impact", 0) for s in self.scenarios
        )
        avg_delay = np.mean(
            [
                s["impact"].get(
                    "estimated_total_delay_hours",
                    s["impact"].get("estimated_delay_hours", 0),
                )
                for s in self.scenarios
            ]
        )

        # Risk categories
        high_risk_scenarios = [
            s for s in self.scenarios if s["impact"].get("cost_impact", 0) > 1000
        ]
        medium_risk_scenarios = [
            s
            for s in self.scenarios
            if 500 <= s["impact"].get("cost_impact", 0) <= 1000
        ]
        low_risk_scenarios = [
            s for s in self.scenarios if s["impact"].get("cost_impact", 0) < 500
        ]

        comparison = {
            "total_simulations": len(self.scenarios),
            "total_cost_impact": total_cost_impact,
            "average_delay_hours": avg_delay,
            "risk_distribution": {
                "high_risk": len(high_risk_scenarios),
                "medium_risk": len(medium_risk_scenarios),
                "low_risk": len(low_risk_scenarios),
            },
            "most_costly_scenario": max(
                self.scenarios, key=lambda x: x["impact"].get("cost_impact", 0)
            ),
            "recommendations": [
                "Develop contingency plans for high-risk scenarios",
                "Maintain buffer capacity for demand spikes",
                "Establish partnerships with backup service providers",
                "Invest in predictive analytics for early warning systems",
                "Regularly review and update risk mitigation strategies",
            ],
        }

        return comparison


def generate_baseline_data():
    """
    Generate sample baseline data for scenario analysis
    """
    # Sample vehicles
    vehicles = [
        {
            "vehicle_id": "VAN-001",
            "type": "Van",
            "capacity_kg": 1000,
            "status": "Available",
        },
        {
            "vehicle_id": "VAN-002",
            "type": "Van",
            "capacity_kg": 1000,
            "status": "Available",
        },
        {
            "vehicle_id": "TRUCK-001",
            "type": "Truck",
            "capacity_kg": 3000,
            "status": "On Route",
        },
        {
            "vehicle_id": "TRUCK-002",
            "type": "Truck",
            "capacity_kg": 3000,
            "status": "Maintenance",
        },
    ]

    # Sample drivers
    drivers = [
        {"driver_id": "DRV-001", "name": "Ali Khan", "status": "Available"},
        {"driver_id": "DRV-002", "name": "Usman Ahmed", "status": "On Duty"},
        {"driver_id": "DRV-003", "name": "Bilal Shah", "status": "Available"},
        {"driver_id": "DRV-004", "name": "Tariq Mahmood", "status": "On Leave"},
    ]

    # Sample orders
    orders = []
    regions = ["North", "South", "East", "West", "Central"]
    for i in range(100):
        orders.append(
            {
                "order_id": f"ORD-{1000+i}",
                "region": np.random.choice(regions),
                "weight_kg": np.random.uniform(1, 50),
                "priority": np.random.randint(1, 5),
                "status": "Pending" if i % 3 != 0 else "Assigned",
            }
        )

    # Sample routes
    routes = [
        {
            "route_id": "RT-001",
            "vehicle_id": "VAN-001",
            "driver_id": "DRV-001",
            "orders": orders[:20],
            "status": "Planned",
        },
        {
            "route_id": "RT-002",
            "vehicle_id": "TRUCK-001",
            "driver_id": "DRV-002",
            "orders": orders[20:45],
            "status": "Active",
        },
    ]

    return {
        "vehicles": vehicles,
        "drivers": drivers,
        "orders": orders,
        "routes": routes,
    }


if __name__ == "__main__":
    # Generate baseline data
    baseline_data = generate_baseline_data()

    # Create analyzer
    analyzer = ScenarioAnalyzer(baseline_data)

    # Run sample scenarios
    print("Running Scenario Analysis...")
    print("=" * 50)

    # Vehicle breakdown scenario
    breakdown_result = analyzer.simulate_vehicle_breakdown("VAN-001", 24)
    print("Vehicle Breakdown Scenario:")
    print(f"Affected Orders: {breakdown_result['affected_orders']}")
    print(f"Cost Impact: ${breakdown_result['cost_impact']}")
    print()

    # Demand spike scenario
    demand_result = analyzer.simulate_demand_spike(50, 7)
    print("Demand Spike Scenario (50% increase):")
    print(f"Additional Orders: {demand_result['additional_orders']}")
    print(f"Cost Impact: ${demand_result['cost_impact']}")
    print()

    # Weather disruption scenario
    weather_result = analyzer.simulate_weather_disruption(
        "moderate", ["North", "Central"], 48
    )
    print("Weather Disruption Scenario:")
    print(f"Affected Orders: {weather_result['affected_orders']}")
    print(f"Total Delay: {weather_result['estimated_total_delay_hours']} hours")
    print(f"Cost Impact: ${weather_result['cost_impact']}")
    print()

    # Driver shortage scenario
    driver_result = analyzer.simulate_driver_shortage(25, 14)
    print("Driver Shortage Scenario (25% shortage):")
    print(f"Affected Drivers: {driver_result['affected_drivers']}")
    print(f"Affect Routes: {driver_result['affected_routes']}")
    print(f"Cost Impact: ${driver_result['cost_impact']}")
    print()

    # Compare scenarios
    comparison = analyzer.compare_scenarios()
    print("Scenario Comparison:")
    print(f"Total Simulations: {comparison['total_simulations']}")
    print(f"Total Cost Impact: ${comparison['total_cost_impact']}")
    print(f"Risk Distribution: {comparison['risk_distribution']}")
