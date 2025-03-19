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
        userEmotion = data['emotion']
        userMood = data['mood']

        try:
            # 2 Table :
            # 1. Feeling & Emotion
            # 2. Mood
            # DbUtils.save_to_db()
            userAnswer = []
            moodAnswer = []

            for mood in userMood:
                print(userEmail, userFeeling, userEmotion, mood)
                # moodAnswer.append({
                #     'mood': mood,
                # })
                moodAnswer.append(mood)

            userAnswer.append({
                'email': userEmail,
                'feeling': userFeeling,
                'emotion': userEmotion,
                'mood': moodAnswer,
            })

            return {
                'status': 200,
                'message': 'Questionnaire Answered Successfully',
                'data': userAnswer,
            }, 200
        
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("User registration failed. Please try again.")