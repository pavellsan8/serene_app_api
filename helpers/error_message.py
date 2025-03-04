# from store.ma import ValidationError

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
    
    def unauthorized_request(message):
        erorrMessage = message
        errorCode = 401
        return {"status": errorCode, "message": erorrMessage}, errorCode

    # def handle_error(resource_name, exception):
    #     if isinstance(exception, ValidationError):
    #         print(f'{resource_name}.post() - ValidationError:', exception.messages)
    #         return exception.messages, 400
    #     else:
    #         print(f'{resource_name}.post() - Exception:', str(exception))
    #         return {'status': 500, 'message': 'Internal Server Error'}, 500