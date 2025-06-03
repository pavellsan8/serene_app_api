from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from flask_restful import Resource
from datetime import timedelta

from helpers.error_message import *
from models.users_model import *
from schemas.authentication_schema import *
from services.authentication_service import *

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

            if isinstance(otp_user, tuple):
                return otp_user

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

        reset_password = UserResetPasswordService.reset_password(data)

        if isinstance(reset_password, tuple):
            return reset_password
        
        return {
            "status": 200,
            "message": "Password reset successfully. Please log in with your new password."
        }, 200

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