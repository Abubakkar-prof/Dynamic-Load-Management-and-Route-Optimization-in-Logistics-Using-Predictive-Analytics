
import sys

print("Starting tests...", flush=True)

try:
    print("Importing lightgbm...", flush=True)
    import lightgbm
    print("lightgbm imported", flush=True)
except Exception as e:
    print(f"lightgbm failed: {e}", flush=True)

try:
    print("Importing ortools...", flush=True)
    import ortools
    print("ortools imported", flush=True)
except Exception as e:
    print(f"ortools failed: {e}", flush=True)
