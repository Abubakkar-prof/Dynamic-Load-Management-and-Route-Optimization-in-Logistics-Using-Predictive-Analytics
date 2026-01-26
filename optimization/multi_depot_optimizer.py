"""
Multi-Depot Logistics Optimizer
Extends CVRP to support multiple warehouses/depots.
"""
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from logistics.models import Order, Vehicle, Depot

class MultiDepotOptimizer:
    """
    Solves Multi-Depot Vehicle Routing Problem (MDVRP).
    """
    
    def __init__(self, orders_queryset, vehicles_queryset, depots_queryset):
        self.orders = list(orders_queryset)
        self.vehicles = list(vehicles_queryset)
        self.depots = list(depots_queryset)
        
    def calculate_distance(self, pos1, pos2):
        lat1, lon1 = pos1
        lat2, lon2 = pos2
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return int(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

    def optimize(self):
        """
        Solves MDVRP by assigning orders to nearest depots and solving CVRP.
        """
        if not self.orders or not self.vehicles or not self.depots:
            return []

        # 1. Assign each order to its nearest depot
        depot_assignments = {depot.id: [] for depot in self.depots}
        for order in self.orders:
            nearest_depot = min(self.depots, 
                                key=lambda d: self.calculate_distance((d.latitude, d.longitude), 
                                                                    (order.latitude, order.longitude)))
            depot_assignments[nearest_depot.id].append(order)

        # 2. Group vehicles by depot
        vehicle_assignments = {depot.id: [] for depot in self.depots}
        for vehicle in self.vehicles:
            if vehicle.depot:
                vehicle_assignments[vehicle.depot.id].append(vehicle)
            else:
                # Assign unassigned vehicles to the first depot for now
                vehicle_assignments[self.depots[0].id].append(vehicle)

        # 3. Solve CVRP for each depot
        results = []
        from optimization.services import LogisticsOptimizer
        
        for depot in self.depots:
            orders_at_depot = depot_assignments[depot.id]
            vehicles_at_depot = vehicle_assignments[depot.id]
            
            if not orders_at_depot or not vehicles_at_depot:
                continue
                
            optimizer = LogisticsOptimizer(
                orders_at_depot, 
                vehicles_at_depot, 
                depot_location=(depot.latitude, depot.longitude)
            )
            depot_results = optimizer.optimize_routes()
            
            for res in depot_results:
                res['depot_name'] = depot.name
                results.append(res)
                
        return results
