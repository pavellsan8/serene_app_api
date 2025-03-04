from marshmallow import fields
from marshmallow.validate import Length
from store.ma import ma

# Contoh Schemas
class UserLoginSchema(ma.Schema):
    username = fields.String(
        required=True, 
        allow_none=False,
        validate=Length(min=1, error="Username cannot be empty, minimum 1 characters."),
        error_messages={
            "required": "Please provide a valid username.", 
            "null": "Username cannot be null."
        }
    )
    password = fields.String(
        required=True, 
        allow_none=False,
        validate=Length(min=3, error="Password cannot be empty, minimum 3 characters."),
        error_messages={
            "required": "Please provide a valid password.",
            "null": "Password cannot be null."
        }
    )