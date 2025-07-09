from flask import request
from flask_restful import Resource

from models.m_feeling_model import MFeelingModel
from models.users_model import UsersModel
from models.questionnaire_model import QuestionnaireModel
from schemas.questionnaire_schema import *
from services.questionnaire_service import UserQuestionnaireAnswerService
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils

class GetListEmotionResource(Resource):
    def get(self):
        data = MFeelingModel.get_all_feelings()
        return {
            'status': 200,
            'message': 'List of Emotion',
            'data': data,
        }

class UserQuestionnaireAnswerResource(Resource): 
    def post(self):
        try: 
            data = UserQuestionnaireAnswerSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request()
        
        userAnswer = UserQuestionnaireAnswerService.submit_answer(data)
        if isinstance(userAnswer, dict) and 'error' in userAnswer:
            return userAnswer, 400

        return {
            'status': 200,
            'message': 'Questionnaire Answered Successfully',
            'data': userAnswer,
        }, 200
    
    def put(self):
        try: 
            data = UserQuestionnaireAnswerSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request()
        
        userAnswer = UserQuestionnaireAnswerService.update_answer(data)
        if isinstance(userAnswer, dict) and 'error' in userAnswer:
            return userAnswer, 400

        return {
            'status': 200,
            'message': 'Questionnaire Answered Successfully',
            'data': userAnswer,
        }, 200