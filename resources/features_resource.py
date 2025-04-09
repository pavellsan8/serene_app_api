import requests
import re
import concurrent.futures

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

        if not query or not google_api_key:
            return ErrorMessageUtils.bad_request()
        
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={google_api_key}'
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return ErrorMessageUtils.internal_error()
            
            data = response.json()
            
            books = []
            for book in data.get('items', []):
                info = book.get('volumeInfo', {})
                access = book.get('accessInfo', {})
                books.append({
                    'title': info.get('title', 'Unknown'),
                    'author': info.get('authors', ['Unknown']),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview_link': info.get('previewLink', ''),
                    'pages': info.get('pageCount', ''),
                    'published_date': self.extract_year(info.get('publishedDate', 'Unknown')),
                    'description': info.get('description', ''),
                    'web_reader': access.get('webReaderLink', ''),
                })
            
            return {
                'status': 200,
                'message': 'Book found successfully',
                'data': books,
            }, 200
    
        except Exception as e:
            print("Error fetchin data:", str(e))
            return ErrorMessageUtils.internal_error()
        
    def extract_year(self, date):
        if date == 'Unknown':
            return date
        # Cari angka 4 digit pertama
        match = re.match(r'\d{4}', date)
        return match.group(0) if match else 'Unknown'

class GetVideoListResource(Resource):
    @staticmethod
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
                    durationParse = GetVideoListResource.parse_youtube_duration(duration)
                    
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
    
class GetSongsListResource(Resource):
    def search_songs(self, query, limit=10):
        results = ytmusic.search(query, filter="songs", limit=limit)

        songs = []
        for song in results:
            songs.append({
                "title": song["title"],
                "video_id": song["videoId"],
                "youtube_link": f"https://music.youtube.com/watch?v={song['videoId']}",
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
            total = data.get('total')
            print(total)

            def fetch_book_details(book):
                try:
                    book_id = book.get('id').rstrip('X')
                    detail_url = f'https://www.dbooks.org/api/book/{book_id}'
                    
                    detail_response = requests.get(detail_url, timeout=10)
                    if detail_response.status_code != 200:
                        print(f"Failed to get details for book {book_id}")
                        return None

                    detail_data = detail_response.json()

                    return {
                        'id': book.get('id').rstrip('X'),
                        'title': book.get('title'),
                        'subtitle': book.get('subtitle'),
                        'authors': book.get('authors'),
                        'description': detail_data.get('description', ''),
                        'pages': detail_data.get('pages'),
                        'year': detail_data.get('year'),
                        'image': book.get('image'),
                        'url': book.get('url'),
                        'download': detail_data.get('download'),
                    }
                except Exception as detail_error:
                    print(f"Error fetching details for book {book.get('id')}: {detail_error}")
                    return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                books = list(filter(None, executor.map(fetch_book_details, data.get('books', []))))

            return {
                'status': 200,
                'message': 'Book found successfully',
                'total': total,
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