from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from store.db import db
from store.ma import ma
from store.mail import mail
from store.url_api import initialize_routes
from helpers.error_message import *

# Config file
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

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

if __name__ == '__main__':    
    app.run(port=5001, debug=True)