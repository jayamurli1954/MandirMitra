"""
HR & Salary Management Models
Complete employee management, salary structure, and payroll processing
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums


class EmployeeStatus(str, enum.Enum):
    """Employee status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class EmployeeType(str, enum.Enum):
    """Employee type"""

    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    PART_TIME = "part_time"
    VOLUNTEER = "volunteer"


class SalaryComponentType(str, enum.Enum):
    """Salary component types"""

    EARNING = "earning"  # Basic, HRA, Allowances, etc. (adds to salary)
    DEDUCTION = "deduction"  # PF, ESI, TDS, etc. (reduces salary)


class PayrollStatus(str, enum.Enum):
    """Payroll processing status"""

    DRAFT = "draft"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


# Models


class Department(Base):
    """Department master"""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Department Details
    code = Column(String(20), nullable=False, index=True)  # HR, ADMIN, POOJA, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department(code='{self.code}', name='{self.name}')>"


class Designation(Base):
    """Designation master"""

    __tablename__ = "designations"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Designation Details
    code = Column(String(20), nullable=False, index=True)  # MGR, CLERK, PRIEST, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(Integer, default=0)  # Hierarchy level

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    employees = relationship("Employee", back_populates="designation")

    def __repr__(self):
        return f"<Designation(code='{self.code}', name='{self.name}')>"


class Employee(Base):
    """Employee master data"""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Employee Identification
    employee_code = Column(String(50), nullable=False, unique=True, index=True)  # EMP001, EMP002
    employee_id_number = Column(String(50))  # Government ID (Aadhaar, etc.)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(300))  # Computed: first + middle + last

    # Contact Information
    phone = Column(String(20), nullable=False, index=True)
    alternate_phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))

    # Employment Details
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation_id = Column(Integer, ForeignKey("designations.id"), nullable=False)
    employee_type = Column(
        SQLEnum(EmployeeType, native_enum=False, length=20),
        nullable=False,
        default=EmployeeType.PERMANENT.value,
    )
    status = Column(
        SQLEnum(EmployeeStatus, native_enum=False, length=20),
        nullable=False,
        default=EmployeeStatus.ACTIVE.value,
        index=True,
    )

    # Dates
    joining_date = Column(Date, nullable=False, index=True)
    confirmation_date = Column(Date)
    resignation_date = Column(Date)
    last_working_date = Column(Date)

    # Bank Details (for salary)
    bank_name = Column(String(200))
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    bank_branch = Column(String(200))

    # Statutory Information
    pan_number = Column(String(20))
    aadhaar_number = Column(String(20))
    pf_number = Column(String(50))  # Provident Fund
    esi_number = Column(String(50))  # Employee State Insurance
    uan_number = Column(String(50))  # Universal Account Number (for PF)

    # Emergency Contact
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(50))

    # Additional Information
    date_of_birth = Column(Date)
    gender = Column(String(20))  # Male, Female, Other
    blood_group = Column(String(10))
    photo_url = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    department = relationship("Department", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    salary_structure = relationship("SalaryStructure", back_populates="employee", uselist=False)
    payrolls = relationship("Payroll", back_populates="employee")

    def __repr__(self):
        return f"<Employee(code='{self.employee_code}', name='{self.full_name}')>"


class SalaryComponent(Base):
    """Salary component master (Basic, HRA, PF, etc.)"""

    __tablename__ = "salary_components"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Component Details
    code = Column(String(20), nullable=False, index=True)  # BASIC, HRA, PF, TDS, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text)
    component_type = Column(
        SQLEnum(SalaryComponentType, native_enum=False, length=20), nullable=False
    )

    # Calculation Rules
    is_percentage = Column(Boolean, default=False)  # If true, calculate as % of base
    base_component_code = Column(
        String(20)
    )  # Which component to base percentage on (usually BASIC)
    default_value = Column(Float, default=0.0)  # Default amount or percentage

    # Statutory Flags
    is_statutory = Column(Boolean, default=False)  # PF, ESI, TDS, etc.
    is_taxable = Column(Boolean, default=True)  # For income tax calculation

    # Display Order
    display_order = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    structure_components = relationship("SalaryStructureComponent", back_populates="component")

    def __repr__(self):
        return f"<SalaryComponent(code='{self.code}', name='{self.name}', type='{self.component_type}')>"


class SalaryStructure(Base):
    """Employee salary structure"""

    __tablename__ = "salary_structures"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False, unique=True, index=True
    )
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Structure Details
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date)  # NULL means current structure

    # Total Salary
    gross_salary = Column(Float, nullable=False)  # Total before deductions
    net_salary = Column(Float, nullable=False)  # Total after deductions

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="salary_structure")
    components = relationship(
        "SalaryStructureComponent", back_populates="salary_structure", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SalaryStructure(employee_id={self.employee_id}, gross={self.gross_salary}, net={self.net_salary})>"


class SalaryStructureComponent(Base):
    """Components in a salary structure"""

    __tablename__ = "salary_structure_components"

    id = Column(Integer, primary_key=True, index=True)
    salary_structure_id = Column(
        Integer, ForeignKey("salary_structures.id"), nullable=False, index=True
    )
    component_id = Column(Integer, ForeignKey("salary_components.id"), nullable=False)

    # Component Value
    amount = Column(Float, nullable=False)  # Fixed amount
    percentage = Column(Float)  # If percentage-based
    calculated_amount = Column(Float, nullable=False)  # Final calculated amount

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    salary_structure = relationship("SalaryStructure", back_populates="components")
    component = relationship("SalaryComponent", back_populates="structure_components")

    def __repr__(self):
        return f"<SalaryStructureComponent(structure_id={self.salary_structure_id}, component_id={self.component_id}, amount={self.calculated_amount})>"


class Payroll(Base):
    """Monthly payroll records"""

    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)

    # Payroll Period
    payroll_month = Column(Integer, nullable=False, index=True)  # 1-12
    payroll_year = Column(Integer, nullable=False, index=True)
    payroll_date = Column(Date, nullable=False, index=True)  # Date salary is paid

    # Salary Details
    days_worked = Column(Integer, default=0)  # Days worked in the month
    days_payable = Column(Integer, default=0)  # Days for which salary is paid
    leave_days = Column(Integer, default=0)  # Leave days (unpaid)

    # Amounts
    gross_salary = Column(Float, nullable=False)  # Before deductions
    total_earnings = Column(Float, nullable=False)  # Sum of all earnings
    total_deductions = Column(Float, nullable=False)  # Sum of all deductions
    net_salary = Column(Float, nullable=False)  # After deductions

    # Status
    status = Column(
        SQLEnum(PayrollStatus, native_enum=False, length=20),
        nullable=False,
        default=PayrollStatus.DRAFT.value,
        index=True,
    )

    # Payment Details
    payment_mode = Column(String(20))  # bank_transfer, cash, cheque
    payment_reference = Column(String(100))  # Transaction reference
    paid_date = Column(Date)
    paid_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Salary Slip
    salary_slip_url = Column(String(500))  # PDF URL

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    employee = relationship("Employee", back_populates="payrolls")
    journal_entry = relationship("JournalEntry")
    payroll_components = relationship(
        "PayrollComponent", back_populates="payroll", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Payroll(employee_id={self.employee_id}, month={self.payroll_month}/{self.payroll_year}, net={self.net_salary})>"


class PayrollComponent(Base):
    """Salary components in a payroll"""

    __tablename__ = "payroll_components"

    id = Column(Integer, primary_key=True, index=True)
    payroll_id = Column(Integer, ForeignKey("payrolls.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("salary_components.id"), nullable=False)

    # Component Details
    component_code = Column(String(20), nullable=False)
    component_name = Column(String(100), nullable=False)
    component_type = Column(
        SQLEnum(SalaryComponentType, native_enum=False, length=20), nullable=False
    )

    # Amount
    amount = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    payroll = relationship("Payroll", back_populates="payroll_components")
    component = relationship("SalaryComponent")

    def __repr__(self):
        return f"<PayrollComponent(payroll_id={self.payroll_id}, component='{self.component_code}', amount={self.amount})>"


class LeaveType(Base):
    """Leave type master"""

    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Leave Type Details
    code = Column(String(20), nullable=False, index=True)  # CL, SL, EL, etc.
    name = Column(String(100), nullable=False)  # Casual Leave, Sick Leave, etc.
    description = Column(Text)

    # Leave Rules
    is_paid = Column(Boolean, default=True)  # Paid or unpaid leave
    max_days_per_year = Column(Integer, default=0)  # 0 = unlimited
    carry_forward_allowed = Column(Boolean, default=False)
    max_carry_forward_days = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")

    def __repr__(self):
        return f"<LeaveType(code='{self.code}', name='{self.name}')>"


class LeaveApplication(Base):
    """Employee leave applications"""

    __tablename__ = "leave_applications"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)

    # Leave Details
    from_date = Column(Date, nullable=False, index=True)
    to_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    reason = Column(Text)

    # Status
    status = Column(
        String(20), default="pending", index=True
    )  # pending, approved, rejected, cancelled
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    employee = relationship("Employee")
    leave_type = relationship("LeaveType")

    def __repr__(self):
        return f"<LeaveApplication(employee_id={self.employee_id}, from={self.from_date}, to={self.to_date}, days={self.days})>"
