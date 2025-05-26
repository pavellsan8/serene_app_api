import datetime
import requests
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

class GetVideoListResource(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('query', '')
        google_api_key = current_app.config.get('GOOGLE_API_KEY')
        if not query or google_api_key is None:
            return ErrorMessageUtils.bad_request()
        
        try:
            youtube = build('youtube', 'v3', developerKey=google_api_key)
            videos = []
            
            search_request = youtube.search().list(
                part='snippet',
                q=query,
                maxResults=50,  # Max limit per request
                type='video' 
            )
            search_response = search_request.execute()
            
            # Extract video IDs
            video_ids = [
                item['id']['videoId'] 
                for item in search_response.get('items', []) 
                if 'videoId' in item.get('id', {})
            ]
            
            # Fetch video details including duration
            if video_ids:
                video_details_request = youtube.videos().list(
                    part='snippet,contentDetails',
                    id=','.join(video_ids)
                )
                video_details_response = video_details_request.execute()
                
                # Create a dictionary for quick lookup of details
                details_dict = {
                    item['id']: item 
                    for item in video_details_response.get('items', [])
                }
            
            # Process and combine search and details results
            for item in search_response.get('items', []):
                if 'videoId' in item.get('id', {}):
                    video_id = item['id']['videoId']
                    
                    # Get additional details from the details dictionary
                    video_detail = details_dict.get(video_id, {})
                    duration = video_detail.get('contentDetails', {}).get('duration', 'N/A')
                    durationParse = parse_youtube_duration(duration)
                    
                    videos.append({
                        'title': item['snippet']['title'],
                        'video_id': video_id,
                        'youtube_link': f'https://www.youtube.com/watch?v={video_id}',
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails']['high']['url'],
                        'duration': durationParse,
                    })
            
            return {
                'status': 200,
                'message': 'Videos found successfully',
                'data': videos
            }
        
        except Exception as e:
            error_message = str(e)
            if "quota" in error_message.lower():
                return {
                    'status': 429,
                    'message': 'YouTube API quota exceeded. Please try again tomorrow.',
                    'data': []
                }, 429
            else:
                return {
                    'status': 500,
                    'message': f'Error fetching videos: {error_message}',
                    'data': []
                }, 500

class GetVideoListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            videoData = VideoModel.getVideoByFeelingId(userId)
            return {
                'status': 200,
                'message': 'Video found successfully',
                'data': videoData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching video data')

class VideoFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        videoId = data['item_id']
        
        favouriteData = VideoFavouriteModel.getVideoFirstFavourite(userId, videoId)
        if favouriteData:
            return ErrorMessageUtils.bad_request('Video already in favourites')

        try :
            favouriteData = VideoFavouriteModel(
                user_id=userId,
                video_id=videoId,
                saved_at=datetime.datetime.now(datetime.timezone.utc),
            )

            # Simulate saving to database
            DbUtils.save_to_db(favouriteData)
            print(f"Saving video ID {videoId} for user {userEmail}")
            
            return {
                'status': 200,
                'message': 'Video added to favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'video_id': videoId
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
        videoId = data['item_id']

        try :
            # Simulate delete from database
            favouriteData = VideoFavouriteModel.getVideoFirstFavourite(userId, videoId)

            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
                print(f"Deleting video ID {videoId} for user {userEmail}")
            else:
                return ErrorMessageUtils.bad_request('Video not found in favourites')
                
            return {
                'status': 200,
                'message': 'Video removed from favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'video_id': videoId
            }, 200
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')
            
class GetVideoFavouriteListResource(Resource):
    @jwt_required()
    def get(self):        
        email = request.args.get('email')
        if not email:
            return ErrorMessageUtils.bad_request('Email is required')
        
        google_api_key = current_app.config.get('GOOGLE_API_KEY')

        # Example video IDs for testing
        video_id = [
            "lh4JdZTJe7k",
            "77ZozI0rw7w"
        ]

        if not video_id or google_api_key is None:
            return ErrorMessageUtils.bad_request()
        
        try:
            print("video id:", video_id)
            youtube = build('youtube', 'v3', developerKey=google_api_key)
            videos = []

            # Fetch video details using video_ids
            video_details_request = youtube.videos().list(
                part='snippet,contentDetails',
                id=','.join(video_id)
            )
            video_details_response = video_details_request.execute()

            for item in video_details_response.get('items', []):
                duration = item.get('contentDetails', {}).get('duration', 'N/A')
                duration_parsed = parse_youtube_duration(duration)

                videos.append({
                    'title': item['snippet']['title'],
                    'video_id': item['id'],
                    'youtube_link': f'https://www.youtube.com/watch?v={item["id"]}',
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'duration': duration_parsed,
                })

            return {
                'status': 200,
                'message': 'Favourite videos found successfully',
                'email': email,
                'data': videos
            }

        except Exception as e:
            error_message = str(e)
            if "quota" in error_message.lower():
                return {
                    'status': 429,
                    'message': 'YouTube API quota exceeded. Please try again tomorrow.',
                    'data': []
                }, 429
            else:
                return {
                    'status': 500,
                    'message': f'Error fetching favourite videos: {error_message}',
                    'data': []
                }, 500

class GetVideoFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            videoData = VideoFavouriteModel.getAllVideoFavourites(userId)
            return {
                'status': 200,
                'message': 'Favourite video found successfully',
                'data': videoData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite video data')

def parse_youtube_duration(duration):
    # Extract hours, minutes, seconds using regex
    hours_match = re.search(r'(\d+)H', duration)
    minutes_match = re.search(r'(\d+)M', duration)
    seconds_match = re.search(r'(\d+)S', duration)
    
    # Default to 0 if not found
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0
    
    # Format as HH:MM:SS
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"