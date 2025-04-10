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

    api.add_resource(UserQuestionnaireAnswerResource, '/api/v1/user-questionnaire-answer')

    api.add_resource(GetBookListResource, '/api/v1/get-book-list')
    api.add_resource(GetBookListV2Resource, '/api/v2/get-book-list')
    api.add_resource(GetBookDetailDataResource, '/api/v1/get-book-detail-data')
    api.add_resource(GetVideoListResource, '/api/v1/get-video-list')
    api.add_resource(GetMusicListResource, '/api/v1/get-song-list')
    api.add_resource(GetSongsListResource, '/api/v2/get-song-list')

    api.add_resource(UserProfileDataResource, '/api/v1/user-profile')