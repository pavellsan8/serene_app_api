import datetime
import requests

from flask import request, current_app
from flask_jwt_extended import get_jwt

from models.book_model import BookModel
from models.bookfavourite_model import BookFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import FeatureUtils, DbUtils

class GetBookListService:
    def get_book_list():
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
                    'published_date': FeatureUtils.extract_year(info.get('publishedDate', 'Unknown')),
                    'description': info.get('description', ''),
                    'web_reader': access.get('webReaderLink', ''),
                })
            return books
        
        except Exception as e:
            print("Error fetchin data:", str(e))
            return ErrorMessageUtils.internal_error()
        
    def get_book_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            bookData = BookModel.getBookByFeelingId(userId)
            return {
                'data': bookData['data'],
            }

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching book data')
        
class GetBookFavouriteListService:
    def get_book_favourite_list():
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
                    'published_date': FeatureUtils.extract_year(info.get('publishedDate', 'Unknown')),
                    'description': info.get('description', ''),
                    'web_reader': access.get('webReaderLink', ''),
                })
                
            except Exception as e:
                print("Error fetching data:", str(e))
                return ErrorMessageUtils.internal_error()
        
        return {
            'data': books,
        }
    
    def get_book_favourite_list_v2():
        claims = get_jwt()
        userId = claims.get("user_id")

        if not userId:
            return ErrorMessageUtils.bad_request('User ID is required')
        
        try:
            bookData = BookFavouriteModel.getAllBookFavourites(userId)
            return {
                'data': bookData['data'],
            }

        except Exception as e:
            print("Error fetching data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while fetching favourite book data')
        
class BookFavouriteService:
    def add_book_to_favourite(data):
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        bookId = data['item_id']

        favouriteData = BookFavouriteModel.getBookFirstFavourite(userId, bookId)
        if favouriteData:
            return ErrorMessageUtils.bad_request('Book already in favourites.')

        try :
            favouriteData = BookFavouriteModel(
                user_id=userId,
                book_id=bookId,
                saved_at=datetime.datetime.now(datetime.timezone.utc),
            )

            DbUtils.save_to_db(favouriteData)
            return {
                'email': userEmail,
                'book_id': bookId
            }
        
        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while adding to favorites.')
        
    def delete_book_from_favourite(data):
        claims = get_jwt()
        userId = claims.get("user_id")
        userEmail = data['email']
        bookId = data['item_id']

        try :
            favouriteData = BookFavouriteModel.getBookFirstFavourite(userId, bookId)

            if favouriteData:
                DbUtils.delete_from_db(favouriteData)
                print(f"Deleting book ID {bookId} for user {userEmail}")
            else:
                return ErrorMessageUtils.bad_request('Book not found in favourites')

            return {
                'email': userEmail,
                'book_id': bookId
            }

        except Exception as e:
            print("Error saving data:", str(e))
            return ErrorMessageUtils.internal_error('An error occurred while removing from favorites')