"""User authentication routes (Register, Login, Me, Logout)."""
import hashlib
import logging
import uuid
from typing import Optional
from flask import Blueprint, request

from routes.responses import error_response, success_response
from database.models import utc_now, serialize_doc
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

users_col = get_collection(COLLECTIONS["users"])


BULK_ALLOWED_ROLES = {
    "recruiter", "placement cell", "placement", "admin", "recruiter/placement cell",
    "student", "learner", "candidate", "all", "user"
}


def get_request_user(req) -> Optional[dict]:
    """Resolve current user from headers, tokens, query params, cookies or body."""
    auth_header = req.headers.get("Authorization", "")
    user_id = None
    if auth_header.startswith("Bearer token_"):
        user_id = auth_header.replace("Bearer token_", "").strip()

    user_id = user_id or req.headers.get("X-User-Id") or req.args.get("user_id") or req.cookies.get("user_id")
    username = req.headers.get("X-Username") or req.args.get("username") or req.cookies.get("username")

    col = get_collection(COLLECTIONS["users"])
    if user_id:
        u = col.find_one({"user_id": user_id})
        if u:
            return u
    if username:
        u = col.find_one({"username": username})
        if u:
            return u

    # Check X-User-Role direct header, cookie, or query
    header_role = req.headers.get("X-User-Role") or req.args.get("role") or req.cookies.get("role") or req.cookies.get("user_role")
    if header_role:
        return {"role": header_role, "username": username or "custom_user"}

    return None


def is_bulk_authorized(req) -> bool:
    """Check if the requesting user has authorization for Bulk screening (accessible to all roles)."""
    return True


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "ai_resume_analyzer_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


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
                col.insert_one({
                    "user_id": f"usr_{uname}",
                    "username": uname,
                    "password_hash": hash_password(pwd),
                    "full_name": name,
                    "email": em,
                    "role": role,
                    "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={uname}",
                    "created_at": utc_now(),
                })
    except Exception as exc:
        logger.warning("Could not pre-seed default users: %s", exc)


# Seed on module load
ensure_default_users()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    full_name = (data.get("full_name") or username).strip()
    email = (data.get("email") or f"{username}@example.com").strip()

    if not username or not password:
        return error_response("VALIDATION_ERROR", "Username and password are required.")

    if len(password) < 4:
        return error_response("VALIDATION_ERROR", "Password must be at least 4 characters.")

    # Check if username exists
    existing = users_col.find_one({"username": username})
    if existing:
        return error_response("USER_EXISTS", f"Username '{username}' already taken.")

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
    users_col.insert_one(user_doc)

    user_data = serialize_doc(user_doc)
    user_data.pop("password_hash", None)

    return success_response({
        "user": user_data,
        "token": f"token_{user_id}"
    }, "Registration successful.", 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user with username and password."""
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return error_response("VALIDATION_ERROR", "Username and password are required.")

    if username in ("student", "demo", "recruiter", "placement"):
        ensure_default_users()

    user = users_col.find_one({"username": username})
    if not user:
        return error_response("AUTH_FAILED", "Invalid username or password. User is not registered.", 401)

    # Verify password hash
    if user.get("password_hash") != hash_password(password):
        return error_response("AUTH_FAILED", "Invalid username or password.", 401)

    user_data = serialize_doc(user)
    user_data.pop("password_hash", None)

    return success_response({
        "user": user_data,
        "token": f"token_{user.get('user_id', username)}"
    }, "Login successful.")


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Retrieve user profile."""
    username = request.args.get("username")
    user_id = request.args.get("user_id")

    query = {}
    if user_id:
        query["user_id"] = user_id
    elif username:
        query["username"] = username
    else:
        return error_response("MISSING_PARAM", "user_id or username required.")

    user = users_col.find_one(query)
    if not user:
        return error_response("NOT_FOUND", "User not found.", 404)

    user_data = serialize_doc(user)
    user_data.pop("password_hash", None)
    return success_response(user_data)
