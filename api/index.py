"""Vercel Serverless Function entrypoint with live diagnostic fallback."""
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from app import app as main_app
    app = main_app
except Exception as exc:
    from flask import Flask
    err_text = traceback.format_exc()
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def show_error(path):
        return f"""<!DOCTYPE html>
<html>
<head><title>Startup Error Diagnostic</title></head>
<body style="font-family: monospace; padding: 2rem; background: #0f172a; color: #f87171;">
  <h2 style="color: #ef4444;">Application Startup Exception</h2>
  <p style="color: #94a3b8;">The following error occurred while importing app.py:</p>
  <pre style="background: #1e293b; padding: 1.5rem; border-radius: 8px; overflow-x: auto; color: #fca5a5; font-size: 14px; line-height: 1.5;">{err_text}</pre>
</body>
</html>""", 200
