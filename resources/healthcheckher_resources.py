from flask_restful import Resource
from flask import request
from flask_restful import Resource

class healthCheckerResources(Resource):
    def get(self):    
        return {
            "status": 200,
            "message": "API safety check",
        }, 200