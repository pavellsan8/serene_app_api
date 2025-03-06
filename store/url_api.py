from flask_restful import Api

from resources.healthcheckher_resources import healthCheckerResources
from resources.authentication_resources import *

def initialize_routes(api: Api):
    # declare API url here
    api.add_resource(healthCheckerResources, '/api/v1/health-checker')  

    api.add_resource(userLoginResource, '/api/v1/login-user')
    api.add_resource(userRegisterResource, '/api/v1/register-user')
    api.add_resource(sendEmailOtpVerificationResource, '/api/v1/email-otp-verification')
    api.add_resource(resetPasswordResource, '/api/v1/reset-password')
    api.add_resource(refreshTokenResource, '/api/v1/refresh-token')