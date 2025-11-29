"""
Example integration tests demonstrating database and API testing

Integration tests verify that different components work together correctly.
They use the database fixtures and test factories.
"""

import pytest
from tests.factories import (
    TempleFactory,
    UserFactory,
    DevoteeFactory,
    DonationFactory,
    AdminUserFactory,
    create_test_temple_with_users,
    create_test_devotee_with_donations,
)


@pytest.mark.integration
@pytest.mark.database
class TestTempleIntegration:
    """Integration tests for Temple model"""

    def test_create_temple(self, db_session):
        """Test creating a temple using factory"""
        # Set the session for the factory
        TempleFactory._meta.sqlalchemy_session = db_session

        # Create temple
        temple = TempleFactory(name="Test Temple")

        # Verify
        assert temple.id is not None
        assert temple.name == "Test Temple"
        assert temple.is_active is True

    def test_temple_with_users(self, db_session):
        """Test creating temple with associated users"""
        temple, users = create_test_temple_with_users(db_session, num_users=3)

        # Verify temple
        assert temple.id is not None

        # Verify users
        assert len(users) == 3
        for user in users:
            assert user.temple_id == temple.id
            assert user.is_active is True

    def test_query_temple(self, db_session):
        """Test querying temples from database"""
        TempleFactory._meta.sqlalchemy_session = db_session

        # Create multiple temples
        temple1 = TempleFactory(name="Temple One")
        temple2 = TempleFactory(name="Temple Two")
        db_session.commit()

        # Query
        result = db_session.query(TempleFactory._meta.model).all()

        # Verify
        assert len(result) >= 2
        names = [t.name for t in result]
        assert "Temple One" in names
        assert "Temple Two" in names


@pytest.mark.integration
@pytest.mark.database
class TestUserIntegration:
    """Integration tests for User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        UserFactory._meta.sqlalchemy_session = db_session
        TempleFactory._meta.sqlalchemy_session = db_session

        user = UserFactory(
            email="test@example.com", full_name="Test User", role="accountant"
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == "accountant"
        assert user.temple_id is not None

    def test_create_admin_user(self, db_session):
        """Test creating admin user with specialized factory"""
        AdminUserFactory._meta.sqlalchemy_session = db_session
        TempleFactory._meta.sqlalchemy_session = db_session

        admin = AdminUserFactory()

        assert admin.role == "super_admin"
        assert admin.is_superuser is True

    def test_user_temple_relationship(self, db_session):
        """Test user-temple relationship"""
        TempleFactory._meta.sqlalchemy_session = db_session
        UserFactory._meta.sqlalchemy_session = db_session

        temple = TempleFactory()
        user = UserFactory(temple=temple)

        # Verify relationship
        assert user.temple_id == temple.id
        assert user.temple.name == temple.name


@pytest.mark.integration
@pytest.mark.database
class TestDonationIntegration:
    """Integration tests for Donation model"""

    def test_create_donation(self, db_session):
        """Test creating a donation"""
        TempleFactory._meta.sqlalchemy_session = db_session
        DevoteeFactory._meta.sqlalchemy_session = db_session
        DonationFactory._meta.sqlalchemy_session = db_session

        temple = TempleFactory()
        devotee = DevoteeFactory(temple=temple)
        donation = DonationFactory(temple=temple, devotee=devotee, amount=1000.00)

        assert donation.id is not None
        assert donation.amount == 1000.00
        assert donation.devotee_id == devotee.id
        assert donation.temple_id == temple.id

    def test_devotee_with_multiple_donations(self, db_session):
        """Test devotee with multiple donations"""
        devotee, donations = create_test_devotee_with_donations(
            db_session, num_donations=5
        )

        # Verify devotee
        assert devotee.id is not None

        # Verify donations
        assert len(donations) == 5
        for donation in donations:
            assert donation.devotee_id == devotee.id
            assert donation.temple_id == devotee.temple_id

    def test_query_donations_by_temple(self, db_session):
        """Test querying donations by temple"""
        TempleFactory._meta.sqlalchemy_session = db_session
        DevoteeFactory._meta.sqlalchemy_session = db_session
        DonationFactory._meta.sqlalchemy_session = db_session

        temple1 = TempleFactory()
        temple2 = TempleFactory()

        devotee1 = DevoteeFactory(temple=temple1)
        devotee2 = DevoteeFactory(temple=temple2)

        # Create donations for each temple
        DonationFactory.create_batch(3, temple=temple1, devotee=devotee1)
        DonationFactory.create_batch(2, temple=temple2, devotee=devotee2)

        db_session.commit()

        # Query donations for temple1
        from app.models.donation import Donation

        temple1_donations = (
            db_session.query(Donation).filter_by(temple_id=temple1.id).all()
        )

        # Verify
        assert len(temple1_donations) == 3


@pytest.mark.integration
class TestBatchCreation:
    """Test efficient batch creation of test data"""

    def test_create_multiple_temples(self, db_session):
        """Test creating multiple temples efficiently"""
        TempleFactory._meta.sqlalchemy_session = db_session

        # Create 10 temples at once
        temples = TempleFactory.create_batch(10)

        assert len(temples) == 10
        for temple in temples:
            assert temple.id is not None

    @pytest.mark.slow
    def test_create_large_dataset(self, db_session):
        """Test creating a large dataset (marked as slow)"""
        TempleFactory._meta.sqlalchemy_session = db_session
        UserFactory._meta.sqlalchemy_session = db_session

        # Create 5 temples with 10 users each
        for _ in range(5):
            temple = TempleFactory()
            UserFactory.create_batch(10, temple=temple)

        db_session.commit()

        # Verify
        from app.models.user import User

        total_users = db_session.query(User).count()
        assert total_users == 50
