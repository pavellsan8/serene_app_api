from flask_restful import Api

from resources.healthcheckher_resource import HealthCheckerResources
from resources.authentication_resource import *
from resources.user_profile_resource import *

def initialize_routes(api: Api):
    # declare API url here
    api.add_resource(HealthCheckerResources, '/api/v1/health-checker')  

    api.add_resource(UserLoginResource, '/api/v1/login-user')
    api.add_resource(UserRegisterResource, '/api/v1/register-user')
    api.add_resource(SendEmailOtpVerificationResource, '/api/v1/email-otp-verification')
    api.add_resource(ResetPasswordResource, '/api/v1/reset-password')
    api.add_resource(RefreshTokenResource, '/api/v1/refresh-token')

    api.add_resource(UserProfileDataResource, '/api/v1/user-profile')
    api.add_resource(UserLogoutResource, '/api/v1/logout-user')