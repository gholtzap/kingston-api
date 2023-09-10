from flask import Flask
from flask_cors import CORS

def create_app():
    print("Creating Flask app instance...")  # New print statement
    
    app = Flask(__name__)
    CORS(app) 

    print("Registering tickers_bp...")  # New print statement
    from .routes import tickers_bp
    app.register_blueprint(tickers_bp)

    print("Registering auth_bp...")  # New print statement
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    return app

print("Calling create_app from __init__.py...")  # New print statement
app = create_app()
