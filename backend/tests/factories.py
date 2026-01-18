"""
Test data factories using factory_boy

These factories provide an efficient way to create test data with:
- Realistic fake data using Faker
- Customizable attributes
- Relationship handling
- Minimal database overhead

Usage:
    # Create a single instance
    user = UserFactory()

    # Create with custom attributes
    user = UserFactory(email="custom@example.com")

    # Create multiple instances
    users = UserFactory.create_batch(10)

    # Build without saving to database
    user = UserFactory.build()
"""

import factory
from factory import fuzzy
from datetime import datetime, timedelta, date
from passlib.context import CryptContext

from app.models.user import User
from app.models.temple import Temple
from app.models.devotee import Devotee
from app.models.donation import Donation, DonationType, DonationCategory
from app.models.seva import Seva


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TempleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Temple test instances"""

    class Meta:
        model = Temple
        sqlalchemy_session_persistence = "commit"

    # Basic Information
    name = factory.Faker("company")
    name_kannada = factory.Faker("word")
    name_sanskrit = factory.Faker("word")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    primary_deity = factory.Faker("first_name")
    deity_name_kannada = factory.Faker("word")
    deity_name_sanskrit = factory.Faker("word")

    # Address
    address = factory.Faker("address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    pincode = factory.Faker("postalcode")

    # Contact
    phone = factory.Faker("phone_number")
    email = factory.Faker("email")
    website = factory.Faker("url")

    # Registration
    registration_number = factory.Sequence(lambda n: f"REG{n:05d}")
    trust_name = factory.Faker("company")
    pan_number = factory.Sequence(lambda n: f"ABCDE{n:04d}F")
    tan_number = factory.Sequence(lambda n: f"KLMN{n:05d}P")

    # Status
    is_active = True

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User test instances"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    # Authentication
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    password_hash = factory.LazyFunction(
        lambda: pwd_context.hash("testpass123")  # Default test password
    )

    # Profile
    full_name = factory.Faker("name")

    # Role
    role = fuzzy.FuzzyChoice(
        ["super_admin", "temple_manager", "accountant", "counter_staff", "priest"]
    )

    # Status
    is_active = True
    is_superuser = False

    # Security
    failed_login_attempts = 0

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())

    # Relationships
    temple = factory.SubFactory(TempleFactory)


class DonationCategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating DonationCategory test instances"""

    class Meta:
        model = DonationCategory
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    is_80g_eligible = True
    is_active = True
    temple = factory.SubFactory(TempleFactory)


class DevoteeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Devotee test instances"""

    class Meta:
        model = Devotee
        sqlalchemy_session_persistence = "commit"

    # Personal Information
    full_name = factory.Faker("name")
    name = factory.LazyAttribute(lambda obj: obj.full_name)  # name is required, use full_name
    first_name = factory.LazyAttribute(
        lambda obj: obj.full_name.split()[0] if obj.full_name else "Test"
    )
    last_name = factory.LazyAttribute(
        lambda obj: " ".join(obj.full_name.split()[1:]) if len(obj.full_name.split()) > 1 else None
    )
    phone = factory.Faker("phone_number")
    email = factory.Faker("email")

    # Address
    address = factory.Faker("address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    pincode = factory.Faker("postalcode")

    # Birth Details
    date_of_birth = factory.Faker("date_between", start_date="-80y", end_date="-18y")
    # Gothra and Star
    gothra = factory.Faker("word")
    nakshatra = fuzzy.FuzzyChoice(["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira"])

    # Status
    is_active = True

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())

    # Relationships
    temple = factory.SubFactory(TempleFactory)


class SevaFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Seva test instances"""

    class Meta:
        model = Seva
        sqlalchemy_session_persistence = "commit"

    # Basic Information
    name = factory.Faker("sentence", nb_words=3)
    name_kannada = factory.Faker("word")
    name_sanskrit = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=200)

    # Category
    category = fuzzy.FuzzyChoice(
        ["pooja", "homam", "abhishekam", "archana", "special_pooja", "festival"]
    )

    # Pricing
    price = fuzzy.FuzzyDecimal(100.0, 10000.0, precision=2)
    is_fixed_price = True

    # Scheduling
    duration_minutes = fuzzy.FuzzyInteger(15, 120)
    max_bookings_per_day = fuzzy.FuzzyInteger(5, 50)

    # Status
    is_active = True

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())

    # Relationships
    temple = factory.SubFactory(TempleFactory)


class DonationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Donation test instances"""

    class Meta:
        model = Donation
        sqlalchemy_session_persistence = "commit"

    # Amount
    amount = fuzzy.FuzzyDecimal(100.0, 100000.0, precision=2)

    # Category
    category = factory.SubFactory(DonationCategoryFactory)

    # Payment
    payment_mode = fuzzy.FuzzyChoice(["cash", "upi", "card", "cheque", "bank_transfer"])
    # Note: payment_status is not a field in Donation model

    # Donation Type
    donation_type = DonationType.CASH

    # Receipt
    receipt_number = factory.Sequence(lambda n: f"RCP{n:08d}")
    # Note: receipt_date is not a field in Donation model
    # Note: is_80g_eligible is a field in DonationCategory, not in Donation model

    # Donation Date (required field)
    donation_date = factory.LazyFunction(lambda: date.today())

    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())

    # Relationships
    temple = factory.SubFactory(TempleFactory)
    devotee = factory.SubFactory(DevoteeFactory)


# Specialized Factories for specific test scenarios


class AdminUserFactory(UserFactory):
    """Factory for creating admin users"""

    role = "super_admin"
    is_superuser = True


class TempleManagerFactory(UserFactory):
    """Factory for creating temple manager users"""

    role = "temple_manager"
    is_superuser = False


class AccountantFactory(UserFactory):
    """Factory for creating accountant users"""

    role = "accountant"
    is_superuser = False


class LargeDonationFactory(DonationFactory):
    """Factory for creating large donations"""

    amount = fuzzy.FuzzyDecimal(50000.0, 500000.0, precision=2)
    is_80g_applicable = True


class CashDonationFactory(DonationFactory):
    """Factory for creating cash donations"""

    payment_mode = "cash"
    amount = fuzzy.FuzzyDecimal(100.0, 5000.0, precision=2)


# Batch creation helpers


def create_test_temple_with_users(session, num_users=5):
    """
    Create a temple with associated users.

    Args:
        session: Database session
        num_users: Number of users to create

    Returns:
        tuple: (temple, list of users)
    """
    TempleFactory._meta.sqlalchemy_session = session
    UserFactory._meta.sqlalchemy_session = session

    temple = TempleFactory()
    users = UserFactory.create_batch(num_users, temple=temple)

    return temple, users


def create_test_devotee_with_donations(session, num_donations=3):
    """
    Create a devotee with associated donations.

    Args:
        session: Database session
        num_donations: Number of donations to create

    Returns:
        tuple: (devotee, list of donations)
    """
    TempleFactory._meta.sqlalchemy_session = session
    DevoteeFactory._meta.sqlalchemy_session = session
    DonationCategoryFactory._meta.sqlalchemy_session = session
    DonationFactory._meta.sqlalchemy_session = session

    temple = TempleFactory()
    devotee = DevoteeFactory(temple=temple)
    donations = DonationFactory.create_batch(num_donations, devotee=devotee, temple=temple)

    return devotee, donations
