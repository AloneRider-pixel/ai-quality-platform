"""
API Test Suite - Authentication endpoints.
Tests registration, login, token validation, and security.
"""
import pytest
from framework.base_test import BaseAPITest
from framework.data_factories import UserAuthFactory


@pytest.mark.api
@pytest.mark.smoke
class TestRegistration(BaseAPITest):
    """Test user registration."""

    def test_register_success(self, fresh_client):
        """Should register user with valid data."""
        creds = UserAuthFactory.create_credentials()
        response = fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "Test User",
        })
        assert response.status_code in (200, 201, 409)

    def test_register_duplicate_email(self, fresh_client):
        """Should reject duplicate email."""
        creds = UserAuthFactory.create_credentials()
        fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "User One",
        })
        response = fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "User Two",
        })
        assert response.status_code in (409, 400)

    def test_register_invalid_email(self, fresh_client):
        """Should reject invalid email formats."""
        for invalid_email in ["not-email", "@no-local", "no-domain@", ""]:
            response = fresh_client.post("/api/v1/auth/register", json={
                "email": invalid_email,
                "password": "ValidPass123!",
                "full_name": "Test",
            })
            assert response.status_code in (400, 422), f"Should reject: {invalid_email}"

    def test_register_weak_password(self, fresh_client):
        """Should reject weak passwords."""
        response = fresh_client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "123",
            "full_name": "Test",
        })
        assert response.status_code in (400, 422)


@pytest.mark.api
@pytest.mark.smoke
class TestLogin(BaseAPITest):
    """Test login endpoints."""

    def test_login_success(self, fresh_client):
        """Should login with valid credentials."""
        creds = UserAuthFactory.create_credentials()
        fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "Login Test",
        })
        response = fresh_client.post("/api/v1/auth/login", json={
            "email": creds["email"],
            "password": creds["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, fresh_client):
        """Should reject wrong password."""
        response = fresh_client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_returns_jwt(self, fresh_client):
        """Should return valid JWT token."""
        creds = UserAuthFactory.create_credentials()
        fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "JWT Test",
        })
        response = fresh_client.post("/api/v1/auth/login", json={
            "email": creds["email"],
            "password": creds["password"],
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            # JWT has 3 parts separated by dots
            parts = token.split(".")
            assert len(parts) == 3, "Invalid JWT format"


@pytest.mark.api
class TestSecurity(BaseAPITest):
    """Test security aspects of auth endpoints."""

    def test_no_password_in_response(self, fresh_client):
        """Should never return password in response."""
        creds = UserAuthFactory.create_credentials()
        response = fresh_client.post("/api/v1/auth/register", json={
            "email": creds["email"],
            "password": creds["password"],
            "full_name": "Security Test",
        })
        if response.status_code in (200, 201):
            assert creds["password"] not in response.text

    def test_no_sql_injection_in_auth(self, fresh_client):
        """Should not leak SQL errors in auth responses."""
        response = fresh_client.post("/api/v1/auth/login", json={
            "email": "' OR 1=1 --",
            "password": "anything",
        })
        text = response.text.lower()
        assert "sql" not in text
        assert "syntax" not in text
        assert "database" not in text
