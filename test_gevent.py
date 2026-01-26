
print("Importing gevent...", flush=True)
try:
    import gevent
    print("gevent imported", flush=True)
    from gevent import monkey
    print("monkey imported", flush=True)
except Exception as e:
    print(f"gevent failed: {e}", flush=True)
