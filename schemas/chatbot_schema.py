from marshmallow import fields
from store.ma import ma

class UserInputChatbotSchema(ma.Schema):
    user_input = fields.String(required=True, allow_none=False, error_messages={"required": "Please provide a valid user input."})