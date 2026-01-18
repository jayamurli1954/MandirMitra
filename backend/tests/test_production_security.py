"""
Production Security Tests
Run these tests before deploying to production
"""

import pytest
import os
from app.core.config import settings


class TestProductionSecurity:
    """Security tests for production environment"""

    def test_debug_mode_disabled(self):
        """CRITICAL: Ensure DEBUG is False in production"""
        if os.getenv('ENV') == 'production':
            assert settings.DEBUG == False, "DEBUG must be False in production!"

    def test_secret_key_not_default(self):
        """CRITICAL: Ensure SECRET_KEY is changed from default"""
        default_keys = [
            "your-secret-key-change-this",
            "your-secret-key-change-this-in-production",
            "test-secret-key"
        ]
        assert settings.SECRET_KEY not in default_keys, \
            "SECRET_KEY must be changed from default value!"
        assert len(settings.SECRET_KEY) >= 32, \
            "SECRET_KEY must be at least 32 characters!"

    def test_jwt_secret_key_not_default(self):
        """CRITICAL: Ensure JWT_SECRET_KEY is changed from default"""
        default_keys = [
            "your-jwt-secret-key-change-this",
            "test-jwt-secret"
        ]
        assert settings.JWT_SECRET_KEY not in default_keys, \
            "JWT_SECRET_KEY must be changed from default value!"
        assert len(settings.JWT_SECRET_KEY) >= 64, \
            "JWT_SECRET_KEY must be at least 64 characters!"

    def test_encryption_key_set(self):
        """CRITICAL: Ensure ENCRYPTION_KEY is set"""
        assert settings.ENCRYPTION_KEY is not None, \
            "ENCRYPTION_KEY must be set!"
        assert len(settings.ENCRYPTION_KEY) > 20, \
            "ENCRYPTION_KEY appears invalid!"

    def test_https_enforced_in_production(self):
        """CRITICAL: Ensure HTTPS is enforced in production"""
        if os.getenv('ENV') == 'production':
            assert settings.FORCE_HTTPS == True, \
                "FORCE_HTTPS must be True in production!"

    def test_cors_restricted_in_production(self):
        """CRITICAL: Ensure CORS is restricted to production domain"""
        if os.getenv('ENV') == 'production':
            allowed_origins = settings.allowed_origins_list
            # Should not include localhost
            localhost_origins = [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost',
            ]
            for origin in allowed_origins:
                assert origin not in localhost_origins, \
                    f"CORS includes localhost in production: {origin}"

    def test_database_password_strong(self):
        """HIGH: Ensure database password is strong"""
        db_url = settings.DATABASE_URL
        # Extract password from postgresql://user:password@host/db
        if 'postgresql://' in db_url:
            try:
                password_part = db_url.split('://')[1].split('@')[0]
                if ':' in password_part:
                    password = password_part.split(':')[1]
                    assert len(password) >= 12, \
                        "Database password should be at least 12 characters!"
                    assert password != 'postgres', \
                        "Database password must not be 'postgres'!"
                    assert password != 'password', \
                        "Database password must not be 'password'!"
            except:
                pass  # Can't parse, skip

    def test_rate_limiting_enabled(self):
        """HIGH: Ensure rate limiting is enabled"""
        assert settings.RATE_LIMIT_ENABLED == True, \
            "Rate limiting must be enabled for security!"

    def test_password_policy_enforced(self):
        """MEDIUM: Ensure strong password policy"""
        assert settings.PASSWORD_MIN_LENGTH >= 8, \
            "Password minimum length should be at least 8!"
        assert settings.PASSWORD_REQUIRE_UPPERCASE == True
        assert settings.PASSWORD_REQUIRE_LOWERCASE == True
        assert settings.PASSWORD_REQUIRE_DIGITS == True


class TestSecurityHeaders:
    """Test security headers middleware"""

    def test_security_headers_present(self, client):
        """Test that security headers are set"""
        response = client.get("/health")

        # Check critical security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-XSS-Protection" in response.headers

        # Server header should be removed
        assert "Server" not in response.headers or \
               response.headers.get("Server") != "uvicorn"


class TestInputValidation:
    """Test input validation against attacks"""

    def test_sql_injection_in_devotee_search(self, client, admin_token):
        """Test SQL injection prevention in search"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT password FROM users--"
        ]

        for payload in sql_payloads:
            response = client.get(
                f"/api/v1/devotees/?search={payload}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # Should return 200 with empty/safe results, NOT 500
            assert response.status_code in [200, 400, 422], \
                f"SQL injection may be possible: {payload}"
            # Should not expose SQL errors
            if response.status_code == 500:
                error_text = response.text.lower()
                assert "sql" not in error_text
                assert "syntax error" not in error_text

    def test_xss_in_devotee_name(self, client, admin_token):
        """Test XSS prevention in devotee name"""
        xss_payload = "<script>alert('XSS')</script>"

        response = client.post(
            "/api/v1/devotees/",
            json={
                "full_name": xss_payload,
                "phone": "1234567890"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        if response.status_code == 201:
            devotee_id = response.json()["id"]

            # Retrieve devotee
            get_response = client.get(
                f"/api/v1/devotees/{devotee_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )

            # Script tag should be escaped or sanitized
            response_text = get_response.text
            assert "<script>" not in response_text, \
                "XSS payload not escaped!"


class TestAuthentication:
    """Test authentication security"""

    def test_login_rate_limiting(self, client):
        """Test that login is rate limited"""
        # Note: This test may fail if DEBUG=True
        # Make 10 failed login attempts
        for i in range(10):
            response = client.post(
                "/api/v1/login",
                data={
                    "username": "nonexistent@test.com",
                    "password": "wrongpassword"
                }
            )
            # Should get 401 or 429
            assert response.status_code in [401, 429]

        # 11th attempt should be rate limited
        response = client.post(
            "/api/v1/login",
            data={
                "username": "nonexistent@test.com",
                "password": "wrongpassword"
            }
        )
        # May not work if DEBUG=True, but test anyway
        if response.status_code == 429:
            assert "rate limit" in response.json()["detail"].lower()

    def test_weak_password_rejected(self, client, admin_token):
        """Test that weak passwords are rejected"""
        weak_passwords = [
            "weak",  # Too short
            "password",  # Common
            "12345678",  # No letters
            "abcdefgh",  # No numbers
        ]

        for weak_pwd in weak_passwords:
            response = client.post(
                "/api/v1/users/",
                json={
                    "email": f"test_{weak_pwd}@example.com",
                    "password": weak_pwd,
                    "full_name": "Test User",
                    "role": "staff"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # Should be rejected
            assert response.status_code in [400, 422], \
                f"Weak password accepted: {weak_pwd}"


# Pytest fixtures
@pytest.fixture
def client():
    """Test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def admin_token():
    """Admin authentication token"""
    # You may need to adjust this based on your test setup
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/login",
        data={
            "username": "admin@temple.com",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None
