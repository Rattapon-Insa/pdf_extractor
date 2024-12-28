from flask import Flask
from flask_cors import CORS
from app.routes import routes


def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register your routes
    app.register_blueprint(routes)

    return app