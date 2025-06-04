from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

from helpers.error_message import ErrorMessageUtils
from schemas.chatbot_schema import UserInputChatbotSchema
from services.chatbot_service import ChatbotResponseService
    
class ChatbotGeneratedResponseResource(Resource):
    @jwt_required()
    def post(self):
        try: 
            data = UserInputChatbotSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')

        response_text = ChatbotResponseService.chatbot_response(data)
        if isinstance(response_text, tuple):
            return response_text

        return {
            'status': 200,
            'message': 'Chatbot response generated successfully',
            'response': response_text,
        }, 200