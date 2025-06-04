import datetime
import requests
import re

from flask_restful import Resource
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt

from models.music_model import MusicModel
from models.musicfavourite_model import MusicFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils
from schemas.user_profile_schema import UserFavouriteSchema
from services.music_service import *

class GetMusicListResource(Resource):
    @jwt_required()
    def get(self):
        data = GetMusicListService.get_music_list()
        if isinstance(data, tuple):
            return data
            
        return {
            'status': 200,
            'message': 'Music found successfully',
            'data': data,
        }, 200
        
class GetMusicListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetMusicListService.get_music_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Music found successfully',
            'data': data,
        }, 200

class MusicFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        savedMusic = MusicFavouriteService.add_music_to_favourite(data)
        if isinstance(savedMusic, tuple):
            return savedMusic

        return {
            'status': 200,
            'message': 'Music added to favourites successfully',
            'email': savedMusic['email'],
            'music_id': savedMusic['music_id'],
        }, 200
    
    @jwt_required()
    def delete(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        removeMusic = MusicFavouriteService.delete_music_from_favourite(data)
        if isinstance(removeMusic, tuple):
            return removeMusic
    
        return {
            'status': 200,
            'message': 'Music removed from favourites successfully',
            'email': removeMusic['email'],
            'music_id': removeMusic['music_id']
        }, 200

class GetMusicFavouriteListResource(Resource):
    @jwt_required()
    def get(self):
        data = GetMusicFavouriteListService.get_music_favourite_list()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Music found successfully',
            'data': data,
        }, 200
        
class GetMusicFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetMusicFavouriteListService.get_music_favourite_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Favourite music found successfully',
            'data': data,
        }, 200