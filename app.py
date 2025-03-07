from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os

from store.db import db
from store.ma import ma
from store.mail import mail
from store.url_api import initialize_routes
from helpers.error_message import *

# Config file
app = Flask(__name__, instance_relative_config=True)

# Try to load from instance config, but fall back to environment variables
# This helps with serverless environments like Vercel
try:
    app.config.from_pyfile('config.py')
except:
    # Load config from environment variables directly
    app.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    
    # Flask-Mail Configuration
    app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
    app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
    app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

# Settings file
api = Api(app)
db.init_app(app)
ma.init_app(app)
mail.init_app(app)
jwt = JWTManager(app)

# Initialize routes
initialize_routes(api)

# @jwt.unauthorized_loader
# def unauthorized(msg):
#     return ErrorMessageUtils.unauthorized_request(message=msg)


# @jwt.expired_token_loader
# def expireToken(self, callback):
#     return ErrorMessageUtils.unauthorized_request(message="Token has Expired")

# For Vercel serverless deployment
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Set debug to False for production
app.debug = False

# This is for local development
if __name__ == '__main__':    
    app.run(port=5001, debug=True)