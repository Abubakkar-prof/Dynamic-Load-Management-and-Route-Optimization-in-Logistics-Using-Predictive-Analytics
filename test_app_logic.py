import requests
import re

BASE_URL = "http://127.0.0.1:5000"

def test_app():
    session = requests.Session()
    
    # 1. Get Login Page & CSRF Token
    print("Testing Login Page...")
    response = session.get(f"{BASE_URL}/auth/login")
    if response.status_code == 200:
        print("[SUCCESS] Login page loaded.")
    else:
        print(f"[FAILED] Login page status: {response.status_code}")
        return

    # Check for CSRF token more robustly
    csrf_token = None
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', response.text)
    if not match:
        match = re.search(r'id="csrf_token" name="csrf_token" type="hidden" value="([^"]+)"', response.text)
    if not match:
        match = re.search(r'value="([^"]+)" name="csrf_token"', response.text)
    
    if match:
        csrf_token = match.group(1)
        print(f"[SUCCESS] CSRF Token found: {csrf_token[:10]}...")
    else:
        print("[FAILED] CSRF Token not found in HTML.")
        # print("DEBUG HTML SNIPPET:", response.text[response.text.find("<form"):response.text.find("</form>")+7])
    
    # 2. Login
    print("\nAttempting Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    if csrf_token:
        login_data["csrf_token"] = csrf_token

    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=True)
    if "Intelligence Hub" in response.text or "Dashboard" in response.text or "dashboard" in response.url:
        print("[SUCCESS] Logged in successfully.")
    else:
        print("[FAILED] Login failed. Check credentials or template.")

    # 3. Check Dashboard Stats API
    print("\nTesting Stats API...")
    response = session.get(f"{BASE_URL}/api/stats")
    if response.status_code == 200:
        print(f"[SUCCESS] Stats API returned: {response.json()}")
    else:
        print(f"[FAILED] Stats API status: {response.status_code}")

    # 4. Check Vehicle API
    print("\nTesting Vehicles API...")
    response = session.get(f"{BASE_URL}/api/vehicles/")
    if response.status_code == 200:
        vehicles = response.json()
        print(f"[SUCCESS] Vehicles API returned {len(vehicles)} vehicles.")
    else:
        print(f"[FAILED] Vehicles API list status: {response.status_code}")

    # 5. Check Scenario Templates API
    print("\nTesting Scenario Templates API...")
    response = session.get(f"{BASE_URL}/api/scenario/templates")
    if response.status_code == 200:
        templates = response.json().get("templates", [])
        print(f"[SUCCESS] Found {len(templates)} scenario templates.")
    else:
        print(f"[FAILED] Scenario Templates API status: {response.status_code}")

    # 6. Check Bin Packing Vehicle Types
    print("\nTesting Bin Packing Vehicle Types API...")
    response = session.get(f"{BASE_URL}/api/bin_packing/vehicle_types")
    if response.status_code == 200:
        types = response.json().get("vehicle_types", [])
        print(f"[SUCCESS] Found {len(types)} vehicle types for bin packing.")
    else:
        print(f"[FAILED] Bin Packing API status: {response.status_code}")

    # 7. Check Scenario Baseline API
    print("\nTesting Scenario Baseline API...")
    response = session.get(f"{BASE_URL}/api/scenario/baseline")
    if response.status_code == 200:
        data = response.json()
        if "baseline_data" in data:
            print(f"[SUCCESS] Scenario baseline data loaded: {len(data['baseline_data']['vehicles'])} vehicles.")
        else:
             print(f"[FAILED] Scenario baseline missing 'baseline_data' key: {data}")
    else:
        print(f"[FAILED] Scenario Baseline API status: {response.status_code}")

if __name__ == "__main__":
    test_app()
