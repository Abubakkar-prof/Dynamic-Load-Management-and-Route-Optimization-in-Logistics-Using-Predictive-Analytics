import numpy as np
from typing import List, Dict, Tuple, Optional

class Bin:
    """Represents a bin/container for packing items"""
    def __init__(self, width: float, height: float, depth: float, max_weight: float, bin_id: str = ""):
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
        return self.width * self.height * self.depth

    def get_remaining_volume(self) -> float:
        occupied_volume = sum(item["volume"] for item in self.items)
        return self.get_volume() - occupied_volume

    def can_fit(self, item: Dict) -> bool:
        if self.current_weight + item["weight"] > self.max_weight:
            return False
        if item["volume"] > self.get_remaining_volume():
            return False
        return True

    def add_item(self, item: Dict) -> bool:
        if not self.can_fit(item):
            return False
        item_copy = item.copy()
        if "volume" not in item_copy:
            item_copy["volume"] = item["length"] * item["width"] * item["height"]
        self.items.append(item_copy)
        self.current_weight += item["weight"]
        self.volume_utilization = (sum(i["volume"] for i in self.items) / self.get_volume()) * 100
        self.weight_utilization = (self.current_weight / self.max_weight) * 100
        return True

    def get_utilization(self) -> Dict:
        return {
            "bin_id": self.bin_id,
            "current_weight": self.current_weight,
            "max_weight": self.max_weight,
            "weight_utilization": self.weight_utilization,
            "volume_utilization": self.volume_utilization,
            "item_count": len(self.items),
            "remaining_volume": self.get_remaining_volume()
        }

class Item:
    """Represents an item to be packed"""
    def __init__(self, item_id: str, width: float, height: float, depth: float, weight: float):
        self.item_id = item_id
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.volume = width * height * depth

class ExtremePointBinPacker:
    """Implements a 3D bin packing algorithm using extreme point heuristic"""
    def __init__(self):
        self.bins = []
        self.items = []

    def add_bin(self, bin_obj: Bin):
        self.bins.append(bin_obj)

    def add_item(self, item: Item):
        self.items.append(item)

    def pack_items(self) -> List[Dict]:
        sorted_items = sorted(self.items, key=lambda x: x.volume, reverse=True)
        for bin_obj in self.bins:
            bin_obj.items = []
            bin_obj.current_weight = 0.0
            bin_obj.volume_utilization = 0.0
            bin_obj.weight_utilization = 0.0

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
            placed = False
            for bin_obj in self.bins:
                if bin_obj.add_item(item_dict):
                    placed = True
                    break
            if not placed:
                unpacked_items.append(item_dict)

        results = []
        for bin_obj in self.bins:
            results.append({
                "bin": bin_obj.get_utilization(),
                "packed_items": bin_obj.items,
                "unpacked_items": unpacked_items if bin_obj == self.bins[-1] else []
            })
        return results

def optimize_loading(fleet_data: List[Dict], orders_data: List[Dict]) -> Dict:
    packer = ExtremePointBinPacker()
    for i, vehicle in enumerate(fleet_data):
        bin_obj = Bin(
            width=vehicle.get("width", 2.5),
            height=vehicle.get("height", 2.0),
            depth=vehicle.get("depth", 4.0),
            max_weight=vehicle.get("capacity_kg", 1000),
            bin_id=vehicle.get("vehicle_id", f"VEHICLE-{i}"),
        )
        packer.add_bin(bin_obj)

    for order in orders_data:
        # Default dims if not present
        w = order.get("package_width", order.get("width", 0.5))
        h = order.get("package_height", order.get("height", 0.5))
        d = order.get("package_depth", order.get("depth", 0.5))
        wt = order.get("weight_kg", 1.0)
        
        item = Item(
            item_id=order.get("order_id", "UNKNOWN"),
            width=float(w), height=float(h), depth=float(d), weight=float(wt)
        )
        packer.add_item(item)

    results = packer.pack_items()
    
    # Stats
    total_items = len(orders_data)
    packed_items = sum(len(result["packed_items"]) for result in results)
    unpacked_items = total_items - packed_items
    
    return {
        "packing_results": results,
        "statistics": {
            "total_items": total_items,
            "packed_items": packed_items,
            "packing_efficiency": (packed_items / total_items * 100) if total_items > 0 else 0
        }
    }
