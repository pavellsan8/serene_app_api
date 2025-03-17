import requests

from flask_restful import Resource
from flask import request, current_app
from googleapiclient.discovery import build
from store.ytmusic import ytmusic
from flask_jwt_extended import jwt_required

from helpers.error_message import ErrorMessageUtils

class GetBookListResource(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('query', '')
        google_api_key = current_app.config.get('GOOGLE_API_KEY')

        if not query or google_api_key:
            return ErrorMessageUtils.bad_request
        
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={google_api_key}'
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return ErrorMessageUtils.internal_error
            
            data = response.json()
            
            books = []
            for book in data.get('items', []):
                info = book['volumeInfo']
                access = book['accessInfo']
                books.append({
                    'title': info.get('title', 'Unknown'),
                    'author': info.get('authors', ['Unknown']),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview_link': info.get('previewLink', ''),
                    'pages': info.get('pageCount', ''),
                    'published_date': info.get('publishedDate', 'Unknown'),
                    'description': info.get('description', ''),
                    'web_reader': access.get('webReaderLink', ''),
                })
            
            return {
                'status': 200,
                'message': 'Book found successfully',
                'data': books,
            }, 200
    
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.internal_error

class GetVideoListResource(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('query', '')
        google_api_key = current_app.config.get('GOOGLE_API_KEY')

        if not query or google_api_key:
            return ErrorMessageUtils.bad_request
        
        try:
            youtube = build('youtube', 'v3', developerKey=google_api_key)
            videos = []  # List to store videos
            
            # Only make one request to avoid excessive quota usage
            yt_request = youtube.search().list(
                part='snippet',
                q=query,
                maxResults=50,  # Max limit per request
            )
            response = yt_request.execute()

            for item in response.get('items', []):
                if 'videoId' in item.get('id', {}):
                    video_id = item['id']['videoId']
                    videos.append({
                        'title': item['snippet']['title'],
                        'video_id': video_id,
                        'youtube_link': f'https://www.youtube.com/watch?v={video_id}',
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'description': item['snippet']['description'],
                        'thumbnail_url': item['snippet']['thumbnails']['high']['url']
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
    
class GetSongsListResource(Resource):
    def search_songs(self, query, limit=10):
        results = ytmusic.search(query, filter="songs", limit=limit)

        songs = []
        for song in results:
            songs.append({
                "title": song["title"],
                "video_id": song["videoId"],
                "youtube_music_link": f"https://music.youtube.com/watch?v={song['videoId']}",
                "artist": song["artists"][0]["name"],
                "album": song["album"]["name"] if "album" in song else "N/A",
                "duration": song.get("duration", "N/A"),
                "thumbnail": song["thumbnails"][-1]["url"]
            })

        return songs
    
    @jwt_required()
    def get(self):
        try:
            query = request.args.get('query', '')
            limit = 15

            songs = self.search_songs(query, limit)
            
            return {
                "status": 200,
                "message": "Songs found successfully",
                "data": songs
            }, 200
        
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.internal_error
        
class GetBookListV2Resource(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('query', '')
        if not query:
            return ErrorMessageUtils.bad_request
        
        url = f'https://www.dbooks.org/api/search/{query}'

        try:
            response = requests.get(url)
            if response.status_code != 200:
                return ErrorMessageUtils.internal_error
            
            data = response.json()

            books = []
            for book in data.get('books', []):

                books.append({
                    'id': book.get('id').rstrip('X'),
                    'title': book.get('title'),
                    'subtitle': book.get('subtitle'),
                    'authors': book.get('authors'),
                    'image': book.get('image'),
                    'url': book.get('url'),
                })

            return {
                'status': 200,
                'message': 'Book found successfully',
                'data': books,
            }, 200
        
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.internal_error

class GetBookDetailDataResource(Resource):
    @jwt_required()
    def get(self):
        book_id = request.args.get('bookId', '') 
        if not book_id:
            return ErrorMessageUtils.bad_request

        url = f'https://www.dbooks.org/api/book/{book_id}'

        try:
            response = requests.get(url)
            if response.status_code != 200:
                return ErrorMessageUtils.internal_error

            data = response.json()
            data.pop('status', None)

            return {
                'status': 200,
                'message': f"Book detail data {data.get('id')}",
                'data': data
            }, 200

        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.internal_error