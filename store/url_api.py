from flask_restful import Api
from resources.healthcheckher_resources import HealthCheckerResources
from resources.useractivity_resource import *

def initialize_routes(api: Api):
    # declare API url here
    api.add_resource(HealthCheckerResources, '/api/v1/health-checker')    
    api.add_resource(LoginUserResource, '/api/v1/login_user')