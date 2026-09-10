"""API response helpers."""
from flask import jsonify
from typing import Any, Dict, Optional, Tuple


def success_response(data: Any = None, message: str = "Success", status: int = 200):
    return jsonify({"success": True, "data": data, "message": message}), status


def error_response(code: str, message: str, status: int = 400):
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status
