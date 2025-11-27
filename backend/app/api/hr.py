"""
HR & Salary Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.audit import log_action, get_entity_dict
from app.models.hr import (
    Employee, Department, Designation, SalaryComponent, SalaryStructure,
    SalaryStructureComponent, Payroll, PayrollComponent, EmployeeStatus, EmployeeType,
    PayrollStatus, SalaryComponentType
)
from app.models.temple import Temple
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, TransactionType
from app.schemas.hr import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    DesignationCreate, DesignationUpdate, DesignationResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    SalaryComponentCreate, SalaryComponentResponse,
    SalaryStructureCreate, SalaryStructureResponse,
    PayrollCreate, PayrollUpdate, PayrollResponse, BulkPayrollCreate, BulkPayrollResponse
)

router = APIRouter(prefix="/api/v1/hr", tags=["hr"])


def get_enum_value(enum_obj, enum_class):
    """Safely extract enum value from enum object or string"""
    if enum_obj is None:
        return None
    # If it's an enum instance, get its value
    if hasattr(enum_obj, 'value'):
        return enum_obj.value
    # If it's a string, convert to lowercase (all enum values are lowercase)
    if isinstance(enum_obj, str):
        return enum_obj.lower()
    # Fallback: convert to lowercase string
    return str(enum_obj).lower()


# ===== DEPARTMENT MANAGEMENT =====

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new department"""
    # Check if code already exists
    existing = db.query(Department).filter(
        Department.temple_id == current_user.temple_id,
        Department.code == dept_data.code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Department code '{dept_data.code}' already exists")
    
    department = Department(
        temple_id=current_user.temple_id,
        code=dept_data.code,
        name=dept_data.name,
        description=dept_data.description
    )
    
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return department


@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of departments"""
    query = db.query(Department).filter(Department.temple_id == current_user.temple_id)
    
    if active_only:
        query = query.filter(Department.is_active == True)
    
    departments = query.order_by(Department.code).offset(skip).limit(limit).all()
    return departments


# ===== DESIGNATION MANAGEMENT =====

@router.post("/designations", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
def create_designation(
    desig_data: DesignationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new designation"""
    existing = db.query(Designation).filter(
        Designation.temple_id == current_user.temple_id,
        Designation.code == desig_data.code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Designation code '{desig_data.code}' already exists")
    
    designation = Designation(
        temple_id=current_user.temple_id,
        code=desig_data.code,
        name=desig_data.name,
        description=desig_data.description,
        level=desig_data.level
    )
    
    db.add(designation)
    db.commit()
    db.refresh(designation)
    
    return designation


@router.get("/designations", response_model=List[DesignationResponse])
def list_designations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of designations"""
    query = db.query(Designation).filter(Designation.temple_id == current_user.temple_id)
    
    if active_only:
        query = query.filter(Designation.is_active == True)
    
    designations = query.order_by(Designation.level, Designation.code).offset(skip).limit(limit).all()
    return designations


# ===== EMPLOYEE MANAGEMENT =====

def generate_employee_code(db: Session, temple_id: int) -> str:
    """Generate unique employee code"""
    year = datetime.now().year
    prefix = f"EMP/{year}/"
    
    last_employee = db.query(Employee).filter(
        Employee.temple_id == temple_id,
        Employee.employee_code.like(f"{prefix}%")
    ).order_by(Employee.id.desc()).first()
    
    if last_employee:
        try:
            last_num = int(last_employee.employee_code.split('/')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    emp_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new employee"""
    # Verify department and designation exist
    department = db.query(Department).filter(
        Department.id == emp_data.department_id,
        Department.temple_id == current_user.temple_id
    ).first()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    designation = db.query(Designation).filter(
        Designation.id == emp_data.designation_id,
        Designation.temple_id == current_user.temple_id
    ).first()
    
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    # Generate employee code if not provided
    employee_code = emp_data.employee_code
    if not employee_code or employee_code.strip() == '':
        employee_code = generate_employee_code(db, current_user.temple_id)
    else:
        # Check if code already exists
        existing = db.query(Employee).filter(
            Employee.temple_id == current_user.temple_id,
            Employee.employee_code == employee_code
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Employee code '{employee_code}' already exists")
    
    # Build full name
    name_parts = [emp_data.first_name]
    if emp_data.middle_name:
        name_parts.append(emp_data.middle_name)
    if emp_data.last_name:
        name_parts.append(emp_data.last_name)
    full_name = " ".join(name_parts)
    
    employee = Employee(
        temple_id=current_user.temple_id,
        employee_code=employee_code,
        first_name=emp_data.first_name,
        middle_name=emp_data.middle_name,
        last_name=emp_data.last_name,
        full_name=full_name,
        phone=emp_data.phone,
        email=emp_data.email,
        address=emp_data.address,
        city=emp_data.city,
        state=emp_data.state,
        pincode=emp_data.pincode,
        department_id=emp_data.department_id,
        designation_id=emp_data.designation_id,
        employee_type=get_enum_value(emp_data.employee_type, EmployeeType),
        joining_date=emp_data.joining_date,
        bank_name=emp_data.bank_name,
        bank_account_number=emp_data.bank_account_number,
        bank_ifsc_code=emp_data.bank_ifsc_code,
        pan_number=emp_data.pan_number,
        aadhaar_number=emp_data.aadhaar_number,
        status=EmployeeStatus.ACTIVE.value,
        created_by=current_user.id
    )
    
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    # Add department and designation names to response
    emp_dict = {
        **{k: v for k, v in employee.__dict__.items() if not k.startswith('_')},
        'department_name': department.name,
        'designation_name': designation.name
    }
    
    log_action(
        db=db,
        user=current_user,
        action="CREATE_EMPLOYEE",
        entity_type="Employee",
        entity_id=employee.id,
        new_values=get_entity_dict(employee),
        description=f"Created employee: {employee.employee_code} - {full_name}"
    )
    
    return EmployeeResponse(**emp_dict)


@router.get("/employees", response_model=List[EmployeeResponse])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[EmployeeStatus] = Query(None, alias="status"),
    department_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of employees"""
    query = db.query(Employee).filter(Employee.temple_id == current_user.temple_id)
    
    if status_filter:
        query = query.filter(Employee.status == status_filter)
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Employee.employee_code.ilike(search_filter),
                Employee.first_name.ilike(search_filter),
                Employee.last_name.ilike(search_filter),
                Employee.full_name.ilike(search_filter),
                Employee.phone.ilike(search_filter)
            )
        )
    
    employees = query.order_by(Employee.employee_code).offset(skip).limit(limit).all()
    
    # Add department and designation names
    result = []
    for emp in employees:
        emp_dict = {
            **{k: v for k, v in emp.__dict__.items() if not k.startswith('_')},
            'department_name': emp.department.name if emp.department else None,
            'designation_name': emp.designation.name if emp.designation else None
        }
        result.append(EmployeeResponse(**emp_dict))
    
    return result


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee details"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.temple_id == current_user.temple_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    emp_dict = {
        **{k: v for k, v in employee.__dict__.items() if not k.startswith('_')},
        'department_name': employee.department.name if employee.department else None,
        'designation_name': employee.designation.name if employee.designation else None
    }
    
    return EmployeeResponse(**emp_dict)


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    emp_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update employee"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.temple_id == current_user.temple_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update fields
    update_data = emp_data.dict(exclude_unset=True)
    
    # Update full name if name fields changed
    if 'first_name' in update_data or 'middle_name' in update_data or 'last_name' in update_data:
        first = update_data.get('first_name', employee.first_name)
        middle = update_data.get('middle_name', employee.middle_name)
        last = update_data.get('last_name', employee.last_name)
        name_parts = [first]
        if middle:
            name_parts.append(middle)
        if last:
            name_parts.append(last)
        update_data['full_name'] = " ".join(name_parts)
    
    for field, value in update_data.items():
        if hasattr(employee, field):
            setattr(employee, field, value)
    
    employee.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(employee)
    
    emp_dict = {
        **{k: v for k, v in employee.__dict__.items() if not k.startswith('_')},
        'department_name': employee.department.name if employee.department else None,
        'designation_name': employee.designation.name if employee.designation else None
    }
    
    log_action(
        db=db,
        user=current_user,
        action="UPDATE_EMPLOYEE",
        entity_type="Employee",
        entity_id=employee.id,
        new_values=update_data,
        description=f"Updated employee: {employee.employee_code}"
    )
    
    return EmployeeResponse(**emp_dict)


# ===== SALARY COMPONENT MANAGEMENT =====

@router.post("/salary-components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
def create_salary_component(
    component_data: SalaryComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a salary component"""
    existing = db.query(SalaryComponent).filter(
        SalaryComponent.temple_id == current_user.temple_id,
        SalaryComponent.code == component_data.code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Component code '{component_data.code}' already exists")
    
    component = SalaryComponent(
        temple_id=current_user.temple_id,
        **component_data.dict()
    )
    
    db.add(component)
    db.commit()
    db.refresh(component)
    
    return component


@router.get("/salary-components", response_model=List[SalaryComponentResponse])
def list_salary_components(
    component_type: Optional[SalaryComponentType] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of salary components"""
    query = db.query(SalaryComponent).filter(SalaryComponent.temple_id == current_user.temple_id)
    
    if component_type:
        query = query.filter(SalaryComponent.component_type == component_type)
    
    if active_only:
        query = query.filter(SalaryComponent.is_active == True)
    
    components = query.order_by(SalaryComponent.display_order, SalaryComponent.code).all()
    return components


# ===== SALARY STRUCTURE MANAGEMENT =====

def calculate_salary_structure(db: Session, employee_id: int, components_data: List[dict]) -> tuple:
    """Calculate gross and net salary from components"""
    total_earnings = 0.0
    total_deductions = 0.0
    
    # Get component details
    component_map = {}
    for comp_data in components_data:
        component = db.query(SalaryComponent).filter(SalaryComponent.id == comp_data['component_id']).first()
        if component:
            component_map[comp_data['component_id']] = component
    
    # First pass: Calculate fixed amounts
    calculated_amounts = {}
    for comp_data in components_data:
        comp_id = comp_data['component_id']
        component = component_map.get(comp_id)
        if not component:
            continue
        
        if component.is_percentage:
            # Will calculate in second pass
            calculated_amounts[comp_id] = None
        else:
            amount = comp_data.get('amount', component.default_value)
            calculated_amounts[comp_id] = amount
            
            if component.component_type == SalaryComponentType.EARNING.value:
                total_earnings += amount
            else:
                total_deductions += amount
    
    # Second pass: Calculate percentages
    for comp_data in components_data:
        comp_id = comp_data['component_id']
        component = component_map.get(comp_id)
        if not component or not component.is_percentage:
            continue
        
        # Find base component
        base_component_id = None
        for cid, comp in component_map.items():
            if comp.code == component.base_component_code:
                base_component_id = cid
                break
        
        if base_component_id and calculated_amounts.get(base_component_id) is not None:
            base_amount = calculated_amounts[base_component_id]
            percentage = comp_data.get('percentage', component.default_value)
            amount = (base_amount * percentage) / 100
            calculated_amounts[comp_id] = amount
            
            if component.component_type == SalaryComponentType.EARNING.value:
                total_earnings += amount
            else:
                total_deductions += amount
    
    gross_salary = total_earnings
    net_salary = total_earnings - total_deductions
    
    return gross_salary, net_salary, calculated_amounts


@router.post("/salary-structures", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
def create_salary_structure(
    structure_data: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create salary structure for an employee"""
    # Verify employee exists
    employee = db.query(Employee).filter(
        Employee.id == structure_data.employee_id,
        Employee.temple_id == current_user.temple_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Deactivate existing structure if any
    existing = db.query(SalaryStructure).filter(
        SalaryStructure.employee_id == structure_data.employee_id,
        SalaryStructure.is_active == True
    ).first()
    
    if existing:
        existing.is_active = False
        if not existing.effective_to:
            existing.effective_to = structure_data.effective_from - timedelta(days=1)
    
    # Calculate salary
    components_list = [comp.dict() for comp in structure_data.components]
    gross_salary, net_salary, calculated_amounts = calculate_salary_structure(
        db, structure_data.employee_id, components_list
    )
    
    # Create structure
    structure = SalaryStructure(
        employee_id=structure_data.employee_id,
        temple_id=current_user.temple_id,
        effective_from=structure_data.effective_from,
        effective_to=structure_data.effective_to,
        gross_salary=gross_salary,
        net_salary=net_salary,
        created_by=current_user.id
    )
    
    db.add(structure)
    db.flush()
    
    # Create structure components
    for comp_data in structure_data.components:
        component = db.query(SalaryComponent).filter(SalaryComponent.id == comp_data.component_id).first()
        if component:
            structure_comp = SalaryStructureComponent(
                salary_structure_id=structure.id,
                component_id=comp_data.component_id,
                amount=comp_data.amount or 0,
                percentage=comp_data.percentage,
                calculated_amount=calculated_amounts.get(comp_data.component_id, 0)
            )
            db.add(structure_comp)
    
    db.commit()
    db.refresh(structure)
    
    # Build response with components
    structure_components = db.query(SalaryStructureComponent).filter(
        SalaryStructureComponent.salary_structure_id == structure.id
    ).all()
    
    comp_responses = []
    for sc in structure_components:
        comp = db.query(SalaryComponent).filter(SalaryComponent.id == sc.component_id).first()
        if comp:
            comp_responses.append({
                'id': sc.id,
                'component_id': sc.component_id,
                'component_code': comp.code,
                'component_name': comp.name,
                'component_type': comp.component_type,
                'amount': sc.amount,
                'percentage': sc.percentage,
                'calculated_amount': sc.calculated_amount
            })
    
    structure_dict = {
        **{k: v for k, v in structure.__dict__.items() if not k.startswith('_')},
        'components': comp_responses
    }
    
    return SalaryStructureResponse(**structure_dict)


@router.get("/employees/{employee_id}/salary-structure", response_model=Optional[SalaryStructureResponse])
def get_employee_salary_structure(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current salary structure for an employee"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.temple_id == current_user.temple_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    structure = db.query(SalaryStructure).filter(
        SalaryStructure.employee_id == employee_id,
        SalaryStructure.is_active == True
    ).first()
    
    if not structure:
        return None
    
    # Build response with components
    structure_components = db.query(SalaryStructureComponent).filter(
        SalaryStructureComponent.salary_structure_id == structure.id
    ).all()
    
    comp_responses = []
    for sc in structure_components:
        comp = db.query(SalaryComponent).filter(SalaryComponent.id == sc.component_id).first()
        if comp:
            comp_responses.append({
                'id': sc.id,
                'component_id': sc.component_id,
                'component_code': comp.code,
                'component_name': comp.name,
                'component_type': comp.component_type,
                'amount': sc.amount,
                'percentage': sc.percentage,
                'calculated_amount': sc.calculated_amount
            })
    
    structure_dict = {
        **{k: v for k, v in structure.__dict__.items() if not k.startswith('_')},
        'components': comp_responses
    }
    
    return SalaryStructureResponse(**structure_dict)


# ===== PAYROLL PROCESSING =====

def process_payroll_for_employee(
    db: Session,
    employee_id: int,
    payroll_month: int,
    payroll_year: int,
    payroll_date: date,
    days_worked: Optional[int] = None,
    days_payable: Optional[int] = None,
    leave_days: Optional[int] = None,
    current_user: User = None
) -> Payroll:
    """Process payroll for a single employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError(f"Employee {employee_id} not found")
    
    # Get active salary structure
    structure = db.query(SalaryStructure).filter(
        SalaryStructure.employee_id == employee_id,
        SalaryStructure.is_active == True
    ).first()
    
    if not structure:
        raise ValueError(f"No active salary structure found for employee {employee.employee_code}")
    
    # Calculate days (default to full month if not provided)
    if days_payable is None:
        # Get number of days in month
        if payroll_month == 12:
            next_month = 1
            next_year = payroll_year + 1
        else:
            next_month = payroll_month + 1
            next_year = payroll_year
        first_day = date(payroll_year, payroll_month, 1)
        last_day = date(next_year, next_month, 1) - timedelta(days=1)
        days_payable = last_day.day
    
    if days_worked is None:
        days_worked = days_payable - (leave_days or 0)
    
    # Calculate prorated salary if days_worked < days_payable
    proration_factor = days_worked / days_payable if days_payable > 0 else 0
    
    # Get structure components
    structure_components = db.query(SalaryStructureComponent).filter(
        SalaryStructureComponent.salary_structure_id == structure.id
    ).all()
    
    total_earnings = 0.0
    total_deductions = 0.0
    
    # Create payroll
    payroll = Payroll(
        temple_id=employee.temple_id,
        employee_id=employee_id,
        payroll_month=payroll_month,
        payroll_year=payroll_year,
        payroll_date=payroll_date,
        days_worked=days_worked,
        days_payable=days_payable,
        leave_days=leave_days or 0,
        status=PayrollStatus.DRAFT.value,
        created_by=current_user.id if current_user else None
    )
    
    db.add(payroll)
    db.flush()
    
    # Process each component
    for sc in structure_components:
        component = db.query(SalaryComponent).filter(SalaryComponent.id == sc.component_id).first()
        if not component:
            continue
        
        # Calculate prorated amount
        amount = sc.calculated_amount * proration_factor
        
        # Create payroll component
        payroll_comp = PayrollComponent(
            payroll_id=payroll.id,
            component_id=component.id,
            component_code=component.code,
            component_name=component.name,
            component_type=component.component_type if isinstance(component.component_type, str) else component.component_type.value,
            amount=amount
        )
        db.add(payroll_comp)
        
        if component.component_type == SalaryComponentType.EARNING.value:
            total_earnings += amount
        else:
            total_deductions += amount
    
    payroll.gross_salary = total_earnings
    payroll.total_earnings = total_earnings
    payroll.total_deductions = total_deductions
    payroll.net_salary = total_earnings - total_deductions
    payroll.status = PayrollStatus.PROCESSED.value
    payroll.processed_at = datetime.utcnow()
    payroll.processed_by = current_user.id if current_user else None
    
    db.commit()
    db.refresh(payroll)
    
    return payroll


@router.post("/payrolls", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
def create_payroll(
    payroll_data: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create/process payroll for an employee"""
    # Check if payroll already exists
    existing = db.query(Payroll).filter(
        Payroll.employee_id == payroll_data.employee_id,
        Payroll.payroll_month == payroll_data.payroll_month,
        Payroll.payroll_year == payroll_data.payroll_year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Payroll already exists for employee {payroll_data.employee_id} for {payroll_data.payroll_month}/{payroll_data.payroll_year}"
        )
    
    try:
        payroll = process_payroll_for_employee(
            db=db,
            employee_id=payroll_data.employee_id,
            payroll_month=payroll_data.payroll_month,
            payroll_year=payroll_data.payroll_year,
            payroll_date=payroll_data.payroll_date,
            days_worked=payroll_data.days_worked,
            days_payable=payroll_data.days_payable,
            leave_days=payroll_data.leave_days,
            current_user=current_user
        )
        
        # Get payroll components for response
        payroll_components = db.query(PayrollComponent).filter(
            PayrollComponent.payroll_id == payroll.id
        ).all()
        
        payroll_dict = {
            **{k: v for k, v in payroll.__dict__.items() if not k.startswith('_')},
            'employee_code': payroll.employee.employee_code,
            'employee_name': payroll.employee.full_name,
            'components': [
                {
                    'id': pc.id,
                    'component_id': pc.component_id,
                    'component_code': pc.component_code,
                    'component_name': pc.component_name,
                    'component_type': pc.component_type,
                    'amount': pc.amount
                }
                for pc in payroll_components
            ]
        }
        
        return PayrollResponse(**payroll_dict)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payrolls/bulk", response_model=BulkPayrollResponse)
def create_bulk_payroll(
    bulk_data: BulkPayrollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process payroll for multiple employees"""
    # Get employees to process
    if bulk_data.employee_ids:
        employees = db.query(Employee).filter(
            Employee.id.in_(bulk_data.employee_ids),
            Employee.temple_id == current_user.temple_id,
            Employee.status == EmployeeStatus.ACTIVE.value
        ).all()
    else:
        # Process all active employees
        employees = db.query(Employee).filter(
            Employee.temple_id == current_user.temple_id,
            Employee.status == EmployeeStatus.ACTIVE.value
        ).all()
    
    processed = 0
    failed = 0
    payroll_ids = []
    errors = []
    
    for employee in employees:
        try:
            # Check if payroll already exists
            existing = db.query(Payroll).filter(
                Payroll.employee_id == employee.id,
                Payroll.payroll_month == bulk_data.payroll_month,
                Payroll.payroll_year == bulk_data.payroll_year
            ).first()
            
            if existing:
                errors.append({
                    'employee_id': employee.id,
                    'employee_code': employee.employee_code,
                    'error': f"Payroll already exists for {bulk_data.payroll_month}/{bulk_data.payroll_year}"
                })
                failed += 1
                continue
            
            payroll = process_payroll_for_employee(
                db=db,
                employee_id=employee.id,
                payroll_month=bulk_data.payroll_month,
                payroll_year=bulk_data.payroll_year,
                payroll_date=bulk_data.payroll_date,
                current_user=current_user
            )
            
            payroll_ids.append(payroll.id)
            processed += 1
            
        except Exception as e:
            errors.append({
                'employee_id': employee.id,
                'employee_code': employee.employee_code,
                'error': str(e)
            })
            failed += 1
    
    return BulkPayrollResponse(
        total_employees=len(employees),
        processed=processed,
        failed=failed,
        payroll_ids=payroll_ids,
        errors=errors
    )


@router.get("/payrolls", response_model=List[PayrollResponse])
def list_payrolls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = Query(None),
    payroll_month: Optional[int] = Query(None, ge=1, le=12),
    payroll_year: Optional[int] = Query(None),
    status_filter: Optional[PayrollStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of payrolls"""
    query = db.query(Payroll).filter(Payroll.temple_id == current_user.temple_id)
    
    if employee_id:
        query = query.filter(Payroll.employee_id == employee_id)
    
    if payroll_month:
        query = query.filter(Payroll.payroll_month == payroll_month)
    
    if payroll_year:
        query = query.filter(Payroll.payroll_year == payroll_year)
    
    if status_filter:
        query = query.filter(Payroll.status == status_filter)
    
    payrolls = query.order_by(Payroll.payroll_year.desc(), Payroll.payroll_month.desc(), Payroll.employee_id).offset(skip).limit(limit).all()
    
    # Build response with components
    result = []
    for payroll in payrolls:
        payroll_components = db.query(PayrollComponent).filter(
            PayrollComponent.payroll_id == payroll.id
        ).all()
        
        payroll_dict = {
            **{k: v for k, v in payroll.__dict__.items() if not k.startswith('_')},
            'employee_code': payroll.employee.employee_code,
            'employee_name': payroll.employee.full_name,
            'components': [
                {
                    'id': pc.id,
                    'component_id': pc.component_id,
                    'component_code': pc.component_code,
                    'component_name': pc.component_name,
                    'component_type': pc.component_type,
                    'amount': pc.amount
                }
                for pc in payroll_components
            ]
        }
        result.append(PayrollResponse(**payroll_dict))
    
    return result


@router.get("/payrolls/{payroll_id}", response_model=PayrollResponse)
def get_payroll(
    payroll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payroll details"""
    payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id,
        Payroll.temple_id == current_user.temple_id
    ).first()
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    payroll_components = db.query(PayrollComponent).filter(
        PayrollComponent.payroll_id == payroll.id
    ).all()
    
    payroll_dict = {
        **{k: v for k, v in payroll.__dict__.items() if not k.startswith('_')},
        'employee_code': payroll.employee.employee_code,
        'employee_name': payroll.employee.full_name,
        'components': [
            {
                'id': pc.id,
                'component_id': pc.component_id,
                'component_code': pc.component_code,
                'component_name': pc.component_name,
                'component_type': pc.component_type,
                'amount': pc.amount
            }
            for pc in payroll_components
        ]
    }
    
    return PayrollResponse(**payroll_dict)


@router.put("/payrolls/{payroll_id}", response_model=PayrollResponse)
def update_payroll(
    payroll_id: int,
    payroll_data: PayrollUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update payroll (approve, mark as paid, etc.)"""
    payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id,
        Payroll.temple_id == current_user.temple_id
    ).first()
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    update_data = payroll_data.dict(exclude_unset=True)
    
    # If marking as paid, post to accounting
    if update_data.get('status') == PayrollStatus.PAID.value and payroll.status != PayrollStatus.PAID.value:
        # Post salary payment to accounting
        journal_entry = post_salary_to_accounting(db, payroll, current_user.temple_id, current_user)
        if journal_entry:
            payroll.journal_entry_id = journal_entry.id
            update_data['paid_date'] = update_data.get('paid_date', date.today())
            update_data['paid_by'] = current_user.id
    
    for field, value in update_data.items():
        if hasattr(payroll, field):
            setattr(payroll, field, value)
    
    payroll.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(payroll)
    
    payroll_components = db.query(PayrollComponent).filter(
        PayrollComponent.payroll_id == payroll.id
    ).all()
    
    payroll_dict = {
        **{k: v for k, v in payroll.__dict__.items() if not k.startswith('_')},
        'employee_code': payroll.employee.employee_code,
        'employee_name': payroll.employee.full_name,
        'components': [
            {
                'id': pc.id,
                'component_id': pc.component_id,
                'component_code': pc.component_code,
                'component_name': pc.component_name,
                'component_type': pc.component_type,
                'amount': pc.amount
            }
            for pc in payroll_components
        ]
    }
    
    return PayrollResponse(**payroll_dict)


def post_salary_to_accounting(db: Session, payroll: Payroll, temple_id: int, current_user: User):
    """Post salary payment to accounting system"""
    try:
        # Get salary expense account (default: 5200 - Salary Expense)
        expense_account_code = '5200'
        expense_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == expense_account_code
        ).first()
        
        if not expense_account:
            # Try to find by subtype
            from app.models.accounting import AccountSubType
            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_subtype == AccountSubType.OPERATIONAL_EXPENSE
            ).first()
        
        # Get bank account (default: 1110 - Bank Account)
        bank_account_code = '1110'
        bank_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == bank_account_code
        ).first()
        
        if not expense_account or not bank_account:
            print(f"Warning: Salary accounts not found. Expense: {expense_account_code}, Bank: {bank_account_code}")
            return None
        
        # Generate entry number
        year = payroll.payroll_year
        prefix = f"JE/{year}/"
        
        last_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.entry_number.like(f"{prefix}%")
        ).order_by(JournalEntry.id.desc()).first()
        
        if last_entry:
            try:
                last_num = int(last_entry.entry_number.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        entry_number = f"{prefix}{new_num:04d}"
        
        # Create journal entry
        narration = f"Salary payment - {payroll.employee.full_name} - {payroll.payroll_month}/{payroll.payroll_year}"
        
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=datetime.combine(payroll.payroll_date, datetime.min.time()),
            entry_number=entry_number,
            narration=narration,
            reference_type=TransactionType.EXPENSE,  # Salary payment
            reference_id=payroll.id,
            total_amount=payroll.net_salary,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow()
        )
        
        db.add(journal_entry)
        db.flush()
        
        # Debit: Salary Expense
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=expense_account.id,
            debit_amount=payroll.net_salary,
            credit_amount=0,
            description=f"Salary - {payroll.employee.full_name}"
        )
        
        # Credit: Bank Account
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=bank_account.id,
            debit_amount=0,
            credit_amount=payroll.net_salary,
            description=f"Salary payment - {payroll.employee.employee_code}"
        )
        
        db.add(debit_line)
        db.add(credit_line)
        
        return journal_entry
        
    except Exception as e:
        print(f"Error posting salary to accounting: {str(e)}")
        return None


# ===== SALARY SLIP GENERATION =====

@router.get("/payrolls/{payroll_id}/salary-slip")
def generate_salary_slip(
    payroll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate PDF salary slip for payroll"""
    from fastapi.responses import StreamingResponse
    
    payroll = db.query(Payroll).filter(
        Payroll.id == payroll_id,
        Payroll.temple_id == current_user.temple_id
    ).first()
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    employee = payroll.employee
    temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
    
    # Get payroll components
    payroll_components = db.query(PayrollComponent).filter(
        PayrollComponent.payroll_id == payroll.id
    ).order_by(PayrollComponent.component_type, PayrollComponent.id).all()
    
    # Separate earnings and deductions
    earnings = [pc for pc in payroll_components if pc.component_type == SalaryComponentType.EARNING.value]
    deductions = [pc for pc in payroll_components if pc.component_type == SalaryComponentType.DEDUCTION.value]
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'SalarySlipTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FF9933'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Header
    if temple:
        if temple.name:
            elements.append(Paragraph(temple.name, title_style))
        if temple.address:
            elements.append(Paragraph(temple.address, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("_" * 80, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Title
    elements.append(Paragraph("SALARY SLIP", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Employee and Period Details
    period_data = [
        ["Employee Code:", employee.employee_code],
        ["Employee Name:", employee.full_name],
        ["Department:", employee.department.name if employee.department else "N/A"],
        ["Designation:", employee.designation.name if employee.designation else "N/A"],
        ["Period:", f"{payroll.payroll_month}/{payroll.payroll_year}"],
        ["Payment Date:", payroll.payroll_date.strftime('%d-%m-%Y') if payroll.payroll_date else "N/A"],
        ["Days Worked:", str(payroll.days_worked)],
        ["Days Payable:", str(payroll.days_payable)],
    ]
    
    period_table = Table(period_data, colWidths=[2.5*inch, 4*inch])
    period_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(period_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Salary Details Table
    salary_data = [["Earnings", "Amount (₹)"]]
    
    for earning in earnings:
        salary_data.append([earning.component_name, f"{earning.amount:,.2f}"])
    
    salary_data.append(["<b>Total Earnings</b>", f"<b>{payroll.total_earnings:,.2f}</b>"])
    salary_data.append(["", ""])  # Empty row
    salary_data.append(["Deductions", "Amount (₹)"])
    
    for deduction in deductions:
        salary_data.append([deduction.component_name, f"{deduction.amount:,.2f}"])
    
    salary_data.append(["<b>Total Deductions</b>", f"<b>{payroll.total_deductions:,.2f}</b>"])
    salary_data.append(["", ""])  # Empty row
    salary_data.append(["<b>Net Salary</b>", f"<b>{payroll.net_salary:,.2f}</b>"])
    
    salary_table = Table(salary_data, colWidths=[4.5*inch, 2*inch])
    salary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9933')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.beige]),
    ]))
    
    elements.append(salary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Bank Details
    if employee.bank_name:
        bank_data = [
            ["Bank Name:", employee.bank_name],
            ["Account Number:", employee.bank_account_number or "N/A"],
            ["IFSC Code:", employee.bank_ifsc_code or "N/A"],
        ]
        
        bank_table = Table(bank_data, colWidths=[2.5*inch, 4*inch])
        bank_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(bank_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    if temple and temple.authorized_signatory_name:
        elements.append(Paragraph(f"Authorized Signatory: {temple.authorized_signatory_name}", styles['Normal']))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph("MandirSync Temple Management System", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"salary_slip_{employee.employee_code}_{payroll.payroll_month}_{payroll.payroll_year}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


# ===== EMPLOYEE SALARY HISTORY =====

@router.get("/employees/{employee_id}/salary-history", response_model=List[PayrollResponse])
def get_employee_salary_history(
    employee_id: int,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get salary history for an employee"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.temple_id == current_user.temple_id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    query = db.query(Payroll).filter(
        Payroll.employee_id == employee_id,
        Payroll.temple_id == current_user.temple_id
    )
    
    if year:
        query = query.filter(Payroll.payroll_year == year)
    
    payrolls = query.order_by(Payroll.payroll_year.desc(), Payroll.payroll_month.desc()).all()
    
    result = []
    for payroll in payrolls:
        payroll_components = db.query(PayrollComponent).filter(
            PayrollComponent.payroll_id == payroll.id
        ).all()
        
        payroll_dict = {
            **{k: v for k, v in payroll.__dict__.items() if not k.startswith('_')},
            'employee_code': payroll.employee.employee_code,
            'employee_name': payroll.employee.full_name,
            'components': [
                {
                    'id': pc.id,
                    'component_id': pc.component_id,
                    'component_code': pc.component_code,
                    'component_name': pc.component_name,
                    'component_type': pc.component_type,
                    'amount': pc.amount
                }
                for pc in payroll_components
            ]
        }
        result.append(PayrollResponse(**payroll_dict))
    
    return result

