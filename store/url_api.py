from flask_restful import Api

from resources.healthcheckher_resource import HealthCheckerResources
from resources.authentication_resource import *
from resources.questionnaire_resource import *
from resources.features_resource import *
from resources.user_profile_resource import *

def initialize_routes(api: Api):
    # declare API url here
    api.add_resource(HealthCheckerResources, '/api/v1/health-checker')  

    api.add_resource(UserLoginResource, '/api/v1/login-user')
    api.add_resource(UserRegisterResource, '/api/v1/register-user')
    api.add_resource(SendEmailOtpVerificationResource, '/api/v1/email-otp-verification')
    api.add_resource(ResetPasswordResource, '/api/v1/reset-password')
    api.add_resource(RefreshTokenResource, '/api/v1/refresh-token')
    api.add_resource(UserLogoutResource, '/api/v1/logout-user')
    api.add_resource(DeleteUserDataResource, '/api/v1/delete-user')

    api.add_resource(GetListEmotionResource, '/api/v1/get-list-emotion')
    api.add_resource(UserQuestionnaireAnswerResource, '/api/v1/user-questionnaire-answer')

    api.add_resource(GetBookListResource, '/api/v1/get-book-list')
    api.add_resource(GetVideoListResource, '/api/v1/get-video-list')
    api.add_resource(GetMusicListResource, '/api/v1/get-music-list')

    api.add_resource(GetBookListV2Resource, '/api/v2/get-book-list')
    api.add_resource(GetVideoListV2Resource, '/api/v2/get-video-list')
    api.add_resource(GetMusicListV2Resource, '/api/v2/get-music-list')

    api.add_resource(ChatbotGeneratedResponseResource, '/api/v1/chatbot-response')

    api.add_resource(BookFavouriteResource, '/api/v1/book-favourite')
    api.add_resource(VideoFavouriteResource, '/api/v1/video-favourite')
    api.add_resource(MusicFavouriteResource, '/api/v1/music-favourite')

    api.add_resource(GetBookFavouriteListResource, '/api/v1/get-book-favourite-list')
    api.add_resource(GetVideoFavouriteListResource, '/api/v1/get-video-favourite-list')
    api.add_resource(GetMusicFavouriteListResource, '/api/v1/get-music-favourite-list')

    api.add_resource(GetBookFavouriteListV2Resource, '/api/v2/get-book-favourite-list')
    api.add_resource(GetVideoFavouriteListV2Resource, '/api/v2/get-video-favourite-list')
    api.add_resource(GetMusicFavouriteListV2Resource, '/api/v2/get-music-favourite-list')

    api.add_resource(UserProfileDataResource, '/api/v1/user-profile')