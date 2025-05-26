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
            else:
                return ErrorMessageUtils.bad_request('Book not found in favourites')

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
                
                book = response.json()
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
                
            except Exception as e:
                print("Error fetching data:", str(e))
                return ErrorMessageUtils.internal_error()
        
        return {
            'status': 200,
            'message': 'Book found successfully',
            'email' : email,
            'data': books,
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
        
def extract_year(date):
    if date == 'Unknown':
        return date
    # Cari angka 4 digit pertama
    match = re.match(r'\d{4}', date)
    return match.group(0) if match else 'Unknown'