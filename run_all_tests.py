#!/usr/bin/env python3
"""
MandirSync Comprehensive System Test
Tests ALL components end-to-end and catches all bugs

Location: D:\MandirSync\run_all_tests.py
Usage: python run_all_tests.py
"""

import requests
import sys
import json
from datetime import datetime, date
import time

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test credentials - update if different
TEST_CREDENTIALS = {
    "email": "admin@temple.com",
    "password": "admin123"
}

# ============================================================
# COLORS FOR OUTPUT
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ============================================================
# PRINT UTILITIES
# ============================================================

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}→ {text}{Colors.END}")

def print_subsection(text):
    print(f"\n{Colors.MAGENTA}  ▸ {text}{Colors.END}")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"    {status}  {name}")
    if details and not passed:
        print(f"           {Colors.YELLOW}→ {details}{Colors.END}")
    return passed

def print_error(message):
    print(f"{Colors.RED}{Colors.BOLD}ERROR: {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}WARNING: {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}INFO: {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}{Colors.BOLD}SUCCESS: {message}{Colors.END}")

# ============================================================
# GLOBAL TEST STATS
# ============================================================

class TestStats:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record(self, name, passed, details=""):
        self.total += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append({"test": name, "details": details})
        return passed

stats = TestStats()

# ============================================================
# TEST FUNCTIONS - INFRASTRUCTURE
# ============================================================

def test_backend_server():
    """Test if backend server is running"""
    print_section("1. Backend Server Tests")

    all_passed = True

    # Test 1: Server reachable
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        all_passed &= stats.record("Backend server reachable", response.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_warning("Start backend: cd backend && python -m uvicorn app.main:app --reload")
        stats.record("Backend server reachable", False, "Connection refused")
        return False
    except Exception as e:
        stats.record("Backend server reachable", False, str(e))
        return False

    # Test 2: API documentation available
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        all_passed &= stats.record("API documentation available", response.status_code == 200)
    except Exception as e:
        stats.record("API documentation available", False, str(e))

    # Test 3: CORS headers
    try:
        response = requests.options(f"{BASE_URL}/api/v1/temples/", timeout=5)
        has_cors = 'access-control-allow-origin' in response.headers
        all_passed &= stats.record("CORS configured", has_cors)
    except Exception as e:
        stats.record("CORS configured", False, str(e))

    return all_passed

def test_frontend_server():
    """Test if frontend server is running"""
    print_section("2. Frontend Server Tests")

    all_passed = True

    # Test 1: Frontend reachable
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        all_passed &= stats.record("Frontend server reachable", response.status_code == 200)
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to frontend at {FRONTEND_URL}")
        print_warning("Start frontend: cd frontend && npm start")
        stats.record("Frontend server reachable", False, "Connection refused")
        return False
    except Exception as e:
        stats.record("Frontend server reachable", False, str(e))
        return False

    # Test 2: React app loads
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        has_react = 'root' in response.text
        all_passed &= stats.record("React app loads", has_react)
    except Exception as e:
        stats.record("React app loads", False, str(e))

    return all_passed

# ============================================================
# TEST FUNCTIONS - AUTHENTICATION
# ============================================================

def test_authentication():
    """Test authentication system"""
    print_section("3. Authentication & Security Tests")

    all_passed = True
    token = None

    # Test 1: Login endpoint exists
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=TEST_CREDENTIALS,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                all_passed &= stats.record("Login successful", True)
                all_passed &= stats.record("JWT token generated", len(token) > 0)
            else:
                all_passed &= stats.record("Login successful", False, "No access_token in response")
        elif response.status_code == 401:
            all_passed &= stats.record("Login successful", False, "Invalid credentials")
            print_warning("Run: cd backend && python scripts/create_admin_user_simple.py")
        else:
            all_passed &= stats.record("Login successful", False, f"Status: {response.status_code}")
    except Exception as e:
        all_passed &= stats.record("Login successful", False, str(e))

    # Test 2: Invalid credentials rejected
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": "wrong@test.com", "password": "wrong"},
            timeout=5
        )
        all_passed &= stats.record("Invalid credentials rejected", response.status_code == 401)
    except Exception as e:
        stats.record("Invalid credentials rejected", False, str(e))

    # Test 3: Protected endpoint requires auth
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/", timeout=5)
        all_passed &= stats.record("Protected endpoints require auth", response.status_code == 401)
    except Exception as e:
        stats.record("Protected endpoints require auth", False, str(e))

    # Test 4: Valid token works
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers, timeout=5)
            all_passed &= stats.record("Token authentication works", response.status_code == 200)
        except Exception as e:
            stats.record("Token authentication works", False, str(e))

    return all_passed, token

# ============================================================
# TEST FUNCTIONS - DATABASE
# ============================================================

def test_database_integrity(token):
    """Test database setup and integrity"""
    print_section("4. Database Integrity Tests")

    if not token:
        print_error("No auth token - skipping database tests")
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Chart of accounts exists
    try:
        response = requests.get(f"{BASE_URL}/api/v1/accounts/", headers=headers, timeout=5)
        if response.status_code == 200:
            accounts = response.json()
            all_passed &= stats.record("Chart of Accounts exists", len(accounts) > 0,
                                      f"Found {len(accounts)} accounts")

            # Test essential accounts
            account_codes = [acc.get('account_code') for acc in accounts]
            essential_accounts = {
                '1101': 'Cash in Hand - Counter',
                '1110': 'Bank Account',
                '4101': 'General Donation Income',
                '5101': 'Priest Salaries',
                '5102': 'Staff Salaries'
            }

            print_subsection("Essential Accounts")
            for code, name in essential_accounts.items():
                exists = code in account_codes
                all_passed &= stats.record(f"Account {code} ({name})", exists)
        else:
            all_passed &= stats.record("Chart of Accounts exists", False)
    except Exception as e:
        stats.record("Chart of Accounts exists", False, str(e))

    # Test 2: Temple configuration
    try:
        response = requests.get(f"{BASE_URL}/api/v1/temples/", headers=headers, timeout=5)
        if response.status_code == 200:
            temples = response.json()
            all_passed &= stats.record("Temple configured", len(temples) > 0,
                                      f"Found {len(temples)} temple(s)")
        else:
            all_passed &= stats.record("Temple configured", False)
    except Exception as e:
        stats.record("Temple configured", False, str(e))

    # Test 3: Donation categories exist
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/categories/", headers=headers, timeout=5)
        if response.status_code == 200:
            categories = response.json()
            all_passed &= stats.record("Donation categories exist", len(categories) > 0,
                                      f"Found {len(categories)} categories")
        else:
            all_passed &= stats.record("Donation categories exist", False)
    except Exception as e:
        stats.record("Donation categories exist", False, str(e))

    return all_passed

# ============================================================
# TEST FUNCTIONS - CORE MODULES
# ============================================================

def test_devotee_management(token):
    """Test devotee management"""
    print_section("5. Devotee Management Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List devotees
    try:
        response = requests.get(f"{BASE_URL}/api/v1/devotees/", headers=headers, timeout=5)
        all_passed &= stats.record("List devotees", response.status_code == 200)
    except Exception as e:
        stats.record("List devotees", False, str(e))

    # Test 2: Create devotee
    devotee_id = None
    try:
        test_devotee = {
            "name": f"Test Devotee {int(time.time())}",
            "phone": "9876543210",
            "email": f"test{int(time.time())}@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/v1/devotees/",
                                headers=headers, json=test_devotee, timeout=5)
        if response.status_code in [200, 201]:
            devotee_id = response.json().get('id')
            all_passed &= stats.record("Create devotee", True)
        else:
            all_passed &= stats.record("Create devotee", False, f"Status: {response.status_code}")
    except Exception as e:
        stats.record("Create devotee", False, str(e))

    # Test 3: Read devotee
    if devotee_id:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/devotees/{devotee_id}",
                                   headers=headers, timeout=5)
            all_passed &= stats.record("Read devotee", response.status_code == 200)
        except Exception as e:
            stats.record("Read devotee", False, str(e))

    # Test 4: Update devotee
    if devotee_id:
        try:
            update_data = {"address": "Test Address"}
            response = requests.put(f"{BASE_URL}/api/v1/devotees/{devotee_id}",
                                   headers=headers, json=update_data, timeout=5)
            all_passed &= stats.record("Update devotee", response.status_code == 200)
        except Exception as e:
            stats.record("Update devotee", False, str(e))

    return all_passed

def test_donation_management(token):
    """Test donation management"""
    print_section("6. Donation Management Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List donations
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/", headers=headers, timeout=5)
        all_passed &= stats.record("List donations", response.status_code == 200)
    except Exception as e:
        stats.record("List donations", False, str(e))

    # Test 2: Get donation categories
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/categories/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Get donation categories", response.status_code == 200)
    except Exception as e:
        stats.record("Get donation categories", False, str(e))

    # Test 3: Donation filtering
    try:
        today = date.today().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/v1/donations/?start_date={today}&end_date={today}",
            headers=headers, timeout=5
        )
        all_passed &= stats.record("Donation filtering works", response.status_code == 200)
    except Exception as e:
        stats.record("Donation filtering works", False, str(e))

    return all_passed

def test_seva_management(token):
    """Test seva management"""
    print_section("7. Seva Management Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List sevas
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sevas/", headers=headers, timeout=5)
        all_passed &= stats.record("List sevas", response.status_code == 200)
    except Exception as e:
        stats.record("List sevas", False, str(e))

    # Test 2: List seva bookings
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sevas/bookings/", headers=headers, timeout=5)
        all_passed &= stats.record("List seva bookings", response.status_code == 200)
    except Exception as e:
        stats.record("List seva bookings", False, str(e))

    # Test 3: Seva schedule
    try:
        today = date.today().isoformat()
        response = requests.get(f"{BASE_URL}/api/v1/sevas/schedule/?date={today}",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Seva schedule", response.status_code == 200)
    except Exception as e:
        stats.record("Seva schedule", False, str(e))

    return all_passed

def test_accounting_module(token):
    """Test accounting module"""
    print_section("8. Accounting Module Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    print_subsection("Chart of Accounts")

    # Test 1: Get accounts
    try:
        response = requests.get(f"{BASE_URL}/api/v1/accounts/", headers=headers, timeout=5)
        all_passed &= stats.record("Get chart of accounts", response.status_code == 200)
    except Exception as e:
        stats.record("Get chart of accounts", False, str(e))

    print_subsection("Journal Entries")

    # Test 2: Get journal entries
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Get journal entries", response.status_code == 200)
    except Exception as e:
        stats.record("Get journal entries", False, str(e))

    # Test 3: Day book
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/day-book/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Day book report", response.status_code == 200)
    except Exception as e:
        stats.record("Day book report", False, str(e))

    # Test 4: Cash book
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/cash-book/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Cash book report", response.status_code == 200)
    except Exception as e:
        stats.record("Cash book report", False, str(e))

    return all_passed

# ============================================================
# TEST FUNCTIONS - NEW MODULES
# ============================================================

def test_hr_module(token):
    """Test HR module"""
    print_section("9. HR Module Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List employees
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/employees/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List employees", response.status_code == 200)
    except Exception as e:
        stats.record("List employees", False, str(e))

    # Test 2: List departments
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/departments/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List departments", response.status_code == 200)
    except Exception as e:
        stats.record("List departments", False, str(e))

    # Test 3: List designations
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/designations/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List designations", response.status_code == 200)
    except Exception as e:
        stats.record("List designations", False, str(e))

    return all_passed

def test_inventory_module(token):
    """Test inventory module"""
    print_section("10. Inventory Module Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List items
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/items/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List inventory items", response.status_code == 200)
    except Exception as e:
        stats.record("List inventory items", False, str(e))

    # Test 2: List stores
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/stores/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List stores", response.status_code == 200)
    except Exception as e:
        stats.record("List stores", False, str(e))

    # Test 3: List transactions
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/transactions/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List transactions", response.status_code == 200)
    except Exception as e:
        stats.record("List transactions", False, str(e))

    return all_passed

def test_asset_module(token):
    """Test asset module"""
    print_section("11. Asset Management Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List assets
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("List assets", response.status_code == 200)
    except Exception as e:
        stats.record("List assets", False, str(e))

    # Test 2: Asset categories
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/categories/",
                               headers=headers, timeout=5)
        all_passed &= stats.record("Asset categories", response.status_code == 200)
    except Exception as e:
        stats.record("Asset categories", False, str(e))

    return all_passed

def test_reports_module(token):
    """Test reports generation"""
    print_section("12. Reports & Analytics Tests")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Donation reports
    try:
        today = date.today().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/v1/reports/donations/?start_date={today}&end_date={today}",
            headers=headers, timeout=5
        )
        all_passed &= stats.record("Donation reports", response.status_code == 200)
    except Exception as e:
        stats.record("Donation reports", False, str(e))

    return all_passed

# ============================================================
# MAIN TEST RUNNER
# ============================================================

def run_all_tests():
    """Run all comprehensive tests"""

    print_header("MANDIRSYNC COMPREHENSIVE SYSTEM TEST")
    print(f"{Colors.WHITE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.WHITE}Backend URL: {BASE_URL}{Colors.END}")
    print(f"{Colors.WHITE}Frontend URL: {FRONTEND_URL}{Colors.END}")

    results = {}
    token = None

    # Infrastructure Tests
    results['backend'] = test_backend_server()
    if not results['backend']:
        print_error("\n❌ Backend not running - Cannot continue tests")
        print_info("Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print_final_summary(results)
        return False

    results['frontend'] = test_frontend_server()

    # Authentication
    auth_passed, token = test_authentication()
    results['auth'] = auth_passed

    if not token:
        print_error("\n❌ Authentication failed - Skipping authenticated tests")
        print_info("Create admin: cd backend && python scripts/create_admin_user_simple.py")
        print_final_summary(results)
        return False

    # Database Tests
    results['database'] = test_database_integrity(token)

    # Core Module Tests
    results['devotees'] = test_devotee_management(token)
    results['donations'] = test_donation_management(token)
    results['sevas'] = test_seva_management(token)
    results['accounting'] = test_accounting_module(token)

    # New Module Tests
    results['hr'] = test_hr_module(token)
    results['inventory'] = test_inventory_module(token)
    results['assets'] = test_asset_module(token)

    # Reports Tests
    results['reports'] = test_reports_module(token)

    # Final Summary
    print_final_summary(results)

    return all(results.values())

def print_final_summary(results):
    """Print final test summary"""

    print_header("TEST SUMMARY")

    # Overall statistics
    print(f"\n{Colors.WHITE}{Colors.BOLD}Test Statistics:{Colors.END}")
    print(f"  Total Tests Run: {stats.total}")
    print(f"  {Colors.GREEN}✓ Passed: {stats.passed}{Colors.END}")
    if stats.failed > 0:
        print(f"  {Colors.RED}✗ Failed: {stats.failed}{Colors.END}")

    success_rate = (stats.passed / stats.total * 100) if stats.total > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")

    # Category results
    print(f"\n{Colors.WHITE}{Colors.BOLD}Category Results:{Colors.END}")
    for category, passed in results.items():
        status = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status}  {category.upper().replace('_', ' ')}")

    # Failed tests details
    if stats.errors:
        print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests Details:{Colors.END}")
        for i, error in enumerate(stats.errors[:10], 1):
            print(f"  {i}. {error['test']}")
            if error['details']:
                print(f"     → {error['details']}")

        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more failures")

    # Final verdict
    print()
    if all(results.values()) and stats.failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'✓ ALL TESTS PASSED - SYSTEM HEALTHY':^80}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"\n{Colors.GREEN}🎉 MandirSync is ready for use!{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'✗ SOME TESTS FAILED - ACTION REQUIRED':^80}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.END}")

        # Provide helpful hints
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.END}")

        if not results.get('backend'):
            print(f"\n{Colors.CYAN}Backend Issue:{Colors.END}")
            print("  cd backend")
            print("  python -m uvicorn app.main:app --reload")

        if not results.get('frontend'):
            print(f"\n{Colors.CYAN}Frontend Issue:{Colors.END}")
            print("  cd frontend")
            print("  npm start")

        if not results.get('auth'):
            print(f"\n{Colors.CYAN}Authentication Issue:{Colors.END}")
            print("  cd backend")
            print("  python scripts/create_admin_user_simple.py")

        if not results.get('database'):
            print(f"\n{Colors.CYAN}Database Issue:{Colors.END}")
            print("  cd backend")
            print("  python seed_chart_of_accounts.py")

        print()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        print(f"\n{Colors.CYAN}MandirSync Comprehensive Test Suite{Colors.END}")
        print(f"{Colors.CYAN}Version 1.0 - Testing all modules{Colors.END}")

        success = run_all_tests()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
