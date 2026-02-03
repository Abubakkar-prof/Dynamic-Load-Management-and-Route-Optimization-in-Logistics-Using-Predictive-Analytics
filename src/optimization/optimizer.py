import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import os
import math


class LogisticsOptimizer:
    def __init__(self, fleet_data, orders_data, depot_location=(31.5204, 74.3587)):
        self.fleet = fleet_data
        self.orders = orders_data
        self.depot = depot_location  # Lat, Lon

    def calculate_distance_matrix(self, locations):
        """
        Calculates Haversine distance matrix.
        More accurate for spherical coordinates (Lat/Lon).
        """
        size = len(locations)
        matrix = {}

        def haversine(pos1, pos2):
            lat1, lon1 = pos1
            lat2, lon2 = pos2
            R = 6371000  # Radius of earth in meters
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_phi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return int(R * c)

        for from_node in range(size):
            matrix[from_node] = {}
            for to_node in range(size):
                if from_node == to_node:
                    matrix[from_node][to_node] = 0
                else:
                    matrix[from_node][to_node] = haversine(
                        locations[from_node], locations[to_node]
                    )
        return matrix

    def optimize_routes(self):
        """
        Solves CVRP using Google OR-Tools.
        """
        # 1. Prepare Data
        # Locations: Depot + Order Locations
        locations = [self.depot] + list(
            zip(self.orders["latitude"], self.orders["longitude"])
        )
        demands_kg = [0] + list(self.orders["weight_kg"].astype(int))  # 0 for depot
        demands_vol = [0] + list(
            self.orders["volume_m3"]
        )  # Checking Weight primarily for CVRP here

        # Vehicle Capacities
        # For simplicity, we'll take top N vehicles or assume homogeneous for basic CVRP
        # Here we try to use the actual fleet if possible, but OR-Tools standard CVRP example usually implies fixed fleet
        # We will iterate through available vehicles.

        vehicle_capacities = [int(v["capacity_kg"]) for v in self.fleet]
        num_vehicles = len(self.fleet)

        data = {
            "distance_matrix": self.calculate_distance_matrix(locations),
            "demands": demands_kg,
            "vehicle_capacities": vehicle_capacities,
            "num_vehicles": num_vehicles,
            "depot": 0,
        }

        # 2. Create Routing Index Manager
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

        # 3. Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Traffic Simulation Logic (Predictive)
        from datetime import datetime
        current_hour = datetime.now().hour
        # Peak hours: 8-10 AM or 5-7 PM
        is_rush_hour = (8 <= current_hour <= 10) or (17 <= current_hour <= 19)
        traffic_multiplier = 1.6 if is_rush_hour else 1.0

        # 4. Define Distance Callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # Apply traffic penalty to distance costs during rush hour
            return int(data["distance_matrix"][from_node][to_node] * traffic_multiplier)

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 5. Add Capacity Constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # 6. Add Time Window Constraint (CVRPTW)
        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # Travel time = Distance / Speed + Service Time
            # Assuming average speed of 40 km/h (approx 11 m/s)
            travel_time = data["distance_matrix"][from_node][to_node] / 11.0
            # Convert to minutes
            travel_time_min = travel_time / 60

            # Add service time at destination
            if to_node != 0:  # If not depot
                service_time = self.orders.iloc[to_node - 1].get("service_time", 15)
                return int(travel_time_min + service_time)
            return int(travel_time_min)

        transit_callback_index = routing.RegisterTransitCallback(time_callback)

        # Define time dimension
        routing.AddDimension(
            transit_callback_index,
            30,  # allow waiting time
            1440,  # maximum time per vehicle (24 hours in minutes)
            False,  # Don't force start cumul to zero
            "Time",
        )
        time_dimension = routing.GetDimensionOrDie("Time")

        # Add time window constraints for each location except depot
        for i in range(1, len(locations)):
            # Get Order's window
            order = self.orders.iloc[i - 1]
            start_hour = order.get("time_window_start", 9)
            end_hour = order.get("time_window_end", 17)

            # Convert hours to minutes from midnight
            start_min = start_hour * 60
            end_min = end_hour * 60

            index = manager.NodeToIndex(i)
            time_dimension.CumulVar(index).SetRange(start_min, end_min)

        # Add time window constraints for depot (e.g., 8 AM to 8 PM)
        depot_start = 8 * 60
        depot_end = 20 * 60
        for i in range(data["num_vehicles"]):
            index = routing.Start(i)
            time_dimension.CumulVar(index).SetRange(depot_start, depot_end)

        # 6. Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = 5  # Quick solve

        solution = routing.SolveWithParameters(search_parameters)

        # 7. Extract Solution
        results = []
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
                        order_info = self.orders.iloc[order_idx].to_dict()
                        route_steps.append(order_info)

                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id
                    )

                if route_steps:  # Only add if vehicle utilized
                    results.append(
                        {
                            "vehicle_id": self.fleet[vehicle_id]["vehicle_id"],
                            "route": route_steps,
                            "total_distance_m": route_distance,
                            "total_load_kg": route_load,
                            "capacity_kg": data["vehicle_capacities"][vehicle_id],
                            "utilization_pct": round(
                                (route_load / data["vehicle_capacities"][vehicle_id])
                                * 100,
                                1,
                            ),
                        }
                    )

        return results


if __name__ == "__main__":
    # Test Run
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    fleet = pd.read_csv(os.path.join(DATA_DIR, "fleet_info.csv")).to_dict("records")

    optimizer = LogisticsOptimizer(fleet, orders)
    routes = optimizer.optimize_routes()

    import json

    print(json.dumps(routes, indent=2))
