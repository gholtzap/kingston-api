from flask import Flask
from flask_cors import CORS
from flask import Blueprint
from .clients.portfolio_display import CustomJSONEncoder

def create_app():
    print("Creating Flask app instance...") 
    
    app = Flask(__name__)
    CORS(app) 
    app.json_encoder = CustomJSONEncoder

    print("Registering tickers_bp...")
    from .routes import tickers_bp
    app.register_blueprint(tickers_bp)

    print("Registering auth_bp...") 
    from .routes import auth_bp
    app.register_blueprint(auth_bp)
    
    print("Registering portfolio_bp...") 
    from .routes import portfolio_bp
    app.register_blueprint(portfolio_bp)

    return app

print("Calling create_app from __init__.py...")
app = create_app()
