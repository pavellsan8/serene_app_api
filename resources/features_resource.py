import requests

from flask_restful import Resource
from flask import request
from googleapiclient.discovery import build
from store.ytmusic import ytmusic

from instance.config import GOOGLE_API_KEY

class GetBookListResource(Resource):
    def get(self):
        query = request.args.get('query', '')
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}'
        
        response = requests.get(url)
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

class GetVideoListResource(Resource):
    def get(self):
        query = request.args.get('query', '')  # Default query if not provided
        youtube = build('youtube', 'v3', developerKey=GOOGLE_API_KEY)

        videos = []  # List to store videos

        while len(videos) < 100:  # Fetch up to 100 videos
            yt_request = youtube.search().list(
                part='snippet',
                q=query,
                maxResults=50,  # Max limit per request
            )
            response = yt_request.execute()

            for item in response.get('items', []):
                video_id = item['id'].get('videoId', 'N/A')  # Extract video ID
                videos.append({
                    'title': item['snippet']['title'],
                    'video_id': video_id,
                    'youtube_link': f'https://www.youtube.com/watch?v={video_id}' if video_id != 'N/A' else 'N/A',
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet']['description'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                })

        return {
            'status': 200,
            'message': 'Videos found successfully',
            'data': videos[:100]  # Limit to 100 results
        }
    
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
    
    def get(self):
        query = request.args.get('query', '')
        limit = 15

        songs = self.search_songs(query, limit)
        
        return {
            "status": 200,
            "message": "Songs found successfully",
            "data": songs
        }, 200