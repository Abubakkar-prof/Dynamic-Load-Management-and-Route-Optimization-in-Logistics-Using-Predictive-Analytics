
print("Importing forms...", flush=True)
try:
    from src.forms import VehicleForm
    print("Imported VehicleForm", flush=True)
except Exception as e:
    print(f"Failed to import forms: {e}", flush=True)
