"""User authentication routes (Register, Login, Me, Logout)."""
import hashlib
import logging
import uuid
from flask import Blueprint, request

from routes.responses import error_response, success_response
from database.models import utc_now, serialize_doc
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

users_col = get_collection(COLLECTIONS["users"])


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "ai_resume_analyzer_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


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
    user_doc = {
        "user_id": user_id,
        "username": username,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "email": email,
        "role": "Learner",
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

    user = users_col.find_one({"username": username})
    if not user:
        # Auto-create guest user for seamless student evaluation if doesn't exist
        user_id = str(uuid.uuid4())[:12]
        user = {
            "user_id": user_id,
            "username": username,
            "password_hash": hash_password(password),
            "full_name": username.title(),
            "email": f"{username}@student.edu",
            "role": "Candidate / Student",
            "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={username}",
            "created_at": utc_now(),
        }
        users_col.insert_one(user)
    else:
        # Verify password
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
