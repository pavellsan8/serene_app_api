from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

from models.users_model import UsersModel
from schemas.user_profile_schema import *
from services.user_profile_service import UserProfileService
from helpers.error_message import ErrorMessageUtils

class UserProfileDataResource(Resource):
    @jwt_required()
    def get(self):
        try:
            userEmail = request.args.get('email')
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        data = UserProfileService.get_user_profile(userEmail)
        if isinstance(data, tuple):
            return data
        
        return {
            "status": 200,
            "message": "User data retrieved successfully.",
            "data": data,
        }, 200

    @jwt_required()
    def put(self):
        try:
            data = UserUpdateProfileSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        updateData = UserProfileService.update_user_profile(data)
        if isinstance(updateData, tuple):
            return updateData
        
        return {
            "status": 200,
            "message": "User profile updated successfully.",
            "data": updateData,
        }, 200