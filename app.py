"""AI Resume Analyzer - Flask Application Entry Point."""
import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from config.settings import CORS_ORIGINS, DEBUG, SECRET_KEY
from api.resume_routes import resume_bp
from api.job_routes import job_bp
from api.analysis_routes import analysis_bp
from database.mongodb import check_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory."""
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

    CORS(app, origins=CORS_ORIGINS)

    # API blueprints
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(job_bp, url_prefix="/api/job")
    app.register_blueprint(analysis_bp, url_prefix="/api")

    # Frontend routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/analyze")
    def analyze_page():
        return render_template("analyze.html")

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

    @app.route("/history")
    def history_page():
        return render_template("history.html")

    @app.route("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.route("/how-it-works")
    def how_it_works():
        return render_template("how-it-works.html")

    # Health check
    @app.route("/api/health")
    def health():
        db_ok = check_connection()
        return {
            "success": True,
            "data": {
                "status": "healthy" if db_ok else "degraded",
                "database": "connected" if db_ok else "disconnected",
                "sbert_model": "sentence-transformers/all-MiniLM-L6-v2",
            },
            "message": "Service is running.",
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
