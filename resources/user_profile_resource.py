from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

from models.users_model import UsersModel
from schemas.user_profile_schema import *
from helpers.error_message import ErrorMessageUtils

class UserProfileDataResource(Resource):
    @jwt_required()
    def get(self):
        try:
            userEmail = request.args.get('email')
        except:
            return ErrorMessageUtils.bad_request
        
        userData = UsersModel.getEmailFirst(userEmail)

        if not userData:
            return ErrorMessageUtils.not_found("User data not found.")
        
        userName = userData.user_name
        return {
            "status": 200,
            "message": "User data retrieved successfully.",
            "data": {
                "name": userName,
                "email": userEmail,
            }
        }, 200

    @jwt_required()
    def put(self):
        try:
            data = UserUpdateProfileSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        userName = data['name']
        userEmail = data['email']

        try:
            UsersModel.updateUserProfile(userName, userEmail)
            return {
                "status": 200,
                "message": "User profile updated successfully.",
                "data": {
                    "name": userName,
                    "email": userEmail,
                }
            }, 200
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request
        
    @jwt_required()
    def delete(self):
        try:
            data = UserDataSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request
        
        userEmail = data['email']
        userData = UsersModel.getEmailFirst(userEmail)

        if userData:
            UsersModel.deleteUser(userData)
            return {
                "status": 200,
                "message": "User data deleted successfully.",
            }, 200
        else:
            return ErrorMessageUtils.not_found