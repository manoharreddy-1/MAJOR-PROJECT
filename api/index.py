"""AI Resume Analyzer - Vercel Serverless Function & Flask Entry Point."""
import logging
import os
import sys

# Ensure root directory is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

load_dotenv()

from config.settings import CORS_ORIGINS, DEBUG, SECRET_KEY
from routes.resume_routes import resume_bp
from routes.job_routes import job_bp
from routes.analysis_routes import analysis_bp
from routes.course_routes import course_bp
from routes.auth_routes import auth_bp, get_request_user, BULK_ALLOWED_ROLES
from routes.bulk_routes import bulk_bp
from database.mongodb import check_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

template_dir = os.path.join(BASE_DIR, "frontend", "templates")
static_dir = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path="/static",
)

# Search paths for templates across serverless environments
search_paths = [
    template_dir,
    os.path.join(BASE_DIR, "api", "frontend", "templates"),
    os.path.join(os.getcwd(), "frontend", "templates"),
    os.path.join(os.getcwd(), "api", "frontend", "templates"),
]
existing_paths = [p for p in search_paths if os.path.exists(p)]
if existing_paths:
    from jinja2 import ChoiceLoader, FileSystemLoader
    app.jinja_loader = ChoiceLoader([FileSystemLoader(p) for p in existing_paths])

app.config["SECRET_KEY"] = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

CORS(app, origins=CORS_ORIGINS)

# API blueprints
app.register_blueprint(resume_bp, url_prefix="/api/resume")
app.register_blueprint(job_bp, url_prefix="/api/job")
app.register_blueprint(analysis_bp, url_prefix="/api")
app.register_blueprint(course_bp, url_prefix="/api/course")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(bulk_bp, url_prefix="/api/bulk")


# WSGI middleware to restore original request path on Vercel rewrites
class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        import urllib.parse
        query = environ.get("QUERY_STRING", "")
        if "path=" in query:
            params = urllib.parse.parse_qs(query)
            path_val = params.get("path", [""])[0].strip()
            if not path_val or path_val == "/":
                environ["PATH_INFO"] = "/"
            else:
                environ["PATH_INFO"] = "/" + path_val.lstrip("/")
            
            if "path" in params:
                del params["path"]
            environ["QUERY_STRING"] = urllib.parse.urlencode(params, doseq=True)
        elif environ.get("PATH_INFO") in ("/api/index", "/api", "/api/"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)


@app.route("/debug_env", methods=["GET", "POST"])
def debug_env():
    import flask
    return flask.jsonify({
        "environ": {k: str(v) for k, v in flask.request.environ.items() if isinstance(v, (str, int, float))},
        "headers": dict(flask.request.headers),
        "path": flask.request.path,
        "method": flask.request.method,
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    logger.exception("Unhandled server error: %s", e)
    return jsonify({"success": False, "error": {"code": "SERVER_ERROR", "message": str(e)}}), 500


# Frontend routes
@app.route("/")
@app.route("/api/index")
@app.route("/api")
@app.route("/api/")
@app.route("/login")
def login_page():
    """Default landing page - Authentication."""
    return render_template("login.html")


@app.route("/home")
@app.route("/dashboard")
def index():
    """Main overview and platform features dashboard."""
    return render_template("index.html")


@app.route("/resume-analysis")
def resume_analysis_mode_page():
    """Mode selector: Choose between Single Resume and Bulk Resumes."""
    return render_template("resume_analysis_mode.html")


@app.route("/resume-analysis/single")
@app.route("/analyze")
def analyze_page():
    """Single Resume Analysis (existing flow, unchanged)."""
    return render_template("analyze.html")


@app.route("/resume-analysis/bulk")
@app.route("/resume-analysis/bulk/results")
@app.route("/resume-analysis/bulk/history")
def bulk_analysis_page():
    """Bulk Screening Flow: Job setup -> Upload -> Live Progress -> Ranked results."""
    user = get_request_user(request)
    role = (user.get("role") if user else request.headers.get("X-User-Role") or request.args.get("role") or "").strip().lower()

    if role and role not in BULK_ALLOWED_ROLES:
        # Backend rejection: Student users cannot access bulk screening
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Access denied. Bulk analysis is available for Placement Cell and Recruiters only."
            }
        }), 403

    return render_template("bulk_analysis.html")


@app.route("/job")
def job_page():
    return render_template("job.html")


@app.route("/results")
def results_page():
    return render_template("results.html")


@app.route("/skills")
def skills_page():
    return render_template("skills.html")


@app.route("/improve")
def improve_page():
    return render_template("improve.html")


@app.route("/interview")
def interview_page():
    return render_template("interview.html")


@app.route("/roadmap")
def roadmap_page():
    return render_template("roadmap.html")


@app.route("/courses")
def courses_page():
    return render_template("courses.html")


@app.route("/course/<course_id>")
def course_view_page(course_id):
    return render_template("course_view.html", course_id=course_id)


@app.route("/history")
def history_page():
    return render_template("history.html")


@app.route("/profile")
def profile_page():
    return render_template("profile.html")


@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html")


# Health checks
@app.route("/api/ping")
def ping():
    return {"success": True, "message": "pong"}


@app.route("/api/health")
def health():
    db_ok = check_connection()
    return {
        "success": True,
        "data": {
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "sbert_model": "sentence-transformers/all-MiniLM-L6-v2 (or keyword fallback)",
        },
        "message": "Service is running.",
    }


# Export handler for Vercel
handler = app
