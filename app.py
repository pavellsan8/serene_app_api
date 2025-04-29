import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

from store.db import db
from store.ma import ma
from store.mail import mail
from store.url_api import initialize_routes
from helpers.error_message import *

# Config file
app = Flask(__name__, instance_relative_config=True)
try:
    app.config.from_pyfile('config.py')
except:
    app.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    
    app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
    app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
    app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

    app.config['GOOGLE_API_KEY'] = os.getenv("GOOGLE_BOOKS_API_KEY")
    app.config['JAMENDO_CLIENT_ID'] = os.getenv("JAMENDO_CLIENT_ID") 

    app.config['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Settings file
api = Api(app)
db.init_app(app)
ma.init_app(app)
mail.init_app(app)
jwt = JWTManager(app)

# Initialize routes
initialize_routes(api)

@app.errorhandler(NoAuthorizationError)
def handle_no_authorization_error(e):
    return ErrorMessageUtils.unauthorized_request("Missing access token. Please provide a valid token.")

@app.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return ErrorMessageUtils.unauthorized_request("Invalid token format. Please check the authorization header.")

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return ErrorMessageUtils.unauthorized_request("Token has expired. Please log in again.")

# For Vercel serverless deployment
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.debug = False

# Connection Testing
if __name__ == '__main__':    
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))  # Simple test query
            print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    app.run(port=5001, debug=True)