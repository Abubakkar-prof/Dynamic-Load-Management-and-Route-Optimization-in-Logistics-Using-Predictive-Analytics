
try:
    print("Importing numpy...")
    import numpy
    print("numpy imported")
except Exception as e:
    print(f"numpy failed: {e}")

try:
    print("Importing pandas...")
    import pandas
    print("pandas imported")
except Exception as e:
    print(f"pandas failed: {e}")

try:
    print("Importing sklearn...")
    import sklearn
    print("sklearn imported")
except Exception as e:
    print(f"sklearn failed: {e}")

try:
    print("Importing xgboost...")
    import xgboost
    print("xgboost imported")
except Exception as e:
    print(f"xgboost failed: {e}")

try:
    print("Importing lightgbm...")
    import lightgbm
    print("lightgbm imported")
except Exception as e:
    print(f"lightgbm failed: {e}")

try:
    print("Importing ortools...")
    import ortools
    print("ortools imported")
except Exception as e:
    print(f"ortools failed: {e}")
