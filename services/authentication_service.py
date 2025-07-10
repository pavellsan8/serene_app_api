import random

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_mail import Message
from datetime import timedelta
from werkzeug.security import check_password_hash

from helpers.function_utils import DbUtils
from helpers.error_message import ErrorMessageUtils
from models.users_model import UsersModel
from store.mail import Mail

class UserRegisterService:
    def register_user(user_data):
        nameRegis = user_data['name']
        emailRegis = user_data['email']
        passwordRegis = user_data['password']
        passwordHash = UsersModel.hash_password(passwordRegis)
        
        with current_app.app_context():
            checkEmail = UsersModel.getEmailFirst(emailRegis)
            if checkEmail is None:
                userRegisData = UsersModel(
                    user_name=nameRegis, 
                    user_email=emailRegis, 
                    user_password=passwordHash,
                )

                try:
                    # DbUtils.save_to_db(userRegisData)

                    otp_service = SendEmailOtpVerificationService()
                    otp_code = otp_service.generate_otp()
                    otp_service.send_registration_email_otp(emailRegis, otp_code)

                    return {
                        "user": userRegisData,
                        "otp_code": otp_code
                    }
                
                except Exception as e:
                    print("Error:", str(e))
                    return ErrorMessageUtils.bad_request("User registration failed. Please try again.")
            
            else:
                return ErrorMessageUtils.bad_request("The provided email is already in use. Please choose another email.")
            
class UserLoginService:
    def login_user(user_data):
        emailLogin = user_data['email']
        passwordInput = user_data['password']

        checkUser = UsersModel.getEmailFirst(emailLogin)

        if checkUser is not None:
            userId = checkUser.user_id 
            passwordRegistered = checkUser.user_password
            passwordLoginCheck = check_password_hash(passwordRegistered, passwordInput)
            submitQuestionnaire = checkUser.submit_questionnaire

            if passwordLoginCheck:
                # create access token and refresh token
                try:
                    expiresAccessToken = timedelta(days=1)
                    expiresRefreshToken = timedelta(days=90)

                    # Add userId to the token's claims
                    additional_claims = {"user_id": userId}

                    access_token = create_access_token(
                        identity=emailLogin,
                        additional_claims=additional_claims,
                        expires_delta=expiresAccessToken,
                    )

                    refresh_token = create_refresh_token(
                        identity=emailLogin,
                        additional_claims=additional_claims,
                        expires_delta=expiresRefreshToken,
                    )

                    return {
                        "email": emailLogin,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "submit_questionnaire": submitQuestionnaire,
                    }
                
                except Exception as e:
                    print("Error:", str(e))
                    return ErrorMessageUtils.bad_request("Login failed... please try again.")
            else:
                return ErrorMessageUtils.bad_request("Invalid credentials. Please check your email and password and try again.")
        
        else:
            return ErrorMessageUtils.not_found("The email you entered is not registered. Please sign up to create an account.")
        
class SendEmailOtpVerificationService:
    def __init__(self):
        self.mail = Mail()

    @staticmethod
    def generate_otp():
        return random.randint(100000, 999999)
    
    def send_forget_password_email_otp(self, email, otp_code):
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
                            <p>If you didn't request this, please ignore this email.</p>
                        <br>
                            <p>Best regards,<br><strong>Serene Team</strong></p>
                    </body>
                </html>
            """
            message = Message(subject, recipients=recipients, html=html_body)
            self.mail.send(message)
        except Exception as e:
            print(f"Email error: {str(e)}")
            raise Exception("Failed to send email")
        
    def send_registration_email_otp(self, email, otp_code):
        try:
            subject = "Account Registration OTP Verification"
            recipients = [email]
            html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center;">
                        <h2 style="color: #2c3e50;">Account Registration OTP Verification</h2>
                            <p>Thank you for registering. To complete your registration, please use the OTP code below:</p>
                        <h1 style="color: #0057FF;">{otp_code}</h1>
                            <p>Enter this code in the app to verify your email address.</p>
                            <p>If you did not request to register, please ignore this email.</p>
                        <br>
                            <p>Best regards,<br><strong>Serene Team</strong></p>
                    </body>
                </html>
            """
            message = Message(subject, recipients=recipients, html=html_body)
            self.mail.send(message)
        except Exception as e:
            print(f"Email error: {str(e)}")
            raise Exception("Failed to send registration email")
        
    def send_otp(self, data):
        email = data["email"]
        userData = UsersModel.getEmailFirst(email)
        if userData is None:
            return ErrorMessageUtils.not_found("This email is not registered. Please check and try again.")

        otp_code = self.generate_otp()
        self.send_email_otp(email, otp_code)
        return {
            "otp_code": otp_code,
        }
    
class UserResetPasswordService:
    def reset_password(data):
        email = data['email']
        newPassword = data['password']

        if not newPassword:
            return ErrorMessageUtils.bad_request("New password cannot be empty. Please provide a valid password.")
        
        userData = UsersModel.getEmailFirst(email)
        oldPassword = userData.user_password if userData else None
        passwordResetCheck = check_password_hash(oldPassword, newPassword)

        try:
            if passwordResetCheck:
                return ErrorMessageUtils.bad_request("The new password cannot be the same as the old password. Please choose a different password.")
            
            UsersModel.updateUserPassword(email, newPassword)
            return
        
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("Unable to reset password. Please try again later.")