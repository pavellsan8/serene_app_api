class ErrorMessageUtils:
    def not_found(message=None):
        erorrMessage = "Data not found"
        if message:
            erorrMessage = message
        errorCode = 404
        return {"status": errorCode, "message": erorrMessage}, errorCode
    
    def bad_request(message=None):
        erorrMessage = "Bad Request"
        if message:
            erorrMessage = message
        errorCode = 400
        return {"status": errorCode, "message": erorrMessage}, errorCode
    
    def internal_error(message=None):
        erorrMessage = "INTERNAL SERVER ERROR"
        if message:
            erorrMessage = message
        errorCode = 500
        return {"status": errorCode, "message": erorrMessage}, errorCode
    
    @staticmethod
    def unauthorized_request(message):
        erorrMessage = message
        errorCode = 401
        return {"status": errorCode, "message": erorrMessage}, errorCode