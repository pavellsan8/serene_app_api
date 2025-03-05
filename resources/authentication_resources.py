import random

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from flask_mail import Message
from store.mail import Mail
from datetime import datetime, timedelta

from helpers.error_message import *
from models.mtusers_model import *
from schemas.authentication_schema import *
from werkzeug.security import check_password_hash

class userRegisterResource(Resource):
    def hash_password(self, password):
        self.hashed_password = generate_password_hash(password)
        return self.hashed_password
    
    def post(self):
        try:
            data = userRegisterSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        nameRegis = data['name']
        emailRegis = data['email']
        passwordRegis = data['password']
        dateRegis = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # save to database
        # checkEmail = MtUsersModel.getEmailFirst(emailRegis)
        # if checkEmail is None:
        #     userRegisData = MtUsersModel(
        #         userName = nameRegis, 
        #         userEmail = emailRegis, 
        #         userPassword = passwordRegis,
        #         userCreatedAt = dateRegis,
        #     )

        try:
            # MtUsersModel.saveToDb(userRegisData)
            return {
                "status": 200,
                "message": "Successfully registered",
            }
        except:
            return ErrorMessageUtils.bad_request("Failed to register")
        
        # else:
        #     return ErrorMessageUtils.bad_request("Email already registered. Please use another email.")

class LoginUserResource(Resource):
    def post(self):
        try:
            data = userLoginSchema().load(request.get_json())
        except Exception as e:
            return ErrorMessageUtils.handle_error(LoginUserResource, e)
        
        emailLogin = data["email"]
        passwordLogin = data["password"]

        # Find user data
        checkUser = MtUsersModel.getEmailFirst(emailLogin)

        if checkUser is not None:
            passwordRegistered = checkUser.userPassword
            passwordLoginCheck = check_password_hash(passwordRegistered, passwordLogin)

            if not passwordLoginCheck:
                return ErrorMessageUtils.bad_request("Authentication failed. Ensure the correct password.")
            
            else:
                # create access token and refresh token
                expiresAcessToken = timedelta(days=1)
                expiresRefreshToken = timedelta(days=90)

                access_token = create_access_token(
                    identity={
                        "username": checkUser.username,
                        "email": checkUser.email,
                    },
                    expires_delta=expiresAcessToken,
                )
                
                refresh_token = create_refresh_token(
                    identity={
                        "username": checkUser.username,
                        "email": checkUser.email,
                    },
                    expires_delta=expiresRefreshToken,
                )
                        
                try:
                    userId = checkUser.userId
                    userEmail = checkUser.userEmail
                    MtUsersModel.updateLoginTime(userId, userEmail)
                    return {
                        "status" : 200,
                        "message" : "Successfully login",
                        "data" : {
                            "email" : userEmail,
                            "access_token" : access_token,
                            "refresh_token" : refresh_token,
                        }
                    }
                except Exception as e:
                    return ErrorMessageUtils.bad_request("Login failed. Please try again.")
                
        else:
            return ErrorMessageUtils.not_found("Username not found or not registered.")

class sendEmailOtpVerificationResource(Resource):
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
                            <p>Best regards,<br><strong>Your App Team</strong></p>
                    </body>
                </html>
            """
            message = Message(subject, recipients=recipients, html=html_body)
            self.mail.send(message)
        except:
            return ErrorMessageUtils.bad_request("Failed to send email OTP verification")
        
    def post(self):
        try:
            data = getEmailOtpSchema().load(request.get_json())
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
                "email": email,
                "otp_code": otp_code
            }

        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Please provide a valid email address.")