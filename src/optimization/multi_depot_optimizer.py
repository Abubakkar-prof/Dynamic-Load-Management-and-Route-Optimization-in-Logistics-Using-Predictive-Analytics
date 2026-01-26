import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import os
import math
import json


class MultiDepotOptimizer:
    def __init__(self, depots_data, fleet_data, orders_data):
        """
        Initialize multi-depot optimizer

        Args:
            depots_data: List of depot locations [(lat, lon), ...]
            fleet_data: List of vehicles with depot assignments
            orders_data: DataFrame with order information
        """
        self.depots = depots_data
        self.fleet = fleet_data
        self.orders = orders_data

    def calculate_distance_matrix(self, locations):
        """
        Calculates Manhattan distance matrix for simplicity in this demo.
        In production, use OSRM or Google Maps API.
        """
        size = len(locations)
        matrix = {}
        for from_node in range(size):
            matrix[from_node] = {}
            for to_node in range(size):
                if from_node == to_node:
                    matrix[from_node][to_node] = 0
                else:
                    # Manhattan distance approximation (deg -> ~km)
                    lat1, lon1 = locations[from_node]
                    lat2, lon2 = locations[to_node]
                    dist = abs(lat1 - lat2) * 111 + abs(lon1 - lon2) * 111
                    matrix[from_node][to_node] = int(dist * 1000)  # Meters
        return matrix

    def assign_orders_to_depots(self):
        """
        Assign orders to nearest depot based on geographic proximity
        """
        order_assignments = []

        for idx, order in self.orders.iterrows():
            min_distance = float("inf")
            assigned_depot = 0

            # Find nearest depot
            for depot_idx, depot_loc in enumerate(self.depots):
                lat_diff = abs(order["latitude"] - depot_loc[0])
                lon_diff = abs(order["longitude"] - depot_loc[1])
                distance = lat_diff * 111 + lon_diff * 111

                if distance < min_distance:
                    min_distance = distance
                    assigned_depot = depot_idx

            order_assignments.append(
                {
                    "order_id": order["order_id"],
                    "latitude": order["latitude"],
                    "longitude": order["longitude"],
                    "weight_kg": order["weight_kg"],
                    "volume_m3": order["volume_m3"],
                    "depot_id": assigned_depot,
                    "distance_to_depot": min_distance,
                }
            )

        return pd.DataFrame(order_assignments)

    def optimize_multi_depot_routes(self):
        """
        Solves multi-depot VRP using Google OR-Tools.
        Each depot handles its assigned orders with its own fleet.
        """
        # Assign orders to depots
        assigned_orders = self.assign_orders_to_depots()

        # Group orders by depot
        depot_groups = {}
        for _, order in assigned_orders.iterrows():
            depot_id = order["depot_id"]
            if depot_id not in depot_groups:
                depot_groups[depot_id] = []
            depot_groups[depot_id].append(order)

        # Optimize routes for each depot
        all_results = []

        for depot_id, depot_orders in depot_groups.items():
            if not depot_orders:
                continue

            # Filter fleet for this depot (assuming vehicles are assigned to depots)
            depot_fleet = [v for v in self.fleet if v.get("depot_id", 0) == depot_id]
            if not depot_fleet:
                # If no specific fleet for depot, use a portion of general fleet
                depot_fleet = self.fleet[: max(1, len(self.fleet) // len(self.depots))]

            # Prepare data for this depot
            depot_location = self.depots[depot_id]
            orders_df = pd.DataFrame(depot_orders)

            # Locations: Depot + Order Locations
            locations = [depot_location] + list(
                zip(orders_df["latitude"], orders_df["longitude"])
            )
            demands_kg = [0] + list(orders_df["weight_kg"].astype(int))  # 0 for depot
            demands_vol = [0] + list(
                orders_df["volume_m3"]
            )  # Volume for secondary constraint

            # Vehicle Capacities
            vehicle_capacities = [int(v["capacity_kg"]) for v in depot_fleet]
            num_vehicles = len(depot_fleet)

            data = {
                "distance_matrix": self.calculate_distance_matrix(locations),
                "demands": demands_kg,
                "vehicle_capacities": vehicle_capacities,
                "num_vehicles": num_vehicles,
                "depot": 0,
            }

            # Create Routing Index Manager
            manager = pywrapcp.RoutingIndexManager(
                len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
            )

            # Create Routing Model
            routing = pywrapcp.RoutingModel(manager)

            # Define Distance Callback
            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return data["distance_matrix"][from_node][to_node]

            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Add Capacity Constraint
            def demand_callback(from_index):
                from_node = manager.IndexToNode(from_index)
                return data["demands"][from_node]

            demand_callback_index = routing.RegisterUnaryTransitCallback(
                demand_callback
            )
            routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,  # null capacity slack
                data["vehicle_capacities"],  # vehicle maximum capacities
                True,  # start cumul to zero
                "Capacity",
            )

            # Solve
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.time_limit.seconds = (
                10  # Allow more time for complex multi-depot
            )

            solution = routing.SolveWithParameters(search_parameters)

            # Extract Solution
            if solution:
                for vehicle_id in range(data["num_vehicles"]):
                    index = routing.Start(vehicle_id)
                    route_distance = 0
                    route_load = 0
                    route_steps = []

                    while not routing.IsEnd(index):
                        node_index = manager.IndexToNode(index)
                        route_load += data["demands"][node_index]

                        # Store step info (Order details)
                        if node_index != 0:  # Not depot
                            order_idx = node_index - 1
                            order_info = orders_df.iloc[order_idx].to_dict()
                            route_steps.append(order_info)

                        previous_index = index
                        index = solution.Value(routing.NextVar(index))
                        route_distance += routing.GetArcCostForVehicle(
                            previous_index, index, vehicle_id
                        )

                    if route_steps:  # Only add if vehicle utilized
                        all_results.append(
                            {
                                "depot_id": depot_id,
                                "depot_location": depot_location,
                                "vehicle_id": (
                                    depot_fleet[vehicle_id]["vehicle_id"]
                                    if vehicle_id < len(depot_fleet)
                                    else f"Vehicle_{vehicle_id}"
                                ),
                                "route": route_steps,
                                "total_distance_m": route_distance,
                                "total_load_kg": route_load,
                                "capacity_kg": data["vehicle_capacities"][vehicle_id],
                                "utilization_pct": (
                                    round(
                                        (
                                            route_load
                                            / data["vehicle_capacities"][vehicle_id]
                                        )
                                        * 100,
                                        1,
                                    )
                                    if data["vehicle_capacities"][vehicle_id] > 0
                                    else 0
                                ),
                            }
                        )

        return all_results

    def optimize_with_depot_selection(self):
        """
        Alternative approach: Optimize depot selection for each order to minimize total cost
        This is a more complex optimization that considers all depots for all orders
        """
        # This would be a more complex implementation involving:
        # 1. Creating a larger distance matrix with all depots and orders
        # 2. Using set covering or facility location algorithms
        # 3. Then applying VRP for each selected depot

        # For now, we'll use the simpler approach above
        return self.optimize_multi_depot_routes()


def generate_multi_depot_scenario():
    """
    Generate sample data for multi-depot optimization
    """
    # Sample depot locations (Karachi, Lahore, Islamabad)
    depots = [
        (24.8607, 67.0011),  # Karachi
        (31.5204, 74.3587),  # Lahore
        (33.6844, 73.0479),  # Islamabad
    ]

    # Sample fleet distributed among depots
    fleet = [
        {"vehicle_id": "KHI-VAN-001", "capacity_kg": 1000, "depot_id": 0},
        {"vehicle_id": "KHI-VAN-002", "capacity_kg": 1000, "depot_id": 0},
        {"vehicle_id": "LHR-TRUCK-001", "capacity_kg": 3000, "depot_id": 1},
        {"vehicle_id": "LHR-VAN-001", "capacity_kg": 1000, "depot_id": 1},
        {"vehicle_id": "ISB-TRUCK-001", "capacity_kg": 3000, "depot_id": 2},
        {"vehicle_id": "ISB-VAN-001", "capacity_kg": 1000, "depot_id": 2},
    ]

    # Generate sample orders near each depot
    orders_data = []
    order_id = 1001

    # Generate orders for Karachi depot
    for _ in range(20):
        lat = 24.8607 + np.random.uniform(-0.1, 0.1)
        lon = 67.0011 + np.random.uniform(-0.1, 0.1)
        orders_data.append(
            {
                "order_id": f"ORD-{order_id}",
                "latitude": lat,
                "longitude": lon,
                "weight_kg": np.random.uniform(5, 50),
                "volume_m3": np.random.uniform(0.1, 2),
                "priority": np.random.randint(1, 5),
            }
        )
        order_id += 1

    # Generate orders for Lahore depot
    for _ in range(15):
        lat = 31.5204 + np.random.uniform(-0.1, 0.1)
        lon = 74.3587 + np.random.uniform(-0.1, 0.1)
        orders_data.append(
            {
                "order_id": f"ORD-{order_id}",
                "latitude": lat,
                "longitude": lon,
                "weight_kg": np.random.uniform(5, 50),
                "volume_m3": np.random.uniform(0.1, 2),
                "priority": np.random.randint(1, 5),
            }
        )
        order_id += 1

    # Generate orders for Islamabad depot
    for _ in range(10):
        lat = 33.6844 + np.random.uniform(-0.1, 0.1)
        lon = 73.0479 + np.random.uniform(-0.1, 0.1)
        orders_data.append(
            {
                "order_id": f"ORD-{order_id}",
                "latitude": lat,
                "longitude": lon,
                "weight_kg": np.random.uniform(5, 50),
                "volume_m3": np.random.uniform(0.1, 2),
                "priority": np.random.randint(1, 5),
            }
        )
        order_id += 1

    orders_df = pd.DataFrame(orders_data)
    return depots, fleet, orders_df


if __name__ == "__main__":
    # Generate sample data
    depots, fleet, orders = generate_multi_depot_scenario()

    # Create optimizer
    optimizer = MultiDepotOptimizer(depots, fleet, orders)

    # Optimize routes
    results = optimizer.optimize_multi_depot_routes()

    # Print results
    print("Multi-Depot Optimization Results:")
    print("=" * 50)
    for result in results:
        print(
            f"Depot {result['depot_id']} ({result['depot_location'][0]:.4f}, {result['depot_location'][1]:.4f})"
        )
        print(f"  Vehicle: {result['vehicle_id']}")
        print(f"  Orders: {len(result['route'])}")
        print(f"  Distance: {result['total_distance_m']/1000:.2f} km")
        print(
            f"  Load: {result['total_load_kg']:.1f} kg / {result['capacity_kg']} kg ({result['utilization_pct']}%)"
        )
        print()
