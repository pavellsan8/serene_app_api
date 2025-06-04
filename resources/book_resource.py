from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

from schemas.user_profile_schema import UserFavouriteSchema
from services.book_service import *
from helpers.error_message import ErrorMessageUtils

class GetBookListResource(Resource):
    @jwt_required()
    def get(self):
        books = GetBookListService.get_book_list()
        if isinstance(books, tuple):
            return books
            
        return {
            'status': 200,
            'message': 'Book found successfully',
            'data': books,
        }, 200
        
class GetBookListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetBookListService.get_book_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Book found successfully',
            'data': data,
        }, 200

class BookFavouriteResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        savedBook = BookFavouriteService.add_book_to_favourite(data)
        if isinstance(savedBook, tuple):
            return savedBook
            
        return {
            'status': 200,
            'message': 'Book added to favourites successfully',
            'email': savedBook['email'],
            'book_id': savedBook['book_id'],
        }, 200
    
    @jwt_required()
    def delete(self):
        try:
            data = UserFavouriteSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')
        
        removeBook = BookFavouriteService.delete_book_from_favourite(data)
        if isinstance(removeBook, tuple):
            return removeBook

        return {
            'status': 200,
            'message': 'Book removed from favourites successfully',
            'email': removeBook['email'],
            'book_id': removeBook['book_id'],
        }, 200

class GetBookFavouriteListResource(Resource):
    @jwt_required()
    def get(self):
        data = GetBookFavouriteListService.get_book_favourite_list()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Book found successfully',
            'data': data,
        }, 200

class GetBookFavouriteListV2Resource(Resource):
    @jwt_required()
    def get(self):
        data = GetBookFavouriteListService.get_book_favourite_list_v2()
        if isinstance(data, tuple):
            return data
        
        return {
            'status': 200,
            'message': 'Favourite book found successfully',
            'data': data,
        }, 200