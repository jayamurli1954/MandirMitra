"""
Locust Load Testing for MandirSync

This file defines load testing scenarios to simulate concurrent users
performing various operations in the temple management system.

Usage:
    locust -f locustfile.py --host=http://localhost:8000

Web UI:
    Open http://localhost:8089
    Set number of users and spawn rate
    Click "Start Swarming"
"""

from locust import HttpUser, task, between
import random
import json
from datetime import date, timedelta


class DonationUser(HttpUser):
    """
    Simulates users recording donations at temple counter
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Login before starting tasks"""
        self.login()

    def login(self):
        """Authenticate user"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "counter_user",
            "password": "password123"
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(10)  # Weight: 10 (most common operation)
    def record_donation(self):
        """Record a new donation"""
        donor_names = ["Ram Kumar", "Sita Devi", "Lakshmi Patel", "Krishna Sharma", "Radha Singh"]
        payment_methods = ["cash", "upi", "card"]

        donation_data = {
            "donor_name": random.choice(donor_names),
            "amount": round(random.uniform(100, 10000), 2),
            "payment_method": random.choice(payment_methods),
            "donation_date": str(date.today()),
            "phone": f"98765{random.randint(10000, 99999)}"
        }

        with self.client.post(
            "/api/v1/donations/",
            json=donation_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to record donation: {response.status_code}")

    @task(5)  # Weight: 5
    def list_donations(self):
        """List recent donations"""
        self.client.get(
            "/api/v1/donations/",
            params={"skip": 0, "limit": 20},
            headers=self.headers,
            name="/api/v1/donations/ [list]"
        )

    @task(3)  # Weight: 3
    def get_donation_by_id(self):
        """Get specific donation details"""
        # Assuming donation IDs range from 1-1000
        donation_id = random.randint(1, 1000)
        self.client.get(
            f"/api/v1/donations/{donation_id}",
            headers=self.headers,
            name="/api/v1/donations/[id]"
        )

    @task(2)  # Weight: 2
    def generate_receipt(self):
        """Generate donation receipt PDF"""
        donation_id = random.randint(1, 1000)
        self.client.get(
            f"/api/v1/donations/{donation_id}/receipt",
            headers=self.headers,
            name="/api/v1/donations/[id]/receipt"
        )


class SevaBookingUser(HttpUser):
    """
    Simulates users booking sevas/poojas
    """
    wait_time = between(2, 5)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/api/v1/auth/login", json={
            "username": "seva_counter",
            "password": "password123"
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(8)  # Weight: 8
    def book_seva(self):
        """Book a seva"""
        devotee_names = ["Krishna", "Govind", "Madhav", "Keshav", "Narayana"]
        gothras = ["Bharadwaja", "Kashyapa", "Vasishtha", "Vishwamitra", "Atri"]

        tomorrow = date.today() + timedelta(days=1)

        booking_data = {
            "seva_id": random.randint(1, 10),  # Assuming 10 sevas
            "devotee_name": random.choice(devotee_names),
            "gotra": random.choice(gothras),
            "seva_date": str(tomorrow),
            "payment_method": random.choice(["cash", "upi"]),
            "phone": f"98765{random.randint(10000, 99999)}"
        }

        with self.client.post(
            "/api/v1/sevas/bookings",
            json=booking_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to book seva: {response.status_code}")

    @task(5)  # Weight: 5
    def list_sevas(self):
        """List available sevas"""
        self.client.get(
            "/api/v1/sevas/",
            headers=self.headers,
            name="/api/v1/sevas/ [list]"
        )

    @task(4)  # Weight: 4
    def list_bookings(self):
        """List seva bookings"""
        self.client.get(
            "/api/v1/sevas/bookings",
            params={"skip": 0, "limit": 20},
            headers=self.headers,
            name="/api/v1/sevas/bookings [list]"
        )

    @task(2)  # Weight: 2
    def check_availability(self):
        """Check seva availability"""
        seva_id = random.randint(1, 10)
        check_date = str(date.today() + timedelta(days=random.randint(1, 7)))

        self.client.get(
            f"/api/v1/sevas/{seva_id}/availability",
            params={"date": check_date},
            headers=self.headers,
            name="/api/v1/sevas/[id]/availability"
        )


class AdminUser(HttpUser):
    """
    Simulates admin users accessing reports and dashboards
    """
    wait_time = between(5, 10)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(5)  # Weight: 5
    def view_dashboard(self):
        """View dashboard summary"""
        self.client.get(
            "/api/v1/dashboard/summary",
            headers=self.headers,
            name="/api/v1/dashboard/summary"
        )

    @task(4)  # Weight: 4
    def generate_trial_balance(self):
        """Generate trial balance"""
        self.client.get(
            "/api/v1/accounting/reports/trial-balance",
            params={"as_of_date": str(date.today())},
            headers=self.headers,
            name="/api/v1/accounting/reports/trial-balance"
        )

    @task(3)  # Weight: 3
    def view_chart_of_accounts(self):
        """View chart of accounts"""
        self.client.get(
            "/api/v1/accounting/accounts",
            headers=self.headers,
            name="/api/v1/accounting/accounts [list]"
        )

    @task(3)  # Weight: 3
    def list_employees(self):
        """List employees"""
        self.client.get(
            "/api/v1/hr/employees",
            headers=self.headers,
            name="/api/v1/hr/employees [list]"
        )

    @task(2)  # Weight: 2
    def generate_income_statement(self):
        """Generate income statement"""
        today = date.today()
        month_start = today.replace(day=1)

        self.client.get(
            "/api/v1/accounting/reports/income-statement",
            params={
                "start_date": str(month_start),
                "end_date": str(today)
            },
            headers=self.headers,
            name="/api/v1/accounting/reports/income-statement"
        )


class MixedWorkloadUser(HttpUser):
    """
    Simulates a mix of donation and seva booking operations
    Represents typical counter operation
    """
    wait_time = between(1, 4)

    tasks = {
        DonationUser: 6,  # 60% donation operations
        SevaBookingUser: 4  # 40% seva operations
    }


# ============================================================================
# LOAD TEST SCENARIOS
# ============================================================================

# Scenario 1: Normal Day
# Run with: locust -f locustfile.py --users 10 --spawn-rate 2
# Simulates 10 concurrent users (2-3 counters operating)

# Scenario 2: Festival Day
# Run with: locust -f locustfile.py --users 50 --spawn-rate 10
# Simulates 50 concurrent users (heavy load, multiple counters)

# Scenario 3: Stress Test
# Run with: locust -f locustfile.py --users 100 --spawn-rate 20
# Simulates 100 concurrent users to identify breaking point

# Scenario 4: Spike Test
# Start with 10 users, then manually increase to 100 in web UI
# Tests system behavior under sudden traffic spike

# ============================================================================
# MONITORING
# ============================================================================
# Open http://localhost:8089 for real-time metrics:
# - Requests per second (RPS)
# - Response times (median, 95th percentile, 99th percentile)
# - Failures
# - Number of users
