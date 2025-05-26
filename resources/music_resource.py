import datetime
import requests
import re

from flask_restful import Resource
from flask import request, current_app
from googleapiclient.discovery import build
from flask_jwt_extended import jwt_required, get_jwt

from models.book_model import BookModel
from models.video_model import VideoModel
from models.music_model import MusicModel
from models.bookfavourite_model import BookFavouriteModel
from models.videofavourite_model import VideoFavouriteModel
from models.musicfavourite_model import MusicFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils
from schemas.user_profile_schema import UserFavouriteSchema
from schemas.chatbot_schema import UserInputChatbotSchema
from store.openai import get_openai_client

class GetMusicListResource(Resource):
    @jwt_required()
    def get(self):
        search = request.args.get('search')
        client_id = current_app.config.get('JAMENDO_CLIENT_ID')

        if not search or not client_id:
            return ErrorMessageUtils.bad_request()
        
        url = f'https://api.jamendo.com/v3.0/tracks?client_id={client_id}&format=json&search={search}'

        try:
            response = requests.get(url)
            data = response.json()  

            if data.get('headers', {}).get('code', None) != 0:
                return ErrorMessageUtils.internal_error()
            
            musics = []
            results = data.get('results', [])

            for music in results:
                duration = music.get('duration')
                musics.append({
                    'id': music.get('id'),
                    'title': music.get('name'),
                    'audio': music.get('audio'),
                    'artist': music.get('artist_name'),
                    'album': music.get('album_name'),
                    'thumbnail': music.get('image'),
                    'duration': format_duration(duration),
                })
            
            return {
                'status': 200,
                'message': 'Music found successfully',
                'data': musics,
            }, 200
    
        except Exception as e:
            print("Error fetchin data:", str(e))
            return ErrorMessageUtils.internal_error()
        
class GetMusicListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            musicData = MusicModel.getMusicByFeelingId(userId)
            return {
                'status': 200,
                'message': 'Music found successfully',
                'data': musicData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching music data')

class MusicFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        musicId = data['item_id']

        favouriteData = MusicFavouriteModel.getMusicFirstFavourite(userId, musicId)
        if favouriteData:
            return ErrorMessageUtils.bad_request('Music already in favourites')

        try :
            favouriteData = MusicFavouriteModel(
                user_id=userId,
                music_id=musicId,
                saved_at=datetime.datetime.now(datetime.timezone.utc),
            )

            # Simulate saving to database
            DbUtils.save_to_db(favouriteData)
            print(f"Saving music ID {musicId} for user {userEmail}")
            
            return {
                'status': 200,
                'message': 'Music added to favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'music_id': musicId
            }, 200
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while adding to favorites')
    
    @jwt_required()
    def delete(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        musicId = data['item_id']

        try :
            # Simulate saving to database
            favouriteData = MusicFavouriteModel.getMusicFirstFavourite(userId, musicId)
    
            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
                print(f"Deleting music ID {musicId} for user {userEmail}")
            else:
                return ErrorMessageUtils.bad_request('Music not found in favourites')   
    
            return {
                'status': 200,
                'message': 'Music removed from favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'music_id': musicId
            }, 200
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')

class GetMusicFavouriteListResource(Resource):
    @jwt_required()
    def get(self):
        email = request.args.get('email', '')
        if not email:
            return ErrorMessageUtils.bad_request('Email is required')
        
        client_id = current_app.config.get('JAMENDO_CLIENT_ID')

        # Example music IDs for testing
        music_id = [
            "1127042",
            "1036834"
        ]

        if not music_id or not client_id:
            return ErrorMessageUtils.bad_request()
        
        musics = []
        for id in music_id:
            print("music id:", id)
            url = f'https://api.jamendo.com/v3.0/tracks?client_id={client_id}&format=json&id={id}'
            try:
                response = requests.get(url)
                data = response.json()
                if data.get('headers', {}).get('code', None) != 0:
                    continue 
                    
                results = data.get('results', [])
                for music in results:
                    duration = music.get('duration')
                    musics.append({
                        'id': music.get('id'),
                        'title': music.get('name'),
                        'audio': music.get('audio'),
                        'artist': music.get('artist_name'),
                        'album': music.get('album_name'),
                        'thumbnail': music.get('image'),
                        'duration': format_duration(duration),
                    })
            except Exception as e:
                print("Error fetching data:", str(e))
                return ErrorMessageUtils.internal_error()
        
        return {
            'status': 200,
            'message': 'Music found successfully',
            'email': email,
            'data': musics,
        }, 200
        
class GetMusicFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            musicData = MusicFavouriteModel.getAllMusicFavourites(userId)
            return {
                'status': 200,
                'message': 'Favourite music found successfully',
                'data': musicData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite music data')

def format_duration(seconds):
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    # Format as MM:SS
    return f"{minutes:02}:{remaining_seconds:02}"