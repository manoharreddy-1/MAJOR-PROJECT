"""Unit and integration tests for SMTP OTP registration, single-email enforcement, and forgot-password reset."""
import pytest
from app import create_app
from routes.auth_routes import _otp_store, hash_password


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAuthOTPandReset:
    def test_case_insensitive_and_email_login(self, client):
        """User can log in with username or email, regardless of casing."""
        # 1. Register candidate
        email = "case_test_user@example.com"
        reg_res = client.post("/api/auth/register", json={
            "username": "CaseSensitiveUser",
            "password": "Password123!",
            "full_name": "Case User",
            "email": email
        })
        assert reg_res.status_code in [200, 201]

        # 2. Login with exact username
        res1 = client.post("/api/auth/login", json={
            "username": "CaseSensitiveUser",
            "password": "Password123!"
        })
        assert res1.status_code == 200

        # 3. Login with lowercase username
        res2 = client.post("/api/auth/login", json={
            "username": "casesensitiveuser",
            "password": "Password123!"
        })
        assert res2.status_code == 200

        # 4. Login with email
        res3 = client.post("/api/auth/login", json={
            "username": "case_test_user@example.com",
            "password": "Password123!"
        })
        assert res3.status_code == 200

        # 5. Login with uppercase email
        res4 = client.post("/api/auth/login", json={
            "username": "CASE_TEST_USER@EXAMPLE.COM",
            "password": "Password123!"
        })
        assert res4.status_code == 200

    def test_registration_otp_and_single_email_enforcement(self, client):
        """Verify OTP sending, verification, and that each email can only be registered once."""
        email = "single_email_owner@example.com"
        username1 = "user_alpha_1"

        # 1. Send registration OTP
        otp_res = client.post("/api/auth/send-register-otp", json={
            "email": email,
            "username": username1,
            "full_name": "Alpha One"
        })
        assert otp_res.status_code == 200
        otp_data = otp_res.get_json()["data"]
        assert otp_data["sender"] == "bommareddymanoharreddy0@gmail.com"

        # Extract generated OTP from test store
        key = f"reg:{email.lower()}"
        assert key in _otp_store
        otp = _otp_store[key]["otp"]
        assert len(otp) == 6

        # 2. Register with wrong OTP fails
        fail_reg = client.post("/api/auth/register", json={
            "username": username1,
            "password": "SecurePassword1",
            "email": email,
            "otp": "000000"
        })
        assert fail_reg.status_code == 400
        assert "Invalid verification code" in fail_reg.get_json()["error"]["message"]

        # 3. Register with correct OTP succeeds
        success_reg = client.post("/api/auth/register", json={
            "username": username1,
            "password": "SecurePassword1",
            "email": email,
            "otp": otp
        })
        assert success_reg.status_code == 201

        # 4. Attempt to send OTP for the SAME email must be rejected (single-use constraint)
        dup_otp_res = client.post("/api/auth/send-register-otp", json={
            "email": email,
            "username": "another_user_beta"
        })
        assert dup_otp_res.status_code in [400, 409]
        assert "already registered" in dup_otp_res.get_json()["error"]["message"]

        # 5. Direct registration attempt with already-registered email is also blocked
        dup_reg = client.post("/api/auth/register", json={
            "username": "another_user_beta",
            "password": "PasswordBeta",
            "email": email,
            "otp": "123456"
        })
        assert dup_reg.status_code in [400, 409]
        assert "already registered" in dup_reg.get_json()["error"]["message"]

    def test_forgot_password_flow(self, client):
        """Verify requesting reset OTP, validating OTP, setting new password, and logging in."""
        email = "forgot_flow_user@example.com"
        username = "forgot_user_test"

        # 1. Register candidate
        reg_res = client.post("/api/auth/register", json={
            "username": username,
            "password": "InitialPassword123",
            "email": email
        })
        assert reg_res.status_code in [200, 201]

        # 2. Request forgot password OTP
        forgot_res = client.post("/api/auth/forgot-password", json={
            "email": email
        })
        assert forgot_res.status_code == 200
        forgot_data = forgot_res.get_json()["data"]
        assert forgot_data["sender"] == "bommareddymanoharreddy0@gmail.com"

        # Extract reset OTP
        reset_key = f"reset:{email.lower()}"
        assert reset_key in _otp_store
        reset_otp = _otp_store[reset_key]["otp"]
        assert len(reset_otp) == 6

        # 3. Reset with wrong OTP fails
        fail_reset = client.post("/api/auth/reset-password", json={
            "email": email,
            "otp": "999999",
            "new_password": "BrandNewPassword456"
        })
        assert fail_reset.status_code == 400
        assert "Invalid verification code" in fail_reset.get_json()["error"]["message"]

        # 4. Reset with valid OTP succeeds
        ok_reset = client.post("/api/auth/reset-password", json={
            "email": email,
            "otp": reset_otp,
            "new_password": "BrandNewPassword456"
        })
        assert ok_reset.status_code == 200

        # 5. Old password no longer works
        old_login = client.post("/api/auth/login", json={
            "username": username,
            "password": "InitialPassword123"
        })
        assert old_login.status_code == 401

        # 6. New password works
        new_login = client.post("/api/auth/login", json={
            "username": username,
            "password": "BrandNewPassword456"
        })
        assert new_login.status_code == 200
        assert new_login.get_json()["success"] is True
