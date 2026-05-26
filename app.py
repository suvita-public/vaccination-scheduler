from flask import Flask
from routes import register_routes
from waitress import serve

app = Flask(__name__)

register_routes(app)

if __name__ == '__main__':
    print("Starting Vaccination Scheduler with Waitress...")
    serve(app, host='0.0.0.0', port=5000)
