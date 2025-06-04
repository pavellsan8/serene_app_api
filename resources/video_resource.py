import datetime
import re

from flask_restful import Resource
from flask import request, current_app
from googleapiclient.discovery import build
from flask_jwt_extended import jwt_required, get_jwt

from models.video_model import VideoModel
from models.videofavourite_model import VideoFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils
from schemas.user_profile_schema import UserFavouriteSchema
from services.video_service import *

class GetVideoListResource(Resource):
    @jwt_required()
    def get(self):
        data = GetVideoListService.get_video_list()
        if isinstance(data, tuple):
            return data
            
        return {
            'status': 200,
            'message': 'Videos found successfully',
            'data': data,
        }

class GetVideoListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetVideoListService.get_video_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Video found successfully',
            'data': data,
        }, 200

class VideoFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        savedVideo = VideoFavouriteService.add_video_to_favourite(data)
        if isinstance(savedVideo, tuple):
            return savedVideo
            
        return {
            'status': 200,
            'message': 'Video added to favourites successfully',
            'email': savedVideo['email'],
            'video_id': savedVideo['video_id'],
        }, 200
    
    @jwt_required()
    def delete(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        removeVideo = VideoFavouriteService.delete_video_from_favourite(data)
        if isinstance(removeVideo, tuple):
            return removeVideo
                
        return {
            'status': 200,
            'message': 'Video removed from favourites successfully',
            'email': removeVideo['email'],
            'video_id': removeVideo['video_id'],
        }, 200
            
class GetVideoFavouriteListResource(Resource):
    @jwt_required()
    def get(self):
        data = GetVideoFavouriteListService.get_video_favourite_list()
        if isinstance(data, tuple):
            return data

        return {
            'status': 200,
            'message': 'Favourite videos found successfully',
            'data': data,
        }

class GetVideoFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetVideoFavouriteListService.get_video_favourite_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Favourite video found successfully',
            'data': data,
        }