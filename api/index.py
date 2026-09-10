"""Vercel Serverless Function entrypoint."""
import os
import sys

# Ensure root directory is in sys.path so all imports resolve
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Expose WSGI handler for Vercel
handler = app
