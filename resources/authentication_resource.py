import random

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from flask_mail import Message
from store.mail import Mail
from datetime import timedelta
from werkzeug.security import check_password_hash

from helpers.error_message import *
from helpers.function_utils import DbUtils
from models.mtusers_model import *
from schemas.authentication_schema import *

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = UserRegisterSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        nameRegis = data['name']
        emailRegis = data['email']
        passwordRegis = data['password']
        passwordHash = MtUsersModel.hash_password(passwordRegis)

        print(nameRegis, emailRegis, passwordRegis, passwordHash)

        # save to database
        # checkEmail = MtUsersModel.getEmailFirst(emailRegis)
        # if checkEmail is None:
        #     userRegisData = MtUsersModel(
        #         userName = nameRegis, 
        #         userEmail = emailRegis, 
        #         userPassword = passwordHash,
        #     )

        try:
            # DbUtils.save_to_db(userRegisData)
            return {
                "status": 200,
                "message": "User registration completed successfully."
            }, 200
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("User registration failed. Please try again.")
        
        # else:
        #     return ErrorMessageUtils.bad_request("The provided email is already in use. Please choose another email.")

class UserLoginResource(Resource):
    def post(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        emailLogin = data["email"]
        passwordInput = data["password"]
        passwordInputCheck = MtUsersModel.hash_password(passwordInput)

        print(emailLogin, passwordInput, passwordInputCheck)

        # find user data in database
        # checkUser = MtUsersModel.getEmailFirst(emailLogin)

        # if checkUser is not None:
        #     passwordRegistered = checkUser.userPassword
        #     passwordLoginCheck = check_password_hash(passwordRegistered, passwordInputCheck)

        #     if passwordLoginCheck:
        #         create access token and refresh token
        try:
            expiresAccessToken = timedelta(days=1)
            expiresRefreshToken = timedelta(days=90)

            access_token = create_access_token(
                identity=emailLogin,
                expires_delta=expiresAccessToken,
            )

            refresh_token = create_refresh_token(
                identity=emailLogin,
                expires_delta=expiresRefreshToken,
            )

            # userId = checkUser.userId
            # userEmail = checkUser.userEmail
            # MtUsersModel.updateLoginTime(userId, userEmail)
            return {
                "status": 200,
                "message": "Login successful. Welcome back!",
                "data": {
                    "email": emailLogin,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }, 200
        
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("Login failed... please try again.")
            
        #     else:
        #         return ErrorMessageUtils.bad_request("Invalid credentials. Please check your email and password and try again.")
                
        # else:
        #     return ErrorMessageUtils.not_found("The email you entered is not registered. Please sign up to create an account.")

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
    def __init__(self):
        self.mail = Mail()

    def generateOtp(self):
        return random.randint(100000, 999999)
    
    def sendEmailOtp(self, email, otp_code):
        try:
            subject = "Reset Password OTP Verification"
            recipients = [email]
            html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center;">
                        <h2 style="color: #2c3e50;">Reset Password OTP Verification</h2>
                            <p>Your OTP code is:</p>
                        <h1 style="color: #e74c3c;">{otp_code}</h1>
                            <p>Please use this code to complete your verification.</p>
                            <p>If you didn’t request this, please ignore this email.</p>
                        <br>
                            <p>Best regards,<br><strong>Serene Team</strong></p>
                    </body>
                </html>
            """
            message = Message(subject, recipients=recipients, html=html_body)
            self.mail.send(message)
        except:
            return ErrorMessageUtils.bad_request("OTP verification email could not be sent. Ensure your email address is correct and try again.")
        
    def post(self):
        try:
            data = GetEmailDataSchema().load(request.get_json())
            email = data["email"]

            # untuk search email di database
            # emailData = MtUsersModel.getEmailFirst(email)
            # if not emailData:
            #     return ErrorMessageUtils.not_found("This email is not registered. Please check and try again.")

            otp_code = self.generateOtp()
            self.sendEmailOtp(email, otp_code)

            return {
                "status": 200,
                "message": "A verification OTP has been sent to your email. Please check your inbox.",
                "otp_code": otp_code
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
        passwordDb = MtUsersModel.hash_password(newPassword)

        print(userEmail, passwordDb)

        try:
            # MtUsersModel.updateUserPassword(userEmail, passwordDb)
            return {
                'status': 200,
                'message': 'Your password has been successfully reset.'
            }, 200
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Unable to reset password. Please try again later.")
        
class DeleteUserDataResource(Resource):
    @jwt_required()
    def delete(self):
        try:
            data = GetEmailDataSchema().load(request.get_json())
            email = data["email"]

            # if MtUsersModel.getEmailFirst(email):
            #     MtUsersModel.deleteUser(email)
            # else:
            #     return ErrorMessageUtils.not_found("This email is not registered. Please check and try again.")
            
            return {
                'status': 200,
                'message': 'User has been successfully deleted.',
            }, 200
        
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Invalid email address. Please check and try again.")

class RefreshTokenResource(Resource):
    @jwt_required(refresh=True) 
    def post(self):
        identity = get_jwt_identity()
        new_access_token = create_access_token(
            identity=identity, 
            expires_delta=timedelta(days=1)
        )
        return {
            "status": 200,
            "message": "Access token refreshed successfully",
            "data": {
                "access_token": new_access_token
            }
        }, 200