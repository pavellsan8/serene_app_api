import random

from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from flask_restful import Resource
from flask_mail import Message
from datetime import timedelta
from werkzeug.security import check_password_hash

from helpers.error_message import *
from helpers.function_utils import DbUtils
from models.users_model import *
from schemas.authentication_schema import *
from services.authentication_service import *
from store.mail import Mail

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = UserRegisterSchema().load(request.get_json())
        except Exception as e:
            return ErrorMessageUtils.bad_request("Invalid input data. Please check your request and try again.")
        
        registered_user = UserRegisterService.register_user(data)

        if isinstance(registered_user, tuple):
            return registered_user

        return {
            "status": 200,
            "message": "Successfully registered your account."
        }, 200

class UserLoginResource(Resource):
    def post(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        logined_user = UserLoginService.login_user(data)

        if isinstance(logined_user, tuple):
            return logined_user
        
        return {
            "status": 200,
            "message": "Successfully logged in to your account.",
            "data": logined_user
        }, 200

class UserLogoutResource(Resource):
    @jwt_required()
    def post(self):
        try:
            return {
                "status": 200, 
                "message": "Log out successful.",
            }, 200
        except:
            return ErrorMessageUtils.unauthorized_request("Your session is invalid or has expired. Please log in again.")

class SendEmailOtpVerificationResource(Resource):
    def post(self):
        try:
            data = GetEmailDataSchema().load(request.get_json())

            service = SendEmailOtpVerificationService()
            otp_user = service.send_otp(data)
            return {
                "status": 200,
                "message": "OTP verification email has been sent successfully.",
                "otp_code": otp_user["otp_code"]
            }, 200

        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Please provide a valid email address.")
        
class ResetPasswordResource(Resource):
    def put(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request

        userEmail = data['email']
        newPassword = data['password']

        print(userEmail, newPassword)

        if newPassword == "" or newPassword is None:
            return ErrorMessageUtils.bad_request("New password cannot be empty. Please provide a valid password.")
        
        try:
            UsersModel.updateUserPassword(userEmail, newPassword)
            return {
                'status': 200,
                'message': 'Your password has been successfully reset.'
            }, 200
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Unable to reset password. Please try again later.")

class RefreshTokenResource(Resource):
    @jwt_required(refresh=True) 
    def post(self):
        identity = get_jwt_identity()
        claims = get_jwt()
        new_access_token = create_access_token(
            identity=identity, 
            additional_claims={"user_id": claims.get("user_id")},
            expires_delta=timedelta(days=1)
        )
        return {
            "status": 200,
            "message": "Access token refreshed successfully",
            "data": {
                "access_token": new_access_token
            }
        }, 200