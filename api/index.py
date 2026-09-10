"""Vercel Serverless Function entrypoint with exception capturing."""
import os
import sys
import traceback

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

_app_instance = None
_startup_error = None

try:
    from app import app as flask_app
    _app_instance = flask_app
except Exception as exc:
    _startup_error = traceback.format_exc()


def app(environ, start_response):
    """WSGI entrypoint that captures and displays any startup or runtime errors."""
    global _app_instance, _startup_error

    if _startup_error:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        html = f"""<!DOCTYPE html>
<html>
<head><title>Startup Error - AI Resume Analyzer</title></head>
<body style="font-family: monospace; padding: 2rem; background: #0f172a; color: #f87171;">
  <h2>Application Startup Error</h2>
  <pre style="background: #1e293b; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #fca5a5;">{_startup_error}</pre>
</body>
</html>"""
        return [html.encode('utf-8')]

    try:
        return _app_instance(environ, start_response)
    except Exception as exc:
        runtime_err = traceback.format_exc()
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        html = f"""<!DOCTYPE html>
<html>
<head><title>Runtime Error - AI Resume Analyzer</title></head>
<body style="font-family: monospace; padding: 2rem; background: #0f172a; color: #f87171;">
  <h2>Application Runtime Error</h2>
  <pre style="background: #1e293b; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #fca5a5;">{runtime_err}</pre>
</body>
</html>"""
        return [html.encode('utf-8')]


# Aliases for Vercel WSGI
handler = app
application = app
