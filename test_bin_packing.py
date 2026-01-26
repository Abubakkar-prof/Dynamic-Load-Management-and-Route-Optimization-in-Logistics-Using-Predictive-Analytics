from src.optimization.bin_packing import generate_sample_data, optimize_loading

if __name__ == "__main__":
    # Generate sample data
    fleet, orders = generate_sample_data()
    print(f"Generated {len(fleet)} vehicles and {len(orders)} orders")

    # Test optimization
    results = optimize_loading(fleet, orders)
    stats = results["statistics"]
    print(f"Packed {stats['packed_items']} of {stats['total_items']} items")
    print(f"Packing efficiency: {stats['packing_efficiency']:.1f}%")
    print(f"Average volume utilization: {stats['average_volume_utilization']:.1f}%")
    print(f"Average weight utilization: {stats['average_weight_utilization']:.1f}%")
