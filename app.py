"""Flask development server runner."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import app
from config.settings import DEBUG


def create_app():
    return app


if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
