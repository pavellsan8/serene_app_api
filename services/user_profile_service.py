from models.users_model import UsersModel
from helpers.error_message import ErrorMessageUtils

class UserProfileService:
    def get_user_profile(email):
        userData = UsersModel.getEmailFirst(email)

        if not userData:
            return ErrorMessageUtils.not_found("User data not found.")
        
        userName = userData.user_name
        return {
            "name": userName,
            "email": email,
        }
    
    def update_user_profile(data):
        userName = data['name']
        userEmail = data['email']

        try:
            UsersModel.updateUserProfile(userName, userEmail)
            return {
                "name": userName,
                "email": userEmail,
            }
        
        except Exception as e:
            print("Validation error:", str(e))
            return ErrorMessageUtils.bad_request("Failed to update user profile.")