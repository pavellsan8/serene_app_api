import requests
import datetime

from flask import request, current_app
from flask_jwt_extended import get_jwt

from models.music_model import MusicModel
from models.musicfavourite_model import MusicFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import FeatureUtils, DbUtils

class GetMusicListService:
    def get_music_list():
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
                    'duration': FeatureUtils.format_duration(duration),
                })
            return {
                'data': musics,
            }
    
        except Exception as e:
            print("Error fetchin data:", str(e))
            return ErrorMessageUtils.internal_error()
        
    def get_music_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            musicData = MusicModel.getMusicByFeelingId(userId)
            return musicData['data'] if musicData and 'data' in musicData else []

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching music data')
        
class GetMusicFavouriteListService:
    def get_music_favourite_list():
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
                        'duration': FeatureUtils.format_duration(duration),
                    })
            except Exception as e:
                print("Error fetching data:", str(e))
                return ErrorMessageUtils.internal_error()
        
        return {
            'data': musics,
        }
    
    def get_music_favourite_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            musicData = MusicFavouriteModel.getAllMusicFavourites(userId)
            return musicData['data'] if musicData and 'data' in musicData else []

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite music data')
        
class MusicFavouriteService:
    def add_music_to_favourite(data):
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

            DbUtils.save_to_db(favouriteData)            
            return {
                'email': userEmail,
                'music_id': musicId
            }
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while adding to favorites')
        
    def delete_music_from_favourite(data):
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        musicId = data['item_id']

        try:
            favouriteData = MusicFavouriteModel.getMusicFirstFavourite(userId, musicId)

            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
            else:
                return ErrorMessageUtils.bad_request('Music not found in favourites')   

            return {
                'email': userEmail,
                'music_id': musicId
            }
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')