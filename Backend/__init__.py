# This file makes the Backend directory a Python package
from .app import app, db

# Import routes to register them with the app
from . import routes
