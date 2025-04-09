from flask import request
from flask_restful import Resource

from schemas.questionnaire_schema import *
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils

class UserQuestionnaireAnswerResource(Resource): 
    def post(self):
        try: 
            data = UserQuestionnaireAnswerSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request()
        
        userEmail = data['email']
        userFeeling = data['feeling']
        userMood = data['mood']
        userEmotion = data['emotion']

        try:
            # 2 Table :
            # 1. Feeling & Emotion
            # 2. Mood
            # DbUtils.save_to_db()
            userAnswer = []
            emotionAnswer = []

            for emotion in userEmotion:
                emotionAnswer.append(emotion)
            
            print(userEmail, userFeeling, userMood, userEmotion)

            userAnswer.append({
                'email': userEmail,
                'feeling': userFeeling,
                'mood': userMood,
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