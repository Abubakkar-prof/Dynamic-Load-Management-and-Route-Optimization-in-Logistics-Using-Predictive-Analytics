
try:
    print("Importing ortools...", flush=True)
    from ortools.constraint_solver import pywrapcp
    print("ortools.constraint_solver.pywrapcp imported successfully", flush=True)
except Exception as e:
    print(f"ortools failed: {e}", flush=True)
except ImportError as e:
    print(f"ortools ImportError: {e}", flush=True)
