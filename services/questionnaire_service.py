from models.users_model import UsersModel
from models.questionnaire_model import QuestionnaireModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils

class UserQuestionnaireAnswerService:
    def submit_answer(data):
        userEmail = data['email']
        userEmotion = data['emotion']

        if userEmotion is None or len(userEmotion) == 0:
            return ErrorMessageUtils.bad_request("Emotion list cannot be empty.")

        try:
            userAnswer = []
            emotionAnswer = []

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
                    UsersModel.updateStatusSubmitQuestionnaire(userEmail)
                except Exception as e:
                    print("Error:", str(e))
                    return ErrorMessageUtils.bad_request("Failed to save questionnaire answer. Please try again.")

            userAnswer.append({
                'email': userEmail,
                'emotion': emotionAnswer,
            }) 
            return userAnswer
        
        except Exception as e:
            print("Error:", str(e))
            return ErrorMessageUtils.bad_request("Failed to save questionnaire answer. Please try again.")