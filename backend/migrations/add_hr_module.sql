-- Migration: Add HR & Salary Management Module Tables
-- Complete HR system with employee management, salary structure, and payroll processing

-- ===== DEPARTMENTS =====
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_departments_temple ON departments(temple_id);
CREATE INDEX idx_departments_code ON departments(code);
CREATE UNIQUE INDEX idx_departments_temple_code ON departments(temple_id, code);

-- ===== DESIGNATIONS =====
CREATE TABLE IF NOT EXISTS designations (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_designations_temple ON designations(temple_id);
CREATE INDEX idx_designations_code ON designations(code);
CREATE UNIQUE INDEX idx_designations_temple_code ON designations(temple_id, code);

-- ===== EMPLOYEES =====
CREATE TYPE employeestatus AS ENUM ('active', 'inactive', 'resigned', 'terminated', 'on_leave');
CREATE TYPE employeetype AS ENUM ('permanent', 'contract', 'temporary', 'part_time', 'volunteer');

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    employee_code VARCHAR(50) NOT NULL UNIQUE,
    employee_id_number VARCHAR(50),
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(300),
    phone VARCHAR(20) NOT NULL,
    alternate_phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    designation_id INTEGER NOT NULL REFERENCES designations(id),
    employee_type employeetype NOT NULL DEFAULT 'permanent',
    status employeestatus NOT NULL DEFAULT 'active',
    joining_date DATE NOT NULL,
    confirmation_date DATE,
    resignation_date DATE,
    last_working_date DATE,
    bank_name VARCHAR(200),
    bank_account_number VARCHAR(50),
    bank_ifsc_code VARCHAR(20),
    bank_branch VARCHAR(200),
    pan_number VARCHAR(20),
    aadhaar_number VARCHAR(20),
    pf_number VARCHAR(50),
    esi_number VARCHAR(50),
    uan_number VARCHAR(50),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    photo_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_employees_temple ON employees(temple_id);
CREATE INDEX idx_employees_code ON employees(employee_code);
CREATE INDEX idx_employees_phone ON employees(phone);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_designation ON employees(designation_id);
CREATE INDEX idx_employees_joining_date ON employees(joining_date);

-- ===== SALARY COMPONENTS =====
CREATE TYPE salarycomponenttype AS ENUM ('earning', 'deduction');

CREATE TABLE IF NOT EXISTS salary_components (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    component_type salarycomponenttype NOT NULL,
    is_percentage BOOLEAN DEFAULT FALSE,
    base_component_code VARCHAR(20),
    default_value FLOAT DEFAULT 0.0,
    is_statutory BOOLEAN DEFAULT FALSE,
    is_taxable BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_salary_components_temple ON salary_components(temple_id);
CREATE INDEX idx_salary_components_code ON salary_components(code);
CREATE UNIQUE INDEX idx_salary_components_temple_code ON salary_components(temple_id, code);

-- ===== SALARY STRUCTURES =====
CREATE TABLE IF NOT EXISTS salary_structures (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL UNIQUE REFERENCES employees(id) ON DELETE CASCADE,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    gross_salary FLOAT NOT NULL,
    net_salary FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_salary_structures_employee ON salary_structures(employee_id);
CREATE INDEX idx_salary_structures_temple ON salary_structures(temple_id);
CREATE INDEX idx_salary_structures_effective_from ON salary_structures(effective_from);

-- ===== SALARY STRUCTURE COMPONENTS =====
CREATE TABLE IF NOT EXISTS salary_structure_components (
    id SERIAL PRIMARY KEY,
    salary_structure_id INTEGER NOT NULL REFERENCES salary_structures(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES salary_components(id),
    amount FLOAT NOT NULL,
    percentage FLOAT,
    calculated_amount FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_structure_components_structure ON salary_structure_components(salary_structure_id);
CREATE INDEX idx_structure_components_component ON salary_structure_components(component_id);

-- ===== PAYROLLS =====
CREATE TYPE payrollstatus AS ENUM ('draft', 'processed', 'approved', 'paid', 'cancelled');

CREATE TABLE IF NOT EXISTS payrolls (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    payroll_month INTEGER NOT NULL,
    payroll_year INTEGER NOT NULL,
    payroll_date DATE NOT NULL,
    days_worked INTEGER DEFAULT 0,
    days_payable INTEGER DEFAULT 0,
    leave_days INTEGER DEFAULT 0,
    gross_salary FLOAT NOT NULL,
    total_earnings FLOAT NOT NULL,
    total_deductions FLOAT NOT NULL,
    net_salary FLOAT NOT NULL,
    status payrollstatus NOT NULL DEFAULT 'draft',
    payment_mode VARCHAR(20),
    payment_reference VARCHAR(100),
    paid_date DATE,
    paid_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    journal_entry_id INTEGER REFERENCES journal_entries(id) ON DELETE SET NULL,
    salary_slip_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    processed_at TIMESTAMPTZ,
    processed_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_payrolls_temple ON payrolls(temple_id);
CREATE INDEX idx_payrolls_employee ON payrolls(employee_id);
CREATE INDEX idx_payrolls_month_year ON payrolls(payroll_month, payroll_year);
CREATE INDEX idx_payrolls_date ON payrolls(payroll_date);
CREATE INDEX idx_payrolls_status ON payrolls(status);
CREATE UNIQUE INDEX idx_payrolls_employee_month_year ON payrolls(employee_id, payroll_month, payroll_year);

-- ===== PAYROLL COMPONENTS =====
CREATE TABLE IF NOT EXISTS payroll_components (
    id SERIAL PRIMARY KEY,
    payroll_id INTEGER NOT NULL REFERENCES payrolls(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES salary_components(id),
    component_code VARCHAR(20) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    component_type salarycomponenttype NOT NULL,
    amount FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payroll_components_payroll ON payroll_components(payroll_id);
CREATE INDEX idx_payroll_components_component ON payroll_components(component_id);

-- ===== LEAVE TYPES =====
CREATE TABLE IF NOT EXISTS leave_types (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_paid BOOLEAN DEFAULT TRUE,
    max_days_per_year INTEGER DEFAULT 0,
    carry_forward_allowed BOOLEAN DEFAULT FALSE,
    max_carry_forward_days INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leave_types_temple ON leave_types(temple_id);
CREATE INDEX idx_leave_types_code ON leave_types(code);
CREATE UNIQUE INDEX idx_leave_types_temple_code ON leave_types(temple_id, code);

-- ===== LEAVE APPLICATIONS =====
CREATE TABLE IF NOT EXISTS leave_applications (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    days INTEGER NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_leave_applications_temple ON leave_applications(temple_id);
CREATE INDEX idx_leave_applications_employee ON leave_applications(employee_id);
CREATE INDEX idx_leave_applications_from_date ON leave_applications(from_date);
CREATE INDEX idx_leave_applications_status ON leave_applications(status);

-- Add comments for documentation
COMMENT ON TABLE departments IS 'Department master data';
COMMENT ON TABLE designations IS 'Designation master data';
COMMENT ON TABLE employees IS 'Employee master data with personal and employment details';
COMMENT ON TABLE salary_components IS 'Salary component master (Basic, HRA, PF, etc.)';
COMMENT ON TABLE salary_structures IS 'Employee salary structure';
COMMENT ON TABLE salary_structure_components IS 'Components in a salary structure';
COMMENT ON TABLE payrolls IS 'Monthly payroll records';
COMMENT ON TABLE payroll_components IS 'Salary components in a payroll';
COMMENT ON TABLE leave_types IS 'Leave type master';
COMMENT ON TABLE leave_applications IS 'Employee leave applications';

