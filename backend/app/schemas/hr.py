"""
Pydantic Schemas for HR & Salary Management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.hr import EmployeeStatus, EmployeeType, SalaryComponentType, PayrollStatus


# ===== DEPARTMENT SCHEMAS =====


class DepartmentBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    temple_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== DESIGNATION SCHEMAS =====


class DesignationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    level: int = Field(default=0, ge=0)


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DesignationResponse(DesignationBase):
    id: int
    temple_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== EMPLOYEE SCHEMAS =====


class EmployeeBase(BaseModel):
    employee_code: Optional[str] = Field(
        None, max_length=50
    )  # Optional - will be auto-generated if not provided
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    department_id: int
    designation_id: int
    employee_type: EmployeeType = EmployeeType.PERMANENT
    joining_date: date
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    employee_type: Optional[EmployeeType] = None
    status: Optional[EmployeeStatus] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    temple_id: int
    full_name: str
    status: EmployeeStatus
    employee_type: EmployeeType
    confirmation_date: Optional[date] = None
    resignation_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    department_name: Optional[str] = None
    designation_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== SALARY COMPONENT SCHEMAS =====


class SalaryComponentBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    component_type: SalaryComponentType
    is_percentage: bool = False
    base_component_code: Optional[str] = None
    default_value: float = Field(default=0.0, ge=0)
    is_statutory: bool = False
    is_taxable: bool = True
    display_order: int = 0


class SalaryComponentCreate(SalaryComponentBase):
    pass


class SalaryComponentResponse(SalaryComponentBase):
    id: int
    temple_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ===== SALARY STRUCTURE SCHEMAS =====


class SalaryStructureComponentCreate(BaseModel):
    component_id: int
    amount: Optional[float] = Field(None, ge=0)
    percentage: Optional[float] = Field(None, ge=0, le=100)


class SalaryStructureCreate(BaseModel):
    employee_id: int
    effective_from: date
    effective_to: Optional[date] = None
    components: List[SalaryStructureComponentCreate]


class SalaryStructureComponentResponse(BaseModel):
    id: int
    component_id: int
    component_code: str
    component_name: str
    component_type: SalaryComponentType
    amount: float
    percentage: Optional[float] = None
    calculated_amount: float

    class Config:
        from_attributes = True


class SalaryStructureResponse(BaseModel):
    id: int
    employee_id: int
    effective_from: date
    effective_to: Optional[date] = None
    gross_salary: float
    net_salary: float
    is_active: bool
    components: List[SalaryStructureComponentResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== PAYROLL SCHEMAS =====


class PayrollComponentResponse(BaseModel):
    id: int
    component_id: int
    component_code: str
    component_name: str
    component_type: SalaryComponentType
    amount: float

    class Config:
        from_attributes = True


class PayrollCreate(BaseModel):
    employee_id: int
    payroll_month: int = Field(..., ge=1, le=12)
    payroll_year: int = Field(..., ge=2020)
    payroll_date: date
    days_worked: Optional[int] = Field(None, ge=0, le=31)
    days_payable: Optional[int] = Field(None, ge=0, le=31)
    leave_days: Optional[int] = Field(None, ge=0, le=31)
    notes: Optional[str] = None


class PayrollUpdate(BaseModel):
    status: Optional[PayrollStatus] = None
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None


class PayrollResponse(BaseModel):
    id: int
    temple_id: int
    employee_id: int
    employee_code: str
    employee_name: str
    payroll_month: int
    payroll_year: int
    payroll_date: date
    days_worked: int
    days_payable: int
    leave_days: int
    gross_salary: float
    total_earnings: float
    total_deductions: float
    net_salary: float
    status: PayrollStatus
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_date: Optional[date] = None
    salary_slip_url: Optional[str] = None
    journal_entry_id: Optional[int] = None
    created_at: datetime
    components: List[PayrollComponentResponse] = []

    class Config:
        from_attributes = True


# ===== BULK PAYROLL SCHEMAS =====


class BulkPayrollCreate(BaseModel):
    payroll_month: int = Field(..., ge=1, le=12)
    payroll_year: int = Field(..., ge=2020)
    payroll_date: date
    employee_ids: Optional[List[int]] = None  # If None, process all active employees
    notes: Optional[str] = None


class BulkPayrollResponse(BaseModel):
    total_employees: int
    processed: int
    failed: int
    payroll_ids: List[int]
    errors: List[dict] = []
