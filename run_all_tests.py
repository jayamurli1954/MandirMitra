#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
    MANDIRSYNC COMPREHENSIVE SYSTEM TESTING SUITE
═══════════════════════════════════════════════════════════════════

This comprehensive test suite validates all components of the MandirSync
Temple Management System including:

• Infrastructure (Backend FastAPI + Frontend React)
• Security & Authentication (JWT-based)
• Core Modules (Donations, Sevas, Devotees)
• Financial System (Accounting, Chart of Accounts, Journal Entries)
• HR Management (Employees, Attendance, Payroll)
• Inventory Management (Stock, Stores, Transactions)
• Asset Management (Fixed Assets, Depreciation)
• Reports & Analytics

Usage: python run_all_tests.py

Author: MandirSync Development Team
Version: 2.0 - Ultra Comprehensive Edition
═══════════════════════════════════════════════════════════════════
"""

import requests
import sys
import json
from datetime import datetime, date
import time

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test credentials - update if different
TEST_CREDENTIALS = {
    "email": "admin@temple.com",
    "password": "admin123"
}

# ═══════════════════════════════════════════════════════════════════
# COLORS FOR OUTPUT
# ═══════════════════════════════════════════════════════════════════

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ═══════════════════════════════════════════════════════════════════
# PRINT UTILITIES
# ═══════════════════════════════════════════════════════════════════

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'═'*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'═'*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}→ {text}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.END}")

def print_subsection(text):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}  ▸ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.WHITE}    ℹ {text}{Colors.END}")

def print_test_header(component, description):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}  ▸ Component: {component}{Colors.END}")
    print(f"{Colors.WHITE}    Purpose: {description}{Colors.END}")

def print_test(name, passed, details="", endpoint=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    if endpoint:
        print(f"      {status}  {Colors.BOLD}{endpoint}{Colors.END}")
        print(f"             Test: {name}")
    else:
        print(f"      {status}  {name}")

    if details and not passed:
        print(f"             {Colors.YELLOW}→ Error: {details}{Colors.END}")
    return passed

def print_error(message):
    print(f"\n{Colors.RED}{Colors.BOLD}❌ ERROR: {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ WARNING: {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}{Colors.BOLD}✓ SUCCESS: {message}{Colors.END}")

# ═══════════════════════════════════════════════════════════════════
# GLOBAL TEST STATISTICS
# ═══════════════════════════════════════════════════════════════════

class TestStats:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = datetime.now()

    def record(self, name, passed, details=""):
        self.total += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append({"test": name, "details": details})
        return passed

    def get_duration(self):
        return (datetime.now() - self.start_time).total_seconds()

stats = TestStats()

# ═══════════════════════════════════════════════════════════════════
# TEST FUNCTIONS - INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════

def test_backend_server():
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: INFRASTRUCTURE - Backend Server
    ══════════════════════════════════════════════════════════════════
    Tests the FastAPI backend server which handles:
    - All business logic and data processing
    - RESTful API endpoints for frontend communication
    - Database connectivity and ORM operations
    - Authentication and authorization
    - File handling and PDF generation
    ══════════════════════════════════════════════════════════════════
    """
    print_section("1. INFRASTRUCTURE - BACKEND SERVER")
    print_info("Testing FastAPI application server, API documentation, and CORS configuration")

    all_passed = True

    # Test 1: Server Reachability
    print_test_header(
        "FastAPI Application Server",
        "Verifies that the backend server is running and accessible on port 8000"
    )
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        all_passed &= print_test(
            "Server responds to health check",
            response.status_code == 200,
            endpoint="GET /"
        )
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_warning("Start backend: cd backend && python -m uvicorn app.main:app --reload")
        stats.record("FastAPI server running", False, "Connection refused")
        return False
    except Exception as e:
        stats.record("FastAPI server running", False, str(e))
        return False

    # Test 2: API Documentation
    print_test_header(
        "API Documentation (Swagger UI)",
        "Ensures interactive API documentation is available for developers"
    )
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        all_passed &= print_test(
            "Swagger UI documentation accessible",
            response.status_code == 200,
            endpoint="GET /docs"
        )
    except Exception as e:
        stats.record("API documentation available", False, str(e))

    # Test 3: CORS Configuration
    print_test_header(
        "CORS (Cross-Origin Resource Sharing)",
        "Validates that frontend (port 3000) can communicate with backend (port 8000)"
    )
    try:
        response = requests.options(f"{BASE_URL}/api/v1/temples/", timeout=5)
        has_cors = 'access-control-allow-origin' in response.headers
        all_passed &= print_test(
            "CORS headers configured for frontend access",
            has_cors,
            details="Missing CORS headers" if not has_cors else "",
            endpoint="OPTIONS /api/v1/temples/"
        )
    except Exception as e:
        stats.record("CORS configured", False, str(e))

    return all_passed

def test_frontend_server():
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: INFRASTRUCTURE - Frontend Server
    ══════════════════════════════════════════════════════════════════
    Tests the React development server which provides:
    - User interface for temple staff
    - Responsive web application
    - Forms for data entry (donations, sevas, etc.)
    - Reports and dashboards
    - Single Page Application (SPA) architecture
    ══════════════════════════════════════════════════════════════════
    """
    print_section("2. INFRASTRUCTURE - FRONTEND SERVER")
    print_info("Testing React development server and application bundle loading")

    all_passed = True

    # Test 1: Frontend Reachability
    print_test_header(
        "React Development Server (Port 3000)",
        "Verifies that the React dev server is running and serving the application"
    )
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        all_passed &= print_test(
            "React server responds successfully",
            response.status_code == 200,
            endpoint=f"GET {FRONTEND_URL}"
        )
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to frontend at {FRONTEND_URL}")
        print_warning("Start frontend: cd frontend && npm start")
        stats.record("Frontend server running", False, "Connection refused")
        return False
    except Exception as e:
        stats.record("Frontend server running", False, str(e))
        return False

    # Test 2: React App Bundle
    print_test_header(
        "React Application Bundle",
        "Ensures the HTML page contains the React root element for mounting the app"
    )
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        has_react = 'root' in response.text
        all_passed &= print_test(
            "HTML contains React root element (<div id='root'>)",
            has_react,
            details="Missing root div element" if not has_react else ""
        )
    except Exception as e:
        stats.record("React app bundle loads", False, str(e))

    return all_passed

# ═══════════════════════════════════════════════════════════════════
# TEST FUNCTIONS - SECURITY & AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════

def test_authentication():
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: SECURITY - Authentication & Authorization
    ══════════════════════════════════════════════════════════════════
    Tests the JWT-based authentication system which provides:
    - Secure user login with email/password
    - JSON Web Token (JWT) generation
    - Token-based API access control
    - Protection of sensitive endpoints
    - Role-based authorization (admin, staff, priest, etc.)
    ══════════════════════════════════════════════════════════════════
    """
    print_section("3. SECURITY MODULE - AUTHENTICATION & AUTHORIZATION")
    print_info("Testing JWT-based authentication, login system, and access control mechanisms")

    all_passed = True
    token = None

    # Test 1: Login Endpoint
    print_test_header(
        "Login API Endpoint",
        "Validates user credentials and returns JWT access token for API requests"
    )
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
                all_passed &= print_test(
                    f"Login successful with credentials: {TEST_CREDENTIALS['email']}",
                    True,
                    endpoint="POST /api/v1/auth/login"
                )
                all_passed &= print_test(
                    f"JWT token generated (length: {len(token)} chars)",
                    len(token) > 0
                )
            else:
                all_passed &= print_test(
                    "Login returns access token",
                    False,
                    details="Response missing 'access_token' field"
                )
        elif response.status_code == 401:
            all_passed &= print_test(
                "Login with valid credentials",
                False,
                details="Invalid credentials - admin user may not exist"
            )
            print_warning("Create admin user: cd backend && python scripts/create_admin_user_simple.py")
        else:
            all_passed &= print_test(
                "Login endpoint responds correctly",
                False,
                details=f"Unexpected status code: {response.status_code}"
            )
    except Exception as e:
        all_passed &= print_test("Login endpoint functional", False, details=str(e))

    # Test 2: Invalid Credentials
    print_test_header(
        "Authentication Validation",
        "Ensures system rejects login attempts with incorrect credentials"
    )
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"},
            timeout=5
        )
        all_passed &= print_test(
            "Invalid credentials properly rejected with 401 Unauthorized",
            response.status_code == 401,
            details=f"Expected 401, got {response.status_code}" if response.status_code != 401 else "",
            endpoint="POST /api/v1/auth/login (invalid creds)"
        )
    except Exception as e:
        stats.record("Invalid credentials rejected", False, str(e))

    # Test 3: Protected Endpoint Access Control
    print_test_header(
        "Authorization Middleware",
        "Verifies that protected endpoints reject requests without authentication token"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/", timeout=5)
        all_passed &= print_test(
            "Protected endpoint rejects unauthenticated request",
            response.status_code == 401,
            details=f"Expected 401, got {response.status_code}" if response.status_code != 401 else "",
            endpoint="GET /api/v1/users/ (no token)"
        )
    except Exception as e:
        stats.record("Protected endpoints require auth", False, str(e))

    # Test 4: Token Validation
    print_test_header(
        "JWT Token Validation",
        "Confirms that valid JWT tokens grant access to protected endpoints"
    )
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers, timeout=5)
            all_passed &= print_test(
                "Valid JWT token grants access to user profile",
                response.status_code == 200,
                details=f"Expected 200, got {response.status_code}" if response.status_code != 200 else "",
                endpoint="GET /api/v1/users/me (with token)"
            )
        except Exception as e:
            stats.record("Token authentication works", False, str(e))
    else:
        print_warning("Skipping token validation - no token obtained from login")

    return all_passed, token

# ═══════════════════════════════════════════════════════════════════
# TEST FUNCTIONS - DATABASE & MASTER DATA
# ═══════════════════════════════════════════════════════════════════

def test_database_integrity(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: DATABASE - Schema & Master Data Integrity
    ══════════════════════════════════════════════════════════════════
    Tests database setup and master data which includes:
    - Chart of Accounts (accounting ledgers)
    - Temple configuration and settings
    - Donation categories (80G, General, Special)
    - Essential account codes for transactions
    - Database schema and relationships
    ══════════════════════════════════════════════════════════════════
    """
    print_section("4. DATABASE MODULE - SCHEMA & DATA INTEGRITY")
    print_info("Validating database tables, chart of accounts, and essential master data")

    if not token:
        print_error("No authentication token available - skipping database tests")
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Chart of Accounts
    print_test_header(
        "Accounting - Chart of Accounts (COA)",
        "The Chart of Accounts is the backbone of the accounting system, containing all ledger accounts for financial transactions"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/accounts/", headers=headers, timeout=5)
        if response.status_code == 200:
            accounts = response.json()
            all_passed &= print_test(
                f"Chart of Accounts loaded successfully ({len(accounts)} accounts found)",
                len(accounts) > 0,
                details="No accounts found - run seed_chart_of_accounts.py" if len(accounts) == 0 else "",
                endpoint="GET /api/v1/accounts/"
            )

            # Test essential accounts
            if len(accounts) > 0:
                account_codes = [acc.get('account_code') for acc in accounts]
                essential_accounts = {
                    '1101': 'Cash in Hand - Counter (Asset)',
                    '1110': 'Bank Account - Current (Asset)',
                    '4101': 'General Donation Income (Revenue)',
                    '5101': 'Priest Salaries (Expense)',
                    '5102': 'Staff Salaries (Expense)'
                }

                print_test_header(
                    "Essential Ledger Accounts",
                    "These accounts are critical for daily operations like recording donations and paying salaries"
                )
                for code, name in essential_accounts.items():
                    exists = code in account_codes
                    all_passed &= print_test(
                        f"Account {code}: {name}",
                        exists,
                        details=f"Account {code} not found in chart of accounts" if not exists else ""
                    )
        else:
            all_passed &= print_test(
                "Chart of Accounts API accessible",
                False,
                details=f"API returned status {response.status_code}"
            )
    except Exception as e:
        stats.record("Chart of Accounts exists", False, str(e))

    # Test 2: Temple Configuration
    print_test_header(
        "Temple Master Data",
        "Temple configuration stores basic information like temple name, address, registration details, and 80G certificate"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/temples/", headers=headers, timeout=5)
        if response.status_code == 200:
            temples = response.json()
            all_passed &= print_test(
                f"Temple data configured ({len(temples)} temple(s) found)",
                len(temples) > 0,
                details="No temple configured - add temple in Settings" if len(temples) == 0 else "",
                endpoint="GET /api/v1/temples/"
            )
        else:
            all_passed &= print_test(
                "Temple API accessible",
                False,
                details=f"API returned status {response.status_code}"
            )
    except Exception as e:
        stats.record("Temple configured", False, str(e))

    # Test 3: Donation Categories
    print_test_header(
        "Donation Categories Master",
        "Donation categories classify donations for accounting and 80G tax exemption purposes"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/categories/", headers=headers, timeout=5)
        if response.status_code == 200:
            categories = response.json()
            all_passed &= print_test(
                f"Donation categories loaded ({len(categories)} categories found)",
                len(categories) > 0,
                details="No donation categories - add in Settings" if len(categories) == 0 else "",
                endpoint="GET /api/v1/donations/categories/"
            )
        else:
            all_passed &= print_test(
                "Donation categories API accessible",
                False,
                details=f"API returned status {response.status_code}"
            )
    except Exception as e:
        stats.record("Donation categories exist", False, str(e))

    return all_passed

# ═══════════════════════════════════════════════════════════════════
# CORE MODULES
# ═══════════════════════════════════════════════════════════════════

def test_devotee_management(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: CRM - Devotee/Donor Management
    ══════════════════════════════════════════════════════════════════
    Tests the Customer Relationship Management (CRM) system for devotees:
    - Devotee database with contact information
    - CRUD operations (Create, Read, Update, Delete)
    - Search and filtering capabilities
    - Relationship tracking (family members, address)
    - Donation and seva booking history
    ══════════════════════════════════════════════════════════════════
    """
    print_section("5. CRM MODULE - DEVOTEE MANAGEMENT")
    print_info("Testing devotee database, contact management, and CRUD operations")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List Devotees
    print_test_header(
        "Devotee List API",
        "Retrieves all registered devotees with pagination support for managing large databases"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/devotees/", headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all devotees successfully",
            response.status_code == 200,
            endpoint="GET /api/v1/devotees/"
        )
    except Exception as e:
        stats.record("List devotees", False, str(e))

    # Test 2: Create Devotee
    print_test_header(
        "Create New Devotee (POST Operation)",
        "Adds new devotee to database with name, phone, email, and address information"
    )
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
            all_passed &= print_test(
                f"New devotee created successfully (ID: {devotee_id})",
                True,
                endpoint="POST /api/v1/devotees/"
            )
        else:
            all_passed &= print_test(
                "Create devotee operation",
                False,
                details=f"API returned status {response.status_code}"
            )
    except Exception as e:
        stats.record("Create devotee", False, str(e))

    # Test 3: Read Devotee
    print_test_header(
        "Read Devotee by ID (GET Operation)",
        "Fetches complete details of a specific devotee including history and preferences"
    )
    if devotee_id:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/devotees/{devotee_id}",
                                   headers=headers, timeout=5)
            all_passed &= print_test(
                f"Fetch devotee details by ID: {devotee_id}",
                response.status_code == 200,
                endpoint=f"GET /api/v1/devotees/{devotee_id}"
            )
        except Exception as e:
            stats.record("Read devotee", False, str(e))

    # Test 4: Update Devotee
    print_test_header(
        "Update Devotee (PUT Operation)",
        "Modifies existing devotee information like address, phone, or email"
    )
    if devotee_id:
        try:
            update_data = {"address": "Test Address, Test City"}
            response = requests.put(f"{BASE_URL}/api/v1/devotees/{devotee_id}",
                                   headers=headers, json=update_data, timeout=5)
            all_passed &= print_test(
                f"Update devotee information (ID: {devotee_id})",
                response.status_code == 200,
                endpoint=f"PUT /api/v1/devotees/{devotee_id}"
            )
        except Exception as e:
            stats.record("Update devotee", False, str(e))

    return all_passed

def test_donation_management(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: DONATION - Receipt & Collection Management
    ══════════════════════════════════════════════════════════════════
    Tests the donation management system which handles:
    - Recording cash/online donations
    - Receipt generation with unique numbers
    - 80G tax exemption certificate generation
    - Donation categorization (General, Special, Corpus)
    - Payment mode tracking (Cash, UPI, Card, Cheque)
    - Integration with accounting (automatic journal entries)
    ══════════════════════════════════════════════════════════════════
    """
    print_section("6. DONATION MODULE - RECEIPT & COLLECTION MANAGEMENT")
    print_info("Testing donation recording, receipt generation, categorization, and accounting integration")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: List Donations
    print_test_header(
        "Donation Transaction List",
        "Displays all recorded donations with receipt numbers, amounts, and payment details"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/", headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all donation records",
            response.status_code == 200,
            endpoint="GET /api/v1/donations/"
        )
    except Exception as e:
        stats.record("List donations", False, str(e))

    # Test 2: Donation Categories
    print_test_header(
        "Donation Category Master",
        "Categories help classify donations for accounting and tax purposes (e.g., 80G eligible donations)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/donations/categories/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Fetch all donation categories",
            response.status_code == 200,
            endpoint="GET /api/v1/donations/categories/"
        )
    except Exception as e:
        stats.record("Get donation categories", False, str(e))

    # Test 3: Date Range Filtering
    print_test_header(
        "Date Range Filtering",
        "Allows filtering donations by date range for daily/monthly reports and reconciliation"
    )
    try:
        today = date.today().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/v1/donations/?start_date={today}&end_date={today}",
            headers=headers, timeout=5
        )
        all_passed &= print_test(
            f"Filter donations by date range (today: {today})",
            response.status_code == 200,
            endpoint=f"GET /api/v1/donations/?start_date={today}&end_date={today}"
        )
    except Exception as e:
        stats.record("Donation filtering", False, str(e))

    return all_passed

def test_seva_management(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: SEVA - Pooja Booking & Scheduling
    ══════════════════════════════════════════════════════════════════
    Tests the seva/pooja booking system which manages:
    - Seva service definitions (Satyanarayana Pooja, Abhishekam, etc.)
    - Online/counter booking with devotee details
    - Daily seva schedule for priests
    - Receipt generation for bookings
    - Rescheduling and cancellation
    - Integration with accounting
    ══════════════════════════════════════════════════════════════════
    """
    print_section("7. SEVA MODULE - POOJA BOOKING & SCHEDULING")
    print_info("Testing seva services, booking management, scheduling, and priest assignment")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Seva Service Master
    print_test_header(
        "Seva Service Master",
        "Defines available poojas/sevas with pricing, duration, and requirements"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sevas/", headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all seva/pooja types",
            response.status_code == 200,
            endpoint="GET /api/v1/sevas/"
        )
    except Exception as e:
        stats.record("List sevas", False, str(e))

    # Test 2: Seva Bookings
    print_test_header(
        "Seva Booking Transactions",
        "Records all seva bookings with devotee details, date, time, and gotra information"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sevas/bookings/", headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all seva bookings",
            response.status_code == 200,
            endpoint="GET /api/v1/sevas/bookings/"
        )
    except Exception as e:
        stats.record("List seva bookings", False, str(e))

    # Test 3: Daily Schedule
    print_test_header(
        "Daily Seva Schedule",
        "Generates daily schedule for priests showing all booked sevas with timings"
    )
    try:
        today = date.today().isoformat()
        response = requests.get(f"{BASE_URL}/api/v1/sevas/schedule/?date={today}",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            f"Fetch today's seva schedule ({today})",
            response.status_code == 200,
            endpoint=f"GET /api/v1/sevas/schedule/?date={today}"
        )
    except Exception as e:
        stats.record("Seva schedule", False, str(e))

    return all_passed

def test_accounting_module(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: ACCOUNTING - Financial Management & General Ledger
    ══════════════════════════════════════════════════════════════════
    Tests the double-entry accounting system which provides:
    - Chart of Accounts (Assets, Liabilities, Income, Expenses)
    - Journal Entries (Dr/Cr transactions)
    - Day Book (daily transaction register)
    - Cash Book (cash in/out tracking)
    - Bank Book (bank transaction reconciliation)
    - Trial Balance and Financial Reports
    ══════════════════════════════════════════════════════════════════
    """
    print_section("8. ACCOUNTING MODULE - FINANCIAL MANAGEMENT")
    print_info("Testing chart of accounts, journal entries, day book, cash book, and financial reports")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Chart of Accounts
    print_test_header(
        "Chart of Accounts Master",
        "Lists all ledger accounts organized by type (Assets, Liabilities, Income, Expenses, Equity)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/accounts/", headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve complete chart of accounts",
            response.status_code == 200,
            endpoint="GET /api/v1/accounts/"
        )
    except Exception as e:
        stats.record("Get chart of accounts", False, str(e))

    # Test 2: Journal Entries
    print_test_header(
        "Journal Entry Transactions",
        "Displays all financial transactions in double-entry format (Debit = Credit)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all journal entries",
            response.status_code == 200,
            endpoint="GET /api/v1/journal-entries/"
        )
    except Exception as e:
        stats.record("Get journal entries", False, str(e))

    # Test 3: Day Book
    print_test_header(
        "Day Book Report",
        "Shows all transactions for a specific date - essential for daily cash reconciliation"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/day-book/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Generate day book report",
            response.status_code == 200,
            endpoint="GET /api/v1/journal-entries/day-book/"
        )
    except Exception as e:
        stats.record("Day book report", False, str(e))

    # Test 4: Cash Book
    print_test_header(
        "Cash Book Report",
        "Tracks all cash receipts and payments - critical for cash management and auditing"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/journal-entries/cash-book/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Generate cash book report",
            response.status_code == 200,
            endpoint="GET /api/v1/journal-entries/cash-book/"
        )
    except Exception as e:
        stats.record("Cash book report", False, str(e))

    return all_passed

# ═══════════════════════════════════════════════════════════════════
# NEW MODULES - HR, INVENTORY, ASSETS
# ═══════════════════════════════════════════════════════════════════

def test_hr_module(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: HR - Human Resource Management
    ══════════════════════════════════════════════════════════════════
    Tests the HR management system which handles:
    - Employee master data (priests, staff, accountants)
    - Department and designation management
    - Attendance tracking
    - Leave management
    - Salary structure and processing
    - Payroll generation
    ══════════════════════════════════════════════════════════════════
    """
    print_section("9. HR MODULE - HUMAN RESOURCE MANAGEMENT")
    print_info("Testing employee management, departments, designations, and attendance tracking")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Employee List
    print_test_header(
        "Employee Master Data",
        "Stores complete employee information including personal details, salary, and employment history"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/employees/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all employee records",
            response.status_code == 200,
            endpoint="GET /api/v1/hr/employees/"
        )
    except Exception as e:
        stats.record("List employees", False, str(e))

    # Test 2: Departments
    print_test_header(
        "Department Master",
        "Organizes employees by departments (Priests, Accounting, Administration, Maintenance)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/departments/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all departments",
            response.status_code == 200,
            endpoint="GET /api/v1/hr/departments/"
        )
    except Exception as e:
        stats.record("List departments", False, str(e))

    # Test 3: Designations
    print_test_header(
        "Designation Master",
        "Defines job roles (Head Priest, Assistant Priest, Accountant, Security Guard, etc.)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hr/designations/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all designations",
            response.status_code == 200,
            endpoint="GET /api/v1/hr/designations/"
        )
    except Exception as e:
        stats.record("List designations", False, str(e))

    return all_passed

def test_inventory_module(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: INVENTORY - Stock & Store Management
    ══════════════════════════════════════════════════════════════════
    Tests the inventory management system which manages:
    - Item master (pooja items, flowers, oil, camphor, etc.)
    - Store/godown management
    - Purchase entries
    - Issue/consumption entries
    - Stock reports and valuation
    - Reorder level alerts
    ══════════════════════════════════════════════════════════════════
    """
    print_section("10. INVENTORY MODULE - STOCK MANAGEMENT")
    print_info("Testing inventory items, stores, purchase/issue transactions, and stock reports")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Items
    print_test_header(
        "Inventory Item Master",
        "Maintains catalog of all inventory items with units of measurement and reorder levels"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/items/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all inventory items",
            response.status_code == 200,
            endpoint="GET /api/v1/inventory/items/"
        )
    except Exception as e:
        stats.record("List inventory items", False, str(e))

    # Test 2: Stores
    print_test_header(
        "Store/Godown Master",
        "Manages multiple storage locations (Main Store, Pooja Store, Prasadam Store)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/stores/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all stores/godowns",
            response.status_code == 200,
            endpoint="GET /api/v1/inventory/stores/"
        )
    except Exception as e:
        stats.record("List stores", False, str(e))

    # Test 3: Transactions
    print_test_header(
        "Stock Transactions",
        "Records all inventory movements (purchases, issues, transfers, adjustments)"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inventory/transactions/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all inventory transactions",
            response.status_code == 200,
            endpoint="GET /api/v1/inventory/transactions/"
        )
    except Exception as e:
        stats.record("List transactions", False, str(e))

    return all_passed

def test_asset_module(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: ASSETS - Fixed Asset Management
    ══════════════════════════════════════════════════════════════════
    Tests the fixed asset management system which tracks:
    - Asset register (buildings, vehicles, furniture, equipment)
    - Asset categories and locations
    - Depreciation calculation (SLM, WDV methods)
    - Asset disposal and write-off
    - Asset revaluation
    - Depreciation schedules
    ══════════════════════════════════════════════════════════════════
    """
    print_section("11. ASSET MODULE - FIXED ASSET MANAGEMENT")
    print_info("Testing asset register, categories, depreciation, and disposal tracking")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Assets
    print_test_header(
        "Asset Register",
        "Complete listing of all fixed assets with purchase details, cost, and current value"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all fixed assets",
            response.status_code == 200,
            endpoint="GET /api/v1/assets/"
        )
    except Exception as e:
        stats.record("List assets", False, str(e))

    # Test 2: Asset Categories
    print_test_header(
        "Asset Categories",
        "Classifies assets by type (Building, Vehicle, Furniture, Computer, etc.) for depreciation"
    )
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/categories/",
                               headers=headers, timeout=5)
        all_passed &= print_test(
            "Retrieve all asset categories",
            response.status_code == 200,
            endpoint="GET /api/v1/assets/categories/"
        )
    except Exception as e:
        stats.record("Asset categories", False, str(e))

    return all_passed

def test_reports_module(token):
    """
    ══════════════════════════════════════════════════════════════════
    MODULE: REPORTS - Analytics & Business Intelligence
    ══════════════════════════════════════════════════════════════════
    Tests the reporting system which generates:
    - Donation reports (daily, monthly, category-wise)
    - Seva reports (booking analysis, revenue)
    - Financial reports (P&L, Balance Sheet, Cash Flow)
    - PDF export functionality
    - Excel export for data analysis
    ══════════════════════════════════════════════════════════════════
    """
    print_section("12. REPORTS MODULE - ANALYTICS & BUSINESS INTELLIGENCE")
    print_info("Testing report generation, PDF exports, and data analytics")

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True

    # Test 1: Donation Reports
    print_test_header(
        "Donation Analytics Reports",
        "Generates comprehensive donation reports with filtering by date, category, and payment mode"
    )
    try:
        today = date.today().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/v1/reports/donations/?start_date={today}&end_date={today}",
            headers=headers, timeout=5
        )
        all_passed &= print_test(
            f"Generate donation report for {today}",
            response.status_code == 200,
            endpoint=f"GET /api/v1/reports/donations/?start_date={today}&end_date={today}"
        )
    except Exception as e:
        stats.record("Donation reports", False, str(e))

    return all_passed

# ═══════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════════

def run_all_tests():
    """Execute all test suites"""

    print_header("MANDIRSYNC COMPREHENSIVE SYSTEM TEST SUITE")
    print(f"{Colors.WHITE}Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.WHITE}Backend URL: {BASE_URL}{Colors.END}")
    print(f"{Colors.WHITE}Frontend URL: {FRONTEND_URL}{Colors.END}")
    print(f"{Colors.WHITE}Testing Credentials: {TEST_CREDENTIALS['email']}{Colors.END}")

    results = {}
    token = None

    # Infrastructure Tests
    print_info("Phase 1: Testing infrastructure components...")
    results['backend'] = test_backend_server()
    if not results['backend']:
        print_error("\n❌ Backend server not running - Cannot proceed with tests")
        print_warning("Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print_final_summary(results)
        return False

    results['frontend'] = test_frontend_server()

    # Authentication
    print_info("Phase 2: Testing security and authentication...")
    auth_passed, token = test_authentication()
    results['auth'] = auth_passed

    if not token:
        print_error("\n❌ Authentication failed - Cannot test authenticated endpoints")
        print_warning("Create admin: cd backend && python scripts/create_admin_user_simple.py")
        print_final_summary(results)
        return False

    # Database Tests
    print_info("Phase 3: Testing database and master data...")
    results['database'] = test_database_integrity(token)

    # Core Module Tests
    print_info("Phase 4: Testing core business modules...")
    results['devotees'] = test_devotee_management(token)
    results['donations'] = test_donation_management(token)
    results['sevas'] = test_seva_management(token)
    results['accounting'] = test_accounting_module(token)

    # New Module Tests
    print_info("Phase 5: Testing advanced modules...")
    results['hr'] = test_hr_module(token)
    results['inventory'] = test_inventory_module(token)
    results['assets'] = test_asset_module(token)

    # Reports Tests
    print_info("Phase 6: Testing reports and analytics...")
    results['reports'] = test_reports_module(token)

    # Final Summary
    print_final_summary(results)

    return all(results.values())

def print_final_summary(results):
    """Print comprehensive test summary"""

    duration = stats.get_duration()

    print_header("TEST EXECUTION SUMMARY")

    # Overall Statistics
    print(f"\n{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")
    print(f"{Colors.WHITE}{Colors.BOLD}Test Statistics:{Colors.END}")
    print(f"{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")
    print(f"  Total Tests Executed: {Colors.BOLD}{stats.total}{Colors.END}")
    print(f"  {Colors.GREEN}✓ Passed: {stats.passed}{Colors.END}")
    if stats.failed > 0:
        print(f"  {Colors.RED}✗ Failed: {stats.failed}{Colors.END}")

    success_rate = (stats.passed / stats.total * 100) if stats.total > 0 else 0
    print(f"  Success Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.END}")
    print(f"  Execution Time: {Colors.BOLD}{duration:.2f} seconds{Colors.END}")

    # Module Results
    print(f"\n{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")
    print(f"{Colors.WHITE}{Colors.BOLD}Module Test Results:{Colors.END}")
    print(f"{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")

    module_names = {
        'backend': 'Infrastructure - Backend Server',
        'frontend': 'Infrastructure - Frontend Server',
        'auth': 'Security - Authentication',
        'database': 'Database - Master Data',
        'devotees': 'CRM - Devotee Management',
        'donations': 'Donation Management',
        'sevas': 'Seva/Pooja Management',
        'accounting': 'Accounting & Finance',
        'hr': 'HR & Payroll',
        'inventory': 'Inventory & Stock',
        'assets': 'Asset Management',
        'reports': 'Reports & Analytics'
    }

    for category, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        module_name = module_names.get(category, category.upper())
        print(f"  {status}  {module_name}")

    # Failed Tests Details
    if stats.errors:
        print(f"\n{Colors.RED}{Colors.BOLD}{'═'*80}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}Failed Tests Details:{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'═'*80}{Colors.END}")
        for i, error in enumerate(stats.errors[:15], 1):
            print(f"  {i}. {Colors.BOLD}{error['test']}{Colors.END}")
            if error['details']:
                print(f"     {Colors.YELLOW}→ {error['details']}{Colors.END}")

        if len(stats.errors) > 15:
            print(f"\n  {Colors.YELLOW}... and {len(stats.errors) - 15} more failures{Colors.END}")

    # Final Verdict
    print(f"\n{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")
    if all(results.values()) and stats.failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}{'✓ ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL':^80}{Colors.END}")
        print(f"{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 MandirSync is healthy and ready for production use!{Colors.END}")
        print(f"{Colors.GREEN}All {stats.total} tests passed successfully in {duration:.2f} seconds{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}{'✗ SOME TESTS FAILED - ACTION REQUIRED':^80}{Colors.END}")
        print(f"{Colors.WHITE}{Colors.BOLD}{'═'*80}{Colors.END}")

        # Troubleshooting Guide
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Troubleshooting Guide:{Colors.END}")
        print(f"{Colors.YELLOW}{'─'*80}{Colors.END}")

        if not results.get('backend'):
            print(f"\n{Colors.CYAN}{Colors.BOLD}Backend Server Issue:{Colors.END}")
            print(f"  The FastAPI backend is not responding. Start it with:")
            print(f"  {Colors.WHITE}cd backend{Colors.END}")
            print(f"  {Colors.WHITE}python -m uvicorn app.main:app --reload{Colors.END}")

        if not results.get('frontend'):
            print(f"\n{Colors.CYAN}{Colors.BOLD}Frontend Server Issue:{Colors.END}")
            print(f"  The React development server is not running. Start it with:")
            print(f"  {Colors.WHITE}cd frontend{Colors.END}")
            print(f"  {Colors.WHITE}npm start{Colors.END}")

        if not results.get('auth'):
            print(f"\n{Colors.CYAN}{Colors.BOLD}Authentication Issue:{Colors.END}")
            print(f"  Admin user doesn't exist or credentials are wrong. Create admin with:")
            print(f"  {Colors.WHITE}cd backend{Colors.END}")
            print(f"  {Colors.WHITE}python scripts/create_admin_user_simple.py{Colors.END}")

        if not results.get('database'):
            print(f"\n{Colors.CYAN}{Colors.BOLD}Database Setup Issue:{Colors.END}")
            print(f"  Chart of accounts or master data is missing. Set it up with:")
            print(f"  {Colors.WHITE}cd backend{Colors.END}")
            print(f"  {Colors.WHITE}python seed_chart_of_accounts.py{Colors.END}")

        print()

# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'MandirSync Comprehensive Test Suite - Ultra Detailed Edition':^80}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'Version 2.0':^80}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'═'*80}{Colors.END}")

        success = run_all_tests()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}{Colors.BOLD}Tests interrupted by user (Ctrl+C){Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}{Colors.BOLD}Unexpected error occurred:{Colors.END}")
        print(f"{Colors.RED}{e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
