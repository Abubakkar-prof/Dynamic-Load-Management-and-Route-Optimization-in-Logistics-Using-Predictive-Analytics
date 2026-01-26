import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from logistics.models import Order, Vehicle

class LogisticsOptimizer:
    def __init__(self, orders_queryset, vehicles_queryset, depot_location=(31.5204, 74.3587)):
        self.orders = list(orders_queryset)
        self.vehicles = list(vehicles_queryset)
        self.depot = depot_location # Lat, Lon
        
    def calculate_distance_matrix(self, locations):
        """
        Calculates Haversine distance matrix.
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
            
            a = math.sin(delta_phi / 2)**2 + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return int(R * c)

        for from_node in range(size):
            matrix[from_node] = {}
            for to_node in range(size):
                if from_node == to_node:
                    matrix[from_node][to_node] = 0
                else:
                    matrix[from_node][to_node] = haversine(locations[from_node], locations[to_node])
        return matrix

    def optimize_routes(self):
        """
        Solves CVRPTW using Google OR-Tools.
        """
        if not self.orders or not self.vehicles:
            return []

        # 1. Prepare Data
        # Locations: Depot + Order Locations
        locations = [self.depot] + [(o.latitude, o.longitude) for o in self.orders]
        demands_kg = [0] + [int(o.weight_kg) for o in self.orders]
        
        vehicle_capacities = [int(v.capacity_kg) for v in self.vehicles]
        num_vehicles = len(self.vehicles)
        
        data = {
            'distance_matrix': self.calculate_distance_matrix(locations),
            'demands': demands_kg,
            'vehicle_capacities': vehicle_capacities,
            'num_vehicles': num_vehicles,
            'depot': 0
        }
        
        # 2. Create Routing Index Manager
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])

        # 3. Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # 4. Define Distance Callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 5. Add Capacity Constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],
            True,  # start cumul to zero
            'Capacity'
        )
        
        # 6. Time Window Constraint
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = data['distance_matrix'][from_node][to_node] / 11.0 # 40km/h
            travel_time_min = travel_time / 60
            
            if to_node != 0:
                service_time = self.orders[to_node-1].service_time
                return int(travel_time_min + service_time)
            return int(travel_time_min)

        transit_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            transit_callback_index,
            30, 1440, False, 'Time'
        )
        time_dimension = routing.GetDimensionOrDie('Time')
        
        for i in range(1, len(locations)):
            order = self.orders[i-1]
            start_min = order.time_window_start * 60
            end_min = order.time_window_end * 60
            index = manager.NodeToIndex(i)
            time_dimension.CumulVar(index).SetRange(start_min, end_min)

        # 7. Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.time_limit.seconds = 5

        solution = routing.SolveWithParameters(search_parameters)

        # 8. Extract Solution
        results = []
        if solution:
            for vehicle_id in range(data['num_vehicles']):
                index = routing.Start(vehicle_id)
                route_distance = 0
                route_load = 0
                route_steps = []
                
                while not routing.IsEnd(index):
                    node_index = manager.IndexToNode(index)
                    route_load += data['demands'][node_index]
                    
                    if node_index != 0:
                        order = self.orders[node_index - 1]
                        route_steps.append({
                            'order_id': order.order_id,
                            'address': order.delivery_address,
                            'lat': order.latitude,
                            'lon': order.longitude
                        })
                    
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id)
                
                if route_steps:
                    results.append({
                        'vehicle_id': self.vehicles[vehicle_id].vehicle_id,
                        'route': route_steps,
                        'total_distance_m': route_distance,
                        'total_load_kg': route_load,
                        'utilization_pct': round((route_load / data['vehicle_capacities'][vehicle_id]) * 100, 1)
                    })
                    
        return results
