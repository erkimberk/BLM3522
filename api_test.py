"""
REST API Test Script
Flask API endpoint'lerini test et

Kullanım:
    python api_test.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Renkler
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
END = "\033[0m"


def print_header(title):
    """Header yazdır"""
    print(f"\n{BLUE}{'=' * 60}{END}")
    print(f"{BLUE}{title:^60}{END}")
    print(f"{BLUE}{'=' * 60}{END}\n")


def print_test(name, passed, response=None):
    """Test sonucu yazdır"""
    status = f"{GREEN}✅ PASS{END}" if passed else f"{RED}❌ FAIL{END}"
    print(f"  {status} | {name}")
    if response and not passed:
        print(f"       Response: {response}")


def test_health():
    """Health check test"""
    print_header("🏥 API Health Check Test")

    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200

        print_test("Health endpoint accessible", passed)

        if passed:
            data = response.json()
            print(f"    Status: {data.get('status')}")
            print(f"    Database: {data.get('database')}")
            print(f"    Version: {data.get('version')}")
    except Exception as e:
        print_test("Health endpoint accessible", False, str(e))


def test_sensors():
    """Sensör data endpoint'leri test"""
    print_header("📊 Sensor Endpoints Test")

    sensor_types = ["traffic_light", "air_quality", "trash_bin"]

    for sensor_type in sensor_types:
        # Test 1: Latest readings
        try:
            url = f"{BASE_URL}/sensors/{sensor_type}?limit=5"
            response = requests.get(url)
            passed = response.status_code == 200

            print_test(f"GET /sensors/{sensor_type}", passed)

            if passed:
                data = response.json()
                print(f"       Data count: {data.get('count')}")
                if data.get("data"):
                    latest = data["data"][0]
                    print(f"       Latest value: {latest.get('value')}")
                    print(f"       Timestamp: {latest.get('timestamp')}")
        except Exception as e:
            print_test(f"GET /sensors/{sensor_type}", False, str(e))

        # Test 2: Device history
        device_map = {
            "traffic_light": "traffic-light-001",
            "air_quality": "air-quality-001",
            "trash_bin": "trash-bin-001",
        }
        device_id = device_map[sensor_type]

        try:
            url = f"{BASE_URL}/sensors/{sensor_type}/{device_id}?hours=1"
            response = requests.get(url)
            passed = response.status_code == 200

            print_test(f"GET /sensors/{sensor_type}/{device_id}", passed)

            if passed:
                data = response.json()
                stats = data.get("statistics", {})
                print(f"       Data count: {stats.get('count')}")
                print(f"       Min: {stats.get('min')}")
                print(f"       Max: {stats.get('max')}")
                print(f"       Avg: {stats.get('avg')}")
        except Exception as e:
            print_test(f"GET /sensors/{sensor_type}/{device_id}", False, str(e))


def test_alerts():
    """Uyarılar endpoint'i test"""
    print_header("⚠️ Alerts Endpoint Test")

    try:
        # Test 1: All alerts
        response = requests.get(f"{BASE_URL}/alerts")
        passed = response.status_code == 200

        print_test("GET /alerts", passed)

        if passed:
            data = response.json()
            print(f"    Total alerts: {data.get('total')}")
            if data.get("alerts"):
                alert = data["alerts"][0]
                print(f"    Sample alert:")
                print(f"      - Device: {alert.get('device_id')}")
                print(f"      - Severity: {alert.get('severity')}")
                print(f"      - Message: {alert.get('message')[:50]}...")

        # Test 2: Filtered alerts
        response = requests.get(f"{BASE_URL}/alerts?severity=critical")
        passed = response.status_code == 200

        print_test("GET /alerts?severity=critical", passed)

        if passed:
            data = response.json()
            print(f"    Critical alerts: {data.get('total')}")

    except Exception as e:
        print_test("GET /alerts", False, str(e))


def test_stats():
    """İstatistikler endpoint'i test"""
    print_header("📈 Statistics Endpoint Test")

    device_map = {
        "traffic_light": "traffic-light-001",
        "air_quality": "air-quality-001",
        "trash_bin": "trash-bin-001",
    }

    for sensor_type, device_id in device_map.items():
        try:
            url = f"{BASE_URL}/stats/{sensor_type}/{device_id}"
            response = requests.get(url)
            passed = response.status_code == 200

            print_test(f"GET /stats/{sensor_type}/{device_id}", passed)

            if passed:
                data = response.json()
                stats = data.get("statistics", {})
                print(f"    Statistics (24h):")
                print(f"      - Count: {stats.get('count')}")
                print(f"      - Min: {stats.get('min')}")
                print(f"      - Max: {stats.get('max')}")
                print(f"      - Avg: {stats.get('avg')}")

        except Exception as e:
            print_test(f"GET /stats/{sensor_type}/{device_id}", False, str(e))


def test_performance():
    """Performance test"""
    print_header("⚡ Performance Test")

    import time

    endpoints = [
        "/health",
        "/sensors/traffic_light",
        "/sensors/air_quality",
        "/sensors/trash_bin",
        "/alerts",
    ]

    print("  Response times:")
    total_time = 0

    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = (time.time() - start) * 1000  # Convert to ms

            if elapsed < 500:
                status = f"{GREEN}✓{END}"
            elif elapsed < 1000:
                status = f"{YELLOW}⚠{END}"
            else:
                status = f"{RED}✗{END}"

            print(f"    {status} {endpoint:40} {elapsed:6.1f} ms")
            total_time += elapsed

        except Exception as e:
            print(f"    {RED}✗{END} {endpoint:40} ERROR: {e}")

    avg_time = total_time / len(endpoints)
    print(f"\n  Average response time: {avg_time:.1f} ms")

    if avg_time < 500:
        print(f"  {GREEN}✅ Performance is excellent!{END}")
    elif avg_time < 1000:
        print(f"  {YELLOW}⚠️  Performance is acceptable{END}")
    else:
        print(f"  {RED}❌ Performance needs improvement{END}")


def main():
    """Main test function"""
    print("\n")
    print(f"{BLUE}{'*' * 60}{END}")
    print(f"{BLUE}{'🧪 Smart City REST API Test Suite':^60}{END}")
    print(f"{BLUE}{'*' * 60}{END}")

    try:
        # Test API connectivity first
        print(f"\n{YELLOW}Checking API connectivity...{END}")
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"{GREEN}✅ API is reachable{END}")
    except Exception as e:
        print(f"{RED}❌ API is NOT reachable!{END}")
        print(f"   Make sure the Flask server is running:")
        print(f"   python src/api/app.py")
        return

    # Run tests
    test_health()
    test_sensors()
    test_alerts()
    test_stats()
    test_performance()

    # Summary
    print_header("✨ Test Suite Complete")
    print(f"{GREEN}All critical tests completed!{END}\n")


if __name__ == "__main__":
    main()
