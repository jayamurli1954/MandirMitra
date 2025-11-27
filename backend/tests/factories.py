"""
Test Data Factories for MandirSync

Using factory_boy to generate realistic test data efficiently.
This is MUCH faster and more maintainable than creating test data manually.

Usage:
    # Create a single user
    user = UserFactory()

    # Create multiple users
    users = UserFactory.create_batch(10)

    # Create with custom attributes
    admin = UserFactory(role='super_admin', username='admin')

    # Create without saving to database
    user = UserFactory.build()
"""

import factory
from factory.faker import Faker
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.hr import Employee, Department, Designation, Payroll
from app.models.accounting import Account, JournalEntry, JournalLine
from app.database import SessionLocal


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory with common configuration"""
    class Meta:
        abstract = True
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"


# ============================================================================
# USER & AUTHENTICATION FACTORIES
# ============================================================================

class UserFactory(BaseFactory):
    """Factory for creating test users"""
    class Meta:
        model = User

    username = Faker('user_name')
    email = Faker('email')
    full_name = Faker('name')
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYMpXBxwO6u"  # "password123"
    role = "staff"
    is_active = True
    temple_id = 1

    @factory.post_generation
    def set_role(obj, create, extracted, **kwargs):
        """Allow setting role via UserFactory(role='admin')"""
        if extracted:
            obj.role = extracted


# ============================================================================
# DEVOTEE FACTORIES
# ============================================================================

class DevoteeFactory(BaseFactory):
    """Factory for creating test devotees"""
    class Meta:
        model = Devotee

    name = Faker('name')
    phone = factory.LazyAttribute(lambda o: f"+91{random.randint(7000000000, 9999999999)}")
    email = Faker('email')
    address = Faker('address')
    gotra = factory.Faker('random_element', elements=['Bharadwaja', 'Kashyapa', 'Vasishtha', 'Vishwamitra', 'Atri'])
    nakshatra = factory.Faker('random_element', elements=['Ashwini', 'Bharani', 'Rohini', 'Mrigashira', 'Ardra'])
    rashi = factory.Faker('random_element', elements=['Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha'])
    temple_id = 1


# ============================================================================
# DONATION FACTORIES
# ============================================================================

class DonationFactory(BaseFactory):
    """Factory for creating test donations"""
    class Meta:
        model = Donation

    donor_name = Faker('name')
    amount = factory.LazyAttribute(lambda o: Decimal(random.uniform(100, 10000)).quantize(Decimal('0.01')))
    payment_method = factory.Faker('random_element', elements=['cash', 'upi', 'card', 'bank_transfer'])
    donation_date = factory.LazyFunction(date.today)
    phone = factory.LazyAttribute(lambda o: f"+91{random.randint(7000000000, 9999999999)}")
    email = Faker('email')
    purpose = factory.Faker('sentence', nb_words=6)
    receipt_number = factory.Sequence(lambda n: f"DN{date.today().strftime('%Y%m%d')}{n:04d}")
    temple_id = 1
    is_80g_eligible = False


class Donation80GFactory(DonationFactory):
    """Factory for creating 80G eligible donations"""
    is_80g_eligible = True
    pan_number = factory.Faker('random_element', elements=['ABCDE1234F', 'XYZAB5678C', 'PQRST9012D'])
    amount = factory.LazyAttribute(lambda o: Decimal(random.uniform(5000, 50000)).quantize(Decimal('0.01')))


# ============================================================================
# SEVA FACTORIES
# ============================================================================

class SevaFactory(BaseFactory):
    """Factory for creating test sevas"""
    class Meta:
        model = Seva

    name_english = factory.Faker('random_element', elements=[
        'Abhishekam', 'Sahasranama Archana', 'Rudrabhishekam',
        'Lalitha Sahasranama', 'Vishnu Sahasranama'
    ])
    name_local = factory.LazyAttribute(lambda o: o.name_english)  # Simplified
    description = Faker('text', max_nb_chars=200)
    price = factory.LazyAttribute(lambda o: Decimal(random.choice([100, 250, 500, 1000, 2500])))
    duration_minutes = factory.Faker('random_element', elements=[30, 45, 60, 90, 120])
    is_active = True
    temple_id = 1


class SevaBookingFactory(BaseFactory):
    """Factory for creating test seva bookings"""
    class Meta:
        model = SevaBooking

    seva = factory.SubFactory(SevaFactory)
    devotee = factory.SubFactory(DevoteeFactory)
    devotee_name = factory.LazyAttribute(lambda o: o.devotee.name if o.devotee else Faker('name').generate())
    gotra = factory.Faker('random_element', elements=['Bharadwaja', 'Kashyapa', 'Vasishtha'])
    nakshatra = factory.Faker('random_element', elements=['Rohini', 'Ashwini', 'Bharani'])
    seva_date = factory.LazyFunction(lambda: date.today() + timedelta(days=random.randint(1, 30)))
    seva_time = "10:00"
    payment_method = factory.Faker('random_element', elements=['cash', 'upi', 'card'])
    receipt_number = factory.Sequence(lambda n: f"SB{date.today().strftime('%Y%m%d')}{n:04d}")
    status = "confirmed"
    temple_id = 1


# ============================================================================
# HR FACTORIES
# ============================================================================

class DepartmentFactory(BaseFactory):
    """Factory for creating test departments"""
    class Meta:
        model = Department

    code = factory.Sequence(lambda n: f"DEPT{n:03d}")
    name = factory.Faker('random_element', elements=[
        'Accounts', 'Administration', 'Priests', 'Maintenance', 'Kitchen', 'Security'
    ])
    description = Faker('text', max_nb_chars=100)
    is_active = True
    temple_id = 1


class DesignationFactory(BaseFactory):
    """Factory for creating test designations"""
    class Meta:
        model = Designation

    code = factory.Sequence(lambda n: f"DES{n:03d}")
    title = factory.Faker('random_element', elements=[
        'Senior Accountant', 'Junior Accountant', 'Head Priest', 'Assistant Priest',
        'Manager', 'Supervisor', 'Clerk', 'Security Guard'
    ])
    description = Faker('text', max_nb_chars=100)
    is_active = True
    temple_id = 1


class EmployeeFactory(BaseFactory):
    """Factory for creating test employees"""
    class Meta:
        model = Employee

    employee_code = factory.Sequence(lambda n: f"EMP-{n:04d}")
    full_name = Faker('name')
    date_of_birth = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(20*365, 60*365)))
    gender = factory.Faker('random_element', elements=['male', 'female', 'other'])
    phone = factory.LazyAttribute(lambda o: f"+91{random.randint(7000000000, 9999999999)}")
    email = Faker('email')
    address = Faker('address')
    joining_date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(30, 1000)))
    employee_type = "permanent"
    status = "active"
    basic_salary = factory.LazyAttribute(lambda o: Decimal(random.choice([15000, 20000, 25000, 30000, 40000, 50000])))
    department = factory.SubFactory(DepartmentFactory)
    designation = factory.SubFactory(DesignationFactory)
    temple_id = 1


class PayrollFactory(BaseFactory):
    """Factory for creating test payroll"""
    class Meta:
        model = Payroll

    employee = factory.SubFactory(EmployeeFactory)
    month = factory.LazyFunction(lambda: date.today().month)
    year = factory.LazyFunction(lambda: date.today().year)
    basic_salary = factory.LazyAttribute(lambda o: o.employee.basic_salary if o.employee else Decimal('25000.00'))
    gross_salary = factory.LazyAttribute(lambda o: o.basic_salary * Decimal('1.4'))  # 40% allowances
    total_deductions = factory.LazyAttribute(lambda o: o.basic_salary * Decimal('0.12'))  # 12% PF
    net_salary = factory.LazyAttribute(lambda o: o.gross_salary - o.total_deductions)
    status = "draft"
    temple_id = 1


# ============================================================================
# ACCOUNTING FACTORIES
# ============================================================================

class AccountFactory(BaseFactory):
    """Factory for creating test accounts"""
    class Meta:
        model = Account

    account_code = factory.Sequence(lambda n: f"{1000 + n}")
    account_name = factory.Faker('random_element', elements=[
        'Cash - Main Counter', 'Bank - SBI', 'Donation Income',
        'Seva Income', 'Salary Expense', 'Utilities Expense'
    ])
    account_type = factory.Faker('random_element', elements=['asset', 'liability', 'income', 'expense', 'equity'])
    is_active = True
    temple_id = 1


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_test_user(role='staff', **kwargs):
    """Quick helper to create a user with specific role"""
    return UserFactory(role=role, **kwargs)


def create_test_donation(amount=None, **kwargs):
    """Quick helper to create a donation with specific amount"""
    if amount:
        kwargs['amount'] = Decimal(str(amount))
    return DonationFactory(**kwargs)


def create_test_employee(salary=None, **kwargs):
    """Quick helper to create an employee with specific salary"""
    if salary:
        kwargs['basic_salary'] = Decimal(str(salary))
    return EmployeeFactory(**kwargs)


def create_complete_seva_booking(**kwargs):
    """Create a complete seva booking with all relationships"""
    devotee = DevoteeFactory()
    seva = SevaFactory()
    return SevaBookingFactory(devotee=devotee, seva=seva, **kwargs)


# ============================================================================
# EXAMPLE USAGE IN TESTS
# ============================================================================
"""
# In your test files:

from tests.factories import (
    UserFactory, DonationFactory, Donation80GFactory,
    SevaFactory, SevaBookingFactory, EmployeeFactory,
    create_test_user, create_test_donation
)

def test_example_using_factories():
    # Create single instances
    user = UserFactory()
    admin = UserFactory(role='super_admin')

    # Create multiple instances
    donations = DonationFactory.create_batch(10)
    employees = EmployeeFactory.create_batch(5)

    # Create with specific attributes
    large_donation = create_test_donation(amount=100000)

    # Create 80G donation
    tax_donation = Donation80GFactory()

    # Create complete booking
    booking = create_complete_seva_booking()

    assert user.id is not None
    assert len(donations) == 10
    assert booking.seva is not None
"""
