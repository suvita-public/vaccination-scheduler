from flask import Flask
from routes.vaccination_routes import vaccination_bp

def register_routes(app: Flask):
    app.register_blueprint(vaccination_bp)
