import random

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from flask_mail import Message
from store.mail import Mail
from datetime import datetime, timedelta

from helpers.error_message import *
from models.mtusers_model import *
from schemas.authentication_schema import *
from werkzeug.security import check_password_hash

class UserRegisterResource(Resource):
    def post(self):
        try:
            data = UserRegisterSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        nameRegis = data['name']
        emailRegis = data['email']
        passwordRegis = data['password']
        dateRegis = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        passwordHash = MtUsersModel.hash_password(passwordRegis)
        passwordDb_clean = passwordHash.replace("scrypt:32768:8:1$", "", 1)

        print(nameRegis, emailRegis, passwordRegis, passwordDb_clean, dateRegis)

        # save to database
        # checkEmail = MtUsersModel.getEmailFirst(emailRegis)
        # if checkEmail is None:
        #     userRegisData = MtUsersModel(
        #         userName = nameRegis, 
        #         userEmail = emailRegis, 
        #         userPassword = passwordDb_clean,
        #         userCreatedAt = dateRegis,
        #     )

            # try:
            #     MtUsersModel.saveToDb(userRegisData)
        return {
            "status": 200,
            "message": "Successfully registered",
        }, 200
            # except:
            #     return ErrorMessageUtils.bad_request("Failed to register")
        
        # else:
        #     return ErrorMessageUtils.bad_request("Email already registered. Please use another email.")

class UserLoginResource(Resource):
    def post(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except Exception as e:
            return ErrorMessageUtils.bad_request
        
        emailLogin = data["email"]
        passwordInput = data["password"]
        passwordDb = MtUsersModel.hash_password(passwordInput)
        passwordDb_clean = passwordDb.replace("scrypt:32768:8:1$", "", 1)

        print(emailLogin, passwordInput, passwordDb_clean)

        # find user data in database
        # checkUser = MtUsersModel.getEmailFirst(emailLogin)

        # if checkUser is not None:
        #     passwordRegistered = checkUser.userPassword
        #     passwordLoginCheck = check_password_hash(passwordRegistered, passwordLogin)

        #     if not passwordLoginCheck:
        #         return ErrorMessageUtils.bad_request("Authentication failed. Ensure the correct password.")
        #     else:
        #         create access token and refresh token
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
                
        #     try:
        #         userId = checkUser.userId
        #         userEmail = checkUser.userEmail
        #         MtUsersModel.updateLoginTime(userId, userEmail)
        return {
            "status": 200,
            "message": "Successfully login",
            "data": {
                "email": emailLogin,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        }, 200
        #     except Exception as e:
        #         return ErrorMessageUtils.bad_request("Login failed. Please try again.")
                
        # else:
        #     return ErrorMessageUtils.not_found("Username not found or not registered.")

class UserLogoutResource(Resource):
    @jwt_required()
    def post(self):
        return {
            "status": 200, 
            "message": "Successfully logged out",
        }, 200

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
            return ErrorMessageUtils.bad_request("Failed to send email OTP verification")
        
    def post(self):
        try:
            data = GetEmailOtpSchema().load(request.get_json())
            email = data["email"]

            # untuk search email di database
            # emailData = MtUsersModel.getEmailFirst(email)
            # if not emailData:
            #     return ErrorMessageUtils.not_found("The provided email address was not found.")

            otp_code = self.generateOtp()
            self.sendEmailOtp(email, otp_code)

            return {
                "status": 200,
                "message": "Email OTP verification has been sent. Please check your email.",
                "otp_code": otp_code
            }, 200

        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Please provide a valid email address.")
        
class ResetPasswordResource(Resource):
    def post(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request

        userEmail = data['email']
        newPassword = data['password']
        passwordDb = MtUsersModel.hash_password(newPassword)
        passwordDb_clean = passwordDb.replace("scrypt:32768:8:1$", "", 1)

        print(userEmail, passwordDb_clean)

        try:
            # MtUsersModel.updateUserPassword(userEmail, passwordDb)
            return {
                'status': 200,
                'message': 'Successfully reset password.'
            }, 200
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Failed to reset password.")

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