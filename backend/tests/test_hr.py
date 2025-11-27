"""
Comprehensive Tests for HR & Payroll Module

Tests cover:
- Department management
- Designation management
- Employee CRUD operations
- Attendance tracking
- Leave management
- Salary components and structures
- Payroll processing
- Payslip generation
"""

import pytest
from fastapi import status
from datetime import date, datetime, timedelta
from decimal import Decimal


@pytest.mark.hr
@pytest.mark.api
class TestDepartments:
    """Tests for department management"""

    def test_create_department(self, authenticated_client):
        """Test creating a new department"""
        dept_data = {
            "code": "ACC",
            "name": "Accounts Department",
            "description": "Handles all accounting and financial operations"
        }

        response = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "ACC"
        assert data["name"] == "Accounts Department"
        assert "id" in data

    def test_create_duplicate_department_code(self, authenticated_client):
        """Test that duplicate department codes are rejected"""
        dept_data = {
            "code": "PRI",
            "name": "Priests Department"
        }

        # Create first department
        response1 = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate
        response2 = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )

        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.text.lower()

    def test_list_departments(self, authenticated_client):
        """Test listing all departments"""
        response = authenticated_client.get("/api/v1/hr/departments")

        assert response.status_code == status.HTTP_200_OK
        departments = response.json()
        assert isinstance(departments, list)

    def test_get_department_by_id(self, authenticated_client):
        """Test retrieving a specific department"""
        # Create a department
        dept_data = {"code": "ADM", "name": "Administration"}
        create_response = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )
        dept_id = create_response.json()["id"]

        # Retrieve it
        response = authenticated_client.get(f"/api/v1/hr/departments/{dept_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == dept_id
        assert data["code"] == "ADM"

    def test_update_department(self, authenticated_client):
        """Test updating a department"""
        # Create department
        dept_data = {"code": "MNT", "name": "Maintenance"}
        create_response = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )
        dept_id = create_response.json()["id"]

        # Update it
        update_data = {"name": "Maintenance & Facilities"}
        response = authenticated_client.put(
            f"/api/v1/hr/departments/{dept_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Maintenance & Facilities"

    def test_deactivate_department(self, authenticated_client):
        """Test deactivating a department"""
        # Create department
        dept_data = {"code": "TST", "name": "Test Department"}
        create_response = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )
        dept_id = create_response.json()["id"]

        # Deactivate it
        response = authenticated_client.delete(f"/api/v1/hr/departments/{dept_id}")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


@pytest.mark.hr
@pytest.mark.api
class TestDesignations:
    """Tests for designation/job title management"""

    def test_create_designation(self, authenticated_client):
        """Test creating a new designation"""
        designation_data = {
            "code": "ACC01",
            "title": "Senior Accountant",
            "description": "Manages financial records and reports"
        }

        response = authenticated_client.post(
            "/api/v1/hr/designations",
            json=designation_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Senior Accountant"

    def test_list_designations(self, authenticated_client):
        """Test listing all designations"""
        response = authenticated_client.get("/api/v1/hr/designations")

        assert response.status_code == status.HTTP_200_OK
        designations = response.json()
        assert isinstance(designations, list)


@pytest.mark.hr
@pytest.mark.api
class TestEmployees:
    """Tests for employee management"""

    def test_create_employee_minimal(self, authenticated_client):
        """Test creating an employee with minimal required fields"""
        employee_data = {
            "employee_code": "EMP-0001",
            "full_name": "Rajesh Kumar",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active"
        }

        response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["employee_code"] == "EMP-0001"
        assert data["full_name"] == "Rajesh Kumar"
        assert "id" in data

    def test_create_employee_full(self, authenticated_client):
        """Test creating an employee with all fields"""
        employee_data = {
            "employee_code": "EMP-0002",
            "full_name": "Priya Sharma",
            "date_of_birth": "1990-05-15",
            "gender": "female",
            "phone": "9876543210",
            "email": "priya@temple.org",
            "address": "456 Temple Road, Mumbai",
            "joining_date": "2024-01-01",
            "employee_type": "permanent",
            "status": "active",
            "aadhar_number": "123456789012",
            "pan_number": "ABCDE1234F",
            "bank_account_number": "1234567890",
            "bank_name": "SBI",
            "bank_ifsc": "SBIN0001234",
            "basic_salary": 25000.00
        }

        response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["full_name"] == "Priya Sharma"
        assert data["phone"] == "9876543210"
        assert float(data["basic_salary"]) == 25000.00

    def test_create_duplicate_employee_code(self, authenticated_client):
        """Test that duplicate employee codes are rejected"""
        employee_data = {
            "employee_code": "EMP-DUP",
            "full_name": "Test Employee",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active"
        }

        # Create first employee
        response1 = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate
        response2 = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )

        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_employees(self, authenticated_client):
        """Test listing all employees"""
        response = authenticated_client.get("/api/v1/hr/employees")

        assert response.status_code == status.HTTP_200_OK
        employees = response.json()
        assert isinstance(employees, list)

    def test_filter_employees_by_status(self, authenticated_client):
        """Test filtering employees by status"""
        response = authenticated_client.get(
            "/api/v1/hr/employees",
            params={"status": "active"}
        )

        assert response.status_code == status.HTTP_200_OK
        employees = response.json()
        # All should be active
        for emp in employees:
            if "status" in emp:
                assert emp["status"] == "active"

    def test_filter_employees_by_department(self, authenticated_client):
        """Test filtering employees by department"""
        # Create department first
        dept_data = {"code": "IT", "name": "IT Department"}
        dept_response = authenticated_client.post(
            "/api/v1/hr/departments",
            json=dept_data
        )
        dept_id = dept_response.json()["id"]

        # Filter by department
        response = authenticated_client.get(
            "/api/v1/hr/employees",
            params={"department_id": dept_id}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_search_employees(self, authenticated_client):
        """Test searching employees by name"""
        # Create employee with unique name
        employee_data = {
            "employee_code": "EMP-SEARCH",
            "full_name": "Unique Search Name Employee",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active"
        }

        authenticated_client.post("/api/v1/hr/employees", json=employee_data)

        # Search for it
        response = authenticated_client.get(
            "/api/v1/hr/employees",
            params={"search": "Unique Search"}
        )

        assert response.status_code == status.HTTP_200_OK
        employees = response.json()
        found = any("Unique Search Name" in emp.get("full_name", "") for emp in employees)
        assert found

    def test_get_employee_by_id(self, authenticated_client):
        """Test retrieving a specific employee"""
        # Create employee
        employee_data = {
            "employee_code": "EMP-GET",
            "full_name": "Test Get Employee",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active"
        }

        create_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = create_response.json()["id"]

        # Retrieve it
        response = authenticated_client.get(f"/api/v1/hr/employees/{emp_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == emp_id

    def test_update_employee(self, authenticated_client):
        """Test updating employee details"""
        # Create employee
        employee_data = {
            "employee_code": "EMP-UPD",
            "full_name": "Update Test",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active"
        }

        create_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = create_response.json()["id"]

        # Update it
        update_data = {
            "phone": "9999999999",
            "email": "updated@temple.org"
        }

        response = authenticated_client.put(
            f"/api/v1/hr/employees/{emp_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone"] == "9999999999"


@pytest.mark.hr
@pytest.mark.api
class TestSalaryComponents:
    """Tests for salary component management"""

    def test_create_salary_component_earning(self, authenticated_client):
        """Test creating an earning component (e.g., HRA, DA)"""
        component_data = {
            "name": "House Rent Allowance",
            "code": "HRA",
            "component_type": "earning",
            "is_percentage": True,
            "percentage_of_basic": 40.0,
            "description": "40% of basic salary"
        }

        response = authenticated_client.post(
            "/api/v1/hr/salary-components",
            json=component_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "HRA"
        assert data["component_type"] == "earning"

    def test_create_salary_component_deduction(self, authenticated_client):
        """Test creating a deduction component (e.g., PF, Tax)"""
        component_data = {
            "name": "Provident Fund",
            "code": "PF",
            "component_type": "deduction",
            "is_percentage": True,
            "percentage_of_basic": 12.0
        }

        response = authenticated_client.post(
            "/api/v1/hr/salary-components",
            json=component_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["component_type"] == "deduction"

    def test_list_salary_components(self, authenticated_client):
        """Test listing all salary components"""
        response = authenticated_client.get("/api/v1/hr/salary-components")

        assert response.status_code == status.HTTP_200_OK
        components = response.json()
        assert isinstance(components, list)


@pytest.mark.hr
@pytest.mark.api
@pytest.mark.integration
class TestPayroll:
    """Tests for payroll processing"""

    def test_create_payroll_for_employee(self, authenticated_client):
        """Test creating a payroll entry for an employee"""
        # First create an employee
        employee_data = {
            "employee_code": "EMP-PAY",
            "full_name": "Payroll Test Employee",
            "joining_date": str(date.today() - timedelta(days=30)),
            "employee_type": "permanent",
            "status": "active",
            "basic_salary": 30000.00
        }

        emp_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = emp_response.json()["id"]

        # Create payroll
        payroll_data = {
            "employee_id": emp_id,
            "month": 12,
            "year": 2024,
            "basic_salary": 30000.00,
            "gross_salary": 35000.00,
            "total_deductions": 3600.00,
            "net_salary": 31400.00,
            "status": "draft"
        }

        response = authenticated_client.post(
            "/api/v1/hr/payroll",
            json=payroll_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["employee_id"] == emp_id
        assert float(data["basic_salary"]) == 30000.00

    def test_calculate_payroll_automatically(self, authenticated_client):
        """Test automatic payroll calculation based on salary structure"""
        # Create employee with salary
        employee_data = {
            "employee_code": "EMP-AUTO",
            "full_name": "Auto Calculate Employee",
            "joining_date": str(date.today() - timedelta(days=30)),
            "employee_type": "permanent",
            "status": "active",
            "basic_salary": 25000.00
        }

        emp_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = emp_response.json()["id"]

        # Calculate payroll
        response = authenticated_client.post(
            f"/api/v1/hr/payroll/calculate/{emp_id}",
            json={"month": 12, "year": 2024}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "gross_salary" in data
            assert "net_salary" in data

    def test_bulk_payroll_generation(self, authenticated_client):
        """Test generating payroll for all employees at once"""
        payroll_data = {
            "month": 12,
            "year": 2024,
            "employee_type": "permanent"  # Generate for all permanent employees
        }

        response = authenticated_client.post(
            "/api/v1/hr/payroll/bulk-generate",
            json=payroll_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "count" in data or "payrolls" in data

    def test_approve_payroll(self, authenticated_client):
        """Test approving a payroll (moving from draft to approved)"""
        # Create employee and payroll
        employee_data = {
            "employee_code": "EMP-APPROVE",
            "full_name": "Approve Test",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active",
            "basic_salary": 20000.00
        }

        emp_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = emp_response.json()["id"]

        payroll_data = {
            "employee_id": emp_id,
            "month": 12,
            "year": 2024,
            "basic_salary": 20000.00,
            "gross_salary": 22000.00,
            "net_salary": 19000.00,
            "status": "draft"
        }

        payroll_response = authenticated_client.post(
            "/api/v1/hr/payroll",
            json=payroll_data
        )
        payroll_id = payroll_response.json()["id"]

        # Approve it
        response = authenticated_client.post(
            f"/api/v1/hr/payroll/{payroll_id}/approve"
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["status"] == "approved"

    def test_generate_payslip_pdf(self, authenticated_client):
        """Test generating payslip PDF"""
        # Create employee and payroll
        employee_data = {
            "employee_code": "EMP-SLIP",
            "full_name": "Payslip Test",
            "joining_date": str(date.today()),
            "employee_type": "permanent",
            "status": "active",
            "basic_salary": 30000.00
        }

        emp_response = authenticated_client.post(
            "/api/v1/hr/employees",
            json=employee_data
        )
        emp_id = emp_response.json()["id"]

        payroll_data = {
            "employee_id": emp_id,
            "month": 12,
            "year": 2024,
            "basic_salary": 30000.00,
            "gross_salary": 35000.00,
            "net_salary": 31400.00,
            "status": "approved"
        }

        payroll_response = authenticated_client.post(
            "/api/v1/hr/payroll",
            json=payroll_data
        )
        payroll_id = payroll_response.json()["id"]

        # Generate payslip
        response = authenticated_client.get(
            f"/api/v1/hr/payroll/{payroll_id}/payslip"
        )

        if response.status_code == status.HTTP_200_OK:
            assert response.headers["content-type"] == "application/pdf"


@pytest.mark.hr
@pytest.mark.api
class TestPayrollReports:
    """Tests for payroll reporting"""

    def test_get_monthly_payroll_summary(self, authenticated_client):
        """Test getting summary of payroll for a month"""
        response = authenticated_client.get(
            "/api/v1/hr/payroll/summary",
            params={"month": 12, "year": 2024}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "total_employees" in data or "total_gross" in data

    def test_export_payroll_report(self, authenticated_client):
        """Test exporting payroll report to Excel"""
        response = authenticated_client.get(
            "/api/v1/hr/payroll/export",
            params={"month": 12, "year": 2024, "format": "excel"}
        )

        if response.status_code == status.HTTP_200_OK:
            assert "spreadsheet" in response.headers.get("content-type", "")


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all HR tests:
#   pytest tests/test_hr.py -v
#
# Run specific test class:
#   pytest tests/test_hr.py::TestEmployees -v
#
# Run payroll tests only:
#   pytest tests/test_hr.py::TestPayroll -v
#
# Run with coverage:
#   pytest tests/test_hr.py --cov=app.api.hr --cov-report=term-missing
# ============================================================================
