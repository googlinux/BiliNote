"""
API Integration Tests for BiliNote SaaS

Run with: python -m pytest tests/test_api.py -v
Or manually: python tests/test_api.py
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8483"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "Test1234!"
TEST_NAME = "Test User"

# Global variables to store tokens
access_token = None
refresh_token = None


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'


def print_test(name):
    """Print test name"""
    print(f"\n{Colors.BLUE}▶ Testing: {name}{Colors.END}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 404:
            # Health endpoint might not exist, that's okay
            print_info("Health endpoint not found (optional)")
            return True

        response.raise_for_status()
        print_success("Server is running")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_user_registration():
    """Test user registration"""
    print_test("User Registration")

    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": TEST_NAME
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            user_data = result["data"]
            print_success(f"User registered: {user_data['email']}")
            print_info(f"User ID: {user_data['id']}")
            return True
        else:
            print_error(f"Registration failed: {result}")
            return False

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_detail = e.response.json().get("detail", "Unknown error")
            print_error(f"Registration failed: {error_detail}")
        else:
            print_error(f"HTTP Error: {e}")
        return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False


def test_user_login():
    """Test user login"""
    global access_token, refresh_token
    print_test("User Login")

    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            token_data = result["data"]
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
            print_success("Login successful")
            print_info(f"Access token: {access_token[:20]}...")
            return True
        else:
            print_error(f"Login failed: {result}")
            return False

    except Exception as e:
        print_error(f"Login error: {e}")
        return False


def test_get_current_user():
    """Test getting current user info"""
    print_test("Get Current User")

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            user_data = result["data"]
            print_success(f"Retrieved user: {user_data['email']}")
            print_info(f"Active: {user_data['is_active']}")
            return True
        else:
            print_error(f"Failed to get user: {result}")
            return False

    except Exception as e:
        print_error(f"Get user error: {e}")
        return False


def test_get_subscription():
    """Test getting user subscription"""
    print_test("Get Subscription")

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/subscription/current", headers=headers)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            sub_data = result["data"]
            print_success(f"Subscription plan: {sub_data['plan_type']}")
            print_info(f"Status: {sub_data['status']}")
            print_info(f"Videos: {sub_data['videos_used']}/{sub_data['max_videos_per_month']}")
            return True
        else:
            print_error(f"Failed to get subscription: {result}")
            return False

    except Exception as e:
        print_error(f"Get subscription error: {e}")
        return False


def test_get_usage():
    """Test getting usage statistics"""
    print_test("Get Usage Statistics")

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/subscription/usage", headers=headers)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            usage_data = result["data"]
            print_success("Usage statistics retrieved")
            print_info(f"Videos used: {usage_data['videos_used']}/{usage_data['videos_limit']}")
            print_info(f"Duration used: {usage_data['duration_used_minutes']} min")
            return True
        else:
            print_error(f"Failed to get usage: {result}")
            return False

    except Exception as e:
        print_error(f"Get usage error: {e}")
        return False


def test_get_plans():
    """Test getting available plans"""
    print_test("Get Available Plans")

    try:
        response = requests.get(f"{BASE_URL}/api/subscription/plans")
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            plans = result["data"]
            print_success(f"Retrieved {len(plans)} plans")
            for plan in plans:
                print_info(f"- {plan['plan_type']}: ${plan['price_monthly']}/month")
            return True
        else:
            print_error(f"Failed to get plans: {result}")
            return False

    except Exception as e:
        print_error(f"Get plans error: {e}")
        return False


def test_token_refresh():
    """Test token refresh"""
    global access_token
    print_test("Token Refresh")

    data = {"refresh_token": refresh_token}

    try:
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("data"):
            token_data = result["data"]
            access_token = token_data["access_token"]
            print_success("Token refreshed successfully")
            print_info(f"New token: {access_token[:20]}...")
            return True
        else:
            print_error(f"Token refresh failed: {result}")
            return False

    except Exception as e:
        print_error(f"Token refresh error: {e}")
        return False


def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    print_test("Protected Endpoint (No Auth)")

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")

        if response.status_code == 401:
            print_success("Correctly rejected unauthenticated request")
            return True
        else:
            print_error(f"Should have returned 401, got {response.status_code}")
            return False

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print_success("Correctly rejected unauthenticated request")
            return True
        else:
            print_error(f"Unexpected error: {e}")
            return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}BiliNote SaaS API Integration Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test Email: {TEST_EMAIL}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Health Check", test_health_check),
        ("User Registration", test_user_registration),
        ("User Login", test_user_login),
        ("Get Current User", test_get_current_user),
        ("Get Subscription", test_get_subscription),
        ("Get Usage", test_get_usage),
        ("Get Plans", test_get_plans),
        ("Token Refresh", test_token_refresh),
        ("Protected Endpoint (No Auth)", test_protected_endpoint_without_auth),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((name, False))
        time.sleep(0.5)  # Small delay between tests

    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {name}")

    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total: {len(results)} | Passed: {Colors.GREEN}{passed}{Colors.END} | Failed: {Colors.RED}{failed}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        exit(1)
