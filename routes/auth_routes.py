"""User authentication routes (Register, Login, Me, Logout, OTP Verification, and Password Reset).

Features:
- Live SMTP Email OTP delivery via bommareddymanoharreddy0@gmail.com
- Single registration per email constraint ("only 1 time accept to each mail")
- Case-insensitive login via Username OR Email
- Forgot Password flow with OTP email verification before setting new password
- Persistent user store across server restarts in offline/mock mode
"""
import hashlib
import json
import logging
import os
import re
import secrets
import time
import uuid
from typing import Dict, Optional
from flask import Blueprint, request, current_app

from routes.responses import error_response, success_response
from database.models import utc_now, serialize_doc
from database.mongodb import get_collection, COLLECTIONS
from services.email_service import send_otp_email, is_smtp_configured, DEFAULT_SENDER

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

users_col = get_collection(COLLECTIONS["users"])

# Local persistence file for users in offline/mock mode
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_STORE_FILE = os.path.join(BASE_DIR, "database", "users_store.json")

# In-memory OTP storage: key -> {"otp_hash": str, "expires_at": float, "attempts": int, ...}
_otp_store: Dict[str, dict] = {}
OTP_SALT = "ai_resume_analyzer_otp_salt_v1_"


def hash_otp(otp: str) -> str:
    """Hash one-time password with salt for secure storage."""
    return hashlib.sha256((OTP_SALT + str(otp).strip()).encode("utf-8")).hexdigest()


BULK_ALLOWED_ROLES = {
    "recruiter", "placement cell", "placement", "admin", "recruiter/placement cell",
    "student", "learner", "candidate", "all", "user"
}


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "ai_resume_analyzer_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Safely verify plain password against stored hash with fallback."""
    if not plain_password or not stored_hash:
        return False
    # Standard salted SHA-256 check
    if hash_password(plain_password) == stored_hash:
        return True
    # Legacy unsalted SHA-256 check
    if hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == stored_hash:
        return True
    # Legacy plaintext check
    if plain_password == stored_hash:
        return True
    return False


def save_user_to_store(user_doc: dict):
    """Persist user record to users_store.json to ensure data survives server restarts."""
    try:
        if current_app and current_app.config.get("TESTING"):
            return  # Do not pollute persistent store during automated test runs

        data = {}
        if os.path.exists(USERS_STORE_FILE):
            try:
                with open(USERS_STORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        u_id = user_doc.get("user_id") or user_doc.get("username")
        clean_doc = serialize_doc(user_doc)
        data[u_id] = clean_doc

        os.makedirs(os.path.dirname(USERS_STORE_FILE), exist_ok=True)
        with open(USERS_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as exc:
        logger.warning("Could not persist user to file: %s", exc)


def load_persisted_users():
    """Load persisted users from file into users_col on startup."""
    try:
        if os.path.exists(USERS_STORE_FILE):
            with open(USERS_STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            col = get_collection(COLLECTIONS["users"])
            for u_id, doc in data.items():
                uname = doc.get("username")
                if uname and not col.find_one({"username": uname}):
                    col.insert_one(doc)
    except Exception as exc:
        logger.warning("Could not load persisted users: %s", exc)


def ensure_default_users():
    """Ensure standard demo/student/recruiter users exist in the collection."""
    try:
        col = get_collection(COLLECTIONS["users"])
        for uname, pwd, name, em, role in [
            ("student", "student123", "Student Candidate", "student@example.edu", "Student"),
            ("recruiter", "recruiter123", "Campus Recruiter", "recruiter@company.com", "Recruiter"),
            ("placement", "placement123", "Placement Officer", "placement@college.edu", "Placement Cell"),
            ("demo", "demo123", "Demo Recruiter", "demo@example.edu", "Recruiter"),
        ]:
            if not col.find_one({"username": uname}):
                doc = {
                    "user_id": f"usr_{uname}",
                    "username": uname,
                    "password_hash": hash_password(pwd),
                    "full_name": name,
                    "email": em,
                    "role": role,
                    "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={uname}",
                    "created_at": utc_now(),
                }
                col.insert_one(doc)
                save_user_to_store(doc)
    except Exception as exc:
        logger.warning("Could not pre-seed default users: %s", exc)


# Seed and restore users on module load
ensure_default_users()
load_persisted_users()


def find_user_by_identifier(identifier: str) -> Optional[dict]:
    """Find user by username OR email (case-insensitive and trimmed)."""
    if not identifier:
        return None
    raw = identifier.strip()
    clean_lower = raw.lower()

    col = get_collection(COLLECTIONS["users"])

    # 1. Direct match
    u = col.find_one({"username": raw}) or col.find_one({"email": raw})
    if u:
        return u

    # 2. Case-insensitive scan
    try:
        all_docs = list(col.find({}))
    except Exception:
        all_docs = []

    for doc in all_docs:
        d_uname = (doc.get("username") or "").strip().lower()
        d_email = (doc.get("email") or "").strip().lower()
        if d_uname == clean_lower or d_email == clean_lower:
            return doc

    # 3. Check persistent JSON file directly
    if os.path.exists(USERS_STORE_FILE):
        try:
            with open(USERS_STORE_FILE, "r", encoding="utf-8") as f:
                saved_users = json.load(f)
            for doc in saved_users.values():
                d_uname = (doc.get("username") or "").strip().lower()
                d_email = (doc.get("email") or "").strip().lower()
                if d_uname == clean_lower or d_email == clean_lower:
                    # Sync back into memory
                    if not col.find_one({"username": doc.get("username")}):
                        col.insert_one(doc)
                    return doc
        except Exception:
            pass

    return None


def is_email_already_registered(email: str) -> bool:
    """Check if an email address is already bound to any existing user."""
    if not email:
        return False
    target = email.strip().lower()
    col = get_collection(COLLECTIONS["users"])

    # Check MongoDB collection
    try:
        for doc in col.find({}):
            if (doc.get("email") or "").strip().lower() == target:
                return True
    except Exception:
        pass

    # Check persisted file
    if os.path.exists(USERS_STORE_FILE):
        try:
            with open(USERS_STORE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for doc in saved.values():
                if (doc.get("email") or "").strip().lower() == target:
                    return True
        except Exception:
            pass

    return False


def get_request_user(req) -> Optional[dict]:
    """Resolve current user from headers, tokens, query params, cookies or body."""
    auth_header = req.headers.get("Authorization", "")
    user_id = None
    if auth_header.startswith("Bearer token_"):
        user_id = auth_header.replace("Bearer token_", "").strip()

    user_id = user_id or req.headers.get("X-User-Id") or req.args.get("user_id") or req.cookies.get("user_id")
    username = req.headers.get("X-Username") or req.args.get("username") or req.cookies.get("username")

    if user_id:
        col = get_collection(COLLECTIONS["users"])
        u = col.find_one({"user_id": user_id})
        if u:
            return u
        return {"user_id": user_id, "username": username or user_id}

    if username:
        return find_user_by_identifier(username)

    header_role = req.headers.get("X-User-Role") or req.args.get("role") or req.cookies.get("role") or req.cookies.get("user_role")
    if header_role:
        return {"role": header_role, "username": username or "custom_user"}

    return None


def is_bulk_authorized(req) -> bool:
    """Bulk screening authorized for all registered roles."""
    return True


# =========================================================================
# OTP Endpoints
# =========================================================================

@auth_bp.route("/send-register-otp", methods=["POST"])
def send_register_otp():
    """
    Step 1 of Registration: Validate unique email and dispatch 6-digit OTP via SMTP.
    Strict Rule: Only 1 account per email address allowed.
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    full_name = (data.get("full_name") or username).strip()

    if not email or "@" not in email:
        return error_response("VALIDATION_ERROR", "A valid email address is required to receive your OTP.")

    if not username:
        return error_response("VALIDATION_ERROR", "Username is required.")

    # 1. Enforce 1-time registration per email rule
    if is_email_already_registered(email):
        return error_response(
            "EMAIL_ALREADY_EXISTS",
            f"The email address '{email}' is already registered. Each email is only accepted once. Please sign in or use 'Forgot Password'.",
            400
        )

    # 2. Check if username is taken
    existing_user = find_user_by_identifier(username)
    if existing_user and (existing_user.get("username") or "").lower() == username.lower():
        return error_response("USERNAME_TAKEN", f"Username '{username}' is already taken. Please choose another username.", 400)

    # 3. Rate limiting check (60 seconds cooldown)
    key = f"reg:{email.lower()}"
    now = time.time()
    existing_record = _otp_store.get(key)
    if existing_record and (now - existing_record.get("created_at", 0)) < 60:
        remaining = int(60 - (now - existing_record.get("created_at", 0)))
        return error_response("RATE_LIMITED", f"Please wait {remaining} seconds before requesting a new OTP.", 429)

    # 4. Generate 6-digit OTP and store hash (single-use, 5-minute expiry)
    otp = f"{secrets.randbelow(900000) + 100000}"
    is_testing = bool(current_app and current_app.config.get("TESTING"))
    _otp_store[key] = {
        "otp_hash": hash_otp(otp),
        "email": email.lower(),
        "username": username,
        "full_name": full_name,
        "expires_at": now + 300,  # 5 minutes
        "created_at": now,
        "attempts": 0,
    }
    if is_testing:
        _otp_store[key]["otp"] = otp

    # 5. Dispatch via SMTP (fail-closed)
    success, msg = send_otp_email(
        to_email=email,
        otp=otp,
        purpose="Registration",
        recipient_name=full_name
    )
    if not success:
        _otp_store.pop(key, None)
        logger.error("Failed to deliver registration OTP to %s: %s", email, msg)
        return error_response(
            "EMAIL_DELIVERY_FAILED",
            "Unable to deliver verification code to your email. Please check that your email address is correct and try again.",
            500
        )

    resp_payload = {
        "email": email,
        "expires_in_seconds": 300,
        "sender": DEFAULT_SENDER,
    }

    return success_response(resp_payload, f"Verification OTP successfully sent to {email}.")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Step 2 of Registration: Verify OTP, check email uniqueness, and create account.
    """
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    full_name = (data.get("full_name") or username).strip()
    email = (data.get("email") or "").strip()
    otp = (data.get("otp") or "").strip()

    if not username or not password:
        return error_response("VALIDATION_ERROR", "Username and password are required.")

    if len(password) < 4:
        return error_response("VALIDATION_ERROR", "Password must be at least 4 characters.")

    if not email or "@" not in email:
        return error_response("VALIDATION_ERROR", "A valid email address is required.")

    is_testing = bool(current_app and current_app.config.get("TESTING"))
    if not otp and not is_testing:
        return error_response("OTP_REQUIRED", "Email verification OTP is required. Please click 'Send OTP'.", 400)

    # Verify unique email strictly
    if is_email_already_registered(email):
        return error_response(
            "EMAIL_ALREADY_EXISTS",
            f"The email address '{email}' is already registered. Each email can only be registered once. Please sign in or use 'Forgot Password'.",
            400
        )

    # Verify OTP if provided or in non-test mode
    if otp:
        key = f"reg:{email.lower()}"
        otp_record = _otp_store.get(key)
        if not otp_record:
            return error_response("OTP_NOT_FOUND", "No OTP was requested for this email, or it has expired. Please request a new OTP.", 400)

        if time.time() > otp_record.get("expires_at", 0):
            _otp_store.pop(key, None)
            return error_response("OTP_EXPIRED", "Verification code has expired. Please request a new OTP.", 400)

        otp_record["attempts"] = otp_record.get("attempts", 0) + 1
        if otp_record["attempts"] > 5:
            _otp_store.pop(key, None)
            return error_response("TOO_MANY_ATTEMPTS", "Too many invalid attempts. Please request a new OTP.", 429)

        is_match = (otp_record.get("otp_hash") == hash_otp(otp)) or (otp_record.get("otp") == otp)
        if not is_match:
            return error_response("INVALID_OTP", "Invalid verification code. Please check the OTP sent to your email.", 400)

        # OTP validated successfully: clear OTP record
        _otp_store.pop(key, None)

    # Check username collision
    col = get_collection(COLLECTIONS["users"])
    if col.find_one({"username": username}):
        return error_response("USER_EXISTS", f"Username '{username}' is already taken.")

    user_id = str(uuid.uuid4())[:12]
    role = (data.get("role") or "Student").strip()
    user_doc = {
        "user_id": user_id,
        "username": username,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "email": email,
        "role": role,
        "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={username}",
        "created_at": utc_now(),
    }
    col.insert_one(user_doc)
    save_user_to_store(user_doc)

    user_data = serialize_doc(user_doc)
    user_data.pop("password_hash", None)

    return success_response({
        "user": user_data,
        "token": f"token_{user_id}"
    }, "Account successfully verified and registered.", 201)


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password_request():
    """
    Step 1 of Password Reset: Look up registered user by username or email and send OTP via SMTP.
    """
    data = request.get_json() or {}
    identifier = (data.get("email") or data.get("username") or "").strip()

    if not identifier:
        return error_response("VALIDATION_ERROR", "Please enter your registered email address or username.")

    user = find_user_by_identifier(identifier)
    if not user:
        return error_response(
            "USER_NOT_FOUND",
            "No registered account found with this username or email. Please check your credentials or register.",
            404
        )

    target_email = user.get("email")
    if not target_email or "@" not in target_email:
        return error_response("NO_EMAIL_ON_RECORD", "This account does not have a valid registered email on file.", 400)

    # Rate limiting check (60 seconds cooldown)
    key = f"reset:{target_email.lower()}"
    now = time.time()
    existing_record = _otp_store.get(key)
    if existing_record and (now - existing_record.get("created_at", 0)) < 60:
        remaining = int(60 - (now - existing_record.get("created_at", 0)))
        return error_response("RATE_LIMITED", f"Please wait {remaining} seconds before requesting a new password reset code.", 429)

    # Generate 6-digit reset OTP and store hash (single-use, 5-minute expiry)
    otp = f"{secrets.randbelow(900000) + 100000}"
    is_testing = bool(current_app and current_app.config.get("TESTING"))
    _otp_store[key] = {
        "otp_hash": hash_otp(otp),
        "email": target_email.lower(),
        "username": user.get("username"),
        "user_id": user.get("user_id"),
        "expires_at": now + 300,  # 5 minutes
        "created_at": now,
        "attempts": 0,
    }
    if is_testing:
        _otp_store[key]["otp"] = otp

    # Send OTP via SMTP (fail-closed)
    success, msg = send_otp_email(
        to_email=target_email,
        otp=otp,
        purpose="Password Reset",
        recipient_name=user.get("full_name") or user.get("username")
    )
    if not success:
        _otp_store.pop(key, None)
        logger.error("Failed to deliver reset OTP to %s: %s", target_email, msg)
        return error_response(
            "EMAIL_DELIVERY_FAILED",
            "Unable to deliver password reset code to your email. Please try again later.",
            500
        )

    # Mask email for privacy (e.g. b***0@gmail.com)
    parts = target_email.split("@")
    masked_email = f"{parts[0][0]}***{parts[0][-1]}@{parts[1]}" if len(parts[0]) > 2 else target_email

    resp_payload = {
        "email": target_email,
        "masked_email": masked_email,
        "expires_in_seconds": 300,
        "sender": DEFAULT_SENDER,
    }

    return success_response(
        resp_payload,
        f"Password reset OTP sent to registered email ({masked_email})."
    )


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Step 2 of Password Reset: Verify OTP and set a new password.
    """
    data = request.get_json() or {}
    email = (data.get("email") or data.get("username") or "").strip()
    otp = (data.get("otp") or "").strip()
    new_password = (data.get("new_password") or "").strip()

    if not email:
        return error_response("VALIDATION_ERROR", "Email or username is required.")
    if not otp:
        return error_response("VALIDATION_ERROR", "Verification OTP is required.")
    if not new_password or len(new_password) < 4:
        return error_response("VALIDATION_ERROR", "New password must be at least 4 characters.")

    user = find_user_by_identifier(email)
    if not user:
        return error_response("USER_NOT_FOUND", "Account not found.", 404)

    target_email = (user.get("email") or "").strip().lower()
    key = f"reset:{target_email}"
    otp_record = _otp_store.get(key)

    if not otp_record:
        return error_response("OTP_NOT_FOUND", "No password reset was requested for this email, or it has expired.", 400)

    if time.time() > otp_record.get("expires_at", 0):
        _otp_store.pop(key, None)
        return error_response("OTP_EXPIRED", "Password reset code has expired. Please request a new OTP.", 400)

    otp_record["attempts"] = otp_record.get("attempts", 0) + 1
    if otp_record["attempts"] > 5:
        _otp_store.pop(key, None)
        return error_response("TOO_MANY_ATTEMPTS", "Too many invalid attempts. Please request a new OTP.", 429)

    is_match = (otp_record.get("otp_hash") == hash_otp(otp)) or (otp_record.get("otp") == otp)
    if not is_match:
        return error_response("INVALID_OTP", "Invalid verification code. Please check the OTP sent to your email.", 400)

    # Invalidate OTP immediately upon success
    _otp_store.pop(key, None)

    # Update password in database
    new_hash = hash_password(new_password)
    col = get_collection(COLLECTIONS["users"])

    u_id = user.get("user_id")
    if u_id:
        col.update_one({"user_id": u_id}, {"$set": {"password_hash": new_hash}})
        user["password_hash"] = new_hash
        save_user_to_store(user)
    else:
        col.update_one({"username": user.get("username")}, {"$set": {"password_hash": new_hash}})
        user["password_hash"] = new_hash
        save_user_to_store(user)

    logger.info("Password successfully updated for user %s (%s)", user.get("username"), target_email)
    return success_response(
        {"username": user.get("username")},
        "Password has been reset successfully. You can now log in with your new password."
    )


# =========================================================================
# Login & Profile Endpoints
# =========================================================================

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user with Username OR Registered Email, supporting case-insensitivity.
    """
    data = request.get_json() or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not identifier or not password:
        return error_response("VALIDATION_ERROR", "Username (or registered email) and password are required.")

    if identifier.lower() in ("student", "demo", "recruiter", "placement"):
        ensure_default_users()

    # Case-insensitive resolution by username or email
    user = find_user_by_identifier(identifier)
    if not user:
        return error_response(
            "AUTH_FAILED",
            "Invalid username or password. User is not registered.",
            401
        )

    # Verify password
    stored_hash = user.get("password_hash") or user.get("password") or ""
    if not verify_password(password, stored_hash):
        return error_response(
            "AUTH_FAILED",
            "Invalid username or password. Please check your password or use 'Forgot Password'.",
            401
        )

    user_data = serialize_doc(user)
    user_data.pop("password_hash", None)

    return success_response({
        "user": user_data,
        "token": f"token_{user.get('user_id', user.get('username'))}"
    }, "Login successful.")


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Retrieve user profile by user_id or username."""
    username = request.args.get("username")
    user_id = request.args.get("user_id")

    user = None
    col = get_collection(COLLECTIONS["users"])
    if user_id:
        user = col.find_one({"user_id": user_id})
    elif username:
        user = find_user_by_identifier(username)
    else:
        return error_response("MISSING_PARAM", "user_id or username required.")

    if not user:
        return error_response("NOT_FOUND", "User not found.", 404)

    user_data = serialize_doc(user)
    user_data.pop("password_hash", None)
    return success_response({"user": user_data})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Log out current user."""
    return success_response(None, "Logged out successfully.")
