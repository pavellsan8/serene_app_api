from flask import request
from flask_restful import Resource

from models.m_feeling_model import MFeelingModel
from models.users_model import UsersModel
from models.questionnaire_model import QuestionnaireModel
from schemas.questionnaire_schema import *
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils

class GetListEmotionResource(Resource):
    def get(self):
        data = MFeelingModel.get_all_feelings()
        return {
            'status': 200,
            'message': 'List of Emotion',
            'data': MFeelingModel.get_all_feelings(),
        }

class UserQuestionnaireAnswerResource(Resource): 
    def post(self):
        try: 
            data = UserQuestionnaireAnswerSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request()
        
        userEmail = data['email']
        userEmotion = data['emotion']

        try:
            userAnswer = []
            emotionAnswer = []

            # Get user ID
            userData = UsersModel.getEmailFirst(userEmail)

            for emotion in userEmotion:
                userId = userData.user_id
                emotionAnswer.append(emotion)

                questionnaireAnswer = QuestionnaireModel(
                    user_id=userId,
                    feeling_id=emotion,
                )

                try: 
                    DbUtils.save_to_db(questionnaireAnswer)
                except Exception as e:
                    print("Error:", str(e))
                    return ErrorMessageUtils.bad_request("Failed to save questionnaire answer. Please try again.")
            
            print(userEmail, userEmotion)

            userAnswer.append({
                'email': userEmail,
                'emotion': emotionAnswer,
            })

            return {
                'status': 200,
                'message': 'Questionnaire Answered Successfully',
                'data': userAnswer,
            }, 200
        
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("Failed to save questionnaire answer. Please try again.")