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
                    'id': book.get('id'),
                    'title': info.get('title', 'Unknown'),
                    'author': ', '.join(info.get('authors', ['Unknown'])),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview_link': info.get('previewLink', ''),
                    'pages': info.get('pageCount', ''),
                    'published_date': extract_year(info.get('publishedDate', 'Unknown')),
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
        
class GetBookListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            bookData = BookModel.getBookByFeelingId(userId)
            return {
                'status': 200,
                'message': 'Book found successfully',
                'data': bookData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching book data')

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

class BookFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        bookId = data['item_id']

        favouriteData = BookFavouriteModel.getBookFirstFavourite(userId, bookId)
        if favouriteData:
            return ErrorMessageUtils.bad_request('Book already in favourites')

        try :
            favouriteData = BookFavouriteModel(
                user_id=userId,
                book_id=bookId,
                saved_at=datetime.datetime.now(datetime.timezone.utc),
            )

            # Simulate saving to database
            DbUtils.save_to_db(favouriteData)
            print(f"Saving book ID {bookId} for user {userEmail}")
            
            return {
                'status': 200,
                'message': 'Book added to favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'book_id': bookId
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
        bookId = data['item_id']

        try :
            # Simulate deleting from database
            favouriteData = BookFavouriteModel.getBookFirstFavourite(userId, bookId)

            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
                print(f"Deleting book ID {bookId} for user {userEmail}")

            return {
                'status': 200,
                'message': 'Book removed from favourites successfully',
                'user_id': userId,
                'email': userEmail,
                'book_id': bookId
            }, 200

        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')

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

class GetBookFavouriteListResource(Resource):
    @jwt_required()
    def get(self):
        email = request.args.get('email', '')
        if not email:
            return ErrorMessageUtils.bad_request('Email is required')
        
        google_api_key = current_app.config.get('GOOGLE_API_KEY')

        # Example book IDs for testing
        book_id = [
            "I9B4dG4XJ8AC",
            "wceHDwAAQBAJ"
        ]

        if not book_id or not google_api_key:
            return ErrorMessageUtils.bad_request()
                
        books = []
        for id in book_id:
            print("book id:", id)
            url = f'https://www.googleapis.com/books/v1/volumes/{id}?key={google_api_key}'

            try:
                response = requests.get(url)
                if response.status_code != 200:
                    continue
                
                book = response.json()  # This is now a single book, not search results
                info = book.get('volumeInfo', {})
                access = book.get('accessInfo', {})
                books.append({
                    'id': book.get('id'),
                    'title': info.get('title', 'Unknown'),
                    'author': info.get('authors', ['Unknown']),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview_link': info.get('previewLink', ''),
                    'pages': info.get('pageCount', ''),
                    'published_date': extract_year(info.get('publishedDate', 'Unknown')),
                    'description': info.get('description', ''),
                    'web_reader': access.get('webReaderLink', ''),
                })
                
            except Exception as e:
                print("Error fetching data:", str(e))
                return ErrorMessageUtils.internal_error()
        
        return {
            'status': 200,
            'message': 'Book found successfully',
            'email' : email,
            'data': books,
        }, 200
            
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

class GetBookFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            bookData = BookFavouriteModel.getAllBookFavourites(userId)
            return {
                'status': 200,
                'message': 'Favourite book found successfully',
                'data': bookData['data'],
            }, 200

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite book data')

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
    
class ChatbotGeneratedResponseResource(Resource):
    @jwt_required()
    def post(self):
        try: 
            data = UserInputChatbotSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')

        userInput = data['user_input']
        print ("User input:", userInput)

        client = get_openai_client()
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "You are a virtual mental health assistant who is friendly, empathetic, and supportive. Your task is to listen and respond to users’ questions or concerns in a way that feels human, relatable, and relevant.\n\nUse a warm yet professional tone, and adapt your approach based on the user’s situation—whether they are stressed, anxious, sad, confused, or simply in need of someone to talk to.\n\nYou do not provide medical diagnoses or treatments, but you can suggest relaxation techniques, offer emotional support, or recommend seeking professional help if needed.\n\nIf the input message didn't related to mental health, the answer must be like this :\n\"I’d love to help where I can, but my focus is on mental health and emotional well-being. If there’s something along those lines you’d like to talk about, I’m here for you.\"\n\nYour responses must:\n- Be as simple and straightforward as possible.\n- Reflective (show that you understand the user's feelings).\n- Tailored to the context of the user’s input, not a generic template.\n- Written in everyday language that is polite and easy to read.\n- Avoid being overly directive or sounding like unsolicited advice.\n\nExample tone:\n- “That must feel really heavy for you...”\n- “You’ve come this far, and that’s something to be proud of.”\n- “Feel free to share more if you’re comfortable.”\n\nIf a user seems highly distressed or shows signs of danger (such as self-harm), respond seriously and empathetically, and gently encourage them to seek professional help without sounding judgmental."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": userInput
                        }
                    ]
                }
            ],
            text={
                "format": {
                "type": "text"
                }
            },
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
        )
        
        response_text = response.output[0].content[0].text

        return {
            'status': 200,
            'message': 'Chatbot response generated successfully',
            'response': response_text,
        }, 200
        
def extract_year(date):
    if date == 'Unknown':
        return date
    # Cari angka 4 digit pertama
    match = re.match(r'\d{4}', date)
    return match.group(0) if match else 'Unknown'

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

def format_duration(seconds):
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    # Format as MM:SS
    return f"{minutes:02}:{remaining_seconds:02}"