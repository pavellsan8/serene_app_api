import datetime

from flask import request, current_app
from googleapiclient.discovery import build
from flask_jwt_extended import get_jwt

from models.video_model import VideoModel
from models.videofavourite_model import VideoFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import FeatureUtils, DbUtils

class GetVideoListService:
    def get_video_list():
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
                    durationParse = FeatureUtils.parse_youtube_duration(duration)
                    
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
                'data': videos,
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

    def get_video_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            videoData = VideoModel.getVideoByFeelingId(userId)
            return {
                'data': videoData['data'],
            }

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching video data')
        
class GetVideoFavouriteListService:
    def get_video_favourite_list():
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
                duration_parsed = FeatureUtils.parse_youtube_duration(duration)

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
            
    def get_video_favourite_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            videoData = VideoFavouriteModel.getAllVideoFavourites(userId)
            return {
                'data': videoData['data'],
            }

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite video data')
        
class VideoFavouriteService:
    def add_video_to_favourite(data):
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

            DbUtils.save_to_db(favouriteData)            
            return {
                'email': userEmail,
                'video_id': videoId
            }
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while adding to favorites')
        
    def delete_video_from_favourite(data):
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        videoId = data['item_id']

        try :
            favouriteData = VideoFavouriteModel.getVideoFirstFavourite(userId, videoId)

            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
            else:
                return ErrorMessageUtils.bad_request('Video not found in favourites')
                
            return {
                'email': userEmail,
                'video_id': videoId
            }
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')