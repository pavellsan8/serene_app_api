from flask_restful import Resource
# from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask import request
from datetime import timedelta
from schemas.user_schemas import *
from helpers.error_message import ErrorMessageUtils
from models.mtusers_model import MtUsersModel
from werkzeug.security import check_password_hash

# Contoh Resources
class LoginUserResource(Resource):
    def post(self):
        try:
            data = UserLoginSchema().load(request.get_json())
        except Exception as e:
            return ErrorMessageUtils.handle_error(LoginUserResource, e)
        
        userLogin = data["username"]
        passLogin = data["password"]

        # Find user data
        checkUser = MtUsersModel.get_username_first(userLogin)

        if checkUser is not None:
            passwordRegistered = checkUser.password_hash
            passwordLoginCheck = check_password_hash(passwordRegistered, passLogin)

            if not passwordLoginCheck:
                return ErrorMessageUtils.bad_request("Authentication failed. Ensure the correct password.")
            
            else:
                # create access token and refresh token
                # expiresAcessToken = timedelta(days=1)
                # expiresRefreshToken = timedelta(days=90)

                # access_token = create_access_token(
                #     identity={
                #         "username": checkUser.username,
                #         "email": checkUser.email,
                #     },
                #     expires_delta=expiresAcessToken,
                # )
                
                # refresh_token = create_refresh_token(
                #     identity={
                #         "username": checkUser.username,
                #         "email": checkUser.email,
                #     },
                #     expires_delta=expiresRefreshToken,
                # )
                        
                try:              
                    ipAdress = request.remote_addr  
                    MtUsersModel.update_login_time(userLogin, ipAdress)
                    return {
                        "status" : 200,
                        "message" : "Successfully login",
                        "data" : {
                            "username" : userLogin,
                            "email" : checkUser.email,
                            # "access_token" : access_token,
                            # "refresh_token" : refresh_token,
                        }
                    }
                except Exception as e:
                    return ErrorMessageUtils.bad_request("Login failed. Please try again.")
                
        else:
            return ErrorMessageUtils.not_found("Username not found or not registered.")