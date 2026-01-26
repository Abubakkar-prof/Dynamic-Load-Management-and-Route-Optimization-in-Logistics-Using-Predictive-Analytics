import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json


class Bin:
    """
    Represents a bin/container for packing items
    """

    def __init__(
        self,
        width: float,
        height: float,
        depth: float,
        max_weight: float,
        bin_id: str = "",
    ):
        self.width = width
        self.height = height
        self.depth = depth
        self.max_weight = max_weight
        self.current_weight = 0.0
        self.items = []
        self.bin_id = bin_id
        self.volume_utilization = 0.0
        self.weight_utilization = 0.0

    def get_volume(self) -> float:
        """Calculate total volume of the bin"""
        return self.width * self.height * self.depth

    def get_remaining_volume(self) -> float:
        """Calculate remaining volume in the bin"""
        occupied_volume = sum(item["volume"] for item in self.items)
        return self.get_volume() - occupied_volume

    def get_remaining_weight(self) -> float:
        """Calculate remaining weight capacity"""
        return self.max_weight - self.current_weight

    def can_fit(self, item: Dict) -> bool:
        """
        Check if an item can fit in this bin based on weight and volume
        """
        # Check weight constraint
        if self.current_weight + item["weight"] > self.max_weight:
            return False

        # Check volume constraint (simplified - in reality would need 3D placement algorithm)
        item_volume = item["volume"]
        if item_volume > self.get_remaining_volume():
            return False

        return True

    def add_item(self, item: Dict) -> bool:
        """
        Add an item to the bin if it fits
        """
        if not self.can_fit(item):
            return False

        # Add item to bin
        item_copy = item.copy()
        if "volume" not in item_copy:
            item_copy["volume"] = item["length"] * item["width"] * item["height"]
        self.items.append(item_copy)
        self.current_weight += item["weight"]

        # Update utilization metrics
        self.volume_utilization = (
            sum(i["volume"] for i in self.items) / self.get_volume()
        ) * 100
        self.weight_utilization = (self.current_weight / self.max_weight) * 100

        return True

    def get_utilization(self) -> Dict:
        """
        Get bin utilization statistics
        """
        return {
            "bin_id": self.bin_id,
            "current_weight": self.current_weight,
            "max_weight": self.max_weight,
            "weight_utilization": self.weight_utilization,
            "volume_utilization": self.volume_utilization,
            "item_count": len(self.items),
            "remaining_volume": self.get_remaining_volume(),
            "remaining_weight": self.get_remaining_weight(),
        }


class Item:
    """
    Represents an item to be packed
    """

    def __init__(
        self, item_id: str, width: float, height: float, depth: float, weight: float
    ):
        self.item_id = item_id
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.length = depth  # For compatibility with existing code
        self.volume = width * height * depth


class ExtremePointBinPacker:
    """
    Implements a 3D bin packing algorithm using extreme point heuristic
    """

    def __init__(self):
        self.bins = []
        self.items = []

    def add_bin(self, bin_obj: Bin):
        """Add a bin to the packer"""
        self.bins.append(bin_obj)

    def add_item(self, item: Item):
        """Add an item to be packed"""
        self.items.append(item)

    def pack_items(self) -> List[Dict]:
        """
        Pack items into bins using extreme point heuristic
        Returns packing results for each bin
        """
        # Sort items by volume (largest first) for better packing
        sorted_items = sorted(self.items, key=lambda x: x.volume, reverse=True)

        # Reset bins
        for bin_obj in self.bins:
            bin_obj.items = []
            bin_obj.current_weight = 0.0
            bin_obj.volume_utilization = 0.0
            bin_obj.weight_utilization = 0.0

        # Pack items
        unpacked_items = []

        for item in sorted_items:
            item_dict = {
                "item_id": item.item_id,
                "width": item.width,
                "height": item.height,
                "depth": item.depth,
                "weight": item.weight,
                "volume": item.volume,
            }

            # Try to place item in existing bins
            placed = False
            for bin_obj in self.bins:
                if bin_obj.add_item(item_dict):
                    placed = True
                    break

            if not placed:
                unpacked_items.append(item_dict)

        # Prepare results
        results = []
        for bin_obj in self.bins:
            results.append(
                {
                    "bin": bin_obj.get_utilization(),
                    "packed_items": bin_obj.items,
                    "unpacked_items": (
                        unpacked_items if bin_obj == self.bins[-1] else []
                    ),
                }
            )

        return results


def optimize_loading(fleet_data: List[Dict], orders_data: List[Dict]) -> Dict:
    """
    Optimize loading of orders into vehicles using 3D bin packing

    Args:
        fleet_data: List of vehicles with dimensions and weight capacity
        orders_data: List of orders with package dimensions and weights

    Returns:
        Dictionary with packing results and statistics
    """
    # Create bin packer
    packer = ExtremePointBinPacker()

    # Add bins (vehicles)
    for i, vehicle in enumerate(fleet_data):
        bin_obj = Bin(
            width=vehicle.get("width", 2.5),  # meters
            height=vehicle.get("height", 2.0),  # meters
            depth=vehicle.get("depth", 4.0),  # meters
            max_weight=vehicle.get("capacity_kg", 1000),
            bin_id=vehicle.get("vehicle_id", f"VEHICLE-{i}"),
        )
        packer.add_bin(bin_obj)

    # Add items (packages)
    for order in orders_data:
        item = Item(
            item_id=order.get("order_id", "UNKNOWN"),
            width=order.get("package_width", 0.3),  # meters
            height=order.get("package_height", 0.2),  # meters
            depth=order.get("package_depth", 0.3),  # meters
            weight=order.get("weight_kg", 1.0),
        )
        packer.add_item(item)

    # Pack items
    results = packer.pack_items()

    # Calculate overall statistics
    total_items = len(orders_data)
    packed_items = sum(len(result["packed_items"]) for result in results)
    unpacked_items = total_items - packed_items

    # Calculate utilization statistics
    total_volume_capacity = sum(
        bin_result["bin"]["max_weight"] for bin_result in results
    )
    total_weight_loaded = sum(
        bin_result["bin"]["current_weight"] for bin_result in results
    )

    avg_volume_utilization = (
        np.mean([r["bin"]["volume_utilization"] for r in results]) if results else 0
    )
    avg_weight_utilization = (
        np.mean([r["bin"]["weight_utilization"] for r in results]) if results else 0
    )

    return {
        "packing_results": results,
        "statistics": {
            "total_items": total_items,
            "packed_items": packed_items,
            "unpacked_items": unpacked_items,
            "packing_efficiency": (
                (packed_items / total_items * 100) if total_items > 0 else 0
            ),
            "average_volume_utilization": avg_volume_utilization,
            "average_weight_utilization": avg_weight_utilization,
            "total_weight_loaded": total_weight_loaded,
            "total_volume_capacity": total_volume_capacity,
        },
    }


def generate_sample_data():
    """
    Generate sample data for testing the bin packing algorithm
    """
    # Sample fleet data
    fleet = [
        {
            "vehicle_id": "VAN-001",
            "type": "Van",
            "width": 2.0,  # meters
            "height": 1.8,  # meters
            "depth": 3.0,  # meters
            "capacity_kg": 1000,
        },
        {
            "vehicle_id": "VAN-002",
            "type": "Van",
            "width": 2.0,
            "height": 1.8,
            "depth": 3.0,
            "capacity_kg": 1000,
        },
        {
            "vehicle_id": "TRUCK-001",
            "type": "Truck",
            "width": 2.5,
            "height": 2.0,
            "depth": 4.0,
            "capacity_kg": 3000,
        },
    ]

    # Sample orders data
    np.random.seed(42)
    orders = []
    for i in range(50):
        orders.append(
            {
                "order_id": f"ORDER-{1000+i}",
                "package_width": round(np.random.uniform(0.1, 0.8), 2),  # meters
                "package_height": round(np.random.uniform(0.1, 0.6), 2),  # meters
                "package_depth": round(np.random.uniform(0.1, 0.8), 2),  # meters
                "weight_kg": round(np.random.uniform(0.5, 20), 2),  # kg
                "volume_m3": round(np.random.uniform(0.01, 0.5), 2),  # m³
            }
        )

    return fleet, orders


if __name__ == "__main__":
    # Generate sample data
    fleet, orders = generate_sample_data()

    # Optimize loading
    results = optimize_loading(fleet, orders)

    # Print results
    print("3D Bin Packing Results:")
    print("=" * 50)
    print(f"Total Items: {results['statistics']['total_items']}")
    print(f"Packed Items: {results['statistics']['packed_items']}")
    print(f"Unpacked Items: {results['statistics']['unpacked_items']}")
    print(f"Packing Efficiency: {results['statistics']['packing_efficiency']:.1f}%")
    print(
        f"Average Volume Utilization: {results['statistics']['average_volume_utilization']:.1f}%"
    )
    print(
        f"Average Weight Utilization: {results['statistics']['average_weight_utilization']:.1f}%"
    )
    print()

    # Print per-bin results
    for i, bin_result in enumerate(results["packing_results"]):
        bin_info = bin_result["bin"]
        print(f"Bin {bin_info['bin_id']}:")
        print(f"  Items: {bin_info['item_count']}")
        print(
            f"  Weight: {bin_info['current_weight']:.1f}/{bin_info['max_weight']:.1f} kg ({bin_info['weight_utilization']:.1f}%)"
        )
        print(f"  Volume Utilization: {bin_info['volume_utilization']:.1f}%")
        print()
